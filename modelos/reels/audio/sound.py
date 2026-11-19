"""SHORT 03 (REELS 3) — final soundtrack for the split-panel version: voice treatment + sound design + master,
muxed onto the rendered picture. Same approach as REELS 2 (the user asked there for "um tratamento de áudio bacana
e sons que aumentem a retenção"); the first version of this short had a synthesized music bed and only four effects
(the written script), and the user rejected that version as a whole ("tá ruim, volta pra pegada antiga").

  voice   : 90 Hz high-pass, denoise with the take's own room tone, level rider for his quiet sentence endings
            (the last word is 13 dB under the rest), EQ, two de-esser stages, compressor, peak limiter, pauses down.
  design  : every sound is tied to something visible and anchored to the same word times as the picture.
            All sounds are synthesized here (numpy, fixed seed) - no samples, no music.
  master  : -14 LUFS, true peak below -1 dBTP, stereo (voice centre, effects placed where things happen on screen).

Run from the edit folder:  python -X utf8 audio/sound.py        (after every new render of the picture)
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import ndimage as ndi
from scipy import signal

HERE = Path(__file__).resolve().parent
EDIT = HERE.parent
NAME = EDIT.parent.name                       # REELS_3
RAW = EDIT / "reels3_raw.mp4"                 # the picture rendered by HyperFrames
SR = 48000
FPS = 30
rng = np.random.default_rng(11)
ROOM = (0.12, 0.95)                           # seconds of the SOURCE with room tone only (before he speaks)

WORDS = json.load(open(EDIT / "words_out.json", encoding="utf8"))
SEGS = json.load(open(EDIT / "segments.json", encoding="utf8"))
REEL = json.load(open(EDIT / "hf" / "reel.json", encoding="utf8"))          # the same times the picture uses
TOTAL = sum(s["f1"] - s["f0"] for s in SEGS) / FPS
BY = {w["i"]: w for w in WORDS}


def fr(t):
    return round(t * FPS) / FPS


def S(i):
    return fr(BY[i]["start"])


def E(i):
    return fr(BY[i]["end"])


def seg(k):
    return fr(SEGS[k]["out"])


def db(x):
    return 10 ** (x / 20)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12)


# =====================================================================================================
# 1. VOICE
# =====================================================================================================
def butter(x, fc, kind, order=4):
    return signal.sosfiltfilt(signal.butter(order, fc, kind, fs=SR, output="sos"), x)


def biquad(x, b, a):
    return signal.lfilter(np.array(b) / a[0], np.array(a) / a[0], x)


def peaking(x, fc, gain, q):
    A, w = 10 ** (gain / 40), 2 * np.pi * fc / SR
    al = np.sin(w) / (2 * q)
    return biquad(x, [1 + al * A, -2 * np.cos(w), 1 - al * A], [1 + al / A, -2 * np.cos(w), 1 - al / A])


def highshelf(x, fc, gain, slope=0.8):
    A, w = 10 ** (gain / 40), 2 * np.pi * fc / SR
    al = np.sin(w) / 2 * np.sqrt((A + 1 / A) * (1 / slope - 1) + 2)
    c, r = np.cos(w), 2 * np.sqrt(A) * al
    return biquad(x, [A * ((A + 1) + (A - 1) * c + r), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - r)],
                  [(A + 1) - (A - 1) * c + r, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - r])


def denoise(x, noise, nfft=2048, hop=512, over=1.6, floor_db=-13.0):
    """Spectral gating with the take's own room tone as the profile. Never gates fully (floor), gains are smoothed."""
    kw = dict(fs=SR, window="hann", nperseg=nfft, noverlap=nfft - hop, boundary="zeros", padded=True)
    _, _, X = signal.stft(x, **kw)
    _, _, N = signal.stft(noise, **kw)
    nm = np.abs(N)
    thr = nm.mean(1) + 1.5 * nm.std(1)
    g = np.sqrt(np.clip(1 - (over * thr[:, None] / (np.abs(X) + 1e-12)) ** 2, 0, 1))
    g = np.maximum(g, db(floor_db))
    g = ndi.uniform_filter(g, size=(5, 3), mode="nearest")
    _, y = signal.istft(X * g, **{k: v for k, v in kw.items() if k != "padded"})
    return y[: len(x)]


def leveler(x, max_boost=11.0, max_cut=5.0, strength=0.8):      # 11 dB: his last word ("conta?") is 13 dB under the rest
    """Slow gain rider on the speech band: brings quiet sentence endings up, tames loud words. Holds its gain in pauses."""
    hop = SR // 100
    p = ndi.uniform_filter1d(butter(x, [150, 4000], "bandpass", 2) ** 2, int(0.3 * SR))[::hop]
    lev = 10 * np.log10(p + 1e-12)
    active = lev > np.percentile(lev, 95) - 26
    target = np.median(lev[active])
    g = np.clip((target - lev) * strength, -max_cut, max_boost)
    last = 0.0
    for i in range(len(g)):                      # in pauses keep a cut but never a boost: the room must not pump up
        if active[i]:
            last = g[i]
        else:
            g[i] = min(last, 0.0)
    g = ndi.gaussian_filter1d(g, 12, mode="nearest")
    gain = np.interp(np.arange(len(x)), np.arange(len(g)) * hop, g)
    return x * db(gain), g


def limiter(x, ceiling, look=0.002, smooth=0.05):
    """Look-ahead peak limiter: the gain dips are known in advance and eased in and out, so nothing clicks or overshoots."""
    mono = np.abs(x) if x.ndim == 1 else np.abs(x).max(1)
    n = int(look * SR)
    g = np.minimum(1.0, ceiling / (ndi.maximum_filter1d(mono, 2 * n + 1) + 1e-12))
    g = np.minimum(g, ndi.uniform_filter1d(g, int(smooth * SR)))
    return (x * g if x.ndim == 1 else x * g[:, None]), float(20 * np.log10(g.min())), float((g < 0.999).mean())


def pause_gate(x, depth=10.0, margin=0.08, ramp=0.05):
    """Turn the room down between phrases. Keyed on the word times (not on level), so soft consonants are never touched."""
    mask = np.ones(len(x))
    for w in WORDS:
        mask[max(0, int((w["start"] - margin) * SR)): int((w["end"] + margin) * SR)] = 0.0
    mask = ndi.uniform_filter1d(ndi.uniform_filter1d(mask, int(ramp * SR)), int(ramp * SR))   # eased in and out
    return x * db(-depth * mask), float(mask.mean() * len(x) / SR)


def loudness(x):
    """Integrated loudness (LUFS) and true peak (dBTP) of an array, measured by ffmpeg's EBU R128 meter."""
    tmp = HERE / "_meter.wav"
    sf.write(str(tmp), x.astype("float32"), SR)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    tmp.unlink()
    tail = r[r.rindex("Summary"):]
    num = lambda key: float(tail.split(key)[1].split()[0])
    return num("I:"), num("Peak:"), num("LRA:")


def deess(x, lo=4500, hi=10000, amount=0.45, max_red=6.0):
    s = butter(x, [lo, hi], "bandpass", 2)
    a = np.exp(-1 / (0.012 * SR))
    env = signal.lfilter([1 - a], [1, -a], np.abs(s))
    e = 20 * np.log10(env + 1e-9)
    thr = np.percentile(e[e > np.percentile(e, 60)], 55)
    red = np.clip((e - thr) * amount, 0, max_red)
    return x - s * (1 - db(-red)), float(red.max()), float((red > 1).mean())


def sibilant_cap(x, rel_cap=-2.5, lo=4500, hi=10000, max_red=6.0):
    """Second de-esser, after the dynamics: the s / z / ch band may not rise above (speech rms + rel_cap) dB."""
    s = butter(x, [lo, hi], "bandpass", 2)
    e = 10 * np.log10(ndi.uniform_filter1d(s ** 2, int(0.005 * SR)) + 1e-12)
    red = ndi.uniform_filter1d(np.clip(e - (rms_db(x) + rel_cap), 0, max_red), int(0.004 * SR))
    return x - s * (1 - db(-red)), float(red.max()), float((red > 0.5).mean())


def treat_voice():
    x, sr = sf.read(str(EDIT / "audio_raw.wav"), dtype="float64")
    src, _ = sf.read(str(EDIT / "source_48k.wav"), dtype="float64")
    assert sr == SR
    room = butter(src[int(ROOM[0] * SR): int(ROOM[1] * SR)], 90, "highpass", 4)
    y = butter(x, 90, "highpass", 4)
    y = denoise(y, room)
    y, gains = leveler(y)
    y = peaking(y, 330, -2.5, 1.0)
    y = peaking(y, 3400, 2.5, 1.0)
    y = highshelf(y, 8500, 1.5)
    y, red_max, red_share = deess(y)
    y = butter(y, 16000, "lowpass", 4)
    sf.write(str(HERE / "voice_pre.wav"), (y / max(1.0, np.abs(y).max() / 0.98)).astype("float32"), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "voice_pre.wav"), "-af",
                    "acompressor=threshold=-24dB:ratio=3.2:attack=6:release=130:knee=5:makeup=1", "-ar", str(SR), "-c:a", "pcm_f32le",
                    str(HERE / "voice_comp.wav")], check=True)
    v, _ = sf.read(str(HERE / "voice_comp.wav"), dtype="float64")
    v = v[: len(x)]
    # speech is spiky (consonant bursts 19 dB above its body): shave only the top 0.1 % of samples
    ceil = np.percentile(np.abs(v), 99.9) * db(2.5)
    v, lim_max, lim_share = limiter(v, ceil)
    v, gated = pause_gate(v)
    print(f"       pauses between phrases turned down 10 dB ({gated:.1f} s in total)")
    v, cap_max, cap_share = sibilant_cap(v)
    print(f"       hottest sibilants capped: up to {cap_max:.1f} dB on {cap_share * 100:.1f} % of the time")
    v *= db(-17.5 - rms_db(v))                    # working level before the master
    print(f"voice: rider gains {gains.min():+.1f} .. {gains.max():+.1f} dB, de-esser max {red_max:.1f} dB on {red_share * 100:.0f} % of the time, "
          f"peak limiter down to {lim_max:.1f} dB on {lim_share * 100:.1f} % of the time")
    print(f"       rms {rms_db(v):.1f} dBFS, peak {20 * np.log10(np.abs(v).max()):.1f} dBFS, crest {20 * np.log10(np.abs(v).max()) - rms_db(v):.1f} dB")
    return x, v


# =====================================================================================================
# 2. SYNTH
# =====================================================================================================
def tt(dur):
    return np.arange(int(dur * SR)) / SR


def fade(x, a=0.002, r=0.006):
    x = x.copy()
    na, nr = min(int(a * SR), len(x) // 2), min(int(r * SR), len(x) // 2)
    if na:
        x[:na] *= np.linspace(0, 1, na)
    if nr:
        x[-nr:] *= np.linspace(1, 0, nr)
    return x


def unit(x):
    return x / (np.abs(x).max() + 1e-12)


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, "lowpass", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, "highpass", fs=SR, output="sos"), x)


def sweep(f0, f1, dur, curve=None):
    t = tt(dur)
    f = f0 * (f1 / f0) ** (t / dur) if curve is None else curve(t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def svf(x, fc, q=1.2, out="band"):
    """State-variable filter with a moving cutoff (per sample)."""
    f = 2 * np.sin(np.pi * np.minimum(fc, SR / 6.5) / SR)
    damp, low, band = 1.0 / q, 0.0, 0.0
    y = np.empty(len(x))
    for i in range(len(x)):
        low += f[i] * band
        high = x[i] - low - damp * band
        band += f[i] * high
        y[i] = band if out == "band" else low
    return y


def boom(f0=110, f1=42, dur=0.55, tau=0.14, click=0.25, knock=0.5):
    t = tt(dur)
    body = np.sin(2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t / 0.05)) / SR) * np.exp(-t / tau)
    body += 0.2 * np.sin(2 * np.pi * np.cumsum(2 * (f1 + (f0 - f1) * np.exp(-t / 0.05))) / SR) * np.exp(-t / (tau * 0.6))
    kn = np.sin(2 * np.pi * np.cumsum(125 + 70 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.05) * knock   # audible on phone speakers
    ck = bp(noise(dur), 1500, 5000) * np.exp(-t / 0.004) * click
    return fade(unit(np.tanh(1.4 * (body + kn)) + ck), 0.0005, 0.03)


def pop(f=600, dur=0.1):
    t = tt(dur)
    y = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.8 * np.exp(-t / 0.012))) / SR) * np.exp(-t / 0.03)
    return fade(unit(y + 0.15 * hp(noise(dur), 3000) * np.exp(-t / 0.002)), 0.0005, 0.01)


def tick(f=2200, dur=0.035):
    t = tt(dur)
    return fade(unit(bp(noise(dur), f * 0.6, min(f * 1.6, 11000)) * np.exp(-t / 0.004) + 0.5 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.008)), 0.0003, 0.004)


def clack(f=1500, body=220, dur=0.12):
    t = tt(dur)
    y = np.zeros(len(t))
    k = tick(f)
    y[: len(k)] += k
    return fade(unit(y + 0.8 * np.sin(2 * np.pi * body * t) * np.exp(-t / 0.03)), 0.0003, 0.01)


def whoosh(dur=0.5, f0=400, f1=3000, q=1.3, shape="pass"):
    t = tt(dur)
    y = svf(noise(dur), f0 * (f1 / f0) ** (t / dur), q)
    u = t / dur
    env = {"pass": np.sin(np.pi * u) ** 1.6, "in": u ** 2.2, "out": np.minimum(t / 0.012, 1) * (1 - u) ** 2}[shape]
    return fade(unit(y * env), 0.003, 0.012)


def riser(dur=0.42):
    t = tt(dur)
    u = t / dur
    y = svf(noise(dur), 500 * 14 ** u, 2.0) * u ** 2.5
    y += 0.3 * sweep(300, 1200, dur) * u ** 3
    y *= 1 - 0.3 * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(8 + 16 * u) / SR))
    return fade(unit(y), 0.01, 0.004)


def beep(f=880, dur=0.07, sq=0.5):
    y = np.sin(2 * np.pi * f * tt(dur))
    return fade(unit(lp((1 - sq) * y + sq * np.tanh(4 * y) / np.tanh(4), 6000)), 0.004, 0.006)


def seq(*parts):
    """parts: arrays and numbers (gaps in seconds)."""
    return np.concatenate([np.zeros(int(p * SR)) if np.isscalar(p) else p for p in parts])


def chime(f, dur=0.7, bright=1.0):
    t = tt(dur)
    y = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / tau) for m, a, tau in ((1, 1, 0.28), (2.76, 0.45 * bright, 0.16), (5.4, 0.25 * bright, 0.09), (8.93, 0.1 * bright, 0.05)) if f * m < 16000)
    return fade(unit(lp(y, 10000)), 0.001, 0.05)


def scan(dur, f0=500, f1=1500, trem=22):
    t = tt(dur)
    y = sweep(f0, f1, dur) + 0.2 * sweep(2 * f0, 2 * f1, dur)
    y = y * (1 + 0.5 * np.sin(2 * np.pi * trem * t)) + 0.05 * hp(noise(dur), 4000)
    return fade(unit(lp(y, 7000)), 0.03, 0.06)


def servo(dur=0.5, f0=140, f1=330):
    t = tt(dur)
    ph = 2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (t / dur)) / SR
    y = sum(np.sin(k * ph) / k for k in range(1, 6)) * (1 + 0.35 * np.sin(2 * np.pi * 34 * t))
    return fade(unit(lp(y, 2200)), 0.04, 0.08)


def bloop(f0=300, f1=640, dur=0.12):
    return fade(unit(sweep(f0, f1, dur) * np.exp(-tt(dur) / 0.045)), 0.002, 0.02)


def poof(dur=0.32):
    t = tt(dur)
    y = svf(noise(dur), 2500 * (400 / 2500) ** (t / dur), 0.9, "low") * np.minimum(t / 0.005, 1) * np.exp(-t / 0.09)
    y = unit(y)
    for k in range(6):
        p = 0.25 * pop(900 + 110 * k, 0.05)
        i = int((0.03 + 0.035 * k) * SR)
        y[i: i + len(p)] += p[: len(y) - i]
    return fade(unit(y), 0.001, 0.03)


def crack(dur=0.3):
    t = tt(dur)
    y = bp(noise(dur), 1500, 6000) * np.exp(-t / 0.006) + 0.5 * np.sin(2 * np.pi * 240 * t) * np.exp(-t / 0.02)
    for _ in range(9):
        i = int(rng.uniform(0.03, 0.22) * SR)
        b = bp(noise(0.012), 2000, 8000) * np.exp(-tt(0.012) / 0.002) * rng.uniform(0.2, 0.6)
        y[i: i + len(b)] += b
    return fade(unit(y), 0.0003, 0.02)


def shatter(dur=0.8):
    t = tt(dur)
    y = np.zeros(len(t))
    for part, g in ((boom(120, 38, 0.7, 0.2, 0.3, 0.7), 1.0), (crack(0.3), 0.8)):
        y[: len(part)] += g * part
    for _ in range(14):
        i = int(rng.uniform(0.06, 0.45) * SR)
        c = clack(rng.uniform(900, 2600), rng.uniform(180, 320), 0.09) * 0.3 * np.exp(-i / SR / 0.18)
        y[i: i + len(c)] += c[: len(y) - i]
    y += 0.3 * lp(noise(dur), 2500) * np.exp(-t / 0.15)
    return fade(unit(y), 0.0003, 0.08)


def partials(freqs, taus, amps, dur):
    t = tt(dur)
    return sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau) for f, tau, a in zip(freqs, taus, amps))


def shing(dur=0.42):
    t = tt(dur)
    y = partials([1900, 2870, 4150, 5600], [0.18, 0.14, 0.1, 0.07], [1, 0.7, 0.5, 0.3], dur) + 0.4 * hp(noise(dur), 6000) * np.exp(-t / 0.02)
    return fade(unit(y), 0.002, 0.04)


def clang(dur=0.45):
    y = partials([410, 725, 1130, 1710], [0.2, 0.16, 0.12, 0.08], [1, 0.6, 0.4, 0.25], dur)
    b = boom(130, 60, 0.28, 0.07, 0.15, 0.6)
    y[: len(b)] += 0.9 * b
    return fade(unit(y), 0.0005, 0.04)


def thud():
    return boom(130, 60, 0.28, 0.07, 0.15, 0.6)


def typeclick():
    t = tt(0.02)
    f = 1300 * rng.uniform(0.9, 1.1)
    return fade(unit(bp(noise(0.02), 2000, 5500) * np.exp(-t / 0.0025) + 0.4 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006)), 0.0003, 0.003)


def tok(f=820):
    t = tt(0.05)
    return fade(unit(lp(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012) + 0.5 * bp(noise(0.05), 1500, 3000) * np.exp(-t / 0.002), 3500)), 0.0003, 0.01)


def rumble(dur):
    t = tt(dur)
    y = lp(noise(dur), 110) * 3 + bp(noise(dur), 150, 420) * 1.2
    return fade(unit(y * (t / dur) ** 2), 0.05, 0.02)


def zip_up(dur=0.28):
    t = tt(dur)
    y = sweep(500, 2400, dur) * 0.6 + svf(noise(dur), 900 * 5 ** (t / dur), 1.5) * 0.6
    return fade(unit(y * np.sin(np.pi * t / dur) ** 0.8), 0.004, 0.02)


def paper(dur=0.2):
    t = tt(dur)
    flut = 0.35 + 0.65 * np.abs(np.sin(2 * np.pi * 9 * t + 0.6))
    return fade(unit(bp(noise(dur), 2500, 9000) * flut * np.sin(np.pi * t / dur) ** 1.2), 0.004, 0.03)


def rev(x):
    return x[::-1].copy()

# ---- extra voices for this short
def coin(f=3000, dur=0.2):
    """A small metal disc landing: inharmonic ring + a tick."""
    y = partials([f, f * 1.48, f * 2.26], [0.055, 0.04, 0.028], [1, 0.6, 0.35], dur)
    k = tick(4200, 0.02)
    y[: len(k)] += 0.5 * k
    return fade(unit(y), 0.0003, 0.03)


def slam(dur=0.5):
    """A door thrown shut: low thump, the wooden knock, the latch."""
    y = np.zeros(int(dur * SR))
    for part, at, g in ((boom(120, 44, dur, 0.13, 0.35, 0.9), 0.0, 1.0), (clack(900, 180, 0.14), 0.0, 0.7), (tick(3000, 0.03), 0.045, 0.4)):
        i = int(at * SR)
        y[i: i + len(part)] += g * part[: len(y) - i]
    return fade(unit(y), 0.0003, 0.05)


def heartbeat():
    """lub-dub"""
    return seq(boom(70, 45, 0.16, 0.05, 0.0, 0.5), 0.06, 0.8 * boom(62, 42, 0.14, 0.045, 0.0, 0.4))


def flatline(dur=0.5, f=880):
    t = tt(dur)
    return fade(unit(lp(np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t), 5000)), 0.004, 0.03)


def sting(dur=0.5):
    """Two low notes a semitone apart: 'evil' in half a second."""
    t = tt(dur)
    y = sum(0.5 * np.sign(np.sin(2 * np.pi * f * t)) + np.sin(2 * np.pi * f * t) for f in (98.0, 103.8))
    return fade(unit(lp(y, 900) * np.minimum(t / 0.01, 1) * np.exp(-t / 0.22)), 0.003, 0.05)


def buzz(dur=0.15, f=150):
    """The short 'no' of a machine."""
    return fade(unit(lp(np.sign(np.sin(2 * np.pi * f * tt(dur))), 1800)), 0.004, 0.02)


def register():
    """Ka-ching: the drawer knock and two bright bells."""
    y = np.zeros(int(0.7 * SR))
    for part, at, g in ((clack(1200, 240, 0.1), 0.0, 0.7), (chime(2093, 0.6), 0.05, 1.0), (chime(2637, 0.55), 0.11, 0.8)):
        i = int(at * SR)
        y[i: i + len(part)] += g * part[: len(y) - i]
    return fade(unit(y), 0.0005, 0.05)


def cardboard():
    """A parcel landing: soft and boxy."""
    t = tt(0.14)
    return fade(unit(lp(noise(0.14), 900) * np.exp(-t / 0.02) + 0.7 * np.sin(2 * np.pi * 150 * t) * np.exp(-t / 0.035)), 0.0005, 0.02)


# =====================================================================================================
# 3. SOUND DESIGN: what plays when (output seconds), how loud (peak dBFS before the master), where (pan -1..1)
# =====================================================================================================
SFX_TRIM = -2.5                    # dB on the whole effects bus: denser than REELS 2, so it sits a little lower (voice first)
T = REEL["T"]
FS1, C3, C4, FS2, C5 = T["fs1"], T["sc3"], T["sc4"], T["fs2"], T["sc5"]
N = int(round(TOTAL * SR))
bus = np.zeros((N, 2))
log = []


def put(t, snd, peak, pan=0.0, why=""):
    """pan: number or (from, to) for a moving sound."""
    snd = unit(snd) * db(peak)
    i = int(round(t * SR))
    if i < 0:
        snd, i = snd[-i:], 0
    snd = snd[: max(0, N - i)]
    p = np.linspace(pan[0], pan[1], len(snd)) if isinstance(pan, tuple) else np.full(len(snd), float(pan))
    a = (p + 1) * np.pi / 4
    bus[i: i + len(snd), 0] += snd * np.cos(a) * np.sqrt(2) * db(-3)
    bus[i: i + len(snd), 1] += snd * np.sin(a) * np.sqrt(2) * db(-3)
    log.append((round(t, 2), why, peak))


def design():
    # ---- 1 · hook: the meeting-room door slams (this is also what the loop lands on)
    put(0.0, whoosh(0.28, 300, 1900, shape="in"), -16, (-0.5, -0.2), "the door swings")
    put(0.0, pop(700), -21, 0.2, "room display pops")
    put(0.25, slam(), -9, -0.2, "the door slams (hook)")
    put(0.42, bloop(360, 620), -25, -0.3, "they are talking: bubble")
    put(0.82, bloop(420, 700), -25, -0.2, "they are talking about the pawn: bubble")
    put(S(2) + 0.02, tok(900), -24, -0.3, "REUNIÃO sign pulses")
    put(S(6) - 0.22, whoosh(0.5, 300, 2200), -20, (-0.3, 0.3), "camera pulls back")
    put(S(6) - 0.06, pop(520), -18, 0.5, "VOCÊ (the pawn) appears outside")
    put(S(6) + 0.06, pop(700), -22, 0.5, "VOCÊ plate")
    put(S(7) - 0.03, buzz(0.14, 160), -17, -0.3, "no entry")
    put(S(7) - 0.03, clack(1400, 220), -20, -0.3, "no-entry badge lands")
    put(S(9) + 0.02, seq(beep(523, 0.07, 0.2), 0.03, beep(784, 0.1, 0.2)), -21, 0.5, "question mark over the pawn")
    # ---- full screen 1: the cost sheet
    put(FS1 - 0.42, riser(0.42), -17, 0, "riser into full screen")
    put(FS1, whoosh(0.45, 2500, 500, shape="out"), -15, (-0.4, 0.4), "full screen wipe")
    put(FS1, thud(), -16, 0, "full screen hit")
    put(FS1, paper(0.2), -23, 0, "cost sheet drops in")
    put(FS1 + 0.3, clack(1300, 200), -19, 0, "cost sheet lands")
    put(FS1 + 0.2, zip_up(0.34), -23, -0.2, "VOCÊ rises on the pedestal")
    put(FS1 + 0.5, thud(), -19, -0.2, "pedestal stops")
    put(S(15) - 0.04, tick(1800), -22, 0.3, "cursor lands on the cost cell")
    put(S(16) - 0.04, pop(620), -19, -0.2, "VOCÊ lights up")
    put(S(17) + 0.02, zip_up(0.5), -25, 0.3, "gold bar grows in the cell")
    for k in range(8):
        put(S(17) + 0.06 + k * 0.085 + 0.09, coin(2600 * 1.045 ** k), -19 + 0.5 * k, 0.4, "coin on the stack (custa)")
    put(S(18) - 0.04, pop(760), -20, 0.4, "calendar MÊS")
    put(S(19) + 0.04, paper(0.16), -21, 0.4, "calendar page flips")
    put(C3 - 0.02, whoosh(0.4, 1800, 500), -19, 0, "back to the face")
    # ---- the tool
    put(C3 - 0.14, servo(0.46), -24, 0.2, "robot rises")
    put(C3 + 0.16, thud(), -19, 0.2, "robot lands")
    put(C3 + 0.36, seq(beep(880, 0.05), 0.03, beep(1320, 0.07)), -26, 0.2, "robot switches on")
    put(S(22) + 0.04, pop(880), -20, 0.5, "price tag R$ ?")
    put(S(24) - 0.04, pop(600), -20, 0.2, "FERRAMENTA plate")
    put(S(24), beep(990, 0.05), -25, 0.2, "robot tilts its head")
    put(S(25) - 0.14, whoosh(0.45, 400, 1800), -22, (0.0, 0.5), "camera pans to the parcels")
    for k, t in enumerate([S(26) - 0.02, S(27), S(28) + 0.02, S(29) + 0.14]):
        put(t, bloop(300 + 30 * k, 640 + 40 * k), -22, 0.2, "parcel out")
        put(t + 0.34, cardboard(), -16, 0.5, "parcel lands")
        put(t + 0.37, tick(2400 + 150 * k), -25, 0.5, "delivered")
    put(S(29) + 0.06, pop(700), -21, 0.5, "ENTREGAS plate")
    put(S(30) - 0.16, whoosh(0.5, 300, 2200), -20, (0.4, -0.3), "camera pulls back to both")
    put(S(30) - 0.04, pop(520), -19, -0.6, "VOCÊ appears")
    for k in range(8):
        t = S(30) + 0.1 + k * 0.05 + 0.09
        put(t, coin(2500 * 1.045 ** k), -22 + 0.4 * k, -0.3, "coin: your stack")
        put(t + 0.012, coin(2700 * 1.045 ** k), -22 + 0.4 * k, 0.1, "coin: the tool's stack")
    tm = S(31)
    put(tm, boom(95, 50, 0.4, 0.1, 0.2, 0.6), -11, 0, "METADE: the 1/2 lands")
    put(tm + 0.02, register(), -16, 0, "half the price")
    for j in range(4):
        put(tm + 0.05 + j * 0.03, whoosh(0.2, 1500, 4000), -23, (0.0, 0.3), "half of the tool's coins fly off")
    for k, (f, p) in enumerate(zip([1568, 2093, 2637], [-0.5, 0.3, -0.1])):
        put(S(33) + 0.02 + k * 0.11, chime(f, 0.5), -25, p, "sparkle")
    put(tm + 0.12, beep(1320, 0.05), -25, 0.5, "robot nods")
    # ---- not evil
    put(C4 - 0.08, sting(), -15, 0, "the little devil")
    put(C4 - 0.08, pop(320), -19, 0, "devil pops")
    tn = S(36) - 0.06
    put(tn, clang(), -14, 0, "crossed out: NÃO é maldade")
    put(tn + 0.02, buzz(0.12, 170), -21, 0, "no")
    # ---- full screen 2: the sheet, the heart, the zero
    put(FS2 - 0.42, riser(0.42), -17, 0, "riser into full screen")
    put(FS2 - 0.02, whoosh(0.36, 2500, 500, shape="out"), -15, (0.4, -0.4), "the sheet falls from the top")
    tl0 = FS2 + 0.32
    put(tl0, boom(100, 40, 0.5), -9, 0, "É PLANILHA: the sheet lands")
    put(tl0, clack(1100, 190), -17, 0, "sheet knock")
    for n in range(15):
        put(tl0 + 0.12 + n * 0.034, tick(1900 + 70 * n), -27, -0.5 + n / 15, "cell fills")
    put(S(39) - 0.06, pop(640), -20, 0, "formula bar: = SENTIMENTO")
    put(S(39) - 0.03, tick(1800), -23, 0.2, "cursor on the empty cell")
    put(S(40) - 0.06, bloop(400, 720), -19, 0.2, "the heart appears")
    for t in (S(40) + 0.2, S(40) + 0.42):
        put(t, heartbeat(), -14, 0.2, "heartbeat")
    tf, land = S(41) + 0.02, S(42) + 0.06
    put(tf, whoosh(max(0.12, land - tf), 1800, 500, shape="in"), -21, 0.2, "the heart falls")
    put(land, boom(140, 70, 0.2, 0.06, 0.1, 0.5), -15, 0.2, "the heart lands on the cell")
    ts = S(43) - 0.1
    put(ts, scan(0.3, 1500, 500), -21, 0, "the sheet scans it")
    put(ts + 0.1, bloop(600, 160, 0.26), -20, 0.2, "the heart goes grey")
    put(ts + 0.36, buzz(0.14, 150), -18, 0.2, "= 0")
    put(ts + 0.38, flatline(max(0.1, C5 - 0.04 - (ts + 0.38))), -26, 0, "flatline")
    put(C5 - 0.06, whoosh(0.34, 1800, 500), -23, 0, "back to the face")
    # ---- CTA
    put(C5 - 0.1, paper(0.2), -22, -0.5, "mini sheet flips in")
    put(C5 + 0.04, pop(640), -21, 0.4, "comment card")
    for n in range(14):
        put(C5 + 0.2 + n * 0.03, tick(1800 + 60 * n), -28, -0.5, "mini sheet fills")
    put(S(47) - 0.03, tick(1800), -23, -0.5, "cursor on the cell")
    put(S(50) - 0.05, chime(1568, 0.5), -20, -0.5, "what you deliver appears")
    put(S(50) - 0.05, pop(700), -21, -0.5, "gift pops")
    tg = S(52) - 0.02
    put(tg, zip_up(0.42), -19, -0.5, "it grows")
    tb = tg + 0.12
    put(tb, crack(), -13, -0.5, "the cell gives way")
    put(tb, boom(110, 50, 0.4), -12, -0.3, "it does not fit")
    for k, f in enumerate([1568, 1976, 2349, 2637]):
        put(S(54) + 0.1 + k * 0.16, chime(f, 0.5), -24, -0.5 + 0.15 * k, "sparkle")
    for t in REEL["typed"]:
        put(t, typeclick(), -27, 0.4, "typing")
    put(E(55) + 0.02, chime(1568, 0.4), -22, 0.4, "comment ready")
    for k, f in enumerate([2093, 2637, 3136]):
        put(E(55) + 0.02 + k * 0.12, chime(f, 0.45), -26, -0.5, "sparkle")
    put(E(55) + 0.3, tok(1100), -22, 0.5, "follow")
    put(TOTAL - 0.42, riser(0.42), -19, 0, "loop: riser into the door slam")


# =====================================================================================================
# 4. MIX + MASTER + MUX
# =====================================================================================================
def main():
    raw, voice = treat_voice()
    design()
    sfx = bus.copy() * db(SFX_TRIM)
    for c in range(2):                                        # effects sit behind the voice: no rumble, no fizz, a dip where speech lives
        sfx[:, c] = peaking(lp(hp(sfx[:, c], 45), 11000), 2000, -3.0, 0.7)
    n = min(len(voice), N)
    # the voice always wins where speech lives: while he speaks, the 300-3400 Hz part of the effects ducks up to 9 dB
    # (their lows and highs stay, so an impact still lands on the word without covering it)
    sos = signal.butter(2, [300, 3400], "bandpass", fs=SR, output="sos")
    mid = np.stack([signal.sosfiltfilt(sos, sfx[:, c]) for c in range(2)], 1)
    vb = np.zeros(N)
    vb[:n] = signal.sosfiltfilt(sos, voice[:n])
    e = 10 * np.log10(ndi.uniform_filter1d(vb ** 2, int(0.03 * SR)) + 1e-12)
    act = np.clip((e - (np.percentile(e, 95) - 24)) / 18, 0, 1)
    duck = db(-9.0 * ndi.uniform_filter1d(act, int(0.02 * SR)))
    sfx = (sfx - mid) + mid * duck[:, None]
    mix = np.zeros((N, 2))
    mix[:n, 0] += voice[:n]
    mix[:n, 1] += voice[:n]
    mix += sfx
    peak = np.abs(mix).max()
    print(f"pre-master: voice rms {rms_db(voice):.1f}, sfx rms {rms_db(sfx):.1f} dBFS, mix peak {20 * np.log10(peak):.1f} dBFS, {len(log)} sound events")
    vst = np.zeros((N, 2))
    vst[:n, 0] = voice[:n]
    vst[:n, 1] = voice[:n]
    sf.write(str(HERE / "stem_voice.wav"), vst.astype("float32"), SR)
    sf.write(str(HERE / "stem_sfx.wav"), sfx.astype("float32"), SR)
    # master: bring the mix to -14 LUFS with a plain gain, hold the peaks at -1.6 dBFS, and repeat
    # (limiting takes a little loudness away). No automatic normaliser touches the dynamics.
    master = mix
    for _ in range(3):
        i, tp, lra = loudness(master)
        master, lim_max, lim_share = limiter(master * db(-14.0 - i), db(-1.6))
    i, tp, lra = loudness(master)
    print(f"master: {i:.1f} LUFS, true peak {tp:.1f} dBTP, LRA {lra:.1f} LU (limiter down to {lim_max:.1f} dB on {lim_share * 100:.1f} % of the time)")
    sf.write(str(HERE / "master.wav"), master, SR, subtype="PCM_24")
    json.dump([{"t": t, "what": w, "peak_db": p} for t, w, p in sorted(log)], open(HERE / "events.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    out = EDIT.parent / f"{NAME}_final.mp4"
    tmp = EDIT / "_newaudio.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(RAW), "-i", str(HERE / "master.wav"), "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", str(SR), "-movflags", "+faststart", str(tmp)], check=True)
    tmp.replace(out)
    print("written", out)


if __name__ == "__main__":
    main()
