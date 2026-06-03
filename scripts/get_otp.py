"""
Production OTP Fetcher — reads the latest OTP for a virtual test number.

Supported backends (set via PROD_OTP_BACKEND env var):
  receivesmsfast  — scrapes receivesmsfast.com      (free, no account, BD/US/many countries)
  quackr          — scrapes quackr.io               (free, no account, US/EU/many countries)
  smsonline       — scrapes sms-online.co           (free, no account, many countries)
  waha            — polls WAHA WhatsApp HTTP API    (free OSS Docker, real WhatsApp)
  whatsapp_local  — polls local whatsapp-web.js     (free OSS, real WhatsApp via QR)
  twilio          — polls Twilio WhatsApp API       (paid)
  fixed           — returns TEST_OTP env var        (staging/dev only)
  manual          — prompts tester to paste OTP    (CI-incompatible)

IMPORTANT: Mehad sends OTPs via WhatsApp. For production testing use one of:
  - waha            (run: docker run -p 3000:3000 devlikeapro/waha)
  - whatsapp_local  (run: cd scripts && node whatsapp_otp_server.js)
  The SMS-based backends (receivesmsfast / quackr / smsonline) only work if
  Mehad also sends an SMS fallback to the test number.

Environment variables
─────────────────────
# === STAGING / DEV (fixed OTP, no real message needed) ===
TEST_OTP=123456
TEST_PHONE=98976564
TEST_COUNTRY=+880

# === PRODUCTION — receivesmsfast.com (Bangladesh number) ===
PROD_OTP_BACKEND=receivesmsfast
RECEIVESMSFAST_NUMBER=8801755572498    # full number without + prefix
PROD_COUNTRY_CODE=+880
PROD_TEST_PHONE=1755572498

# === PRODUCTION — quackr.io (US/EU/BD numbers, no account) ===
PROD_OTP_BACKEND=quackr
QUACKR_NUMBER=12025551234             # full number without +
PROD_COUNTRY_CODE=+1
PROD_TEST_PHONE=2025551234

# === PRODUCTION — sms-online.co (many countries) ===
PROD_OTP_BACKEND=smsonline
SMSONLINE_NUMBER=12025551234
PROD_COUNTRY_CODE=+1

# === PRODUCTION — WAHA (free OSS Docker WhatsApp API, recommended) ===
# docker run -p 3000:3000 devlikeapro/waha
# Scan QR once at http://localhost:3000/dashboard
PROD_OTP_BACKEND=waha
WAHA_URL=http://localhost:3000
WAHA_SESSION=default
WAHA_CHAT_ID=+966XXXXXXXXX@c.us     # your test number in WhatsApp chat ID format

# === PRODUCTION — whatsapp-web.js local bridge (OSS, WhatsApp) ===
# cd scripts && npm install && node whatsapp_otp_server.js  (scan QR once)
PROD_OTP_BACKEND=whatsapp_local
WA_OTP_PORT=3001
"""

from __future__ import annotations
import os
import re
import sys
import time
import urllib.request
import json as _json
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))


# ── Helper ────────────────────────────────────────────────────────────────────

def _http_get(url: str, ua: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36") -> str:
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", errors="replace")


# ── Backend: receivesmsfast.com ───────────────────────────────────────────────

def _receivesmsfast_otp(phone_n: str, max_wait: int = 90) -> str | None:
    """
    Free, no account — Bangladesh/US/many countries.
    Messages publicly visible. Works for SMS-based OTPs.
    Set RECEIVESMSFAST_NUMBER=8801755572498
    """
    url = f"https://receivesmsfast.com/messages?n={phone_n}"

    def _parse(html: str) -> list[dict]:
        times = re.findall(r'class="message-time"[^>]*>\s*([^<]+)\s*<', html)
        texts = re.findall(r'class="message-text"[^>]*>\s*([^<]+)\s*<', html)
        out = []
        for t, msg in zip(times, texts):
            hit = re.search(r"\b(\d{6})\b", msg.strip())
            out.append({"time": t.strip(), "text": msg.strip(), "code": hit.group(1) if hit else ""})
        return out

    known: set[str] = set()
    try:
        known = {m["text"] for m in _parse(_http_get(url))}
        print(f"[OTP] receivesmsfast: {len(known)} existing messages snapshotted", flush=True)
    except Exception as exc:
        print(f"[OTP] receivesmsfast snapshot error: {exc}", flush=True)

    deadline = time.time() + max_wait
    print(f"[OTP] Polling receivesmsfast.com for +{phone_n} …", flush=True)
    while time.time() < deadline:
        time.sleep(5)
        try:
            for msg in _parse(_http_get(url)):
                if msg["text"] in known:
                    continue
                if msg["code"]:
                    print(f"[OTP] receivesmsfast OTP: {msg['code']}", flush=True)
                    return msg["code"]
        except Exception as exc:
            print(f"[OTP] receivesmsfast error: {exc}", flush=True)

    print(f"[OTP] receivesmsfast: no new OTP within {max_wait}s", flush=True)
    return None


# ── Backend: quackr.io ────────────────────────────────────────────────────────

def _quackr_otp(phone_n: str, max_wait: int = 90) -> str | None:
    """
    Free, no account — US/EU/BD and many country numbers.
    Works for SMS-based OTPs.
    Set QUACKR_NUMBER=12025551234  (full number without +)
    """
    # quackr exposes messages at /temporary-numbers/{country-code}/{number}
    # Try both the HTML page and any JSON endpoint
    url = f"https://quackr.io/temporary-numbers/{phone_n}"

    def _parse(html: str) -> list[str]:
        # quackr shows OTPs in .message-body or similar divs
        texts = re.findall(
            r'(?:message-body|msg-body|sms-body|message-text|sms-text)[^>]*>\s*([^<]{5,200})\s*<',
            html
        )
        if not texts:
            # Fallback: grab any 6-digit number near "code" keyword
            texts = re.findall(r'(?:code|otp|verification)[^\n]{0,50}?(\d{6})', html, re.IGNORECASE)
        return texts

    known: set[str] = set()
    try:
        known = set(_parse(_http_get(url)))
    except Exception:
        pass

    deadline = time.time() + max_wait
    print(f"[OTP] Polling quackr.io for +{phone_n} …", flush=True)
    while time.time() < deadline:
        time.sleep(5)
        try:
            texts = _parse(_http_get(url))
            for t in texts:
                if t in known:
                    continue
                hit = re.search(r"\b(\d{6})\b", t)
                if hit:
                    print(f"[OTP] quackr OTP: {hit.group(1)}", flush=True)
                    return hit.group(1)
        except Exception as exc:
            print(f"[OTP] quackr error: {exc}", flush=True)

    print(f"[OTP] quackr: no new OTP within {max_wait}s", flush=True)
    return None


# ── Backend: sms-online.co ────────────────────────────────────────────────────

def _smsonline_otp(phone_n: str, max_wait: int = 90) -> str | None:
    """
    Free, no account — US/BD/many countries.
    Set SMSONLINE_NUMBER=12025551234
    """
    url = f"https://sms-online.co/receive-free-sms/{phone_n}"

    def _parse(html: str) -> list[dict]:
        texts = re.findall(r'class="[^"]*(?:sms|message)[^"]*"[^>]*>\s*([^<]{5,200})\s*<', html)
        out = []
        for t in texts:
            hit = re.search(r"\b(\d{6})\b", t.strip())
            if hit:
                out.append({"text": t.strip(), "code": hit.group(1)})
        return out

    known: set[str] = set()
    try:
        known = {m["text"] for m in _parse(_http_get(url))}
    except Exception:
        pass

    deadline = time.time() + max_wait
    print(f"[OTP] Polling sms-online.co for +{phone_n} …", flush=True)
    while time.time() < deadline:
        time.sleep(5)
        try:
            for msg in _parse(_http_get(url)):
                if msg["text"] in known:
                    continue
                print(f"[OTP] sms-online OTP: {msg['code']}", flush=True)
                return msg["code"]
        except Exception as exc:
            print(f"[OTP] sms-online error: {exc}", flush=True)

    print(f"[OTP] sms-online: no new OTP within {max_wait}s", flush=True)
    return None


# ── Backend: WAHA (WhatsApp HTTP API — free OSS Docker) ──────────────────────

def _waha_otp(chat_id: str, max_wait: int = 90) -> str | None:
    """
    Poll WAHA (https://waha.devlike.pro/) for an OTP message.
    WAHA is a free, open-source WhatsApp HTTP API — runs in Docker.

    Setup (one-time):
      docker run -p 3000:3000 devlikeapro/waha
      Open http://localhost:3000/dashboard → scan QR with test phone
      Set WAHA_CHAT_ID=+8801755572498@c.us (or the full chat ID)

    Set in .env:
      PROD_OTP_BACKEND=waha
      WAHA_URL=http://localhost:3000
      WAHA_SESSION=default
      WAHA_CHAT_ID=+8801755572498@c.us
    """
    base    = os.environ.get("WAHA_URL", "http://localhost:3000").rstrip("/")
    session = os.environ.get("WAHA_SESSION", "default")

    # Clear snapshot of known messages first
    known_ids: set[str] = set()
    try:
        url = f"{base}/api/{session}/chats/{urllib.parse.quote(chat_id, safe='')}/messages?limit=20"
        data = _json.loads(_http_get(url))
        known_ids = {m.get("id", "") for m in (data if isinstance(data, list) else [])}
    except Exception:
        pass

    deadline = time.time() + max_wait
    print(f"[OTP] Polling WAHA for {chat_id} …", flush=True)
    while time.time() < deadline:
        time.sleep(4)
        try:
            url = f"{base}/api/{session}/chats/{urllib.parse.quote(chat_id, safe='')}/messages?limit=10"
            msgs = _json.loads(_http_get(url))
            if not isinstance(msgs, list):
                continue
            for msg in msgs:
                if msg.get("id") in known_ids:
                    continue
                body = msg.get("body", "") or msg.get("text", "") or ""
                hit = re.search(r"\b(\d{6})\b", body)
                if hit:
                    print(f"[OTP] WAHA OTP: {hit.group(1)}", flush=True)
                    return hit.group(1)
        except Exception as exc:
            print(f"[OTP] WAHA error: {exc}", flush=True)

    print(f"[OTP] WAHA: no new OTP within {max_wait}s", flush=True)
    return None


# ── Backend: local whatsapp-web.js bridge ────────────────────────────────────

def _whatsapp_local_otp(max_wait: int = 90) -> str | None:
    """
    Poll the local whatsapp-web.js bridge server for a fresh OTP.
    Start: cd scripts && npm install && node whatsapp_otp_server.js (scan QR once)
    """
    port = os.environ.get("WA_OTP_PORT", "3001")
    base = f"http://127.0.0.1:{port}"

    try:
        req = urllib.request.Request(f"{base}/clear", method="POST")
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass

    deadline = time.time() + max_wait
    print(f"[OTP] Polling local WhatsApp bridge at {base}/otp …", flush=True)
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base}/otp", timeout=5) as resp:
                if resp.status == 200:
                    data = _json.loads(resp.read())
                    otp = data.get("otp")
                    if otp:
                        print(f"[OTP] WhatsApp bridge OTP: {otp}", flush=True)
                        return otp
        except Exception:
            pass
        time.sleep(3)

    print(f"[OTP] WhatsApp bridge: no OTP within {max_wait}s", flush=True)
    return None


# ── Backend: Twilio ───────────────────────────────────────────────────────────

def _twilio_otp(to_number: str, max_wait: int = 60) -> str | None:
    try:
        from twilio.rest import Client  # type: ignore[import]
    except ImportError:
        raise RuntimeError("Twilio SDK not installed. Run: pip install twilio")

    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    from_n = os.environ.get("TWILIO_WHATSAPP_NUMBER", "+14155238886")
    deadline = time.time() + max_wait

    print(f"[OTP] Polling Twilio for OTP to {to_number} …", flush=True)
    while time.time() < deadline:
        for msg in client.messages.list(to=f"whatsapp:{to_number}", from_=f"whatsapp:{from_n}", limit=5):
            m = re.search(r"\b(\d{6})\b", msg.body or "")
            if m:
                print(f"[OTP] Twilio OTP: {m.group(1)}", flush=True)
                return m.group(1)
        time.sleep(3)

    print(f"[OTP] Twilio: no OTP within {max_wait}s", flush=True)
    return None


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_otp(
    phone: str | None = None,
    country: str | None = None,
    max_wait: int = 60,
) -> str:
    """
    Return a 6-digit OTP string using the configured backend.
    Call AFTER clicking 'Send Code' in the app.
    """
    import urllib.parse  # noqa: F401 — used by WAHA backend

    backend = os.environ.get(
        "PROD_OTP_BACKEND",
        "twilio" if os.environ.get("TWILIO_ACCOUNT_SID") else "fixed",
    )

    if backend == "receivesmsfast":
        phone_n = os.environ.get("RECEIVESMSFAST_NUMBER", "")
        if not phone_n:
            raise RuntimeError("Set RECEIVESMSFAST_NUMBER=<full_number_without_plus>")
        otp = _receivesmsfast_otp(phone_n, max_wait=max_wait)
        if otp:
            return otp
        raise RuntimeError(f"receivesmsfast: no new OTP within {max_wait}s for +{phone_n}")

    if backend == "quackr":
        phone_n = os.environ.get("QUACKR_NUMBER", "")
        if not phone_n:
            raise RuntimeError("Set QUACKR_NUMBER=<full_number_without_plus>")
        otp = _quackr_otp(phone_n, max_wait=max_wait)
        if otp:
            return otp
        raise RuntimeError(f"quackr: no new OTP within {max_wait}s for +{phone_n}")

    if backend == "smsonline":
        phone_n = os.environ.get("SMSONLINE_NUMBER", "")
        if not phone_n:
            raise RuntimeError("Set SMSONLINE_NUMBER=<full_number_without_plus>")
        otp = _smsonline_otp(phone_n, max_wait=max_wait)
        if otp:
            return otp
        raise RuntimeError(f"sms-online: no new OTP within {max_wait}s for +{phone_n}")

    if backend == "waha":
        chat_id = os.environ.get("WAHA_CHAT_ID", "")
        if not chat_id:
            raise RuntimeError("Set WAHA_CHAT_ID=+<country><number>@c.us")
        otp = _waha_otp(chat_id, max_wait=max_wait)
        if otp:
            return otp
        raise RuntimeError(f"WAHA: no OTP within {max_wait}s for {chat_id}")

    if backend == "whatsapp_local":
        otp = _whatsapp_local_otp(max_wait=max_wait)
        if otp:
            return otp
        raise RuntimeError("WhatsApp bridge: no OTP. Run: cd scripts && node whatsapp_otp_server.js")

    if backend == "twilio":
        _country = country or os.environ.get("PROD_COUNTRY_CODE", "+966")
        _local   = phone   or os.environ.get("PROD_TEST_PHONE",   "")
        if not _local:
            raise RuntimeError("PROD_TEST_PHONE required for Twilio backend.")
        e164 = f"{_country}{_local.lstrip('0')}"
        otp = _twilio_otp(e164, max_wait=max_wait)
        if otp:
            return otp
        raise RuntimeError(f"Twilio: no OTP within {max_wait}s for {e164}")

    if backend == "fixed":
        otp = os.environ.get("TEST_OTP") or os.environ.get("TEACHER_OTP") or os.environ.get("STUDENT_OTP")
        if otp:
            print(f"[OTP] Using fixed staging OTP: {otp}", flush=True)
            return otp
        raise RuntimeError("No fixed OTP. Set TEST_OTP or switch PROD_OTP_BACKEND.")

    if backend == "manual":
        print("\n" + "─" * 60, flush=True)
        print("[PROD OTP] A WhatsApp message with a 6-digit code has been", flush=True)
        print("           sent to your phone by Mehad.", flush=True)
        print("           Open WhatsApp and look for a message from Mehad.", flush=True)
        print("─" * 60, flush=True)
        for attempt in range(3):
            otp = input("[PROD OTP] Enter the 6-digit OTP from your WhatsApp: ").strip()
            if re.match(r"^\d{6}$", otp):
                print(f"[PROD OTP] OTP accepted: {otp}", flush=True)
                return otp
            print(f"[PROD OTP] That doesn't look right — need exactly 6 digits (got: {otp!r}). Try again.", flush=True)
        raise ValueError("Manual OTP: 3 failed attempts. Aborting.")

    raise RuntimeError(f"Unknown PROD_OTP_BACKEND: {backend!r}")


def get_test_credentials() -> dict:
    """Return active credentials for student/teacher roles (staging or prod)."""
    base_url = os.environ.get("BASE_URL", "https://dev.mehadedu.com/en")
    is_prod  = "mehadedu.com" in base_url and "dev." not in base_url

    if is_prod:
        country   = os.environ.get("PROD_COUNTRY_CODE",  "+880")
        std_phone = os.environ.get("PROD_STUDENT_PHONE", os.environ.get("PROD_TEST_PHONE", ""))
        tch_phone = os.environ.get("PROD_TEACHER_PHONE", os.environ.get("PROD_TEST_PHONE", ""))
        otp_fn    = lambda: fetch_otp(max_wait=90)
    else:
        country   = os.environ.get("TEST_COUNTRY", "+880")
        std_phone = os.environ.get("STUDENT_PHONE", os.environ.get("TEST_PHONE", "98976564"))
        tch_phone = os.environ.get("TEACHER_PHONE", os.environ.get("TEST_PHONE", "98976564"))
        fixed_otp = os.environ.get("TEST_OTP", "123456")
        otp_fn    = lambda: fixed_otp

    return {
        "student":  {"phone": std_phone, "country": country, "otp_fn": otp_fn},
        "teacher":  {"phone": tch_phone, "country": country, "otp_fn": otp_fn},
        "base_url": base_url,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse, urllib.parse

    parser = argparse.ArgumentParser(description="Fetch the latest OTP")
    parser.add_argument("--phone",   help="Local phone number (no country code)")
    parser.add_argument("--country", help="Country dial code, e.g. +880")
    parser.add_argument("--wait",    type=int, default=60)
    args = parser.parse_args()

    try:
        code = fetch_otp(phone=args.phone, country=args.country, max_wait=args.wait)
        print(f"OTP: {code}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
