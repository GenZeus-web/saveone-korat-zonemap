# ป้ายตลาด "SAVEONE" — กล่องไฟสีส้มซ้อนเหลื่อมกัน (ไม่เรียงตรง) + ป้ายใหญ่บนยอด · จากรูปจริงที่เจ้าของส่ง 24 ต.ค.
# รัน: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P blender\sign-tower.py -- [render]
# ได้: models/blender/sign-tower.glb (เมตร · ฐานกลาง = 0,0,0 · ป้ายหันไป -y) · render = ภาพตัวอย่าง blender/sign-tower.png
# ขนาดประมาณจากรูป (รถเก๋งข้างๆ ยาว ≈ 4.6 ม.): กล่อง 1.2–1.5 ม. · สูงรวม ≈ 13 ม. — ยังไม่ได้วัดจริง
import bpy, math, os, sys, random
from mathutils import Vector, Euler
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene

def lin(h): return tuple((int(h[i:i+2], 16) / 255) ** 2.2 for i in (1, 3, 5))
def glow(name, h, s):
    """วัสดุเรืองแสง (ส่งออก GLB เป็น emissive · three.js เห็นสว่างแม้ไม่มีไฟ)"""
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*lin(h), 1); b.inputs['Emission Color'].default_value = (*lin(h), 1)
    b.inputs['Emission Strength'].default_value = s; b.inputs['Roughness'].default_value = .6; return m
FACE, WHITE = glow('face', '#ff9a2e', 1.6), glow('white', '#fff3df', 1.4)   # ไฟในลัง (แรงเกิน = เหลืองจ้า) · ขาว = ตัวอักษร SAVEONE
SIGN = glow('sign', '#f2a43a', 1.1)

WOOD = glow('wood', '#c98a3c', .35)   # ไม้ (เรืองนิดๆ ให้เห็นตอนกลางคืน)
def crate(loc, s, yaw, tilt, core=FACE):
    """ลังไม้ 1 ใบ (เจ้าของ: ฟีลกล่องไม้) — โครงไม้ 12 เส้น + ไม้ระแนง 3 แผ่น/ด้าน มีช่อง → เห็นไฟในลังลอดออกมา
    core = แกนเรืองแสงข้างใน · ทุกลังสีเดียวกัน (เจ้าของ: ที่เห็นขาวในรูปคือมุมแสง)"""
    wood = WOOD; b, t = .07 * s, .03 * s; h = s / 2
    def part(dims, p, m):
        bpy.ops.mesh.primitive_cube_add(size=1, location=p); o = bpy.context.object; o.scale = dims; o.data.materials.append(m); return o
    root = part((s * .86,) * 3, (0, 0, 0), core)                                       # ไฟในลัง
    for a in range(3):                                                                 # โครง 12 เส้น
        for u in (-1, 1):
            for v in (-1, 1):
                p = [0, 0, 0]; d = [b, b, b]; d[a] = s; o1, o2 = [i for i in range(3) if i != a]
                p[o1], p[o2] = u * (h - b / 2), v * (h - b / 2); part(d, p, wood)
    w = (s - 2 * b) / 7                                                                # ระแนง 4 แผ่น ช่อง 3 ช่อง
    for a in range(3):                                                                 # a = แกนตั้งฉากกับด้าน
        run = 0 if a != 0 else 1                                                       # ระแนงวิ่งตามแกนนี้ (แนวนอน)
        across = [i for i in range(3) if i not in (a, run)][0]
        for side in (-1, 1):
            for k in (0, 2, 4, 6):
                p = [0, 0, 0]; d = [0, 0, 0]
                p[a], d[a] = side * (h - t / 2), t; d[run] = s - 2 * b; p[across], d[across] = -h + b + w * (k + .5), w
                part(d, p, wood)
    bpy.ops.object.select_all(action='DESELECT')                                       # รวมชิ้นของลังนี้เป็นวัตถุเดียว แล้วค่อยหมุน/วาง
    for o in bpy.context.scene.objects:
        if o.get('crate') is None and o.type == 'MESH' and o.name not in DONE: o.select_set(True)
    bpy.context.view_layer.objects.active = root; bpy.ops.object.transform_apply(scale=True); bpy.ops.object.join()
    root['crate'] = 1; DONE.add(root.name); root.rotation_euler = (tilt[0], tilt[1], yaw); root.location = loc
DONE = set()

# กองกล่อง: ล่างกว้าง 3–4 ใบ → กลางเหลือ 1–2 ใบ เอียงไปมา → ยอด 2 ใบรับป้าย · สุ่มแบบตายตัว (seed) ได้ผลเดิมทุกครั้ง
R = random.Random(7); z = 0.0; boxes = []
LAYERS = [4, 3, 3, 2, 2, 1, 2, 1, 2, 1]           # จำนวนกล่องต่อชั้น (นับจากพื้น)
for i, n in enumerate(LAYERS):
    s = R.uniform(1.2, 1.45); cx = .35 * math.sin(i * .9)   # แกนกลางส่ายซ้าย-ขวาเหมือนรูป
    for k in range(n):
        x = cx + (k - (n - 1) / 2) * s * .92 + R.uniform(-.3, .3); y = R.uniform(-.4, .4)   # เหลื่อมมาก = ไม่เรียงต่อกัน
        boxes.append(((x, y, z + s / 2), s, math.radians(R.uniform(-35, 35)), (math.radians(R.uniform(-12, 12)), math.radians(R.uniform(-12, 12)))))
    z += s * .9                                       # ซ้อนเหลื่อมลงไปในชั้นล่างนิดหน่อย (ในรูปไม่มีช่องว่าง)
for loc, s, yaw, tilt in boxes: crate(loc, s, yaw, tilt)

# ป้ายใหญ่บนยอด: กล่องยาว + ตัวอักษร SAVEONE ด้านหน้า + "ตลาดเซฟวัน" สีเขียวบนหลังคา (ข้อความไทยใช้รูปจาก PIL · Blender วางสระบนไม่ถูก)
top = z + 1.0; SW, SH, SD = 4.4, 1.7, 1.3
crate((.2, 0, top), 1.0, 0, (0, 0))                   # จุดรับป้าย (ซ่อนในป้าย)
bpy.ops.mesh.primitive_cube_add(size=1, location=(.2, 0, top)); sign = bpy.context.object; sign.scale = (SW, SD, SH); sign.rotation_euler = (0, 0, math.radians(-8))
sign.data.materials.append(SIGN); w = sign.modifiers.new('bv', 'BEVEL'); w.width = .04
YAW = math.radians(-8); C = Vector((.2, 0, top))
FONT = bpy.data.fonts.load('C:/Windows/Fonts/arialbd.ttf')
TH = os.path.join(HERE, 'sign-tower-th.png')          # ทำโดย sign-tower-text.py (Python เครื่อง · PIL)
if os.path.exists(TH):
    img = bpy.data.images.load(TH); m = bpy.data.materials.new('th'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color']); nt.links.new(tex.outputs['Color'], b.inputs['Emission Color']); nt.links.new(tex.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Emission Strength'].default_value = 2.5; m.use_backface_culling = True   # ด้านเดียว → หลังไม่เห็นตัวหนังสือกลับด้าน
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED'
for side in (0, 1):   # ข้อความ 2 ด้าน: ด้านถนน + ด้านในตลาด (ผังมองจากในตลาด)
    ry = YAW + math.pi * side
    n = Vector((0, -1, 0)); n.rotate(Euler((0, 0, ry)))                     # ทิศหน้าป้ายด้านนี้
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = 'SAVEONE'; cu.size = .95; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = .03; cu.font = FONT
    t = bpy.data.objects.new('t', cu); sc.collection.objects.link(t); t.data.materials.append(WHITE)
    t.location = C + n * (SD / 2 + .02); t.rotation_euler = (math.radians(90), 0, ry)
    if os.path.exists(TH):
        bpy.ops.mesh.primitive_plane_add(size=1, location=C + Vector((0, 0, SH / 2 + .45)) + n * .02, rotation=(math.radians(90), 0, ry)); p = bpy.context.object
        p.scale = (SW * .9, SW * .9 * img.size[1] / img.size[0], 1); p.data.materials.append(m)

out = os.path.join(ROOT, 'models', 'blender', 'sign-tower.glb')
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_apply=True)
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in sc.objects if o.type == 'MESH' for c in o.bound_box]
print('SIZE', [round(max(p[i] for p in pts) - min(p[i] for p in pts), 2) for i in range(3)], 'boxes', len(boxes), 'KB', os.path.getsize(out) // 1024)

if 'render' in args:   # ภาพตัวอย่างกลางคืน (พื้นเทาเข้ม · ไฟน้อย ให้เห็นกล่องเรือง)
    bpy.ops.mesh.primitive_plane_add(size=40); g = bpy.context.object; gm = bpy.data.materials.new('g'); gm.use_nodes = True
    gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.05, .05, .055, 1); g.data.materials.append(gm)
    wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; wd.node_tree.nodes['Background'].inputs[0].default_value = (.02, .025, .04, 1)
    cd = bpy.data.cameras.new('c'); cd.lens = 35; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = (9, -17, 9); cam.rotation_euler = (Vector((0, 0, 6.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.engine = 'BLENDER_EEVEE'; sc.view_settings.view_transform = 'Standard'
    for k, v in (('use_bloom', True),):
        if hasattr(sc.eevee, k): setattr(sc.eevee, k, v)
    sc.render.resolution_x, sc.render.resolution_y = 700, 1000
    sc.render.filepath = os.path.join(HERE, 'sign-tower.png'); bpy.ops.render.render(write_still=True)
