"""words_out.json (output timeline) -> SRT with readable 1-line cues."""
import json, sys
from pathlib import Path

HERE = Path(__file__).parent
FIX = {"outubro de 1926": "outubro de 2026", "75 arquivos": "75 artigos", "nascer uma": "nasceu uma", "desverecer": "desmerecer",
       "como apostas": "como opostas", "Sinaepte": "Sinaept", "sobre condições": "sob condições", "será mediada": "será medida",
       "Helio": "Hélio", "já sabe e": "já sabem e", "A primeira vista": "À primeira vista", "a academia": "à academia", "as famílias": "às famílias"}

PAIRS = {}


def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main(out_name):
    w = json.load(open(HERE / "words_out.json", encoding="utf8"))
    # Whisper splits enclitics/percent signs into their own tokens ("utilizá -lo", "56 %"): glue them back
    k = 1
    while k < len(w):
        if w[k]["text"][:1] in "-%" and not w[k]["text"].startswith("-mail"):
            w[k - 1] = {**w[k - 1], "text": w[k - 1]["text"] + w[k]["text"], "end": w[k]["end"]}
            del w[k]
        else:
            k += 1
    # Whisper ran some sentences together without punctuation: restore it word-pair by word-pair
    for i in range(len(w) - 1):
        pr = PAIRS.get((w[i]["text"], w[i + 1]["text"]))
        if pr:
            w[i]["text"], w[i + 1]["text"] = pr
    if w[-1]["text"][-1] not in ".?!":
        w[-1]["text"] += "."
    cues, cur = [], []
    for i, x in enumerate(w):
        cur.append(x)
        txt = " ".join(c["text"] for c in cur)
        nxt = w[i + 1] if i + 1 < len(w) else None
        brk = (nxt is None or x["text"][-1] in ".?!" or len(txt) > 62 or nxt["start"] - x["end"] > 0.6
               or (nxt["text"][:1].isupper() and nxt["start"] - x["end"] > 0.3)
               or (x["text"][-1] in ",:" and len(txt) > 30))
        if brk:
            for a, b in FIX.items():
                txt = txt.replace(a, b)
            cues.append([cur[0]["start"], x["end"] + 0.15, txt])
            cur = []
    for i in range(len(cues) - 1):
        cues[i][1] = min(cues[i][1], cues[i + 1][0] - 0.02)
    (HERE / out_name).write_text("\n".join(f"{k}\n{ts(a)} --> {ts(b)}\n{t}\n" for k, (a, b, t) in enumerate(cues, 1)),
                                 encoding="utf8")
    print(len(cues), "cues ->", out_name)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "legendas.srt")
