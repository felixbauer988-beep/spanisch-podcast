#!/usr/bin/env python3
"""Erzeugt cover.jpg (3000 x 3000 px), wie von Spotify/Apple verlangt."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = 3000
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

img = Image.new("RGB", (W, W))
d = ImageDraw.Draw(img)
top, bottom = (196, 69, 54), (241, 160, 60)          # Terrakotta -> Orange
for y in range(W):
    t = y / W
    d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)))

# Strasse mit Mittelstreifen (Perspektive)
road = [(W * 0.30, W), (W * 0.70, W), (W * 0.53, W * 0.62), (W * 0.47, W * 0.62)]
d.polygon(road, fill=(52, 52, 60))
for k in range(6):
    y0 = W * 0.64 + k * k * 22 + k * 40
    h = 30 + k * 26
    w = 10 + k * 9
    d.rectangle([W / 2 - w / 2, y0, W / 2 + w / 2, y0 + h], fill=(250, 214, 92))

def center(text, font, y, fill):
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=font)
    d.text(((W - (x1 - x0)) / 2, y), text, font=font, fill=fill)

center("Español A1", ImageFont.truetype(BOLD, 400), 520, (255, 248, 235))
center("en el coche", ImageFont.truetype(BOLD, 300), 1000, (255, 248, 235))
center("Spanisch hören im Auto", ImageFont.truetype(REG, 150), 1440, (255, 236, 214))

img.save(os.path.join(ROOT, "cover.jpg"), quality=90)
print("cover.jpg geschrieben")
