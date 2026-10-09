# Fashion-and-Python
A Vogue-inspired fashion styling and wardrobe management application built with Python and Streamlit. Explore clothing collections, create outfit combinations, discover colour palettes, and curate a personal style archive through an elegant editorial interface.

# FASHION & PYTHON

*An exploration of personal style. Discover your wardrobe. Curate your style.*

A Vogue-inspired (but independently designed) fashion styling app built with **Python and Streamlit**.
It combines an editorial landing page, a digital wardrobe, an outfit builder, a colour-matching tool
and an archive of saved looks.

> **Phase 1 status:** the interface and all interactions are complete and run on sample data.
> Data lives in Streamlit **session state**, so it lasts only for the current browser session and
> resets when the app restarts. Persistent storage is planned for phase 2.

## Features

| Page | What it does |
|------|--------------|
| The Editorial | Magazine-style cover, live statistics from the data, featured look, curated pieces |
| The Wardrobe | Search, category and colour filters, sorting, add / edit / delete with validation, optional photo upload |
| The Outfit Studio | Pick pieces by slot, name and tag an outfit, **Style Shuffle**, save, reset, recent looks |
| The Colour Edit | 16-colour palette, analogous and complementary suggestions, matching wardrobe pieces, save palettes |
| The Style Archive | Saved outfits, favourites, filter by style or occasion, remove, JSON and CSV download |

### How Style Shuffle works (no AI involved)
1. Choose an anchor: a dress (for Party and Formal, about half the time) or a top plus a bottom.
2. For each slot, start with wardrobe items of the right category.
3. Prefer items tagged for the chosen occasion.
4. Keep only items whose colour is compatible with what is already chosen
   (neutrals suit everything; analogous colours are within 45 degrees on the colour wheel;
   complementary colours are at least 125 degrees apart; anything else clashes).
5. Prefer the chosen style's signature colours, then pick at random with `random.choice`.
6. If a rule leaves nothing, relax it and explain why. Empty wardrobes and missing categories are handled.

## Project structure

```
fashion-and-python/
    app.py              app config, sidebar navigation, page routing
    sample_data.py      sample clothing, outfits, palettes and option lists
    data_manager.py     all data access: add / update / delete / filter / sort / export
    outfit_logic.py     Style Shuffle and outfit validation (no Streamlit, fully testable)
    colour_logic.py     colour rules and palette building (no Streamlit, fully testable)
    ui.py               CSS loading, image fallbacks, shared HTML snippets
    editorial.py        page 1
    wardrobe.py         page 2
    outfit_studio.py    page 3
    colour_edit.py      page 4
    style_archive.py    page 5
    requirements.txt
    README.md
    .gitignore
    .streamlit/config.toml
    styles/magazine.css
    assets/cover.jpg        (optional: your own cover photograph)
    assets/clothing/        (optional: your own item photographs)
    tests/
        test_outfits.py
        test_colours.py
        test_data.py
```

Logic and page files are split on purpose: `outfit_logic.py` and `colour_logic.py` contain the
Python you will explain in a viva, and the page files only draw the interface.

## Run it (GitHub Codespaces or locally)

```bash
pip install -r requirements.txt
streamlit run app.py
```

In Codespaces, open the forwarded port 8501 when it appears.

## Run the tests

```bash
python -m unittest discover -s tests
```

## Using your own photographs

Without photos, every piece is drawn as a flat silhouette in its own colour, so nothing ever breaks.
- **Cover:** save a photo as `assets/cover.jpg` and it replaces the generated cover automatically.
- **Clothing:** put an image in `assets/clothing/` and set that item's `"image"` field to the file
  name in `sample_data.py`, or upload a photo when adding or editing a piece in the app
  (JPG, PNG or WebP, up to 2 MB).

## Deploy on Streamlit Community Cloud

1. Push the project to a public GitHub repository.
2. Go to <https://share.streamlit.io> and sign in with GitHub.
3. Choose **Create app**, pick the repository and branch, and set the main file to `app.py`.
4. Deploy. Streamlit installs `requirements.txt` automatically.

## Data design and the path to persistence

- Records are plain dictionaries with the same shape everywhere:
  - clothing: `id, name, category, color, season, occasion (list), price, image`
  - outfit: `id, name, occasion, style, item_ids, favourite, created`
  - palette: `id, name, base, colours, created`
- Outfits store clothing **ids**, not copies. If a piece is deleted, the archive shows a
  "piece removed" note instead of breaking.
- Pages never edit lists directly. They call functions in `data_manager.py`
  (`add_item`, `update_item`, `delete_item`, `save_outfit`, `delete_outfit`, and so on).
- To add SQLite, rewrite the functions in the "storage" and CRUD sections of `data_manager.py`
  to read and write the database. The page files stay unchanged.
- `export_json`, `export_wardrobe_csv` and `parse_backup` already exist for backup, export and restore.

## Planned improvements (phase 2)

- Persistent storage (SQLite) replacing session state
- Reliable JSON backup **restore** (`parse_backup` is the first step)
- Stronger validation and more unit tests (for example, tests for the storage layer)
- Optional photo library managed on disk instead of embedded in records
