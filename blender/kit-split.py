# แยก "ชุดของ" จาก Meshy (หลายชิ้นในไฟล์เดียว) เป็นไฟล์ละชิ้น — สร้างทีเดียวหลายชิ้น ประหยัดเครดิต (เจ้าของ 24 ต.ค.)
# รัน: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P blender\kit-split.py -- <ไฟล์ชุด.glb> <โฟลเดอร์ปลายทาง> <ชื่อนำหน้า> [รูปผิว px=1024]
# ได้: <ปลายทาง>/<นำหน้า>-1.glb, -2.glb … (ฐานกลาง = 0,0,0 · ขนาดตามไฟล์ชุด ยังไม่ใช่ขนาดจริง → ปรับตอนวาง/ด้วย meshy-web.py)
#      + blender/<นำหน้า>-ภาพรวม.png (เลขกำกับแต่ละชิ้น ไว้ตั้งชื่อ)
# วิธี: แยกส่วนที่ไม่ติดกัน → ทิ้งพื้นแบน → รวมส่วนที่อยู่ใกล้กัน (ขาเตา + ตัวเตา) เป็นชิ้นเดียว → ส่งออกทีละชิ้น
import bpy, os, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
a = sys.argv[sys.argv.index('--') + 1:]
src, out, pre = os.path.join(ROOT, a[0]), os.path.join(ROOT, a[1]), a[2]
TEX = int(a[3]) if len(a) > 3 else 1024
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=src)
ms = [o for o in sc.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
o = bpy.context.object; o.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for e in [x for x in sc.objects if x.type != 'MESH']: bpy.data.objects.remove(e)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')

def bb(ob):
    p = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return Vector([min(v[i] for v in p) for i in range(3)]), Vector([max(v[i] for v in p) for i in range(3)])
parts = [x for x in sc.objects if x.type == 'MESH']
lo = Vector([min(bb(x)[0][i] for x in parts) for i in range(3)]); hi = Vector([max(bb(x)[1][i] for x in parts) for i in range(3)]); size = hi - lo
for x in list(parts):   # พื้นแบนกว้าง (Meshy ทำพื้นรองให้) = ทิ้ง · เศษเล็กมาก = ทิ้ง
    l, h = bb(x); d = h - l
    if (d.z < size.z * .03 and (d.x > size.x * .5 or d.y > size.y * .5)) or max(d) < max(size) * .004:
        bpy.data.objects.remove(x); parts.remove(x)
M = max(size.x, size.y) * .02                        # ระยะที่ถือว่า "ชิ้นเดียวกัน"
grp = list(range(len(parts))); B = [bb(x) for x in parts]
def f(i):
    while grp[i] != i: grp[i] = grp[grp[i]]; i = grp[i]
    return i
for i in range(len(parts)):
    for j in range(i + 1, len(parts)):
        (l1, h1), (l2, h2) = B[i], B[j]
        if all(l1[k] - M <= h2[k] and l2[k] - M <= h1[k] for k in (0, 1)): grp[f(i)] = f(j)
cl = {}
for i, x in enumerate(parts): cl.setdefault(f(i), []).append(x)
cl = sorted(cl.values(), key=lambda g: (round(-sum(bb(x)[0].y for x in g) / len(g) / (size.y / 3)), sum(bb(x)[0].x for x in g) / len(g)))   # แถวหลัง→หน้า ซ้าย→ขวา
for i, g in enumerate(cl):   # รวมเศษในกลุ่มเป็นวัตถุเดียว (ใบไม้ต้นเดียวแตกเป็นหมื่นชิ้น → ส่งออก/เรนเดอร์ค้าง)
    if len(g) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for x in g: x.select_set(True)
        bpy.context.view_layer.objects.active = g[0]; bpy.ops.object.join(); cl[i] = [g[0]]
for img in bpy.data.images:
    if img.size[0] > TEX: img.scale(TEX, TEX)
os.makedirs(out, exist_ok=True); labels = []
for n, g in enumerate(cl, 1):
    l = Vector([min(bb(x)[0][i] for x in g) for i in range(3)]); h = Vector([max(bb(x)[1][i] for x in g) for i in range(3)])
    c = Vector(((l.x + h.x) / 2, (l.y + h.y) / 2, l.z))
    bpy.ops.object.select_all(action='DESELECT')
    for x in g: x.select_set(True); x.location -= c
    f_ = os.path.join(out, f'{pre}-{n}.glb')
    bpy.ops.export_scene.gltf(filepath=f_, export_format='GLB', use_selection=True, export_image_format='JPEG', export_jpeg_quality=85)
    for x in g: x.location += c
    tris = sum(len(p.vertices) - 2 for x in g for p in x.data.polygons)
    print(f'PART {n} parts={len(g)} size={[round(v, 2) for v in (h - l)]} tris={tris} KB={os.path.getsize(f_) // 1024}')
    labels.append((n, Vector((c.x, c.y, h.z))))

# ภาพรวมพร้อมเลข (มองจากด้านหน้าเฉียงบน)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (.85, .85, .87, 1)
sd = bpy.data.lights.new('s', 'SUN'); sd.energy = 3; s = bpy.data.objects.new('s', sd); sc.collection.objects.link(s); s.rotation_euler = (.7, .2, .5)
red = bpy.data.materials.new('r'); red.use_nodes = True; red.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.9, .05, .05, 1)
for n, p in labels:
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = str(n); cu.size = max(size) * .08; cu.align_x = 'CENTER'
    t = bpy.data.objects.new('t', cu); sc.collection.objects.link(t); t.data.materials.append(red); t.location = p + Vector((0, 0, max(size) * .03)); t.rotation_euler = (1.1, 0, 0)
cd = bpy.data.cameras.new('c'); cd.lens = 35; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
mid = (lo + hi) / 2; D = max(size) * 1.3; cam.location = mid + Vector((0, -D, D * .8))
cam.rotation_euler = (mid - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = 1000, 700; sc.view_settings.view_transform = 'Standard'
sc.render.filepath = os.path.join(HERE, f'{pre}-ภาพรวม.png'); bpy.ops.render.render(write_still=True)
print('SCENE', [round(v, 2) for v in size], 'parts', len(cl))
