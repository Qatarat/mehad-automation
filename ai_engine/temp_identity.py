"""
temp_identity.py — disposable phone + email providers for MehadEdu E2E tests.

Phone  → StagingPhoneIdentity: generates a unique phone number per run.
         Staging accepts ANY valid number with OTP 123456 (hardcoded).
         Pass random=True for new-user signup; False for the known test account.

Email  → GuerrillaEmailIdentity: real disposable inbox via Guerrilla Mail API.
         sharklasers.com is accepted by the signup form.
         Useful for the email field in the tutor application form.

Usage
-----
    from ai_engine.temp_identity import new_staging_phone, new_temp_email

    phone = new_staging_phone()          # fixed test account +880 98976564
    phone = new_staging_phone(random=True)  # unique number for new-signup tests

    email = new_temp_email()
    print(email.email)                   # mehad_abc123@sharklasers.com
    link  = email.wait_for_verification()  # waits for email to arrive
"""
from __future__ import annotations

import random
import re
import string
import time
from dataclasses import dataclass
from typing import Optional

# ── Staging constants ───────────────────────────────────────────────────────────
_STAGING_OTP           = "123456"   # hardcoded OTP on dev.mehadedu.com
_TEST_COUNTRY_CODE     = "+880"     # Bangladesh
_TEST_PHONE_NUMBER     = "98976564" # known test account — "Automations Student"
_TEST_EXPECTED_NAME    = "Automations Student"

# Guerrilla Mail API (all domains share the same per-username inbox)
_GUERRILLA_API         = "https://api.guerrillamail.com/ajax.php"
_GUERRILLA_FORM_DOMAIN = "sharklasers.com"  # accepted by most sign-up forms


# ══════════════════════════════════════════════════════════════════════════════
# PHONE IDENTITY
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class TempPhoneIdentity:
    """
    A disposable phone identity for WhatsApp OTP login on staging.

    On MehadEdu staging (dev.mehadedu.com), OTP is always 123456 regardless
    of the phone number, so we can generate a random number per test run to
    avoid collisions with already-registered accounts.
    """
    country_code: str = _TEST_COUNTRY_CODE
    phone_number: str = _TEST_PHONE_NUMBER
    otp:          str = _STAGING_OTP

    # ── human-readable fields ──────────────────────────────────────────────
    is_test_account: bool = True   # True = the fixed "Automations Student" account

    @property
    def full_number(self) -> str:
        """E.g. '+88098976564'."""
        return f"{self.country_code}{self.phone_number}"

    @property
    def display_country(self) -> str:
        """Country name used in the dropdown search box."""
        _MAP = {
            "+880": "Bangladesh",
            "+966": "Saudi Arabia",
            "+1":   "United States",
            "+44":  "United Kingdom",
            "+971": "United Arab Emirates",
        }
        return _MAP.get(self.country_code, self.country_code)

    def __repr__(self) -> str:
        return (f"TempPhoneIdentity(country={self.country_code!r}, "
                f"phone={self.phone_number!r}, otp={self.otp!r})")


def new_staging_phone(random: bool = False) -> TempPhoneIdentity:
    """
    Return a TempPhoneIdentity for staging tests.

    random=False (default)
        → fixed test account +880 98976564 ("Automations Student").
          Use for login tests that verify the authenticated state.

    random=True
        → fresh random 8-digit BD number every call.
          Use for new-user / tutor signup tests where the phone must not
          already be registered. Staging accepts any number with OTP 123456.
    """
    if not random:
        return TempPhoneIdentity(
            country_code=_TEST_COUNTRY_CODE,
            phone_number=_TEST_PHONE_NUMBER,
            otp=_STAGING_OTP,
            is_test_account=True,
        )

    # Generate a random 8-digit number (starts with 9 to avoid 0-prefix
    # patterns that some validators reject as leading zeros).
    import random as _rng
    rand_digits = "".join(_rng.choices(string.digits, k=7))
    phone = f"9{rand_digits}"   # 8-digit number: 9xxxxxxx
    return TempPhoneIdentity(
        country_code=_TEST_COUNTRY_CODE,
        phone_number=phone,
        otp=_STAGING_OTP,
        is_test_account=False,
    )


# ══════════════════════════════════════════════════════════════════════════════
# EMAIL IDENTITY  (Guerrilla Mail)
# ══════════════════════════════════════════════════════════════════════════════

class GuerrillaEmailIdentity:
    """
    Disposable email inbox via Guerrilla Mail API.

    Generates a unique mehad_<random>@sharklasers.com address per instance.
    Can optionally poll the inbox for a verification / confirmation link
    (used in the tutor signup flow if the platform sends an email after
    the application is submitted).
    """

    def __init__(self) -> None:
        import random as _rng
        suffix = "".join(_rng.choices(string.ascii_lowercase + string.digits, k=10))
        self.username: str = f"mehad{suffix}"
        self.email:    str = f"{self.username}@{_GUERRILLA_FORM_DOMAIN}"
        self._session: str = ""
        self._cookies: dict = {}
        self._seq:     int  = 0
        self.available: bool = self._setup_inbox()

    # ── low-level API helper ───────────────────────────────────────────────
    def _gm_get(self, params: dict) -> dict | None:
        try:
            import requests
            resp = requests.get(
                _GUERRILLA_API, params=params, cookies=self._cookies,
                timeout=12, headers={"User-Agent": "Mozilla/5.0"},
            )
            if resp.status_code == 200:
                self._cookies.update(resp.cookies.get_dict())
                data = resp.json()
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return None

    def _setup_inbox(self) -> bool:
        """Initialise the Guerrilla Mail session and claim our username."""
        data = self._gm_get({"f": "get_email_address", "lang": "en"})
        if not data:
            return False
        self._session = data.get("sid_token", "")
        self._gm_get({
            "f": "set_email_user",
            "email_user": self.username,
            "lang": "en",
            "sid_token": self._session,
        })
        return bool(self._session)

    # ── inbox polling ──────────────────────────────────────────────────────
    def wait_for_email(
        self,
        timeout: int = 90,
        poll:    int = 6,
        verbose: bool = True,
    ) -> tuple[str, str]:
        """
        Poll the inbox until an email arrives.

        Returns (subject, body_text).  Returns ('', '') on timeout.
        """
        if not self.available:
            return "", ""
        deadline = time.time() + timeout
        attempt  = 0
        seen: set[str] = set()
        while time.time() < deadline:
            attempt += 1
            data = self._gm_get({
                "f": "check_email",
                "seq": self._seq,
                "sid_token": self._session,
            })
            if verbose:
                count = len(data.get("list", [])) if isinstance(data, dict) else "err"
                remaining = int(deadline - time.time())
                print(f"    [guerrilla] poll#{attempt} inbox={self.email} "
                      f"msgs={count} remaining={remaining}s")
            if isinstance(data, dict):
                self._seq = data.get("count", self._seq)
                for msg in data.get("list", []):
                    mid = str(msg.get("mail_id", ""))
                    if not mid or mid in seen:
                        continue
                    seen.add(mid)
                    full = self._gm_get({
                        "f": "fetch_email",
                        "email_id": mid,
                        "sid_token": self._session,
                    })
                    if isinstance(full, dict):
                        subject = full.get("mail_subject", "")
                        body    = (full.get("mail_body") or ""
                                   ) + " " + (full.get("mail_text_only") or "")
                        return subject, body
            time.sleep(poll)
        return "", ""

    def wait_for_verification_link(
        self,
        timeout: int = 90,
        poll:    int = 6,
    ) -> str | None:
        """Return the first URL found in any received email, or None."""
        _, body = self.wait_for_email(timeout=timeout, poll=poll)
        if not body:
            return None
        links = re.findall(r'https?://[^\s"\'<>]+', body)
        return links[0] if links else None

    def inbox_url(self) -> str:
        return "https://www.guerrillamail.com/inbox"

    def __repr__(self) -> str:
        return f"GuerrillaEmailIdentity({self.email!r}, available={self.available})"


def new_temp_email() -> GuerrillaEmailIdentity:
    """Create a fresh disposable email inbox backed by Guerrilla Mail."""
    return GuerrillaEmailIdentity()
