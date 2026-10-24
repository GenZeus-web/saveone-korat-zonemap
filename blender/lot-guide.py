# ภาพอธิบายการจัดล็อก (แทนรูปข้อมูลบนเว็บตลาด · วาดใหม่เป็นแบบของเรา)
# รัน: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P blender\lot-guide.py -- [food|boot-v|boot-h|all]
# ได้: photos/lot-food.jpg · photos/lot-boot-v.jpg · photos/lot-boot-h.jpg (ฝังในไฟล์เดียวผ่าน build-assets.py)
# หน่วย = เมตร · x = ขวา · y = ลึกเข้าไป (กล้องมองจากทิศใต้ เอียงลง) · ป้ายภาษาไทยวางใน HTML ตามพิกัด FRAME ข้างล่าง
import bpy, math, os, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
which = args[0] if args else 'all'

def lin(h):
    c = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c)
MAT = {}
def M(h, rough=.6, metal=0.0):
    k = (h, rough, metal)
    if k not in MAT:
        m = bpy.data.materials.new(h); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*lin(h), 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
        MAT[k] = m
    return MAT[k]
def box(size, loc, m, bevel=.01, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel: bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 2
    o.data.materials.append(m); return o
def cyl(r, h, loc, m, rot=(0, 0, 0), v=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=v); o = bpy.context.object
    bpy.ops.object.shade_smooth(); o.data.materials.append(m); return o

def glb(path, length=None, height=None, loc=(0, 0, 0), rz=0.0):
    """นำเข้าโมเดล แล้วย่อ/ขยายตามความยาว (แกนยาวสุดแนวราบ) หรือความสูง · วางฐานบนพื้น"""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, path))
    objs = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new('g', None); bpy.context.scene.collection.objects.link(root)
    for o in objs:
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == 'MESH' for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    s = length / max(mx.x - mn.x, mx.y - mn.y) if length else height / (mx.z - mn.z)
    root.scale = (s, s, s); root.rotation_euler = (0, 0, rz)
    c = (mn + mx) / 2
    off = Vector((-c.x * s, -c.y * s, -mn.z * s)); off.rotate(root.rotation_euler)
    root.location = Vector(loc) + off
    return root

def scene():
    bpy.ops.wm.read_factory_settings(use_empty=True); MAT.clear()
    sc = bpy.context.scene
    sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.energy = 3.0; sun_d.angle = math.radians(4); sun_d.color = (1, .97, .92)
    sun = bpy.data.objects.new('sun', sun_d); sc.collection.objects.link(sun); sun.rotation_euler = (math.radians(38), math.radians(-18), math.radians(-30))
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (.78, .84, .95, 1); bg.inputs[1].default_value = .9
    sc.render.engine = 'BLENDER_EEVEE'
    for k, v in (('use_raytracing', True), ('use_shadows', True), ('taa_render_samples', 48), ('use_fast_gi', True)):
        if hasattr(sc.eevee, k):
            try: setattr(sc.eevee, k, v)
            except Exception: pass
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = .1
    return sc

def shoot(sc, name, x0, x1, ty, tz, H_per_W, tilt=52):
    """กล้องมุมฉาก (ortho) มองจากทิศใต้ ไม่หมุนซ้าย-ขวา → ระยะแนวนอนในภาพเป็นเส้นตรงกับ x จริง"""
    cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = x1 - x0; cd.sensor_fit = 'HORIZONTAL'
    cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    t = math.radians(tilt); d = Vector((0, math.sin(t), -math.cos(t)))
    cam.rotation_euler = (t, 0, 0); cam.location = Vector(((x0 + x1) / 2, ty, tz)) - d * 30
    sc.render.resolution_x = 1200; sc.render.resolution_y = round(1200 * H_per_W)
    sc.render.image_settings.file_format = 'PNG'
    png = os.path.join(HERE, 'lot-' + name + '.png'); sc.render.filepath = png
    bpy.ops.render.render(write_still=True)
    # Blender ไม่มี PIL → แปลงเป็น photos/lot-*.jpg ด้วย Python ในเครื่อง (อาหารตัดขอบ y 90–470)
    try:  # ย่อเป็น JPEG ให้ไฟล์เดียวไม่บวม (ใช้ Python ในเครื่องแปลงทีหลังถ้า Blender ไม่มี PIL)
        from PIL import Image
        Image.open(png).convert('RGB').save(os.path.join(ROOT, 'photos', 'lot-' + name + '.jpg'), quality=80, optimize=True, progressive=True)
    except ImportError: pass
    print('RENDER', name, x0, x1)

# สีพื้น/เส้น สร้างใหม่ทุกฉาก (read_factory_settings ลบวัสดุเก่าทิ้ง)
ASPH = lambda: M('#9aa0a6', .9); LINE = lambda: M('#f7f7f4', .6); YEL = lambda: M('#f2c230', .6); SELLC = lambda: M('#c9b0f2', .85)
def ground(x0, x1, y0, y1, m=None):
    box((x1 - x0, y1 - y0, .02), ((x0 + x1) / 2, (y0 + y1) / 2, -.01), m or ASPH(), 0)
def stripe(a, b, w=.07, m=None, dash=0):
    (ax, ay), (bx, by) = a, b; L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
    segs = [(0, L)] if not dash else [(s, min(s + dash, L)) for s in [i * dash * 2 for i in range(int(L / dash / 2) + 1)]]
    for s, e in segs:
        if e <= s: continue
        cx, cy = ax + ux * (s + e) / 2, ay + uy * (s + e) / 2
        box(((e - s) if abs(ux) > .5 else w, (e - s) if abs(uy) > .5 else w, .006), (cx, cy, .003), m or LINE(), 0)

PEOPLE = ['models/people/character-a.glb', 'models/people/character-f.glb', 'models/people/character-k.glb', 'models/people/character-n.glb']

# ── อาหาร: โต๊ะ 75 × 75 ซม. = 1 ล็อก · 1 / 2 / 3 ล็อก โต๊ะต่อกัน · คนขายยืนหลังโต๊ะ ──
FOOD_G = [(0.0, 1), (1.9, 2), (4.4, 3)]   # (x เริ่ม, จำนวนโต๊ะ)
FOOD_FRAME = (-0.8, 7.45)
def table(x, y, i):
    T = .75; RED, LEG = M('#d8322f', .45), M('#3a3f46', .4, .8)
    box((T - .02, T - .02, .035), (x + T / 2, y + T / 2, .72), RED, .008)
    for dx in (.06, T - .06):
        for dy in (.06, T - .06): cyl(.014, .7, (x + dx, y + dy, .355), LEG, v=8)
    goods = [('#f6f4ef', '#e7a443'), ('#2d6fd1', '#f6cf45'), ('#f6f4ef', '#4fbf86')][i % 3]
    box((.5, .34, .05), (x + T / 2, y + .26, .765), M(goods[0], .5), .01)       # ถาด
    for k in range(4): cyl(.045, .05, (x + .18 + k * .13, y + .26, .81), M(goods[1], .55))
    box((.22, .16, .14), (x + .2, y + .58, .81), M('#cfe8f2', .1), .01)          # กล่องใส
def build_food():
    sc = scene(); x0, x1 = FOOD_FRAME
    ground(x0 - 2, x1 + 2, -4, 12, M('#b7b1a6', .9))
    for gi, (gx, n) in enumerate(FOOD_G):
        for i in range(n): table(gx + i * .75, 0, gi + i)
        stripe((gx - .05, -.05), (gx + n * .75 + .05, -.05), .04, YEL())           # เส้นหน้าล็อก
        glb(PEOPLE[gi], height=1.62, loc=(gx + n * .75 / 2, 1.15, 0), rz=0)      # คนขายหันหน้าเข้ากล้อง
    shoot(sc, 'food', x0, x1, .75, .5, .5, tilt=44)

# ── เปิดท้าย: ล็อก 2.4 × 8 ม. · ขาย 3.5 ม. (ใกล้กล้อง) + รถ 4.5 ม. (ด้านหลัง ท้ายรถหันเข้าที่ขาย) ──
LOT_W, SELL, CAR = 2.4, 3.5, 4.5
BOOT_V = [(0.0, 1), (4.4, 2)]; BOOT_V_FRAME = (-1.0, 10.2)
BOOT_H = [(0.0, 3), (9.2, 4)]; BOOT_H_FRAME = (-1.0, 19.8)
def rack(x, y):
    P = M('#c9ced6', .3, 1.0)
    for dx in (0, 1.4): cyl(.02, 1.5, (x + dx, y, .75), P, v=8)
    cyl(.018, 1.44, (x + .7, y, 1.45), P, rot=(0, math.pi / 2, 0), v=8)
    for k, h in enumerate(('#e23b3b', '#2d6fd1', '#f6cf45', '#4fbf86', '#a874e2', '#f27cb4', '#f6f4ef')):
        box((.16, .42, .62), (x + .12 + k * .19, y, 1.08), M(h, .8), .03)
def lots(gx, n, horiz, car_i):
    w = n * LOT_W
    box((w, SELL, .008), (gx + w / 2, SELL / 2, .004), SELLC(), 0)                   # พื้นที่ขาย (ทาสีม่วงอ่อน)
    for e in ((gx, 0, gx + w, 0), (gx, 0, gx, SELL + CAR), (gx + w, 0, gx + w, SELL + CAR), (gx, SELL + CAR, gx + w, SELL + CAR)):
        stripe(e[:2], e[2:])
    for i in range(1, n): stripe((gx + i * LOT_W, 0), (gx + i * LOT_W, SELL + CAR), .05, dash=.35)
    stripe((gx, SELL), (gx + w, SELL), .05, dash=.35)
    stripe((gx, SELL + CAR - .12), (gx + w, SELL + CAR - .12), .08, YEL())          # แนวท้ายล็อก
    if horiz: glb('models/car/' + ('suv.glb', 'sedan.glb')[car_i % 2], length=4.4, loc=(gx + 2.45, SELL + 2.2, 0), rz=math.pi / 2)
    else: glb('models/car/' + ('truck.glb', 'van.glb')[car_i % 2], length=4.3, loc=(gx + LOT_W / 2, SELL + CAR / 2, 0), rz=math.pi)
    # ของในที่ขาย: ราวเสื้อ + โต๊ะ + คนขาย
    rack(gx + .45, 1.5)
    if n > 1:
        box((1.2, .6, .74), (gx + LOT_W + 1.2, 1.2, .37), M('#f6f4ef', .6), .01)                 # โต๊ะวางของ
        for k, c in enumerate(('#2d6fd1', '#e7a443', '#e23b3b', '#4fbf86')): box((.22, .3, .12), (gx + LOT_W + .78 + k * .28, 1.2, .8), M(c, .6), .02)
        rack(gx + LOT_W + .5, 2.6)
    if n > 2:
        for i in range(2, n): rack(gx + i * LOT_W + .45, 1.5 + (i % 2) * .9)
    glb(PEOPLE[n % 4], height=1.62, loc=(gx + 1.95, 1.2, 0))
def build_boot(name, groups, frame, horiz, H):
    sc = scene(); x0, x1 = frame
    ground(x0 - 3, x1 + 3, -4, 12)
    for i, (gx, n) in enumerate(groups): lots(gx, n, horiz, i)
    shoot(sc, name, x0, x1, 3.6, .6, H, tilt=50)

if which in ('food', 'all'): build_food()
if which in ('boot-v', 'all'): build_boot('boot-v', BOOT_V, BOOT_V_FRAME, False, .62)
if which in ('boot-h', 'all'): build_boot('boot-h', BOOT_H, BOOT_H_FRAME, True, .36)
