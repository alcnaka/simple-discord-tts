"""Attachments."""

from __future__ import annotations

from pathlib import Path

IMAGE_EXT = [
    "jpg",
    "jpeg",
    "png",
    "aping",
    "gif",
    "tiff",
    "bmp",
    "webp",
]

VIDEO_EXT = [
    "mp4",
    "webm",
    "avi",
    "mov",
]

AUDIO_EXT = [
    "mp3",
    "m4a",
    "wav",
    "flac",
]


def judge_filetype(filename: str) -> str | None:
    ext = Path(filename).suffix
    if ext.lower() in IMAGE_EXT:
        return "画像"
    if ext.lower() in VIDEO_EXT:
        return "動画"
    if ext.lower() in AUDIO_EXT:
        return "音声"
    return None


def extract_filetypes(filenames: list[str]) -> str:
    """ファイル名のリストから読み上げ内容を取得.

    「画像,音声を送信しました」
    """
    result = set()
    for f in filenames:
        t = judge_filetype(f)
        if t:
            result.add(t)
    if result:
        return ",".join(result) + "を送信しました。"
    return ""