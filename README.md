# MacBook Teardown Explorer

An interactive, exploded-view study of the 14-inch MacBook Pro with M3 Pro.

## Run locally

From this directory, start a static server and open `http://localhost:8000`:

```sh
python3 -m http.server 8000
```

The page loads `macbook_parts.glb` and `part-data.js` from this directory. Three.js and gltf-exploder are loaded from their CDN import map in `index.html`.

## Project files

- `index.html` — responsive Three.js viewer, picking, selection details and exploded-view controls.
- `part-data.js` — Chinese descriptions, specifications and source links for the 22 parts.
- `macbook_parts.glb` — exported model used by the viewer.
- `macbook_product_grade.blend` — editable Blender scene.
- `未命名.blend` — source scene used by the model rebuild script.
- `scripts/build_macbook_product_grade.py` — rebuild and export script.
- `docs/superpowers/` — design and implementation notes.
- `macbook_preview.png`, `macbook_exploded_preview.png` — assembled and exploded render previews.
