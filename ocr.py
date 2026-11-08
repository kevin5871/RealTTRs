
import easyocr
import time
import logging
import torch
from functools import lru_cache


@lru_cache(maxsize=8)
def get_reader(langCode):
    start = time.perf_counter()

    reader = easyocr.Reader(
        [langCode],
        gpu=True if torch.cuda.is_available() else False
    )

    logging.info(
        "EasyOCR model loaded (%s): %.2f ms",
        langCode,
        (time.perf_counter() - start) * 1000
    )

    return reader


def ImagetoTxt(td, path, langCode):
    reader = get_reader(langCode)

    start = time.perf_counter()

    results = reader.readtext(path)

    elapsed = (time.perf_counter() - start) * 1000

    logging.info(
        "OCR inference (%s): %.2f ms",
        langCode,
        elapsed
    )

    texts = [item[1] for item in results]

    return results, texts
