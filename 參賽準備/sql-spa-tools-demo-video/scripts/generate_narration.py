"""Generate the eight synthetic Traditional Chinese narration tracks.

Run: python scripts/generate_narration.py
Requires: edge-tts and mutagen
"""

import asyncio
import json
import re
from pathlib import Path

import edge_tts
from mutagen.mp3 import MP3


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "data" / "narration.json"
DESTINATION = ROOT / "public" / "audio"
VOICE = "zh-TW-HsiaoChenNeural"


def split_chunks(text: str) -> list[str]:
    phrases = [part for part in re.split(r"(?<=[，。；：！？])", text) if part]
    chunks: list[str] = []
    for phrase in phrases:
        while len(phrase) > 28:
            cut = 28
            if phrase[cut - 1].isascii() and phrase[cut].isascii():
                space = phrase.rfind(" ", 12, cut + 1)
                if space > 0:
                    cut = space + 1
            chunks.append(phrase[:cut])
            phrase = phrase[cut:]
        if phrase:
            chunks.append(phrase)
    merged: list[str] = []
    for chunk in chunks:
        if len(chunk.strip()) < 5 and merged:
            merged[-1] += chunk
        else:
            merged.append(chunk)
    if len(merged) > 1 and len(merged[0].strip()) < 5:
        merged[1] = merged[0] + merged[1]
        merged.pop(0)
    return merged


def build_captions(metadata: Path) -> list[dict[str, object]]:
    cues: list[dict[str, object]] = []
    events = [json.loads(line) for line in metadata.read_text(encoding="utf-8").splitlines()]
    sentences = [item for item in events if item["type"] == "SentenceBoundary"]
    if not sentences:
        raise RuntimeError(f"No sentence timing data in {metadata}")
    for sentence in sentences:
        chunks = split_chunks(str(sentence["text"]))
        start = int(sentence["offset"]) / 10_000_000
        duration = int(sentence["duration"]) / 10_000_000
        total_weight = sum(len(chunk) for chunk in chunks)
        cursor = start
        for chunk in chunks:
            chunk_duration = duration * len(chunk) / total_weight
            cues.append({"start": round(cursor, 2), "end": round(cursor + chunk_duration, 2), "text": chunk.strip()})
            cursor += chunk_duration
    return cues


async def main() -> None:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    scenes = json.loads(SOURCE.read_text(encoding="utf-8"))
    all_captions: dict[str, list[dict[str, object]]] = {}
    for index, scene in enumerate(scenes, start=1):
        target = DESTINATION / f"{index:02d}-{scene['id']}.mp3"
        metadata = DESTINATION / f"{index:02d}-{scene['id']}.jsonl"
        await edge_tts.Communicate(
            scene["narration"], VOICE,
            rate="+8%" if scene["id"] in {"copilot", "warning"} else "+4%" if scene["id"] == "next" else "+0%",
            volume="+0%",
        ).save(str(target), str(metadata))
        length = MP3(target).info.length
        all_captions[scene["id"]] = build_captions(metadata)
        metadata.unlink()
        print(f"{target.name}: {length:.1f}s / {scene['seconds']}s")
        if length > scene["seconds"]:
            print("  WARNING: narration exceeds scene allocation")
    (ROOT / "src" / "data" / "captions.json").write_text(
        json.dumps(all_captions, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    asyncio.run(main())
