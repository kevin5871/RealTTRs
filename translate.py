
"""
RealTTRs - Papago Translation Module

Papago Web Instant Translation API
Note: This is an unofficial web endpoint.
"""

import logging
import time
from functools import lru_cache

import requests


class TranslationError(Exception):
    """Raised when translation fails."""
    pass


class PapagoTranslator:
    API_URL = (
        "https://papago.naver.com"
        "/api/text/translation/instant"
    )

    def __init__(self, timeout=10):
        self.session = requests.Session()
        self.timeout = timeout

        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": (
                "application/x-www-form-urlencoded; charset=UTF-8"
            ),
            "Origin": "https://papago.naver.com",
            "Referer": "https://papago.naver.com/",
            "User-Agent": "RealTTRs/2.0"
        })

    @lru_cache(maxsize=1024)
    def translate(self, text, source="ko", target="en"):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not text.strip():
            return ""

        if source == target:
            return text

        payload = {
            "source": source,
            "target": target,
            "text": text,
            "dict": "false",
            "useGlossary": "false",
            "honorific": "false",
            "dictDisplay": "0",
            "usageAgreed": "true"
        }

        start_time = time.perf_counter()

        try:
            response = self.session.post(
                self.API_URL,
                data=payload,
                timeout=self.timeout
            )

            response.raise_for_status()

            result = response.json()
            translated = result.get("translatedText")

            if not isinstance(translated, str):
                raise TranslationError(
                    "Invalid response: translatedText missing"
                )

            elapsed = (
                time.perf_counter() - start_time
            ) * 1000

            logging.debug(
                "Papago translation: %.2f ms",
                elapsed
            )

            return translated

        except requests.RequestException as exc:
            logging.error(
                "Papago request failed: %s", exc
            )
            raise TranslationError(
                f"Translation request failed: {exc}"
            ) from exc

        except ValueError as exc:
            raise TranslationError(
                "Invalid JSON response"
            ) from exc

    def clear_cache(self):
        self.translate.cache_clear()

    def close(self):
        self.session.close()


# Shared translator instance
_translator = PapagoTranslator()


def Trans(text, start="ko", target="en"):
    """
    Compatibility function for RealTTRs main.py.

    Example:
        Trans("안녕하세요", "ko", "en")
    """
    return _translator.translate(text, start, target)


def clear_cache():
    _translator.clear_cache()


def close():
    _translator.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    print("RealTTRs - Papago Translation Test")

    while True:
        try:
            text = input("\nText (exit to quit): ")

            if text.lower() == "exit":
                break

            result = Trans(text, "ko", "en")
            print("Translated:", result)

        except TranslationError as exc:
            print("Error:", exc)

    close()
