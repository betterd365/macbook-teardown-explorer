# MacBook Pro M3 Pro Product-Grade Teardown Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 22-box MacBook mockup with a convincing open-lid 14-inch MacBook Pro M3 Pro display model and an interactive, source-aware exploded-view experience.

**Architecture:** Rebuild the existing Blender assembly through a repeatable Blender Python (`bpy`) script, preserving the 22 semantic mesh objects and exporting a fresh GLB. Keep the Three.js + `gltf-exploder` page, move part facts into a structured data module, and refine the scene, controls, selected-part panel, materials and camera for the new asset.

**Tech Stack:** Blender 4.5.15 LTS Python API, glTF 2.0 Binary, Three.js 0.170.0, `gltf-exploder` 1.0.2, HTML/CSS/ES modules, local `python3 -m http.server`.

**Spec:** [2026-10-27-macbook-product-grade-teardown-design.md](../specs/2026-10-27-macbook-product-grade-teardown-design.md)

## Global Constraints

- Base the product exterior and product data on the 2023 14-inch MacBook Pro M3 Pro.
- Keep the 22 semantic mesh names from the approved spec, no `.001` suffixes, one unique mesh datablock per object.
- Keep each semantic component in `MacBook_Assembly`; keep the screen open at approximately 105° in assembly and exploded views.
- Initial web view shows the lid open and internals visibly exploded at about 82%; slider can return to the open assembled view.
- Keep `gltf-exploder` automatic `SIZE_WEIGHTED` behavior (1.0.2 runtime enum value `size_weighted`) and the existing Canvas-based raycast/highlight interaction.
- Clearly separate official specifications, values measured from the rebuilt mesh and visual estimates.
- Do not invent component suppliers; use “未公开/未核实” where a reliable model-specific source is unavailable.
- Preserve `未命名.blend` and the current rough GLB as `macbook_parts_rough.glb`; save the rebuilt editable scene to a new path before replacing the site GLB.
- No automated test files or test suite are in scope; verify the actual Blender scene, exported GLB and browser interaction visually and by inspection.

## Review Focus

- **Open-lid transform during explosion:** inspect both assembled and exploded progress to ensure the display keeps its open orientation and remains compositionally connected to the chassis.
- **22-name glTF contract:** inspect the exported GLB to ensure every approved semantic name appears exactly once and no helper geometry is exported as an extra Mesh.
- **Data truthfulness:** inspect all 22 descriptions for an explicit parameter type and supplier confidence; unknown suppliers must never be guessed.
- **Small-screen composition:** inspect a narrow viewport to ensure model, detail panel and explosion controls remain visible without overlap.
- **Repeated rebuild safety:** run the authoring script against the original input and confirm it writes to the new scene path without changing the original `.blend` or rough GLB.

---

### Task 1: Build sourced part information

**Files:**
- Create: `part-data.js`

**Interfaces:**
- Produces: `export const productInfo` for model identity and verified whole-device specs.
- Produces: `export const partData`, keyed by the exact 22 Mesh names. Each record contains `label`, `role`, `parameters`, `parameterType`, `designCompany`, `manufacturer`, and `sources`.
- `parameterType` is one of `官方规格`, `按模型测量`, or `示意估算`; missing supplier evidence is rendered as `未公开/未核实`.

- [ ] Research official model dimensions and component facts against Apple technical/specification pages; research internal layout only from traceable teardown sources, and record source URLs at field level.
- [ ] Add all 22 records to `part-data.js`; keep facts SKU-scoped and avoid claiming supplier data unsupported by a source.
- [ ] Manually inspect the records for all 22 keys, complete fields, safe external links and correctly labeled estimates.

### Task 2: Rebuild the Blender product asset

**Files:**
- Create: `scripts/build_macbook_product_grade.py`
- Create: `macbook_product_grade.blend`
- Create: `macbook_parts_rough.glb` (backup copy of the current rough export)
- Replace: `macbook_parts.glb` after the new scene is saved and export checks are complete

**Interfaces:**
- Script input: existing `未命名.blend`.
- Script outputs: a new editable Blender project and a glTF 2.0 Binary with 22 semantic meshes under `MacBook_Assembly`.
- Required mesh names are listed in the approved design spec; each gets its own mesh datablock.

- [ ] Rebuild only from the original file, leaving `未命名.blend` and the original rough GLB untouched; create the output scene at `macbook_product_grade.blend`.
- [ ] Shape the base case and display assembly to the approved 14-inch product proportions, with product-like corner radii, thin-wall silhouette, screen border/notch, hinge and coherent open angle.
- [ ] Add recognizable geometry within the existing 22 semantic meshes: individual keyboard keycap islands, trackpad bevel, port cutouts, separated battery cells, PCB details, chip packages, fan blades/shrouds, speakers and connector details.
- [ ] Apply distinct physically based material settings for anodized aluminum, glass, keyboard, rubberized details, circuit boards, silicon packages and metallic components; retain Blender-native editable shaders compatible with glTF export.
- [ ] Keep geometry-center origins and unique mesh data. Use a non-Mesh hinge transform only if needed to hold the 105° lid pose; keep semantic Mesh count at 22.
- [ ] Inspect Blender scene dimensions/names/users, verify collection membership, and render a preview from open assembled and exploded states before exporting.
- [ ] Export GLB with exactly the 22 named Meshes and material appearance; exclude cameras and lights from the exported selection.

### Task 3: Refine exploded-view and interaction presentation

**Files:**
- Modify: `index.html`
- Consume: `part-data.js`, rebuilt `macbook_parts.glb`

**Interfaces:**
- `gltf-exploder` remains configured with `viewport: '#scene-container'`, `model: './macbook_parts.glb'`, `createUI: true`, `adaptModel: true`, and `SIZE_WEIGHTED` mode.
- `partData` is the sole source for selected part panel content.
- Raycast selection still traverses the scene recursively, ignores unlabelled helpers, restores the prior material, and applies an independent translucent highlight material.

- [ ] Refit the camera and tune opening scene framing for the open 14-inch laptop; verify the model is large enough to read and remains centered after resize.
- [ ] Keep the screen assembly’s hinge orientation while tuning explosion amount and distance; retain the approved 82% initial value and 0–1 slider.
- [ ] Add a clear assembled/exploded state cue, optional concise startup/part callouts and a measured dark studio environment with ambient/directional lighting and contact shadows.
- [ ] Replace hardcoded short strings in `nameMap` with `partData`-driven long-form explanations, parameters, enterprise, sources and uncertainty labels.
- [ ] Keep all pointer picking on the canvas; validate `intersects.length > 0`, named-part mapping, warning path, restoration of original material and highlight opacity.
- [ ] Manually inspect desktop and narrow viewport layouts; tune any overlap, clipping, readability or frame-rate problems.

### Task 4: End-to-end visual handoff

**Files:**
- Modify: `index.html` and/or Blender script only for fixes found in visual inspection

- [ ] Start or reuse `python3 -m http.server 8000` from the project directory and open `http://localhost:8000/` in the browser.
- [ ] Confirm the first visible state has an open screen and visibly separated internals; move the slider to assembled and back to exploded.
- [ ] Click representative shell, board, chip, battery and display components; confirm each gets the correct panel content and independent highlight.
- [ ] Inspect browser console for load/picking errors and verify all 22 Mesh names from the loaded GLB.
- [ ] Confirm `.blend` source is saved separately, output GLB is readable, and report model/display limits where supplier or exact internal measurements remain unavailable.

---

## Self-review

- **Spec coverage:** Tasks 1–4 cover sourced explanations, all 22 semantic Meshes, open-lid posture, realistic geometry/materials, glTF explosion, click/highlight behavior, responsive layout and browser handoff.
- **Step scan:** Every checklist item names a concrete artifact or directly inspectable result; source research, asset rebuild and web presentation are separated by their deliverables.
- **Type consistency:** `partData` uses exact mesh names as keys; the page reads the defined fields; Blender export preserves those same names.
- **Review focus:** The five most likely failures are covered by manual Blender/GLB/browser inspections in Tasks 2–4.
- **Proportion:** Four implementation tasks separate data, asset creation, browser integration and final presentation review without restructuring the one-page site.
