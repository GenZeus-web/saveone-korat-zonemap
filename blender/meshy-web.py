# ย่อโมเดลจาก Meshy ให้เบาพอขึ้นเว็บ (ใช้ซ้ำได้ทุกชิ้นในคลัง models/meshy/)
# รัน: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P blender\meshy-web.py -- <ต้นฉบับ> <ปลายทาง> <สูง ม.> [รูปผิว px=512] [หน้า=0 ไม่ลด] [render]
# เช่น  -- models/meshy/shopper-woman-raw.glb models/people/shopper-woman.glb 1.6 512
#       -- models/meshy/shopper-woman-idle-raw.glb models/people/shopper-woman-idle.glb 1.6 512 0 rig   (มีกระดูก: ย่อรูปผิวอย่างเดียว)
# ได้: GLB หน่วยเมตร · ฐานกลาง = 0,0,0 · รูปผิวย่อ + เก็บเป็น JPEG · ทิศเดิมจาก Meshy (หน้า +z ใน three.js)
import bpy, os, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
a = sys.argv[sys.argv.index('--') + 1:]
src, dst, H = os.path.join(ROOT, a[0]), os.path.join(ROOT, a[1]), float(a[2])
TEX = int(a[3]) if len(a) > 3 and a[3].isdigit() else 512
FACES = int(a[4]) if len(a) > 4 and a[4].isdigit() else 0
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=src)
if 'rig' in a:   # มีกระดูก + ท่า (meshy_rig/animate): ห้ามรวม/ย้ายจุด ไม่งั้นกระดูกเพี้ยน → แค่ย่อรูปผิวแล้วส่งออกพร้อมท่า
    for img in bpy.data.images:
        if img.size[0] > TEX: img.scale(TEX, int(img.size[1] * TEX / img.size[0]))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='JPEG', export_jpeg_quality=82, export_animations=True)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in sc.objects if o.type == 'MESH' for c in o.bound_box]
    print('SIZE', [round(max(p[i] for p in pts) - min(p[i] for p in pts), 2) for i in range(3)], 'anims', [x.name for x in bpy.data.actions], 'KB', os.path.getsize(dst) // 1024)
    sys.exit(0)
ms = [o for o in sc.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
o = bpy.context.object; o.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for e in [x for x in sc.objects if x.type != 'MESH']: bpy.data.objects.remove(e)

pts = [v.co for v in o.data.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
k = H / (hi.z - lo.z); c = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
for v in o.data.vertices: v.co = (v.co - c) * k
o.data.update()
if FACES and len(o.data.polygons) > FACES:
    d = o.modifiers.new('d', 'DECIMATE'); d.ratio = FACES / len(o.data.polygons); bpy.ops.object.modifier_apply(modifier='d')
for img in bpy.data.images:   # ย่อรูปผิว (คนในผังเห็นแค่ไม่กี่สิบพิกเซล)
    if img.size[0] > TEX: img.scale(TEX, int(img.size[1] * TEX / img.size[0]))

os.makedirs(os.path.dirname(dst), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_apply=True, export_image_format='JPEG', export_jpeg_quality=82)
print('SIZE', [round((hi[i] - lo[i]) * k, 2) for i in range(3)], 'tris', sum(len(p.vertices) - 2 for p in o.data.polygons), 'KB', os.path.getsize(dst) // 1024)

if 'render' in a:   # ภาพตัวอย่างหน้า/ข้าง → blender/<ชื่อ>-front.png, -side.png
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (.8, .8, .82, 1)
    sd = bpy.data.lights.new('s', 'SUN'); sd.energy = 3; s = bpy.data.objects.new('s', sd); sc.collection.objects.link(s); s.rotation_euler = (.8, .2, .6)
    cd = bpy.data.cameras.new('c'); cd.lens = 50; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = sc.render.resolution_y = 500; sc.view_settings.view_transform = 'Standard'
    name = os.path.splitext(os.path.basename(dst))[0]; D = H * 2.8
    for tag, loc in (('front', (0, -D, H * .55)), ('side', (D, 0, H * .55))):
        cam.location = loc; cam.rotation_euler = (Vector((0, 0, H / 2)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(HERE, f'{name}-{tag}.png'); bpy.ops.render.render(write_still=True)
