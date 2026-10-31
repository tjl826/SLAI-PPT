# SLAI-PPT

![SLAI-PPT](imgs/hero.png)

**Academic presentation templates for 深圳河套学院**

[中文](README.md) · [Offline gallery](index.html) · [Source integrity](SOURCE_MANIFEST.json)

A personal collection of five styles, each in Chinese and English: **10 editable PPTX files and 168 source slides**. This is not an official institutional release. Original material is preserved without changes, except that macOS metadata files are omitted.

## Download and preview

Choose PPTX to edit, PDF for the full deck, or Slides for a page-by-page gallery. Download everything with **Code → Download ZIP**. Open `index.html` after extraction for a local filterable gallery.

| Style | Pages per language | Chinese | English |
| :-- | :--: | :-- | :-- |
| 01 · Wave | 12 | [PPTX](https://raw.githubusercontent.com/tjl826/SLAI-PPT/main/downloads/zh-01.pptx) · [PDF](https://github.com/tjl826/SLAI-PPT/blob/main/previews/zh-01.pdf) · [Slides](https://github.com/tjl826/SLAI-PPT/blob/main/docs/zh-01.md) | [PPTX](https://raw.githubusercontent.com/tjl826/SLAI-PPT/main/downloads/en-01.pptx) · [PDF](https://github.com/tjl826/SLAI-PPT/blob/main/previews/en-01.pdf) · [Slides](https://github.com/tjl826/SLAI-PPT/blob/main/docs/en-01.md) |
| 02 · Classic | 16 | [PPTX](https://raw.githubusercontent.com/tjl826/SLAI-PPT/main/downloads/zh-02.pptx) · [PDF](https://github.com/tjl826/SLAI-PPT/blob/main/previews/zh-02.pdf) · [Slides](https://github.com/tjl826/SLAI-PPT/blob/main/docs/zh-02.md) | [PPTX](https://raw.githubusercontent.com/tjl826/SLAI-PPT/main/downloads/en-02.pptx) · [PDF](https://github.com/tjl826/SLAI-PPT/blob/main/previews/en-02.pdf) · [Slides](https://github.com/tjl826/SLAI-PPT/blob/main/docs/en-02.md) |
| 03 · Campus | 28 | [PPTX](https://raw.githubusercontent.com/tjl826/SLAI-PPT/main/downloads/zh-03.pptx) · [PDF](https://github.com/tjl826/SLAI-PPT/blob/main/previews/zh-03.pdf) · [Slides](https://github.com/tjl826/SLAI-PPT/blob/main/docs/zh-03.md) | [PPTX](https://raw.githubusercontent.com/tjl826/SLAI-PPT/main/downloads/en-03.pptx) · [PDF](https://github.com/tjl826/SLAI-PPT/blob/main/previews/en-03.pdf) · [Slides](https://github.com/tjl826/SLAI-PPT/blob/main/docs/en-03.md) |
| 04 · Dark | 14 | [PPTX](https://raw.githubusercontent.com/tjl826/SLAI-PPT/main/downloads/zh-04.pptx) · [PDF](https://github.com/tjl826/SLAI-PPT/blob/main/previews/zh-04.pdf) · [Slides](https://github.com/tjl826/SLAI-PPT/blob/main/docs/zh-04.md) | [PPTX](https://raw.githubusercontent.com/tjl826/SLAI-PPT/main/downloads/en-04.pptx) · [PDF](https://github.com/tjl826/SLAI-PPT/blob/main/previews/en-04.pdf) · [Slides](https://github.com/tjl826/SLAI-PPT/blob/main/docs/en-04.md) |
| 05 · Light | 14 | [PPTX](https://raw.githubusercontent.com/tjl826/SLAI-PPT/main/downloads/zh-05.pptx) · [PDF](https://github.com/tjl826/SLAI-PPT/blob/main/previews/zh-05.pdf) · [Slides](https://github.com/tjl826/SLAI-PPT/blob/main/docs/zh-05.md) | [PPTX](https://raw.githubusercontent.com/tjl826/SLAI-PPT/main/downloads/en-05.pptx) · [PDF](https://github.com/tjl826/SLAI-PPT/blob/main/previews/en-05.pdf) · [Slides](https://github.com/tjl826/SLAI-PPT/blob/main/docs/en-05.md) |

![All ten covers](imgs/overview.jpg)

## Assets and editing

The original [logo assets](%E6%B7%B1%E5%9C%B3%E6%B2%B3%E5%A5%97%E5%AD%A6%E9%99%A2logo/) include PNG, SVG and PDF files. The original [color guide](%E6%A0%87%E5%87%86%E8%89%B2.pdf) is also included.

Duplicate an existing slide to reuse its layout. Native text, shapes, charts and layout/master structures are preserved, but a single slide master does not necessarily control every visual element. Replace placeholder text and sample chart data before presenting.

Previews are generated with LibreOffice and include hidden guide slides. Font substitution and chart rendering may differ from PowerPoint. No font files are distributed. See [quality notes](docs/QUALITY_NOTES.md) for known source issues.

## Reproducibility

```bash
python3 -m pip install -r scripts/requirements-preview.txt
python3 scripts/build_previews.py
python3 scripts/verify_repository.py
```

LibreOffice is required to regenerate PDFs. Verification alone uses the Python standard library. The 17 original source assets are recorded in `SOURCE_MANIFEST.json` with SHA-256 checksums.

## Attribution and licensing

Repository organization and screenshot presentation were inspired by [sysuexam/SYSU-PPT](https://github.com/sysuexam/SYSU-PPT). Its university slides and logos are not redistributed here.

MIT applies only to the newly written repository scripts and original documentation, not to the supplied PPTX files, institutional marks, photographs, color guide or derived previews. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

This package does not itself establish official endorsement or permissions for institutional assets. Original filenames containing “官方” are retained from the supplied archive, not independently verified.
