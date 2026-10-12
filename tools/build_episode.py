#!/usr/bin/env python3
"""Vertont eine Podcast-Folge aus einer JSON-Datei.

Aufruf (aus dem Repository-Wurzelverzeichnis):
    python3 tools/build_episode.py episodes/folge-002.json

Erzeugt episodes/folge-002.mp3 und episodes/folge-002.md (Skript zum Mitlesen)
und traegt die Folge in episodes/episodes.json ein. Danach tools/feed.py ausfuehren.
Aufbau der JSON-Datei: siehe ANLEITUNG.md.
"""
import glob, hashlib, json, os, re, subprocess, sys
import numpy as np
import soundfile as sf
import sherpa_onnx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.environ.get("PODCAST_MODELS", os.path.expanduser("~/.cache/spanisch-podcast-models"))
CACHE = os.path.expanduser("~/.cache/spanisch-podcast-tts")
SR = 22050
os.makedirs(CACHE, exist_ok=True)

# Stimmen: Spanisch = Stimme 4 (es_MX "claude", von Felix gewaehlt), Deutsch = thorsten
VOICE = {
    "es": (f"{MODELS}/vits-piper-es_MX-claude-high/", 0),
    "de": (f"{MODELS}/vits-piper-de_DE-thorsten-medium/", 0),
}
ES_SLOW = 0.65   # ca. 120-130 Woerter/Minute - von Felix als gut verstaendlich bestaetigt
DE_SPEED = 1.0

_models = {}

def model(lang):
    if lang not in _models:
        d, _ = VOICE[lang]
        onnx = glob.glob(d + "*.onnx")[0]
        cfg = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                    model=onnx, tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data"),
                num_threads=4, provider="cpu"),
            max_num_sentences=1)
        _models[lang] = sherpa_onnx.OfflineTts(cfg)
    return _models[lang]

def clean(t):
    t = t.replace("—", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", t).strip()

def resample(x, sr):
    if sr == SR:
        return x
    n = int(len(x) * SR / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)

def synth(lang, text, speed):
    d, sid = VOICE[lang]
    key = hashlib.sha1(f"{lang}|{d}|{sid}|{speed}|{text}".encode()).hexdigest()
    path = f"{CACHE}/{key}.npy"
    if os.path.exists(path):
        return np.load(path)
    a = model(lang).generate(text, sid=sid, speed=speed)
    x = resample(np.array(a.samples, dtype=np.float32), a.sample_rate)
    x = x * (10 ** (-21 / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-9))
    peak = np.max(np.abs(x)) + 1e-9
    if peak > 0.95:
        x = x * (0.95 / peak)
    np.save(path, x)
    return x

def chime():
    t = np.arange(int(0.55 * SR)) / SR
    def tone(f, start, dur):
        env = np.exp(-(t - start) * 7) * ((t >= start) & (t < start + dur))
        return np.sin(2 * np.pi * f * t) * env
    return (0.16 * (tone(880, 0.0, 0.3) + tone(1318.5, 0.18, 0.37))).astype(np.float32)

def sentences(t):
    return [x for x in re.split(r"(?<=[.!?])\s+", t.strip()) if x]

class Track:
    def __init__(s):
        s.parts, s.t, s.chapters, s.doc = [], 0.0, [], []
    def add(s, x):
        s.parts.append(x); s.t += len(x) / SR
    def pause(s, sec):
        s.add(np.zeros(int(sec * SR), dtype=np.float32))
    def say(s, lang, text, pause=0.6, speed=None):
        if speed is None:
            speed = ES_SLOW if lang == "es" else DE_SPEED
        s.add(synth(lang, clean(text), speed)); s.pause(pause)
    def chime(s):
        s.add(chime()); s.pause(0.6)
    def mark(s, title):
        s.chapters.append((s.t, title))

def mmss(sec):
    return f"{int(sec // 60):02d}:{int(sec % 60):02d}"

NUM = ["eins", "zwei", "drei", "vier"]

def build(ep):
    tr = Track(); D = tr.doc

    tr.mark("Einführung"); tr.chime()
    D.append("## Einführung\n")
    for s in ep["intro"]:
        tr.say("de", s, 0.7); D.append(s + "\n")

    if ep.get("warmup"):
        tr.chime(); tr.mark("Aufwärmen")
        D.append("\n## Aufwärmen: Wörter aus früheren Mails\n")
        tr.say("de", "Zum Aufwärmen ein paar Wörter aus früheren Mails. Du hörst das spanische Wort, denkst kurz nach, und danach kommt die Lösung.", 1.0)
        for es, de in ep["warmup"]:
            tr.say("es", es, 3.6); tr.say("de", de, 1.0); tr.say("es", es, 1.6)
            D.append(f"- **{es}** – {de}")

    for i, st in enumerate(ep["stories"]):
        tr.chime(); tr.mark(f"Geschichte {i + 1}: {st['title_es']}")
        D.append(f"\n## Geschichte {i + 1}: {st['title_es']} – {st['title_de']}\n*{st['setting']}*\n")
        tr.say("de", f"Geschichte {NUM[i]}.", 0.6)
        tr.say("es", st["title_es"], 0.9)
        tr.say("de", f"{st['title_de']}. {st['setting']}", 1.0)

        # A) einmal komplett, langsam, Satz fuer Satz mit Pausen
        tr.say("de", "Hör dir zuerst die ganze Geschichte an, langsam und mit Pausen. Du musst noch nicht alles verstehen.", 1.2)
        for es, de in st["blocks"]:
            for sen in sentences(es):
                tr.say("es", sen, 1.3)
            tr.pause(0.7)

        # B) Satz fuer Satz mit deutscher Uebersetzung
        tr.say("de", "Jetzt Satz für Satz, mit Übersetzung.", 1.2)
        D.append("\n**Satz für Satz**\n")
        for es, de in st["blocks"]:
            for sen in sentences(es):
                tr.say("es", sen, 1.3)
            tr.pause(0.5)
            tr.say("de", de, 2.2)
            D.append(f"🇪🇸 {es}  \n🇩🇪 *{de}*\n")

        # C) neue Woerter: spanisch - deutsch - spanisch
        tr.say("de", "Die wichtigsten neuen Wörter.", 1.0)
        D.append("\n**Neue Wörter**\n")
        for es, de in st["vocab"]:
            tr.say("es", es, 1.0); tr.say("de", de, 1.0); tr.say("es", es, 2.5)
            D.append(f"- **{es}** – {de}")

        # D) Grammatik-Tipp
        D.append("")
        tip_txt = []
        for lang, txt in st["tip"]:
            tr.say(lang, txt, 0.6 if lang == "de" else 1.0)
            tip_txt.append(txt if lang == "de" else f"*{txt}*")
        D.append("💡 " + " ".join(tip_txt) + "\n")
        tr.pause(0.8)

    # Quiz: deutsches Wort - Pause - spanisches Wort
    tr.chime(); tr.mark("Quiz")
    D.append("\n## Quiz\n")
    tr.say("de", "Zum Abschluss ein kleines Quiz. Du hörst das deutsche Wort, sagst es auf Spanisch, und danach kommt die Lösung.", 1.0)
    for de, es in ep["quiz"]:
        tr.say("de", de, 4.0); tr.say("es", es, 1.6)
        D.append(f"- {de} → **{es}**")
    if ep.get("quiz_grammar"):
        tr.say("de", "Und noch ein paar Formen zur Grammatik.", 0.8)
        for de, es in ep["quiz_grammar"]:
            tr.say("de", de, 4.0); tr.say("es", es, 1.6)
            D.append(f"- {de} → **{es}**")

    tr.chime(); tr.mark("Abschluss")
    D.append("\n## Abschluss\n")
    for s in ep["outro"]:
        tr.say("de", s, 0.7); D.append(s + "\n")
    tr.say("es", "¡Hasta pronto!", 1.0)
    return tr

def main(path):
    ep = json.load(open(path, encoding="utf-8"))
    n = int(ep["number"])
    stem = os.path.join(ROOT, "episodes", f"folge-{n:03d}")
    tr = build(ep)
    audio = np.concatenate(tr.parts)
    wav = stem + ".wav"
    sf.write(wav, audio, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-ac", "1",
                    "-codec:a", "libmp3lame", "-b:a", "64k",
                    "-metadata", f"title={ep['title']}",
                    "-metadata", "artist=Español A1 en el coche",
                    "-metadata", "album=Español A1 en el coche",
                    "-metadata", f"track={n}",
                    stem + ".mp3"], check=True)
    os.remove(wav)
    total = len(audio) / SR

    with open(stem + ".md", "w", encoding="utf-8") as f:
        f.write(f"# {ep['title']}\n\nLänge: ca. {mmss(total)} Minuten\n\n**Kapitel**\n\n")
        for t, title in tr.chapters:
            f.write(f"- {mmss(t)} {title}\n")
        f.write("\n---\n\n" + "\n".join(tr.doc) + "\n")

    idx_path = os.path.join(ROOT, "episodes", "episodes.json")
    idx = json.load(open(idx_path, encoding="utf-8")) if os.path.exists(idx_path) else []
    idx = [e for e in idx if int(e["number"]) != n]
    idx.append({
        "number": n,
        "title": ep["title"],
        "description": ep["description"],
        "date": ep["date"],
        "file": f"episodes/folge-{n:03d}.mp3",
        "bytes": os.path.getsize(stem + ".mp3"),
        "duration": int(round(total)),
        "chapters": [[round(t), title] for t, title in tr.chapters],
    })
    idx.sort(key=lambda e: int(e["number"]))
    json.dump(idx, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Folge {n}: {mmss(total)} min, {os.path.getsize(stem + '.mp3') / 1e6:.1f} MB")
    for t, title in tr.chapters:
        print("  ", mmss(t), title)

if __name__ == "__main__":
    main(sys.argv[1])
