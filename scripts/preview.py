"""Render SVGs to PNG with headless Chrome for visual review: python preview.py a.svg [b.svg ...]"""
import subprocess, sys, re
from pathlib import Path
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
out = Path(__file__).parent / ".preview"; out.mkdir(exist_ok=True)
for f in sys.argv[1:]:
    p = Path(f).resolve(); s = p.read_text(encoding="utf-8")
    w, h = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s).groups())
    html = out / (p.stem + ".html")
    html.write_text(f'<html><body style="margin:0;background:#2a2a2a"><img src="{p.as_uri()}" width="{int(w)}"></body></html>', encoding="utf-8")
    png = out / (p.stem + ".png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--screenshot={png}", f"--window-size={int(w)},{int(h)}", html.as_uri()], capture_output=True, timeout=60)
    print(png, png.exists())
