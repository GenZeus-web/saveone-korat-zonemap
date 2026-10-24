ไ# ชุดของตลาดไทย: รถเข็น · เต็นท์ขาว 3×3 ม. · ร่มแม่ค้า · เวที — สร้างด้วย Blender แบบไม่เปิดหน้าจอ
# รัน: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P blender\thai-set.py
# ได้: models/blender/*.glb (ใช้ในเว็บ) + blender/thai-set.png (ภาพรวมทุกชิ้น)
# หน่วย = เมตร · หน้าร้านหัน -Y ของ Blender (= +Z ในเว็บ)
import bpy, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'models', 'blender')
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def lin(h):  # '#rrggbb' → linear
    c = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c)

MAT = {}
def M(h, rough=.6, metal=0.0, alpha=1.0, emit=0.0):
    k = (h, rough, metal, alpha, emit)
    if k in MAT: return MAT[k]
    m = bpy.data.materials.new(h); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*lin(h), 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
        for a, v in (('surface_render_method', 'BLENDED'), ('blend_method', 'BLEND')):
            if hasattr(m, a):
                try: setattr(m, a, v)
                except Exception: pass
    if emit:
        b.inputs['Emission Color'].default_value = (*lin(h), 1); b.inputs['Emission Strength'].default_value = emit
    MAT[k] = m; return m

PARTS = []  # วัตถุของชิ้นที่กำลังสร้าง
def keep(o, m):
    o.data.materials.append(m); PARTS.append(o); return o

def box(size, loc, m, bevel=.01, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 2
    return keep(o, m)

def cyl(r, h, loc, m, rot=(0, 0, 0), v=20, smooth=True):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=v); o = bpy.context.object
    if smooth: bpy.ops.object.shade_smooth()
    return keep(o, m)

def bar(a, b, r, m, v=8):  # ท่อจากจุด a ไป b
    a, b = [*a], [*b]; d = [b[i] - a[i] for i in range(3)]; L = math.sqrt(sum(x * x for x in d))
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=L, vertices=v, location=[(a[i] + b[i]) / 2 for i in range(3)])
    o = bpy.context.object
    o.rotation_euler = (0, math.acos(max(-1, min(1, d[2] / L))), math.atan2(d[1], d[0])); return keep(o, m)

def panels(cone, cols):  # ระบายสีสลับทีละช่อง
    for c in cols: cone.data.materials.append(c)
    for i, f in enumerate(cone.data.polygons): f.material_index = i % len(cols)
    PARTS.append(cone)

def export(name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in PARTS: o.select_set(True)
    p = os.path.join(OUT, name + '.glb')
    bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', export_apply=True, use_selection=True)
    print('EXPORT', name, os.path.getsize(p))
    done = list(PARTS); PARTS.clear(); return done

def move(objs, dx):  # วางเรียงกันในภาพรวม (หลังส่งออกแล้ว)
    for o in objs: o.location.x += dx

STEEL, TIRE, WOOD = M('#c9ced6', .3, 1.0), M('#26292e', .85), M('#b98a5b', .7)

# ── 1. รถเข็นขายอาหาร (1.6 × 0.7 ม.) ──
box((1.6, .7, .75), (0, 0, .5), M('#d8322f', .45))
box((1.7, .78, .04), (0, 0, .9), STEEL, .005)
box((1.62, .72, .08), (0, 0, .78), M('#f6f4ef', .5), 0)
box((1.2, .5, .02), (-.1, 0, 1.38), STEEL, .004)
for x in (-.7, .5):
    for y in (-.24, .24): box((.02, .02, .46), (x, y, 1.15), STEEL, 0)
box((1.18, .48, .44), (-.1, 0, 1.15), M('#cfe8f2', .05, 0, .3), 0)
for i in range(5): cyl(.06, .05, (-.55 + i * .22, 0, .97), M('#e7a443'))
box((.36, .36, .08), (.6, 0, .96), M('#5a5f66', .3, .9), .01)
cyl(.17, .06, (.6, 0, 1.03), M('#5a5f66', .3, .9))
cyl(.13, .5, (.95, .15, .25), M('#2d6fd1', .4))
for x in (-.6, .6):
    for y in (-.38, .38): cyl(.16, .07, (x, y, .16), TIRE, (math.pi / 2, 0, 0))
cyl(.02, .8, (-.95, 0, 1.0), STEEL, (math.pi / 2, 0, 0), 12)
box((1.3, .03, .26), (-.1, -.26, 1.75), M('#f6cf45', .5), .01)
for x in (-.7, .5): cyl(.015, .36, (x, -.26, 1.56), STEEL, v=8)
bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=1.25, radius2=0, depth=.45, location=(.2, .1, 2.35), end_fill_type='NOTHING')
u = bpy.context.object; u.modifiers.new('s', 'SOLIDIFY').thickness = .015; panels(u, [M('#d8322f', .5), M('#f6f4ef', .5)])
cyl(.02, 2.3, (.2, .1, 1.17), STEEL, v=8)
cart = export('food-cart')

# ── 2. เต็นท์ขาว 3 × 3 ม. หลังคาทรงปิรามิด + ระบายน้ำเงิน ──
W, EAVE, PEAK = 3.0, 2.3, 3.05
for x in (-1.45, 1.45):
    for y in (-1.45, 1.45):
        cyl(.03, EAVE, (x, y, EAVE / 2), STEEL, v=8); cyl(.12, .02, (x, y, .01), STEEL, v=12)
for a, b in (((-1.45, -1.45), (1.45, -1.45)), ((-1.45, 1.45), (1.45, 1.45)), ((-1.45, -1.45), (-1.45, 1.45)), ((1.45, -1.45), (1.45, 1.45))):
    bar((*a, EAVE), (*b, EAVE), .025, STEEL)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=W / math.sqrt(2) + .05, radius2=0, depth=PEAK - EAVE, location=(0, 0, (EAVE + PEAK) / 2),
                                rotation=(0, 0, math.pi / 4), end_fill_type='NOTHING')
roof = bpy.context.object; roof.modifiers.new('s', 'SOLIDIFY').thickness = .02; keep(roof, M('#fbfbf8', .75))
for i, (x, y, w, d) in enumerate(((0, -1.5, 3.04, .02), (0, 1.5, 3.04, .02), (-1.5, 0, .02, 3.04), (1.5, 0, .02, 3.04))):
    box((w, d, .28), (x, y, EAVE - .12), M('#fbfbf8', .75), 0)
    box((w + .002 if w > d else w + .004, d + .004 if w > d else d + .002, .05), (x, y, EAVE - .24), M('#2d6fd1', .5), 0)  # ขอบระบายสีน้ำเงิน
# โต๊ะ/ของวางในเว็บเอง (ล็อกอาหาร = โต๊ะ 75 × 75 ซม.)
tent = export('tent-white')

# ── 3. ร่มแม่ค้า (ร่มสนาม ⌀ 2.6 ม. ลายสี) ──
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.3, radius2=0, depth=.55, location=(0, 0, 2.35), end_fill_type='NOTHING')
c = bpy.context.object; c.modifiers.new('s', 'SOLIDIFY').thickness = .015
panels(c, [M('#e23b3b', .6), M('#f6cf45', .6), M('#2fa35a', .6), M('#2d6fd1', .6)])
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.3, depth=.18, location=(0, 0, 2.0), end_fill_type='NOTHING')
v = bpy.context.object; v.modifiers.new('s', 'SOLIDIFY').thickness = .01
panels(v, [M('#e23b3b', .6), M('#f6cf45', .6), M('#2fa35a', .6), M('#2d6fd1', .6)])
cyl(.025, 2.6, (0, 0, 1.3), STEEL, v=8)
cyl(.28, .08, (0, 0, .04), M('#3a3f4a', .7))
umb = export('umbrella')

# ── 4. เวทีกิจกรรม 8 × 5 ม. สูง 1 ม. + โครงทรัส + จอ LED + ลำโพง ──
SW, SD, SH = 8.0, 5.0, 1.0
box((SW, SD, .08), (0, 0, SH), M('#2b2f36', .5), .01)                      # พื้นเวที
box((SW, SD, SH - .04), (0, 0, (SH - .04) / 2), M('#14161a', .9), 0)        # กระโปรงดำ
box((SW + .02, .02, .12), (0, -SD / 2, SH - .1), M('#e2671c', .5), 0)        # ขอบหน้าเวที
for i in range(4): box((1.4, .3, .2), (0, -SD / 2 - .15 - i * .3, SH - .25 - i * .25), M('#3a3f4a', .7), .005)  # บันได
TR = M('#d9dde3', .35, 1.0); TH = 5.2
for x in (-SW / 2 + .2, SW / 2 - .2):                                      # เสาทรัส 2 ต้น (โครง 4 ท่อ)
    for dx in (-.15, .15):
        for dy in (-.15, .15): bar((x + dx, 1.6 + dy, SH), (x + dx, 1.6 + dy, SH + TH), .025, TR)
    for k in range(10):
        z0 = SH + k * TH / 10; bar((x - .15, 1.45, z0), (x + .15, 1.75, z0 + TH / 10), .012, TR)
for dz in (0, .3):                                                          # คานบน
    for dy in (-.15, .15): bar((-SW / 2 + .05, 1.6 + dy, SH + TH - dz), (SW / 2 - .05, 1.6 + dy, SH + TH - dz), .025, TR)
box((6.2, .12, 3.2), (0, 1.62, SH + 2.7), M('#0b0d12', .3), .02)              # จอ LED
box((6.0, .02, 3.0), (0, 1.55, SH + 2.7), M('#3fb5ff', .3, 0, 1, 1.6), 0)    # ภาพบนจอ
box((2.6, .02, .9), (0, 1.53, SH + 3.0), M('#ffd23f', .3, 0, 1, 2.5), 0)
for x in (-SW / 2 - .5, SW / 2 + .5):                                       # ลำโพงข้างเวที
    for k in range(3): box((.7, .6, .7), (x, -.2, .35 + k * .72), M('#1d2026', .6), .02); cyl(.2, .02, (x, -.51, .35 + k * .72), M('#5a5f66', .4), (math.pi / 2, 0, 0))
for x in (-2.5, -.8, .8, 2.5):                                              # ไฟส่องบนคาน
    cyl(.12, .25, (x, 1.3, SH + TH - .35), M('#1d2026', .5), (math.pi / 2.6, 0, 0))
box((.5, .02, .03), (0, -.8, SH + 1.35), M('#2b2f36'), 0)                    # ขาไมค์
cyl(.012, 1.3, (0, -.8, SH + .7), STEEL, v=6)
stage = export('stage')

# ── ภาพรวม ──
for objs, dx in ((cart, -9.5), (tent, -5.5), (umb, -1.8), (stage, 5.5)): move(objs, dx)
bpy.ops.mesh.primitive_plane_add(size=60); bpy.context.object.data.materials.append(M('#9ea2a7', .95))
bpy.ops.object.light_add(type='SUN'); sun = bpy.context.object; sun.data.energy = 4.2; sun.data.angle = .05
sun.rotation_euler = (math.radians(42), 0, math.radians(30))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (*lin('#cfe3f5'), 1); w.node_tree.nodes['Background'].inputs[1].default_value = .9
bpy.ops.object.camera_add(location=(-1, -25, 11)); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 34
bpy.ops.object.empty_add(location=(-1.2, 0, 2.2)); t = cam.constraints.new('TRACK_TO'); t.target = bpy.context.object
sc.render.resolution_x, sc.render.resolution_y = 1600, 800
for e in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
    try: sc.render.engine = e; break
    except Exception: pass
sc.render.filepath = os.path.join(HERE, 'thai-set.png')
bpy.ops.render.render(write_still=True)
print('RENDER', sc.render.filepath)
