import base64
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


logger = logging.getLogger(__name__)


class V2InvoiceError(RuntimeError):
    """Raised when the V2 invoice endpoint cannot be fetched safely."""


@dataclass(slots=True)
class V2InvoiceFetcher:
    """Fetches V2 agreement data with hardened auth + retry semantics."""

    session: requests.Session
    base_url: str

    def _decode_jwt_payload(self, token: str) -> dict:
        try:
            payload_segment = token.split(".")[1]
            padding = "=" * (4 - (len(payload_segment) % 4)) if len(payload_segment) % 4 else ""
            payload_bytes = base64.urlsafe_b64decode(payload_segment + padding)
            return json.loads(payload_bytes.decode("utf-8"))
        except Exception as exc:  # pragma: no cover - defensive
            raise V2InvoiceError(f"Unable to decode access token payload: {exc}") from exc

    def _build_headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.base_url}/action/PackageAgreementUpdated/spa/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Sec-Ch-Ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
        }

    def _build_cookies(self) -> Dict[str, str]:
        cookies = self.session.cookies.get_dict()
        critical_keys = ["JSESSIONID", "delegatedUserId", "loggedInUserId", "apiV3AccessToken"]
        missing = [key for key in critical_keys if key not in cookies]
        if missing:
            raise V2InvoiceError(f"Missing critical cookies for V2 request: {missing}")
        return {key: cookies[key] for key in critical_keys if cookies.get(key)}

    def _validate_scope(self, token_payload: dict, cookies: Dict[str, str]) -> None:
        delegated = str(token_payload.get("delegatedUserId") or "")
        logged_in = str(token_payload.get("loggedInUserId") or "")
        session_id = token_payload.get("sessionId")
        cookie_delegated = str(cookies.get("delegatedUserId") or "")
        cookie_logged = str(cookies.get("loggedInUserId") or "")
        cookie_session = cookies.get("JSESSIONID")

        if delegated and cookie_delegated and delegated != cookie_delegated:
            raise V2InvoiceError(
                f"Delegated user mismatch: token={delegated} cookie={cookie_delegated}"
            )
        if logged_in and cookie_logged and logged_in != cookie_logged:
            raise V2InvoiceError(
                f"Logged-in user mismatch: token={logged_in} cookie={cookie_logged}"
            )
        if session_id and cookie_session and session_id != cookie_session:
            raise V2InvoiceError(
                "Session mismatch between JWT payload and JSESSIONID cookie"
            )

    def fetch(
        self,
        agreement_id: str,
        token: str,
        timeout: float = 20.0,
        retry_attempts: int = 3,
        retry_backoff: float = 1.5,
    ) -> Dict[str, Any]:
        if not token:
            raise V2InvoiceError("Bearer token required for V2 agreement request")

        headers = self._build_headers(token)
        cookies = self._build_cookies()
        payload = self._decode_jwt_payload(token)
        self._validate_scope(payload, cookies)

        url = (
            f"{self.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
            "?include=invoices&include=scheduledPayments&include=prohibitChangeTypes"
        )

        attempt = 0
        last_error: Optional[Exception] = None
        while attempt < retry_attempts:
            attempt += 1
            timestamp = int(time.time() * 1000)
            request_url = f"{url}&_={timestamp}"
            logger.debug(
                "📄 V2 invoice request",  # emoji for quick log scanning
                extra={
                    "agreement_id": agreement_id,
                    "attempt": attempt,
                    "url": request_url,
                    "headers": headers,
                    "cookies": {k: (v[:10] + "…" if len(v) > 10 else v) for k, v in cookies.items()},
                },
            )
            try:
                response = self.session.get(
                    request_url,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                )
            except Exception as exc:  # pragma: no cover - network issues
                last_error = exc
                logger.warning(
                    "V2 invoice request failed on attempt %s due to exception: %s",
                    attempt,
                    exc,
                )
            else:
                if response.status_code == 200:
                    try:
                        data = response.json()
                    except json.JSONDecodeError as exc:
                        last_error = exc
                        logger.warning(
                            "V2 invoice response JSON decode failed on attempt %s", attempt
                        )
                    else:
                        return data

                else:
                    last_error = V2InvoiceError(
                        f"HTTP {response.status_code}: {(response.text or '')[:200]}"
                    )
                    logger.warning(
                        "V2 invoice request returned %s on attempt %s",
                        response.status_code,
                        attempt,
                    )

            time.sleep(retry_backoff * attempt)

        raise V2InvoiceError(
            f"Unable to fetch V2 agreement {agreement_id}: {last_error}"  # pragma: no cover - terminal path
        )
