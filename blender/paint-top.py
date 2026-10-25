# ทาสีเรียบให้ "ด้านบน" ของโมเดล (หน้าที่หงายขึ้น + อยู่สูงกว่า X% ของความสูง) — แก้สีผิว Meshy ที่ลงผิดเฉพาะหลังคา
# เช่น สองแถว: หลังคาบนได้ลายน้ำเงินจากตุ๊กตุ๊กข้างๆ ในชุดเดียวกัน (24 ต.ค.)
# รัน: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P blender\paint-top.py -- <เข้า.glb> <ออก.glb> <สูงกว่า 0–1> <สี hex> [render]
# ใช้กับไฟล์ที่ผ่าน meshy-web.py แล้ว (วัตถุเดียว · ฐาน = 0)
import bpy, os, sys
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
a = sys.argv[sys.argv.index('--') + 1:]
src, dst, F, HEX = os.path.join(ROOT, a[0]), os.path.join(ROOT, a[1]), float(a[2]), a[3].lstrip('#')
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=src)
o = [x for x in sc.objects if x.type == 'MESH'][0]
mw = o.matrix_world; pts = [mw @ v.co for v in o.data.vertices]; H = max(p.z for p in pts)
lin = lambda c: (c / 255) ** 2.2
m = bpy.data.materials.new('top'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (*[lin(int(HEX[i:i + 2], 16)) for i in (0, 2, 4)], 1); b.inputs['Roughness'].default_value = .6
o.data.materials.append(m); k = len(o.data.materials) - 1
if 'deblue' in a:   # จุดน้ำเงินที่หลุดมาในรูปผิว (เช่น ประตู) → เปลี่ยนเป็นสีเดียวกัน คงความสว่างเดิม
    import numpy as np
    col = np.array([lin(int(HEX[i:i + 2], 16)) for i in (0, 2, 4)])
    for img in bpy.data.images:
        if not img.size[0]: continue
        px = np.array(img.pixels[:]).reshape(-1, 4); r, g, bl = px[:, 0], px[:, 1], px[:, 2]
        sel = (bl > r + .12) & (bl > g + .04)
        px[sel, :3] = col * (np.maximum(np.maximum(r, g), bl)[sel, None] / col.max())
        img.pixels[:] = px.ravel(); img.update(); print('DEBLUE', img.name, int(sel.sum()), 'px')
n3 = mw.to_3x3()
hit = 0
for p in o.data.polygons:
    if (n3 @ p.normal).normalized().z > .6 and (mw @ p.center).z > H * F: p.material_index = k; hit += 1
bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', use_selection=True, export_image_format='JPEG', export_jpeg_quality=82)
print('PAINTED', hit, 'of', len(o.data.polygons), 'KB', os.path.getsize(dst) // 1024)
if 'render' in a:   # ภาพเฉียงบน → blender/<ชื่อ>-top.png
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (.8, .8, .82, 1)
    sd = bpy.data.lights.new('s', 'SUN'); sd.energy = 3; s = bpy.data.objects.new('s', sd); sc.collection.objects.link(s); s.rotation_euler = (.8, .2, .6)
    cd = bpy.data.cameras.new('c'); cd.lens = 50; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = sc.render.resolution_y = 500; sc.view_settings.view_transform = 'Standard'
    D = H * 4; cam.location = (D * .7, -D * .7, D * .8); cam.rotation_euler = (Vector((0, 0, H / 2)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(HERE, os.path.splitext(os.path.basename(dst))[0] + '-top.png'); bpy.ops.render.render(write_still=True)
