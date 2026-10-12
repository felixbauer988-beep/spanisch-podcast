# Español A1 en el coche — Anleitung zum Erstellen neuer Folgen

Dieses Repository ist der Podcast-Feed für Felix' Spanisch-Podcast. GitHub Pages veröffentlicht es unter
`https://felixbauer988-beep.github.io/spanisch-podcast/`, Spotify liest `feed.xml` von dort.

## Wöchentlicher Ablauf (jeden Sonntagabend, zwei Folgen)

1. Repository klonen, dann `bash tools/setup.sh` (installiert sherpa-onnx und lädt die beiden Stimmen).
2. In Gmail (Entwürfe) die sechs Lern-Mails der abgelaufenen Woche lesen, Betreff
   `Spanisch A1 — Tag N — …` (Montag bis Samstag; Montag 12.10.2026 = Tag 21, Sonntage zählen nicht).
3. Zwei JSON-Dateien schreiben:
   - erste Folge: Geschichten aus den Mails von **Montag, Dienstag, Mittwoch**
   - zweite Folge: Geschichten aus den Mails von **Donnerstag, Freitag, Samstag**
   Nummer = höchste Nummer in `episodes/episodes.json` + 1. Dateiname `episodes/folge-NNN.json` (dreistellig).
   `date` = Datum des Sonntags (YYYY-MM-DD).
4. Vertonen: `python3 tools/build_episode.py episodes/folge-NNN.json` (je ca. 2–3 Minuten).
   Erwartete Länge pro Folge: ca. 20–25 Minuten. Bei über 26 Minuten die Geschichten kürzen und neu bauen.
5. `python3 tools/feed.py`, dann `git add -A && git commit -m "Folgen NNN und NNN+1" && git push`.
6. Aufräumen: MP3-Dateien, die älter als 26 Wochen sind, löschen und aus `episodes/episodes.json` entfernen,
   danach `tools/feed.py` erneut ausführen (Speicherplatz im Repository).

## Inhaltliche Regeln

- Niveau **A1** (Präsens, Pretérito Perfecto, estar + gerundio, ir a + Infinitiv; kein Indefinido/Imperfecto/Subjuntivo).
- Pro Folge **genau drei** abgeschlossene Geschichten. Jede Geschichte ist eine **gekürzte Hörfassung** des
  Mail-Textes: 6 Blöcke mit je 2–3 kurzen Sätzen, zusammen ca. 150–180 spanische Wörter, Ich-Erzähler oder
  Dialog, mit der Zielgrammatik und den wichtigsten Vokabeln der Mail. Kurze, klare Sätze (gut fürs Hören).
- Zu jedem Block die deutsche Übersetzung.
- `vocab`: 8 neue Wörter der Geschichte (Spanisch, Deutsch), am besten die aus der Mail-Tabelle „Vokabeln — Neu“.
- `tip`: kurzer Grammatik-Tipp zur Zielgrammatik der Mail, abwechselnd deutsche Erklärung und kurze spanische Beispiele.
- `warmup`: 6 Wörter aus Mails, die 1–3 Wochen zurückliegen (Spanisch, Deutsch).
- `quiz`: 12 Wörter aus den drei Geschichten als (Deutsch, Spanisch); `quiz_grammar`: 3 Verbformen/Kurzsätze.
- Nur den Vornamen „Felix“ verwenden, keine weiteren persönlichen Angaben (der Podcast ist öffentlich).

## JSON-Format (Beispiel: `episodes/folge-001.json`)

```json
{
  "number": 2,
  "title": "Folge 2: Technik, Sprachen lernen und Verabredungen",
  "description": "Ein bis zwei Sätze zum Inhalt (deutsch), Grammatikthemen nennen.",
  "date": "2026-10-18",
  "intro": ["Hallo Felix und willkommen zu Español A1 en el coche, … Das ist Folge zwei.",
            "Heute hörst du drei kleine, abgeschlossene Geschichten aus deinen Lern-Mails: …",
            "Jede Geschichte läuft nach dem gleichen Muster. Zuerst hörst du sie einmal komplett auf Spanisch, langsam und mit Pausen. Dann folgt sie Satz für Satz, direkt mit deutscher Übersetzung. Danach kommen die wichtigsten neuen Wörter, und zum Schluss ein kleiner Grammatik-Tipp.",
            "Du musst nichts mitschreiben. Hör einfach zu und sprich laut mit, wenn du magst. Und jetzt: gute Fahrt!"],
  "warmup": [["la propina", "das Trinkgeld"]],
  "stories": [
    {"title_es": "…", "title_de": "…", "setting": "Ein Satz auf Deutsch zur Situation.",
     "blocks": [["Spanischer Block (2–3 Sätze).", "Deutsche Übersetzung."]],
     "vocab": [["la conexión", "die Verbindung"]],
     "tip": [["de", "Kleiner Grammatik-Tipp: …"], ["es", "Lo uso."], ["de", "ich benutze es"]]}
  ],
  "quiz": [["die Verbindung", "la conexión"]],
  "quiz_grammar": [["ich benutze es", "lo uso"]],
  "outro": ["Das war Folge zwei von Español A1 en el coche. …", "Bis zum nächsten Mal, und fahr sicher."]
}
```

## Technik

- Spanische Stimme: `vits-piper-es_MX-claude-high`, Tempo 0.65 (von Felix gewählt — nicht ändern).
- Deutsche Stimme: `vits-piper-de_DE-thorsten-medium`.
- Ablauf jeder Geschichte (in `tools/build_episode.py` fest eingebaut): einmal komplett langsam mit Pausen →
  Satz für Satz mit Übersetzung → neue Wörter (spanisch – deutsch – spanisch) → Grammatik-Tipp.
  Keine Nachsprech-Runde (von Felix nicht gewünscht).
- MP3: mono, 64 kbit/s, Lautheit -16 LUFS.
