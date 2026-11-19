"""Local transcription with faster-whisper (no API cost), written in the Scribe JSON shape the
Video-Use helpers read: {"words": [{text, start, end, type: word|spacing, speaker_id}]}.

Usage: python -X utf8 whisper_transcribe.py <video> <out.json>
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel

video, out = Path(sys.argv[1]), Path(sys.argv[2])
wav = out.with_suffix(".16k.wav")
if not wav.exists():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)

model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=4)
prompt = ("Eu sou o professor Hélio Laranjeira, e esta é A Nova Ordem Educacional. "
          "Inteligência artificial, ChatGPT, mercado de trabalho, ensino médio, educação.")
import soundfile as sf  # decode ourselves: the installed PyAV rejects faster-whisper's open() kwargs
audio, _ = sf.read(str(wav), dtype="float32")
segments, info = model.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False,
                                  beam_size=5, initial_prompt=prompt, condition_on_previous_text=False)
words, t0 = [], time.time()
for seg in segments:
    for w in seg.words:
        text = w.word.strip()
        if not text:
            continue
        if words:
            words.append({"text": " ", "start": words[-1]["end"], "end": round(w.start, 3), "type": "spacing", "speaker_id": "speaker_0"})
        words.append({"text": text, "start": round(w.start, 3), "end": round(w.end, 3), "type": "word",
                      "speaker_id": "speaker_0", "logprob": round(w.probability, 3)})
    print(f"{seg.end:7.1f}s / {info.duration:.0f}s  ({time.time() - t0:.0f}s elapsed)", flush=True)
json.dump({"language_code": "pt", "text": " ".join(w["text"] for w in words if w["type"] == "word"), "words": words},
          open(out, "w", encoding="utf8"), ensure_ascii=False)
print("DONE", len([w for w in words if w["type"] == "word"]), "words")
