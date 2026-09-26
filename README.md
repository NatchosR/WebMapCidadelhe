# Cidadelhe planting map

Mobile web map for the volunteers: tree positions and names for the Alagoa, Carrascal and Lagar plots, plus a "locate me" GPS button.

Live page: https://natchosr.github.io/WebMapCidadelhe/

## Files
- `index.html` – the whole app (Leaflet, no build step). Works by double-click locally (GPS needs the https link)
- `data/trees.js` – all trees (WGS84), converted from `all_tree_updated.gpkg`
- `data/rows.js` – planting row lines, converted from `all_line.gpkg`
- `tiles/` – drone orthophotos as WebP map tiles (z14–z21, ~6.6 MB)
- `lib/` – Leaflet 1.9.4

No outside map services are used: backgrounds are Drone (local tiles), Dark and Blank.

## Updating the design
1. In QGIS, save the updated layers as `all_tree_updated.gpkg` and `all_line.gpkg` (same fields as now).
2. Run (Python 3, no extra packages needed):
   `python tools/convert.py <folder with the .gpkg files> data`
3. Commit and push `data/`. GitHub Pages updates within a minute or two.

## Updating the drone imagery
Only needed if the orthophotos change (needs numpy, tifffile, Pillow):
`python tools/make_tiles.py <folder with *_orthophoto.tif> tiles`
