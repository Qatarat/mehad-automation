"""
Production OTP Fetcher — reads the latest WhatsApp OTP for a virtual test number.

Supports three backends (tried in order based on available env vars):
  1. Twilio   — TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN + TWILIO_WHATSAPP_NUMBER
  2. Fixed    — TEST_OTP env var (dev/staging fallback, hardcoded in the server)
  3. Manual   — prompts the tester to paste the OTP (CI-incompatible fallback)

Environment variables
─────────────────────
# === STAGING / DEV ===
TEST_OTP=123456                  # hardcoded staging OTP (no real SMS needed)
TEST_PHONE=98976564              # staging phone number
TEST_COUNTRY=+880                # country dial code for staging

# === PRODUCTION ===
PROD_TEST_PHONE=561234567        # virtual phone local number (no country prefix)
PROD_COUNTRY_CODE=+966           # Saudi Arabia (matches app default)
PROD_OTP_BACKEND=twilio          # twilio | fixed | manual

# Twilio credentials (only needed when PROD_OTP_BACKEND=twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886   # Twilio sandbox / production number

# For staging — still use fixed OTP
TEACHER_OTP=123456
STUDENT_OTP=123456

Usage
─────
from scripts.get_otp import fetch_otp

otp = fetch_otp()   # reads from the configured backend, returns 6-digit string
"""

from __future__ import annotations
import os
import re
import sys
import time
from pathlib import Path

# Resolve project root so we can run this as a script too
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))


def _twilio_otp(to_number: str, max_wait: int = 60) -> str | None:
    """
    Poll Twilio for the most recent inbound WhatsApp message containing a
    6-digit OTP sent to `to_number`.  Waits up to `max_wait` seconds.

    `to_number` should be E.164 format, e.g. "+966561234567".
    """
    try:
        from twilio.rest import Client  # type: ignore[import]
    except ImportError:
        raise RuntimeError(
            "Twilio SDK not installed. Run: pip install twilio"
        )

    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token  = os.environ["TWILIO_AUTH_TOKEN"]
    from_number = os.environ.get("TWILIO_WHATSAPP_NUMBER", "+14155238886")

    client = Client(account_sid, auth_token)
    whatsapp_to = f"whatsapp:{to_number}"
    whatsapp_from = f"whatsapp:{from_number}"

    deadline = time.time() + max_wait
    poll_interval = 3

    print(f"[OTP] Polling Twilio for OTP to {to_number} …", flush=True)
    while time.time() < deadline:
        messages = client.messages.list(
            to=whatsapp_to,
            from_=whatsapp_from,
            limit=5,
        )
        for msg in messages:
            m = re.search(r"\b(\d{6})\b", msg.body or "")
            if m:
                print(f"[OTP] Found OTP via Twilio: {m.group(1)}", flush=True)
                return m.group(1)
        time.sleep(poll_interval)

    print(f"[OTP] Twilio: no OTP received within {max_wait}s", flush=True)
    return None


def fetch_otp(
    phone: str | None = None,
    country: str | None = None,
    max_wait: int = 60,
) -> str:
    """
    Return a 6-digit OTP string for the configured test phone.

    Decision tree:
      1. If PROD_OTP_BACKEND=twilio (or TWILIO_ACCOUNT_SID is set)
         → poll Twilio WhatsApp inbox
      2. If TEST_OTP / TEACHER_OTP is set in the environment
         → return it directly (staging / dev)
      3. Otherwise → raise RuntimeError with guidance
    """
    backend = os.environ.get(
        "PROD_OTP_BACKEND",
        "twilio" if os.environ.get("TWILIO_ACCOUNT_SID") else "fixed",
    )

    if backend == "twilio":
        # Build the full E.164 number
        _country = country or os.environ.get("PROD_COUNTRY_CODE", "+966")
        _local   = phone   or os.environ.get("PROD_TEST_PHONE",   "")
        if not _local:
            raise RuntimeError(
                "PROD_TEST_PHONE env var is required for Twilio OTP backend."
            )
        e164 = f"{_country}{_local.lstrip('0')}"
        otp = _twilio_otp(e164, max_wait=max_wait)
        if otp:
            return otp
        raise RuntimeError(
            f"Twilio OTP not received within {max_wait}s for {e164}. "
            "Check that the number is registered with the Twilio WhatsApp sandbox "
            "or production API, and that messages are being forwarded."
        )

    if backend == "fixed":
        # Dev / staging server returns a predictable OTP
        otp = (
            os.environ.get("TEST_OTP")
            or os.environ.get("TEACHER_OTP")
            or os.environ.get("STUDENT_OTP")
        )
        if otp:
            print(f"[OTP] Using fixed staging OTP: {otp}", flush=True)
            return otp
        raise RuntimeError(
            "No fixed OTP available. Set TEST_OTP in the environment "
            "or switch PROD_OTP_BACKEND=twilio for production testing."
        )

    if backend == "manual":
        # Last resort — CI-incompatible, for local dev only
        otp = input("Enter the OTP received on your test phone: ").strip()
        if re.match(r"^\d{6}$", otp):
            return otp
        raise ValueError(f"OTP must be exactly 6 digits, got: {otp!r}")

    raise RuntimeError(f"Unknown PROD_OTP_BACKEND: {backend!r}")


def get_test_credentials() -> dict:
    """
    Return the active test credentials dict keyed by role.

    On staging  → uses hardcoded phone/OTP from env.
    On prod     → PROD_TEST_PHONE + Twilio OTP fetch.

    Returns:
        {
          "student": {"phone": "...", "country": "+...", "otp_fn": callable},
          "teacher": {"phone": "...", "country": "+...", "otp_fn": callable},
          "base_url": "https://...",
        }
    """
    base_url  = os.environ.get("BASE_URL", "https://dev.mehadedu.com/en")
    is_prod   = "mehadedu.com" in base_url and "dev." not in base_url

    if is_prod:
        country      = os.environ.get("PROD_COUNTRY_CODE",  "+966")
        std_phone    = os.environ.get("PROD_STUDENT_PHONE", os.environ.get("PROD_TEST_PHONE", ""))
        tch_phone    = os.environ.get("PROD_TEACHER_PHONE", os.environ.get("PROD_TEST_PHONE", ""))
        otp_fn       = lambda: fetch_otp(max_wait=90)
    else:
        country      = os.environ.get("TEST_COUNTRY", "+880")
        std_phone    = os.environ.get("STUDENT_PHONE",  os.environ.get("TEST_PHONE", "98976564"))
        tch_phone    = os.environ.get("TEACHER_PHONE",  os.environ.get("TEST_PHONE", "98976564"))
        fixed_otp    = os.environ.get("TEST_OTP", "123456")
        otp_fn       = lambda: fixed_otp  # staging always returns the same OTP

    return {
        "student":  {"phone": std_phone, "country": country, "otp_fn": otp_fn},
        "teacher":  {"phone": tch_phone, "country": country, "otp_fn": otp_fn},
        "base_url": base_url,
    }


# ─── CLI helper ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch the latest WhatsApp OTP")
    parser.add_argument("--phone",   help="Local phone number (no country code)")
    parser.add_argument("--country", help="Country dial code, e.g. +966")
    parser.add_argument("--wait",    type=int, default=60, help="Max seconds to wait")
    args = parser.parse_args()

    try:
        code = fetch_otp(phone=args.phone, country=args.country, max_wait=args.wait)
        print(f"OTP: {code}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
