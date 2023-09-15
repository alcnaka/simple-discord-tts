"""Attachments."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)

filetypes = {
    "画像": [
        "jpg",
        "jpeg",
        "png",
        "aping",
        "gif",
        "tiff",
        "bmp",
        "webp",
    ],
    "動画": [
        "mp4",
        "webm",
        "avi",
        "mov",
    ],
    "音声": [
        "mp3",
        "m4a",
        "wav",
        "flac",
    ],
}


def judge_filetype(filename: str) -> str:
    ext = Path(filename).suffix
    # ドットを削除
    ext = ext.replace(".", "")
    for key in filetypes:
        if ext.lower() in filetypes[key]:
            return key
    return "ファイル"


def extract_filetypes(filenames: list[str]) -> str:
    """ファイル名のリストから読み上げ内容を取得.

    「画像,音声を送信しました」
    """
    logger.debug("receved files: %s", str(filenames))
    result = set()
    for f in filenames:
        t = judge_filetype(f)
        if t:
            result.add(t)
    logger.debug(result)
    if result:
        return ",".join(result) + "を送信しました。"
    return ""
