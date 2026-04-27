# Slides Export Guide

This folder contains a presentation draft that is intentionally verbose so you can trim it quickly.

## Source File

- `CS498-Prototype-Deck.md`

## Export to PDF (recommended for 4/29 submission)

Use Marp CLI directly with `npx`:

```bash
npx @marp-team/marp-cli slides/CS498-Prototype-Deck.md --pdf --allow-local-files --output slides/CS498-Prototype-Deck.pdf
```

## Export to PPTX (optional)

```bash
npx @marp-team/marp-cli slides/CS498-Prototype-Deck.md --pptx --allow-local-files --output slides/CS498-Prototype-Deck.pptx
```

## Notes

- The deck includes core slides + backup slides.
- Trim backup slides first if you need a shorter version.
- Add your real screenshots to the placeholder slide before final export.
