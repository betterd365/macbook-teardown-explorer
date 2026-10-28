"""Rebuild the MacBook Pro 14-inch M3 Pro visual asset from a saved .blend.

Usage (from this project directory):
  blender -b '未命名.blend' --python scripts/build_macbook_product_grade.py -- \
    --blend-output /path/to/macbook_product_grade.blend \
    --glb-output /path/to/macbook_parts.glb \
    --preview-output /path/to/macbook_preview.png

The input file is read only. The script replaces geometry on the 22 existing
semantic objects, saves a new editable blend, and exports only those Meshes.
"""

import argparse
import math
import os
import sys

import bmesh
import bpy
from mathutils import Euler, Vector


PART_NAMES = [
    "bottom_case", "logic_board", "soc_m3", "unified_memory_left",
    "unified_memory_right", "ssd_controller", "ssd_nand", "wifi_bt_module",
    "power_management_ic", "display_assembly", "display_connector", "battery",
    "battery_management_board", "trackpad", "keyboard_top_case", "speaker_left",
    "speaker_right", "fan_left", "fan_right", "usb_c_board", "magsafe_board",
    "audio_board",
]

# Coordinates are metres, X is laptop width, positive Y is the hinge side,
# negative Y is the user/front edge, and Z is vertical.
W = 0.3126
D = 0.2212
BASE_H = 0.0155
DISPLAY_H = 0.215
DISPLAY_ANGLE = math.radians(75.0)  # 105-degree included open angle


def args_after_separator():
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend-output", required=True)
    parser.add_argument("--glb-output", required=True)
    parser.add_argument("--preview-output", required=True)
    parser.add_argument("--exploded-preview-output", required=True)
    return parser.parse_args(values)


class PartBuilder:
    """Collect disconnected but semantically related solids into one Mesh."""

    def __init__(self):
        self.vertices = []
        self.faces = []
        self.material_ids = []

    def _push(self, vertices, faces, material):
        offset = len(self.vertices)
        self.vertices.extend(tuple(v) for v in vertices)
        self.faces.extend(tuple(offset + i for i in face) for face in faces)
        self.material_ids.extend([material] * len(faces))

    def box(self, center, dims, material, radius=0.0, rotation=(0, 0, 0), segments=3):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for vertex in bm.verts:
            vertex.co.x *= dims[0]
            vertex.co.y *= dims[1]
            vertex.co.z *= dims[2]
        if radius > 0:
            bevel = min(radius, min(dims) * 0.46)
            bmesh.ops.bevel(
                bm,
                geom=list(bm.edges),
                offset=bevel,
                segments=max(1, segments),
                profile=0.5,
                clamp_overlap=True,
            )
        bm.normal_update()
        rotation_matrix = Euler(rotation, "XYZ").to_matrix()
        position = Vector(center)
        vertices = [rotation_matrix @ v.co + position for v in bm.verts]
        index = {vertex: i for i, vertex in enumerate(bm.verts)}
        faces = [tuple(index[v] for v in face.verts) for face in bm.faces]
        self._push(vertices, faces, material)
        bm.free()

    def cylinder(self, center, radius, depth, material, sides=32):
        cx, cy, cz = center
        vertices = []
        for z in (cz - depth / 2, cz + depth / 2):
            for i in range(sides):
                angle = 2 * math.pi * i / sides
                vertices.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle), z))
        faces = [tuple(range(sides - 1, -1, -1)), tuple(range(sides, 2 * sides))]
        faces += [(i, (i + 1) % sides, (i + 1) % sides + sides, i + sides) for i in range(sides)]
        self._push(vertices, faces, material)

    def cylinder_x(self, center, radius, length, material, sides=32):
        """Create a cylinder whose hinge axis runs across the laptop width."""
        cx, cy, cz = center
        vertices = []
        for x in (cx - length / 2, cx + length / 2):
            for i in range(sides):
                angle = 2 * math.pi * i / sides
                vertices.append((x, cy + radius * math.cos(angle), cz + radius * math.sin(angle)))
        faces = [tuple(range(sides - 1, -1, -1)), tuple(range(sides, 2 * sides))]
        faces += [(i, (i + 1) % sides, (i + 1) % sides + sides, i + sides) for i in range(sides)]
        self._push(vertices, faces, material)

    def ring(self, center, outer_radius, inner_radius, depth, material, sides=48):
        cx, cy, cz = center
        vertices = []
        for z in (cz - depth / 2, cz + depth / 2):
            for radius in (outer_radius, inner_radius):
                for i in range(sides):
                    angle = 2 * math.pi * i / sides
                    vertices.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle), z))
        faces = []
        for i in range(sides):
            j = (i + 1) % sides
            # bottom annulus, top annulus, outer wall, inner wall
            faces.append((i, j, sides + j, sides + i))
            faces.append((2 * sides + i, 3 * sides + i, 3 * sides + j, 2 * sides + j))
            faces.append((i, 2 * sides + i, 2 * sides + j, j))
            faces.append((sides + j, 3 * sides + j, 3 * sides + i, sides + i))
        self._push(vertices, faces, material)

    def prism(self, points, z_bottom, z_top, material):
        """Extrude a convex XY polygon."""
        points = list(points)
        if len(points) < 3:
            return
        area = sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1] for i in range(len(points)))
        if area < 0:
            points.reverse()
        n = len(points)
        vertices = [(x, y, z_bottom) for x, y in points] + [(x, y, z_top) for x, y in points]
        faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
        self._push(vertices, faces, material)


MATERIAL_SPECS = {
    "aluminum": ((0.035, 0.045, 0.058, 1), 0.16, 0.43),
    "aluminum_dark": ((0.018, 0.025, 0.035, 1), 0.24, 0.46),
    "screen_black": ((0.004, 0.007, 0.012, 1), 0.16, 0.12),
    "screen_glass": ((0.012, 0.018, 0.028, 1), 0.03, 0.42),
    "keyboard": ((0.018, 0.023, 0.031, 1), 0.0, 0.62),
    "legend": ((0.62, 0.69, 0.78, 1), 0.0, 0.42),
    "pcb": ((0.024, 0.20, 0.125, 1), 0.16, 0.36),
    "pcb_dark": ((0.012, 0.085, 0.056, 1), 0.12, 0.42),
    "silicon": ((0.025, 0.035, 0.05, 1), 0.12, 0.27),
    "chip_top": ((0.17, 0.20, 0.24, 1), 0.76, 0.25),
    "gold": ((0.62, 0.40, 0.14, 1), 0.76, 0.22),
    "battery": ((0.20, 0.24, 0.28, 1), 0.22, 0.35),
    "battery_label": ((0.54, 0.59, 0.62, 1), 0.08, 0.48),
    "fan": ((0.38, 0.45, 0.52, 1), 0.76, 0.25),
    "fan_dark": ((0.07, 0.09, 0.12, 1), 0.44, 0.3),
    "speaker": ((0.035, 0.043, 0.052, 1), 0.18, 0.40),
    "port": ((0.015, 0.02, 0.026, 1), 0.52, 0.24),
    "rubber": ((0.013, 0.016, 0.021, 1), 0.02, 0.66),
    "silver": ((0.28, 0.33, 0.40, 1), 0.34, 0.38),
}


def make_materials():
    materials = {}
    for name, (color, metalness, roughness) in MATERIAL_SPECS.items():
        material = bpy.data.materials.get("MBP_" + name) or bpy.data.materials.new("MBP_" + name)
        material.diffuse_color = color
        material.use_nodes = True
        # Blender follows the OS UI language for node display names; resolve by
        # stable node type instead of the English label.
        bsdf = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metalness
        bsdf.inputs["Roughness"].default_value = roughness
        materials[name] = material

    # A packed procedural wallpaper texture provides a lit, recognizable screen
    # without fetching external images or including unlicensed artwork.
    size = 384
    image = bpy.data.images.new("MBP_Abstract_Display", width=size, height=size, alpha=True)
    pixels = []
    for y in range(size):
        v = y / (size - 1)
        for x in range(size):
            u = x / (size - 1)
            wave = 0.5 + 0.5 * math.sin((u * 1.1 + v * 0.72) * math.pi * 2.0 + 0.3 * math.sin(v * 6.0))
            glow = math.exp(-((u - 0.68) ** 2 / 0.18 + (v - 0.43) ** 2 / 0.24))
            r = min(1.0, 0.018 + 0.10 * wave + 0.73 * glow) * 0.54
            g = min(1.0, 0.035 + 0.24 * (1 - v) + 0.16 * wave + 0.18 * glow) * 0.58
            b = min(1.0, 0.12 + 0.48 * (1 - u) + 0.28 * wave + 0.07 * glow) * 0.68
            pixels.extend((r, g, b, 1.0))
    image.pixels.foreach_set(pixels)
    image.pack()
    screen = bpy.data.materials.new("MBP_screen_wallpaper")
    screen.use_nodes = True
    nodes = screen.node_tree.nodes
    links = screen.node_tree.links
    bsdf = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = 0.48
    bsdf.inputs["Metallic"].default_value = 0.05
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.interpolation = "Linear"
    links.new(texture.outputs["Color"], bsdf.inputs["Base Color"])
    emission = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission:
        links.new(texture.outputs["Color"], emission)
        strength = bsdf.inputs.get("Emission Strength")
        if strength:
            strength.default_value = 0.08
    materials["screen_wallpaper"] = screen
    return materials


def make_rounded_panel(builder, center, dims, material, radius):
    builder.box(center, dims, material, radius=radius, segments=4)


def fan_part(x, y):
    b = PartBuilder()
    z = 0.0103
    b.box((x, y, z), (0.069, 0.066, 0.0036), "fan_dark", radius=0.010, segments=5)
    b.ring((x, y, z + 0.0022), 0.030, 0.024, 0.002, "fan", sides=48)
    b.ring((x, y, z + 0.003), 0.0225, 0.0205, 0.0012, "fan_dark", sides=48)
    b.cylinder((x, y, z + 0.004), 0.0070, 0.002, "fan", sides=32)
    b.cylinder((x, y, z + 0.0052), 0.0030, 0.0009, "gold", sides=24)
    # Twelve swept radial blades, each as a curved tapered island.
    for i in range(12):
        angle = 2 * math.pi * i / 12 + 0.15
        local = [(0.006, -0.003), (0.023, -0.010), (0.020, 0.000), (0.010, 0.004)]
        points = []
        for px, py in local:
            points.append((x + px * math.cos(angle) - py * math.sin(angle), y + px * math.sin(angle) + py * math.cos(angle)))
        b.prism(points, z + 0.0033, z + 0.0047, "fan")
    for i in range(6):
        angle = 2 * math.pi * i / 6
        b.cylinder((x + 0.027 * math.cos(angle), y + 0.026 * math.sin(angle), z + 0.002), 0.0012, 0.0012, "silver", sides=12)
    return b


def build_bottom_case():
    b = PartBuilder()
    # Thin bottom plate and four segmented side walls form a real-looking tray.
    b.box((0, 0, 0.0010), (W, D, 0.0020), "aluminum", radius=0.008, segments=5)
    wall_h, wall_t = 0.0115, 0.00125
    z = 0.00775
    x_edge = W / 2 - wall_t / 2
    y_edge = D / 2 - wall_t / 2
    # Front and hinge rails.
    b.box((0, -D / 2 + wall_t / 2, z), (W - 0.012, wall_t, wall_h), "aluminum", radius=0.001, segments=2)
    b.box((0, D / 2 - wall_t / 2, z), (W - 0.012, wall_t, wall_h), "aluminum", radius=0.001, segments=2)
    # Side rails broken at port positions: MagSafe/USB-C/audio left; USB-C/HDMI/SD right.
    left_gaps = [(-0.088, -0.078), (-0.035, -0.023), (0.000, 0.012), (0.073, 0.084)]
    right_gaps = [(-0.047, -0.035), (0.036, 0.050), (0.072, 0.084)]
    def side_segments(edge_x, gaps, material):
        intervals = [(-D / 2 + 0.010, D / 2 - 0.010)]
        for lo, hi in sorted(gaps):
            next_intervals = []
            for a, c in intervals:
                if hi <= a or lo >= c:
                    next_intervals.append((a, c))
                else:
                    if lo > a:
                        next_intervals.append((a, lo))
                    if hi < c:
                        next_intervals.append((hi, c))
            intervals = next_intervals
        for a, c in intervals:
            if c - a > 0.003:
                b.box((edge_x, (a + c) / 2, z), (wall_t, c - a, wall_h), material, radius=0.001, segments=2)
    side_segments(-x_edge, left_gaps, "aluminum")
    side_segments(x_edge, right_gaps, "aluminum")
    # Inner stiffeners and mounting pads.
    for x in (-0.125, 0.125):
        b.box((x, 0.015, 0.004), (0.002, 0.145, 0.003), "aluminum_dark", radius=0.0008, segments=2)
    # Hinge saddles align with the two barrel centers in the display assembly.
    for x in (-0.080, 0.080):
        b.box((x, 0.090, 0.0095), (0.022, 0.016, 0.005), "aluminum_dark", radius=0.002, segments=4)
    # Rubber rails and six recessed screw-head details on the underside.
    for x in (-0.132, 0.132):
        b.box((x, 0, -0.00035), (0.006, 0.176, 0.0007), "rubber", radius=0.002, segments=3)
    for x in (-0.137, -0.055, 0.055, 0.137):
        for y in (-0.095, 0.095):
            b.cylinder((x, y, -0.00016), 0.00115, 0.00035, "aluminum_dark", sides=16)
    # Black port liners in the perimeter gaps.
    for x, y, length in [(-0.1557, -0.083, 0.009), (-0.1557, -0.029, 0.010), (-0.1557, 0.006, 0.010), (-0.1557, 0.0785, 0.010), (0.1557, -0.041, 0.010), (0.1557, 0.043, 0.013), (0.1557, 0.078, 0.012)]:
        b.box((x, y, 0.0081), (0.0008, length, 0.0034), "port", radius=0.0015, segments=3)
    return b


def build_keyboard_top_case():
    b = PartBuilder()
    # The top case is the large thin aluminum deck; all keycap islands and marks
    # remain inside this single semantic Mesh.
    half_w = (W - 0.0032) / 2
    rear_y = (D - 0.0040) / 2
    # Keep the hinge relief behind the function-key row, with a visible but clean gap.
    slot_y = 0.100
    # Leave two hinge pockets in the keyboard deck's rear edge. The exposed
    # hinge barrels now emerge from the chassis instead of sitting underneath a solid slab.
    front_depth = slot_y + rear_y
    b.box((0, (slot_y - rear_y) / 2, 0.01325), (2 * half_w, front_depth, 0.0025), "aluminum", radius=0.008, segments=5)
    for x0, x1 in ((-half_w, -0.093), (-0.067, 0.067), (0.093, half_w)):
        width = x1 - x0
        b.box(((x0 + x1) / 2, (slot_y + rear_y) / 2, 0.01325), (width, rear_y - slot_y, 0.0025), "aluminum", radius=0.0015, segments=3)
    keyboard_y = 0.050
    key_rows = [(14, 0.091), (15, 0.076), (15, 0.060), (14, 0.044), (12, 0.028), (8, 0.011)]
    for row, (count, y) in enumerate(key_rows):
        dx = 0.0180
        width = dx * count - 0.002
        start = -width / 2 + dx / 2
        for col in range(count):
            x = start + col * dx
            key_w = 0.0148 if count > 10 else 0.0158
            key_h = 0.0092
            # A few elongated keys match the space/return/shift row rhythm.
            if row == 5 and col == 3:
                key_w = 0.058
            elif row == 3 and col in (0, 13):
                key_w = 0.021
            elif row == 2 and col == 14:
                key_w = 0.020
            b.box((x, y, 0.01505), (key_w, key_h, 0.0010), "keyboard", radius=0.0015, segments=3)
            # Subtle light legend strokes read as glyphs at the presentation scale.
            mark_w = 0.0023 if row < 2 else 0.0030
            b.box((x, y + 0.0012, 0.01558), (mark_w, 0.00028, 0.00008), "legend", radius=0.0001, segments=1)
    # Inset function row and Touch ID key, integrated with the top-case component.
    b.box((0.132, 0.091, 0.0151), (0.012, 0.009, 0.0010), "keyboard", radius=0.002, segments=3)
    b.box((0.132, 0.091, 0.01565), (0.004, 0.002, 0.0001), "silver", radius=0.0006, segments=2)
    # Tiny speaker grille perforation fields on both deck edges.
    for side in (-1, 1):
        for i in range(11):
            for j in range(5):
                x = side * (0.132 + 0.003 * j)
                y = 0.039 + 0.0055 * i
                b.cylinder((x, y, 0.01457), 0.00065, 0.00016, "aluminum_dark", sides=10)
    return b


def build_display():
    # Build the panel in its own plane. The display_hinge Empty rotates this
    # centered Mesh around the chassis pivot instead of baking the pose into vertices.
    h = DISPLAY_H
    local = PartBuilder()
    local.box((0, 0, 0), (W, h, 0.0058), "aluminum_dark", radius=0.010, segments=6)
    local.box((0, 0, 0.0009), (W - 0.004, h - 0.004, 0.0045), "screen_black", radius=0.009, segments=6)
    local.box((0, 0, 0.0032), (W - 0.014, h - 0.018, 0.0010), "screen_glass", radius=0.007, segments=5)
    local.box((0, 0.002, 0.00385), (W - 0.025, h - 0.031, 0.00015), "screen_wallpaper", radius=0.005, segments=4)
    local.box((0, h / 2 - 0.012, 0.00405), (0.050, 0.0065, 0.00045), "screen_black", radius=0.003, segments=4)
    local.cylinder((0.010, h / 2 - 0.012, 0.00436), 0.0012, 0.0002, "aluminum_dark", sides=24)
    # Barrel details sit just proud of the panel's lower edge, in line with the pivot.
    for x in (-0.080, 0.080):
        local.cylinder_x((x, -h / 2 - 0.004, -0.001), 0.0042, 0.024, "aluminum_dark", sides=32)
        for end in (-1, 1):
            local.cylinder_x((x + end * 0.0115, -h / 2 - 0.004, -0.001), 0.0045, 0.0010, "silver", sides=20)
    return local

def build_part(name):
    if name == "bottom_case":
        return build_bottom_case()
    if name == "keyboard_top_case":
        return build_keyboard_top_case()
    if name == "display_assembly":
        return build_display()
    if name == "battery":
        b = PartBuilder()
        # Six pouch cells beneath the palm rest, with crimped foil margins and labels.
        xs = [-0.121, -0.073, -0.025, 0.025, 0.073, 0.121]
        for i, x in enumerate(xs):
            b.box((x, -0.035, 0.0067), (0.044, 0.118, 0.0070), "battery", radius=0.004, segments=5)
            b.box((x, -0.035, 0.01028), (0.032, 0.082, 0.00018), "battery_label", radius=0.001, segments=2)
            # Thin insulated separators emphasize individual cell pouches.
            b.box((x, 0.026, 0.0067), (0.039, 0.0025, 0.0010), "aluminum_dark", radius=0.0008, segments=2)
        return b
    if name == "battery_management_board":
        b = PartBuilder()
        b.box((0.112, -0.026, 0.0121), (0.042, 0.030, 0.0012), "pcb", radius=0.002, segments=3)
        for i in range(5):
            b.box((0.096 + 0.008 * i, -0.026, 0.01285), (0.0045, 0.008, 0.0011), "chip_top", radius=0.0007, segments=2)
        for i in range(8):
            b.box((0.091 + i * 0.006, -0.040, 0.0121), (0.003, 0.002, 0.001), "gold", radius=0.0003, segments=1)
        return b
    if name == "trackpad":
        b = PartBuilder()
        b.box((0, -0.064, 0.0149), (0.135, 0.083, 0.0017), "aluminum_dark", radius=0.008, segments=6)
        b.box((0, -0.064, 0.01565), (0.129, 0.077, 0.0007), "aluminum", radius=0.006, segments=6)
        b.box((0, -0.064, 0.01603), (0.126, 0.074, 0.00018), "screen_glass", radius=0.005, segments=5)
        return b
    if name == "logic_board":
        b = PartBuilder()
        # A three-lobe board silhouette occupies the rear half, leaving fan wells.
        b.box((0, 0.064, 0.0120), (0.155, 0.055, 0.0014), "pcb", radius=0.006, segments=4)
        b.box((-0.091, 0.064, 0.0120), (0.050, 0.034, 0.0014), "pcb", radius=0.004, segments=4)
        b.box((0.091, 0.064, 0.0120), (0.050, 0.034, 0.0014), "pcb", radius=0.004, segments=4)
        # Dense small packages and silver solder pads make the board legible.
        for row in range(4):
            for col in range(15):
                x = -0.073 + col * 0.0104
                y = 0.043 + row * 0.011
                if abs(x) < 0.030 and 0.052 < y < 0.085:
                    continue
                material = "chip_top" if (row + col) % 3 else "silicon"
                b.box((x, y, 0.0130), (0.0065, 0.0052, 0.0010), material, radius=0.0007, segments=2)
        for x in (-0.070, -0.055, 0.055, 0.070):
            for y in (0.037, 0.096):
                b.cylinder((x, y, 0.0130), 0.0022, 0.0010, "gold", sides=16)
        # Edge connectors and cable sockets.
        for x in (-0.060, -0.036, 0.036, 0.060):
            b.box((x, 0.027, 0.0129), (0.013, 0.004, 0.0022), "aluminum_dark", radius=0.0008, segments=2)
        return b
    if name == "soc_m3":
        b = PartBuilder()
        b.box((0, 0.065, 0.0140), (0.028, 0.027, 0.0030), "silicon", radius=0.003, segments=4)
        b.box((0, 0.065, 0.01563), (0.023, 0.022, 0.00035), "chip_top", radius=0.002, segments=3)
        b.box((0, 0.065, 0.01584), (0.012, 0.00045, 0.00006), "silver", radius=0.00015, segments=1)
        return b
    if name in ("unified_memory_left", "unified_memory_right"):
        b = PartBuilder()
        x = -0.020 if name.endswith("left") else 0.020
        b.box((x, 0.065, 0.0139), (0.014, 0.010, 0.0026), "silicon", radius=0.0017, segments=3)
        b.box((x, 0.065, 0.01527), (0.0115, 0.0075, 0.00030), "chip_top", radius=0.0012, segments=3)
        for i in range(5):
            b.box((x - 0.0045 + i * 0.0022, 0.0585, 0.0135), (0.0012, 0.0012, 0.0006), "gold", radius=0.0002, segments=1)
        return b
    if name == "ssd_controller":
        b = PartBuilder()
        b.box((0.060, 0.052, 0.0137), (0.012, 0.010, 0.0022), "silicon", radius=0.0015, segments=3)
        b.box((0.060, 0.052, 0.0149), (0.009, 0.007, 0.00025), "chip_top", radius=0.001, segments=2)
        return b
    if name == "ssd_nand":
        b = PartBuilder()
        for x in (0.078, 0.091):
            b.box((x, 0.052, 0.0138), (0.011, 0.009, 0.0020), "silicon", radius=0.0014, segments=3)
            b.box((x, 0.052, 0.01492), (0.0085, 0.0065, 0.00022), "chip_top", radius=0.001, segments=2)
        return b
    if name == "wifi_bt_module":
        b = PartBuilder()
        b.box((0.105, 0.050, 0.0133), (0.020, 0.016, 0.0016), "pcb_dark", radius=0.002, segments=3)
        b.box((0.105, 0.050, 0.01425), (0.012, 0.010, 0.0010), "chip_top", radius=0.0012, segments=3)
        for i in range(6):
            b.box((0.097 + i * 0.003, 0.0408, 0.0135), (0.0017, 0.0016, 0.0004), "gold", radius=0.00025, segments=1)
        return b
    if name == "power_management_ic":
        b = PartBuilder()
        b.box((-0.052, 0.047, 0.0135), (0.012, 0.010, 0.0022), "silicon", radius=0.0015, segments=3)
        b.box((-0.052, 0.047, 0.0147), (0.009, 0.007, 0.00025), "chip_top", radius=0.001, segments=2)
        return b
    if name in ("fan_left", "fan_right"):
        return fan_part(-0.112 if name.endswith("left") else 0.112, 0.075)
    if name in ("speaker_left", "speaker_right"):
        b = PartBuilder()
        x = -0.126 if name.endswith("left") else 0.126
        b.box((x, -0.020, 0.0090), (0.039, 0.132, 0.0080), "speaker", radius=0.009, segments=5)
        b.box((x, -0.020, 0.0132), (0.032, 0.119, 0.0010), "aluminum_dark", radius=0.007, segments=4)
        # Alternating acoustic chambers and ribs visible once exploded.
        for i in range(8):
            y = -0.073 + i * 0.015
            b.box((x, y, 0.0140), (0.026, 0.004, 0.0010), "speaker", radius=0.0018, segments=3)
        b.cylinder((x, -0.083, 0.014), 0.009, 0.001, "speaker", sides=32)
        b.cylinder((x, 0.043, 0.014), 0.009, 0.001, "speaker", sides=32)
        return b
    if name == "display_connector":
        b = PartBuilder()
        # Flexible ribbon from the hinge into the chassis with connector tabs.
        b.box((0, 0.102, 0.0120), (0.100, 0.004, 0.0010), "speaker", radius=0.001, segments=2)
        for x in (-0.043, -0.014, 0.014, 0.043):
            b.box((x, 0.097, 0.0121), (0.012, 0.009, 0.0015), "gold", radius=0.001, segments=2)
        return b
    if name == "usb_c_board":
        b = PartBuilder()
        # Left and right port boards plus the three USB-C shells and HDMI/SD details.
        for x in (-0.144, 0.144):
            b.box((x, 0.016, 0.0100), (0.018, 0.082, 0.0018), "pcb", radius=0.002, segments=3)
        for x, y in [(-0.153, -0.029), (-0.153, 0.006), (0.153, -0.041)]:
            b.box((x, y, 0.0088), (0.006, 0.015, 0.005), "aluminum_dark", radius=0.002, segments=3)
            b.box((x, y, 0.0092), (0.001, 0.010, 0.0025), "port", radius=0.0014, segments=3)
            b.box((x, y, 0.0084), (0.0012, 0.006, 0.00045), "silver", radius=0.0002, segments=1)
        # Right-side HDMI and SDXC sockets, with black cavities and metal lips.
        b.box((0.153, 0.043, 0.0086), (0.006, 0.020, 0.0048), "aluminum_dark", radius=0.0015, segments=3)
        b.box((0.1537, 0.043, 0.0086), (0.0012, 0.015, 0.0026), "port", radius=0.0008, segments=2)
        b.box((0.153, 0.078, 0.0086), (0.006, 0.018, 0.0035), "aluminum_dark", radius=0.001, segments=2)
        b.box((0.1537, 0.078, 0.0086), (0.001, 0.013, 0.0016), "port", radius=0.0005, segments=1)
        return b
    if name == "magsafe_board":
        b = PartBuilder()
        b.box((-0.137, 0.086, 0.0095), (0.028, 0.020, 0.0017), "pcb", radius=0.002, segments=3)
        b.box((-0.153, 0.0785, 0.0088), (0.006, 0.012, 0.005), "aluminum_dark", radius=0.002, segments=3)
        b.box((-0.1537, 0.0785, 0.0088), (0.001, 0.008, 0.002), "gold", radius=0.0008, segments=2)
        for i in range(5):
            b.cylinder((-0.1535, 0.074 + i * 0.0022, 0.0090), 0.00065, 0.001, "silver", sides=12)
        return b
    if name == "audio_board":
        b = PartBuilder()
        b.box((-0.133, -0.068, 0.0100), (0.035, 0.032, 0.0016), "pcb", radius=0.002, segments=3)
        b.cylinder((-0.153, -0.083, 0.0095), 0.0034, 0.006, "aluminum_dark", sides=32)
        b.cylinder((-0.153, -0.083, 0.0095), 0.0019, 0.0065, "port", sides=24)
        b.box((-0.131, -0.063, 0.0112), (0.006, 0.006, 0.001), "chip_top", radius=0.001, segments=2)
        return b
    raise ValueError("Missing geometry builder for " + name)


def write_part_mesh(obj, builder, material_names, materials):
    if not builder.vertices or not builder.faces:
        raise ValueError("Empty mesh for " + obj.name)
    mins = [min(v[i] for v in builder.vertices) for i in range(3)]
    maxs = [max(v[i] for v in builder.vertices) for i in range(3)]
    center = Vector([(mins[i] + maxs[i]) / 2 for i in range(3)])
    local_vertices = [tuple(Vector(v) - center) for v in builder.vertices]
    mesh_data_name = obj.name + "_Mesh"
    old_mesh = obj.data
    # Free the exact desired datablock name without deleting/cleaning anything.
    # Retained rough geometry is renamed, so neither Blender nor glTF adds .001.
    if old_mesh and old_mesh.name == mesh_data_name:
        old_mesh.name = obj.name + "_Rough_Input_Mesh"
    mesh = bpy.data.meshes.new(mesh_data_name)
    mesh.from_pydata(local_vertices, [], builder.faces)
    mesh.update(calc_edges=True)
    for material_name in material_names:
        mesh.materials.append(materials[material_name])
    material_indices = {name: index for index, name in enumerate(material_names)}
    for polygon, material_id in zip(mesh.polygons, builder.material_ids):
        polygon.material_index = material_indices[material_id]
        polygon.use_smooth = True
    mesh.validate(verbose=False, clean_customdata=False)
    obj.data = mesh
    obj.location = center
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    for modifier in list(obj.modifiers):
        obj.modifiers.remove(modifier)
    obj.name = obj.name.split(".")[0]
    obj.data.name = obj.name + "_Mesh"
    # Original mesh datablocks are retained as orphan data in the new .blend;
    # the supplied source file remains untouched and no cleanup operation runs.


def make_preview_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "AgX"
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 32

    stage = bpy.data.collections.get("Studio_Preview") or bpy.data.collections.new("Studio_Preview")
    if stage.name not in [c.name for c in scene.collection.children]:
        scene.collection.children.link(stage)
    def stage_link(obj):
        for collection in list(obj.users_collection):
            collection.objects.unlink(obj)
        stage.objects.link(obj)
        return obj

    # Matte graphite floor, intentionally outside MacBook_Assembly and excluded from GLB.
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0, 0, -0.004))
    floor = stage_link(bpy.context.object)
    floor.name = "studio_floor"
    floor_mat = bpy.data.materials.get("Studio_Graphite") or bpy.data.materials.new("Studio_Graphite")
    floor_mat.diffuse_color = (0.012, 0.017, 0.026, 1)
    floor_mat.use_nodes = True
    floor_bsdf = next(node for node in floor_mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    floor_bsdf.inputs["Base Color"].default_value = floor_mat.diffuse_color
    floor_bsdf.inputs["Roughness"].default_value = 0.3
    floor.data.materials.clear()
    floor.data.materials.append(floor_mat)

    def area(name, location, energy, color, size):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = color
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(name, data)
        stage.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (Vector((0, 0, 0.08)) - obj.location).to_track_quat("-Z", "Y").to_euler()
        return obj

    area("studio_key", (0.12, -0.30, 0.52), 10, (0.78, 0.86, 1.0), 0.34)
    area("studio_rim", (-0.36, 0.20, 0.31), 15, (0.36, 0.68, 1.0), 0.30)
    area("studio_warm_fill", (0.32, 0.12, 0.42), 10, (1.0, 0.69, 0.42), 0.28)

    cam_data = bpy.data.cameras.new("studio_camera")
    camera = bpy.data.objects.new("studio_camera", cam_data)
    stage.objects.link(camera)
    camera.location = (0.43, -0.47, 0.37)
    target = Vector((0, 0.025, 0.105))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = 55
    scene.camera = camera
    world = scene.world or bpy.data.worlds.new("Studio_World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.035, 0.046, 0.068, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.06


def validate_scene(assembly):
    meshes = [obj for obj in assembly.objects if obj.type == "MESH"]
    names = [obj.name for obj in meshes]
    if len(meshes) != 22 or sorted(names) != sorted(PART_NAMES):
        raise RuntimeError(f"Expected exactly 22 named Mesh objects; got {len(meshes)}: {names}")
    if any("." in name for name in names):
        raise RuntimeError("Object name contains dot suffix")
    if len({obj.data.as_pointer() for obj in meshes}) != len(meshes):
        raise RuntimeError("Mesh datablocks are shared")
    if any(len(obj.data.materials) == 0 for obj in meshes):
        raise RuntimeError("A Mesh has no material slot")
    if any(len(obj.modifiers) for obj in meshes):
        raise RuntimeError("Modifiers are not allowed on the semantic meshes")
    if len({obj.data.as_pointer() for obj in meshes}) != 22:
        raise RuntimeError("Mesh datablocks are shared")
    if any(abs(value) > 1e-5 for obj in meshes for value in obj.scale - Vector((1, 1, 1))):
        raise RuntimeError("A Mesh has unapplied scale")
    hinge = bpy.data.objects.get("display_hinge")
    if hinge is None or bpy.data.objects["display_assembly"].parent != hinge:
        raise RuntimeError("Display mesh must be hinged to display_hinge")
    if abs(hinge.rotation_euler.x - DISPLAY_ANGLE) > 1e-5:
        raise RuntimeError("Display hinge must carry the approved 105-degree open pose")
    print("VALIDATION: 22 unique Mesh objects, exact names, material slots, no modifiers, display hinge parent")
    for obj in sorted(meshes, key=lambda x: x.name):
        print("MESH", obj.name, "dimensions=", tuple(round(v * 100, 2) for v in obj.dimensions), "users=", obj.data.users)


def main():
    args = args_after_separator()
    os.makedirs(os.path.dirname(os.path.abspath(args.blend_output)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.glb_output)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.preview_output)), exist_ok=True)

    assembly = bpy.data.collections.get("MacBook_Assembly")
    if assembly is None:
        raise RuntimeError("Missing MacBook_Assembly in the saved source .blend")
    existing = {obj.name: obj for obj in assembly.objects if obj.type == "MESH"}
    if set(existing) != set(PART_NAMES):
        raise RuntimeError(f"Source part set differs from approved 22 names: {sorted(existing)}")

    materials = make_materials()
    material_names = list(materials.keys())
    for name in PART_NAMES:
        builder = build_part(name)
        write_part_mesh(existing[name], builder, material_names, materials)

    # Hinge cable sits just behind the base and connects toward the tilted panel.
    # Keep the lid Mesh centre origin and avoid parenting semantic Meshes.
    lid = existing["display_assembly"]
    lid["open_angle_degrees"] = 105.0
    lid["design_reference"] = "MacBook Pro 14-inch (Nov 2023) M3 Pro"
    hinge = bpy.data.objects.get("display_hinge")
    if hinge is None:
        hinge = bpy.data.objects.new("display_hinge", None)
        assembly.objects.link(hinge)
    hinge.empty_display_type = "PLAIN_AXES"
    hinge.location = (0.0, D / 2 - 0.007, BASE_H + 0.004)
    hinge.rotation_euler = (DISPLAY_ANGLE, 0.0, 0.0)
    lid_mesh_center = lid.location.copy()
    lid.parent = hinge
    # The display Mesh origin remains its geometric center; its center is half
    # a panel-height from the Empty along the screen's local Y axis.
    lid.location = (0.0, DISPLAY_H / 2 + lid_mesh_center.y, lid_mesh_center.z)
    lid.rotation_euler = (0.0, 0.0, 0.0)
    lid.scale = (1.0, 1.0, 1.0)
    assembly["model_reference"] = "MacBook Pro 14-inch (Nov 2023) M3 Pro"
    assembly["geometry_disclaimer"] = "Visual reconstruction from public specifications and teardown references; not Apple CAD or engineering measurements."
    for obj in existing.values():
        obj["part_id"] = obj.name
        obj["geometry_source"] = "Visual reconstruction; see part-data.js for per-field provenance"
        # Keep semantic Meshes directly in the requested assembly collection.
        if assembly not in obj.users_collection:
            assembly.objects.link(obj)

    make_preview_scene()
    validate_scene(assembly)
    scene = bpy.context.scene
    scene.render.filepath = args.preview_output
    meshes = [obj for obj in assembly.objects if obj.type == "MESH"]

    # Save a new native scene before exporting; never overwrite the input .blend.
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.blend_output))
    bpy.ops.render.render(write_still=True)

    # A second still previews the dramatic separated layout, then restores
    # every transform before GLB export so the saved model stays assembled.
    restore_locations = {obj.name: obj.location.copy() for obj in meshes}
    for obj in meshes:
        name = obj.name
        if name in ("bottom_case", "display_assembly"):
            continue
        if name == "battery":
            offset = Vector((0.0, 0.0, -0.018))
        elif name == "keyboard_top_case":
            offset = Vector((0.0, -0.040, 0.055))
        elif name == "trackpad":
            offset = Vector((-0.055, -0.075, 0.045))
        elif name.startswith("speaker_"):
            offset = Vector((-0.020 if name.endswith("left") else 0.020, 0.0, 0.030))
        elif name.startswith("fan_"):
            offset = Vector((-0.014 if name.endswith("left") else 0.014, 0.015, 0.040))
        elif name in ("logic_board", "usb_c_board", "magsafe_board", "audio_board", "battery_management_board", "display_connector"):
            offset = Vector((0.0, 0.0, 0.045))
        else:
            offset = Vector((0.0, 0.0, 0.060))
        obj.location += offset
    floor = bpy.data.objects.get("studio_floor")
    if floor:
        floor.hide_render = True
    scene.render.filepath = args.exploded_preview_output
    bpy.ops.render.render(write_still=True)
    if floor:
        floor.hide_render = False
    for obj in meshes:
        obj.location = restore_locations[obj.name]

    # Export exactly the 22 semantic Mesh objects. Preview camera/lights/floor are omitted.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    hinge.select_set(True)
    bpy.context.view_layer.objects.active = existing["bottom_case"]
    bpy.ops.export_scene.gltf(
        filepath=os.path.abspath(args.glb_output),
        export_format="GLB",
        use_selection=True,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
        export_apply=True,
        export_animations=False,
    )
    print("SAVED BLEND", os.path.abspath(args.blend_output))
    print("EXPORTED GLB", os.path.abspath(args.glb_output))
    print("PREVIEW", os.path.abspath(args.preview_output))
    print("EXPLODED PREVIEW", os.path.abspath(args.exploded_preview_output))


if __name__ == "__main__":
    main()
