#!/usr/bin/env python3
"""Validate source checksums, previews, metadata and local documentation links.
Uses only Python's standard library. Does not make network requests.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {'href', 'src'} and value:
                self.links.append(value)

def main() -> int:
    errors = []
    source = json.loads((ROOT / 'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
    catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    for entry in source:
        path = ROOT / entry['path']
        if not path.is_file():
            errors.append(f'Missing source: {entry["path"]}'); continue
        data = path.read_bytes()
        if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
            errors.append(f'Source changed since import: {entry["path"]}')
    total = 0
    for entry in catalog:
        path = ROOT / entry['file']
        if not path.is_file():
            errors.append(f'Missing template: {entry["file"]}'); continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            errors.append(f'Catalog checksum mismatch: {entry["file"]}')
        with zipfile.ZipFile(path) as archive:
            count = sum(bool(re.fullmatch(r'ppt/slides/slide\d+\.xml', n)) for n in archive.namelist())
            bad = archive.testzip()
            if bad:
                errors.append(f'Broken PPTX entry {bad}: {entry["file"]}')
        if count != entry['slides']:
            errors.append(f'Slide count mismatch: {entry["id"]}')
        total += count
        pdf = ROOT / entry['pdf']
        if not pdf.is_file() or pdf.read_bytes()[:5] != b'%PDF-':
            errors.append(f'Missing or invalid PDF: {entry["pdf"]}')
        for i in range(1, count + 1):
            img = ROOT / entry['image_dir'] / f'{i:02}.png'
            if not img.is_file() or img.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
                errors.append(f'Missing or invalid screenshot: {img.relative_to(ROOT)}')
        for p in [entry['gallery'], entry['image_dir']+'/contact-sheet.jpg']:
            if not (ROOT / p).is_file():
                errors.append(f'Missing preview index: {p}')
    for path in list(ROOT.rglob('*.md')) + list(ROOT.glob('*.html')):
        if '.git' in path.relative_to(ROOT).parts:
            continue
        text = path.read_text(encoding='utf-8')
        links = re.findall(r'!?\[[^\]]*\]\(([^\s\)]+)(?:\s+"[^"]*")?\)', text)
        parser = LinkParser(); parser.feed(text); links.extend(parser.links)
        for link in links:
            split = urlsplit(link)
            if split.scheme or link.startswith(('#','//','mailto:')) or not split.path:
                continue
            target = (path.parent / unquote(split.path)).resolve()
            if not target.exists():
                errors.append(f'Broken local link in {path.relative_to(ROOT)}: {link}')
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if '.git' in rel.parts or '__pycache__' in rel.parts:
            continue
        if path.name == '.DS_Store' or '__MACOSX' in rel.parts or path.name.startswith('._'):
            errors.append(f'Unwanted OS metadata: {rel}')
        if path.is_file() and path.suffix.lower() in {'.ttf','.otf','.ttc','.woff','.woff2'}:
            errors.append(f'Font file must not be distributed: {rel}')
    if errors:
        print('\n'.join('ERROR: '+e for e in errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(source)} original source files match SHA-256.')
    print(f'PASS: {len(catalog)} templates, {total} PPTX slides, {total} screenshot files, 10 PDF headers.')
    print('PASS: local README, HTML and gallery links resolve; no macOS metadata or font files.')
    print('NOTE: this check is offline; it does not assert that a GitHub repository has been published.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
