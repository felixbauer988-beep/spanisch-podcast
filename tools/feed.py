#!/usr/bin/env python3
"""Schreibt feed.xml (Podcast-RSS fuer Spotify) aus episodes/episodes.json.

Aufruf (aus dem Repository-Wurzelverzeichnis):  python3 tools/feed.py
"""
import json, os
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://felixbauer988-beep.github.io/spanisch-podcast/"
BERLIN = timezone(timedelta(hours=1))  # Uhrzeit nur fuer die Sortierung, Sommerzeit egal

SHOW = {
    "title": "Español A1 en el coche",
    "author": "Español A1 en el coche",
    "owner_name": "Felix",
    "owner_email": "felix.bauer88@yahoo.de",
    "description": ("Spanisch hören im Auto, Niveau A1: In jeder Folge drei kurze Alltagsgeschichten, "
                    "langsam gesprochen, Satz für Satz mit deutscher Übersetzung, dazu die wichtigsten "
                    "neuen Wörter, ein Grammatik-Tipp und ein kleines Vokabelquiz."),
    "language": "de",
}

def hms(sec):
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"

def main():
    eps = json.load(open(os.path.join(ROOT, "episodes", "episodes.json"), encoding="utf-8"))
    eps = sorted(eps, key=lambda e: int(e["number"]), reverse=True)
    now = format_datetime(datetime.now(timezone.utc))
    items = []
    for e in eps:
        d = datetime.strptime(e["date"], "%Y-%m-%d").replace(tzinfo=BERLIN)
        d = d + timedelta(hours=18, minutes=int(e["number"]) % 50)
        url = BASE + e["file"]
        chapters = "\n".join(f"{int(t) // 60:02d}:{int(t) % 60:02d} {c}" for t, c in e.get("chapters", []))
        desc = e["description"] + ("\n\nKapitel:\n" + chapters if chapters else "")
        items.append(f"""    <item>
      <title>{escape(e['title'])}</title>
      <description>{escape(desc)}</description>
      <itunes:summary>{escape(desc)}</itunes:summary>
      <pubDate>{format_datetime(d)}</pubDate>
      <enclosure url="{escape(url)}" length="{e['bytes']}" type="audio/mpeg"/>
      <guid isPermaLink="false">spanisch-podcast-folge-{int(e['number']):03d}</guid>
      <itunes:duration>{hms(int(e['duration']))}</itunes:duration>
      <itunes:episode>{int(e['number'])}</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:explicit>false</itunes:explicit>
    </item>""")
    s = SHOW
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(s['title'])}</title>
    <link>{BASE}</link>
    <atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>
    <description>{escape(s['description'])}</description>
    <language>{s['language']}</language>
    <lastBuildDate>{now}</lastBuildDate>
    <itunes:author>{escape(s['author'])}</itunes:author>
    <itunes:summary>{escape(s['description'])}</itunes:summary>
    <itunes:owner>
      <itunes:name>{escape(s['owner_name'])}</itunes:name>
      <itunes:email>{escape(s['owner_email'])}</itunes:email>
    </itunes:owner>
    <itunes:image href="{BASE}cover.jpg"/>
    <image><url>{BASE}cover.jpg</url><title>{escape(s['title'])}</title><link>{BASE}</link></image>
    <itunes:category text="Education">
      <itunes:category text="Language Learning"/>
    </itunes:category>
    <itunes:explicit>false</itunes:explicit>
    <itunes:type>episodic</itunes:type>
{chr(10).join(items)}
  </channel>
</rss>
"""
    open(os.path.join(ROOT, "feed.xml"), "w", encoding="utf-8").write(xml)
    print(f"feed.xml mit {len(eps)} Folge(n) geschrieben.")

if __name__ == "__main__":
    main()
