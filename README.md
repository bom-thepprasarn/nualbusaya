# Nualbusaya website

One-page website for นวลบุษยา Nualbusaya, a massage shop inside Luka House, Lam Luk Ka, Pathum Thani.

Static HTML served by GitHub Pages. Edit `index.html`; images are in `img/`, scoped styles in `styles/`, and browser enhancements in `scripts/`.

Read `HANDOFF.md` before continuing work. Approved, manually curated Google reviews live in `data/google-reviews.json`; regenerate their static HTML with `python tools/render_reviews.py`. No Places API or key is required for reviews.

Local preview: `python -m http.server 8766 --bind 127.0.0.1`.

Checks:

```powershell
python -m unittest discover -s tests -p test_*.py -v
node tests/test_outcall_runtime.cjs
node --check scripts/reviews.js
node --check scripts/outcall.js
```

GitHub Pages deploys `main` from the repository root. Preserve the custom domain in `CNAME`, existing navigation/contact links, verified prices and genuine review wording. QA screenshots/harness output are local-only and ignored.
