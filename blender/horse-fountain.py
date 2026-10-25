# ม้าน้ำพุ (รูปปั้นโลหะ ม้ายืนสองขา) — ต้นฉบับจาก Meshy image-to-3d (รูปเจ้าของส่ง 24 ต.ค. · ไม่มีสีผิว 20 เครดิต)
# รัน: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P blender\horse-fountain.py -- [render]
# เข้า: models/meshy/horse-fountain-raw.glb · ได้: models/blender/horse-fountain.glb (เมตร · ฐานกลาง = 0,0,0 · หัวหัน -y)
# สูง 4 ม. = เดาจากรูป (เจ้าของ: เดาเอาไม่ต้องเป๊ะ) · ตัวที่ 2 ในผัง = ตัวเดียวกันหมุนกลับ ไม่ต้องสร้างใหม่
import bpy, math, os, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
H = 4.0
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, 'models', 'meshy', 'horse-fountain-raw.glb'))
ms = [o for o in sc.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
o = bpy.context.object; o.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for e in [x for x in sc.objects if x.type != 'MESH']: bpy.data.objects.remove(e)

pts = [o.matrix_world @ v.co for v in o.data.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
k = H / (hi.z - lo.z)
for v in o.data.vertices:   # ฐานกลางลงพื้น แล้วย่อ/ขยายให้สูง H
    v.co = (v.co - Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))) * k
o.data.update()

m = bpy.data.materials.new('steel'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (.62, .63, .66, 1); b.inputs['Metallic'].default_value = .85; b.inputs['Roughness'].default_value = .35
o.data.materials.clear(); o.data.materials.append(m)
bpy.ops.object.shade_smooth()

out = os.path.join(ROOT, 'models', 'blender', 'horse-fountain.glb')
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_apply=True, export_draco_mesh_compression_enable=False)
d = [round((hi[i] - lo[i]) * k, 2) for i in range(3)]
print('SIZE', d, 'tris', sum(len(p.vertices) - 2 for p in o.data.polygons), 'KB', os.path.getsize(out) // 1024)

if 'render' in args:   # ภาพตัวอย่าง 2 มุม (หน้า/ข้าง)
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (.5, .55, .6, 1)
    sd = bpy.data.lights.new('s', 'SUN'); sd.energy = 4; s = bpy.data.objects.new('s', sd); sc.collection.objects.link(s); s.rotation_euler = (.8, .2, .6)
    cd = bpy.data.cameras.new('c'); cd.lens = 50; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = sc.render.resolution_y = 600
    for name, loc in (('front', (0, -11, 2.5)), ('side', (11, 0, 2.5))):
        cam.location = loc; cam.rotation_euler = (Vector((0, 0, H / 2)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(HERE, f'horse-fountain-{name}.png'); bpy.ops.render.render(write_still=True)
