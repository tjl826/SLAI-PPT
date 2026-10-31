#!/usr/bin/env python3
"""Rebuild previews without modifying PPTX sources. Requires PyMuPDF and Pillow.

Usage:
    python3 -m pip install -r scripts/requirements-preview.txt
    python3 scripts/build_previews.py
    python3 scripts/build_previews.py --skip-convert

LibreOffice is required unless --skip-convert is used. Hidden slides are included.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET
import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
STYLES = {
    1: ("波纹学术", "Wave", "适合组会、研究进展与通用学术汇报"),
    2: ("经典校徽", "Classic", "适合开题、答辩与正式研究汇报"),
    3: ("校园图文", "Campus", "适合图文叙事、课程展示与综合汇报"),
    4: ("深色极简", "Dark", "适合简洁的研究展示与专题报告"),
    5: ("浅色极简", "Light", "适合论文分享、日常汇报与成果交流"),
}
P_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}"

def ppt_info(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        slides = sorted([n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)],
                        key=lambda s: int(re.search(r"slide(\d+)", s).group(1)))
        hidden = [i for i, n in enumerate(slides, 1) if ET.fromstring(z.read(n)).get("show") in {"0", "false"}]
        p = ET.fromstring(z.read("ppt/presentation.xml"))
        size = p.find(P_NS + "sldSz")
        return {"slides": len(slides), "hidden_slides": hidden,
                "slide_width_emu": int(size.get("cx")), "slide_height_emu": int(size.get("cy")),
                "native_charts": sum(bool(re.fullmatch(r"ppt/charts/chart\d+\.xml", n)) for n in names)}

def find_font(size: int):
    # System fonts are used only for rasterized labels. No font files are shipped.
    paths = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
             "/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Light.ttc",
             "C:/Windows/Fonts/msyh.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def render(pdf: Path, dest: Path) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    with fitz.open(pdf) as doc:
        for i, page in enumerate(doc, 1):
            scale = 1440 / page.rect.width
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            pix.save(dest / f"{i:02}.png")
        # Remove obsolete numbered previews only after a successful render.
        for old in dest.glob("[0-9][0-9].png"):
            if int(old.stem) > len(doc):
                old.unlink()
        return len(doc)

def contact_sheet(entry: dict):
    cols, tw, th, gap, label_h = 3, 480, 270, 18, 32
    rows = math.ceil(entry["slides"] / cols)
    w = cols * tw + (cols + 1) * gap
    h = 90 + rows * (th + label_h + gap) + gap
    sheet = Image.new("RGB", (w, h), "#f5f2f4")
    d = ImageDraw.Draw(sheet)
    title = f'{entry["label"]} · {entry["style_zh"]} / {entry["style_en"]} · {entry["slides"]} pages'
    d.text((gap, 20), title, font=find_font(28), fill="#881E55")
    for i in range(1, entry["slides"] + 1):
        x = gap + ((i - 1) % cols) * (tw + gap)
        y = 90 + ((i - 1) // cols) * (th + label_h + gap)
        with Image.open(ROOT / entry["image_dir"] / f"{i:02}.png") as im:
            im.thumbnail((tw, th), Image.Resampling.LANCZOS)
            sheet.paste(im, (x, y))
        label = f'{i:02}' + (" · hidden guide" if i in entry["hidden_slides"] else "")
        d.text((x + 5, y + th + 3), label, font=find_font(18), fill="#5c5360")
    sheet.save(ROOT / entry["image_dir"] / "contact-sheet.jpg", quality=90)

def write_gallery(entry: dict):
    p = Path(entry["file"])
    lines = [f'# {entry["label"]} · {entry["style_zh"]} / {entry["style_en"]}', '',
             '[返回首页 / Back](../README.md)', '',
             f'[下载 PPTX](../{quote(p.as_posix())}?raw=true) · [完整 PDF](../{entry["pdf"]}) · [缩略图总览](../{entry["image_dir"]}/contact-sheet.jpg)', '',
             f'共 {entry["slides"]} 页。隐藏页也包含在本预览中，PPTX 原始隐藏状态不变。', '',
             '预览由 LibreOffice 自动导出；字体替代或图表渲染可能与 PowerPoint 略有差异，以下载的原始文件为准。', '']
    for i in range(1, entry['slides'] + 1):
        hidden = ' · 原始文件中为隐藏页 / hidden slide' if i in entry['hidden_slides'] else ''
        lines += [f'## {i:02}{hidden}', '', f'![{entry["label"]} 第 {i} 页](../{entry["image_dir"]}/{i:02}.png)', '']
    (ROOT / 'docs' / f'{entry["id"]}.md').write_text('\n'.join(lines), encoding='utf-8')

def overview(entries: list[dict]):
    width, gap, thumb_w, thumb_h = 1600, 40, 740, 416
    row_h, top = 485, 200
    img = Image.new('RGB', (width, top + 5 * row_h + 70), '#f8f5f7')
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, width, 10), fill='#881E55')
    d.text((gap, 38), 'HETAO–PPT', font=find_font(48), fill='#881E55')
    d.text((gap, 107), '深圳河套学院 · 学术汇报模板 / Academic Presentation Templates', font=find_font(27), fill='#51414c')
    d.text((gap, 157), '中文 / Chinese', font=find_font(22), fill='#881E55')
    d.text((820, 157), '英文 / English', font=find_font(22), fill='#881E55')
    for e in entries:
        x = gap if e['language'] == 'zh' else 820
        y = top + (e['variant'] - 1) * row_h
        with Image.open(ROOT / e['image_dir'] / '01.png') as im:
            im.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            img.paste(im, (x, y))
        d.text((x, y + thumb_h + 8), f'{e["variant"]:02}  {e["style_zh"]} / {e["style_en"]}   ·   {e["slides"]} slides', font=find_font(23), fill='#51414c')
    d.text((gap, img.height - 48), '5 styles · 10 editable PPTX files · 168 source slides · Personal collection / 非官方发布', font=find_font(22), fill='#766574')
    img.save(ROOT / 'imgs' / 'overview.jpg', quality=92)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skip-convert', action='store_true', help='Use PDFs already in previews/.')
    args = ap.parse_args()
    sources = sorted(ROOT.glob('*.pptx'))
    if not sources:
        raise SystemExit('No PPTX source files found in repository root.')
    for name in ['imgs', 'previews', 'docs']:
        (ROOT / name).mkdir(exist_ok=True)
    entries = []
    for f in sources:
        m = re.search(r'_(中文|英文)([1-5])\.pptx$', f.name)
        if not m:
            continue
        language, v = ('zh' if m.group(1) == '中文' else 'en'), int(m.group(2))
        key = f'{language}-{v:02}'
        style_zh, style_en, desc = STYLES[v]
        e = {'id': key, 'file': f.name, 'language': language, 'variant': v,
             'label': f'{m.group(1)} {v}', 'style_zh': style_zh, 'style_en': style_en,
             'description': desc, 'bytes': f.stat().st_size, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest(),
             'pdf': f'previews/{key}.pdf', 'image_dir': f'imgs/{key}', 'gallery': f'docs/{key}.md', **ppt_info(f)}
        entries.append(e)
    if not args.skip_convert:
        soffice = shutil.which('soffice') or shutil.which('libreoffice')
        mac = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
        if not soffice and Path(mac).exists():
            soffice = mac
        if not soffice:
            raise SystemExit('LibreOffice not found. Install it or use --skip-convert with existing PDFs.')
        with tempfile.TemporaryDirectory(prefix='hetoo-ppt-') as temp:
            out = Path(temp) / 'pdf'; out.mkdir()
            profile = (Path(temp) / 'profile').as_uri()
            filt = 'pdf:impress_pdf_Export:{"ExportHiddenSlides":{"type":"boolean","value":"true"}}'
            cmd = [soffice, f'-env:UserInstallation={profile}', '--headless', '--convert-to', filt, '--outdir', str(out)]
            subprocess.run(cmd + [str(ROOT / e['file']) for e in entries], check=True, timeout=300)
            for e in entries:
                result = out / (Path(e['file']).stem + '.pdf')
                if not result.exists():
                    raise RuntimeError(f'Conversion did not create {result.name}')
                shutil.copy2(result, ROOT / e['pdf'])
    for e in entries:
        pdf = ROOT / e['pdf']
        if not pdf.exists():
            raise FileNotFoundError(f'Missing PDF: {pdf}; run without --skip-convert first.')
        pages = render(pdf, ROOT / e['image_dir'])
        if pages != e['slides']:
            raise RuntimeError(f'{e["id"]}: PDF has {pages} pages, PPTX has {e["slides"]}. Check ExportHiddenSlides.')
        contact_sheet(e)
        write_gallery(e)
        print(f'{e["id"]}: {pages} pages rendered')
    (ROOT / 'catalog.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    overview(entries)
    print(f'Done: {len(entries)} templates / {sum(e["slides"] for e in entries)} pages. PPTX sources unchanged.')

if __name__ == '__main__':
    main()
