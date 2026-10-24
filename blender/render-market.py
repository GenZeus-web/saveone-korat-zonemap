# เรนเดอร์ภาพนิ่งทั้งตลาดจากฉากที่ส่งออกจากเว็บ (blender/export-scene.js)
# รัน: blender.exe -b --factory-startup -P blender\render-market.py -- market [กว้าง] [มุม]
#   มุม: top = ตรงลงแบบผังเว็บ · tilt = เอียงมองจากทิศใต้
import bpy, json, math, os, sys
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
name = args[0] if args else 'market'
W = int(args[1]) if len(args) > 1 else 3840
view = args[2] if len(args) > 2 else 'top'
H = round(W / math.sqrt(2))  # สัดส่วนกระดาษ A (พิมพ์โปสเตอร์ได้)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
info = json.load(open(os.path.join(HERE, name + '.json')))
bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, name + '.glb'))
B = lambda v: Vector((v[0], -v[2], v[1]))  # three (y ขึ้น) → Blender (z ขึ้น)

# กล้อง: เล็งจุดเดียวกับเว็บ · ทิศเหนืออยู่บน
target = B(info['camTarget']); pos = B(info['camPos'])
if view == 'tilt':
    d = (pos - target).length * 1.02; a = math.radians(38)
    pos = target + Vector((0, -math.sin(a) * d, math.cos(a) * d)); target = target + Vector((0, -110, 0)); pos = pos + Vector((0, -110, 0))
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
f = (target - pos).normalized(); up = Vector((0, 1, 0))
r = f.cross(up).normalized(); u = r.cross(f)
cam.matrix_world = Matrix((r, u, -f)).transposed().to_4x4() @ Matrix.Identity(4); cam.location = pos
cam_d.sensor_fit = 'VERTICAL'; cam_d.angle_y = math.radians(info['fov'] * (1.0 if view == 'top' else .92)); cam_d.clip_start = 5; cam_d.clip_end = 20000

# แดดเที่ยง (ทิศเดียวกับเว็บ) + ฟ้า
sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.energy = 3.2; sun_d.angle = math.radians(1.5); sun_d.color = (1, .96, .9)
sun = bpy.data.objects.new('sun', sun_d); sc.collection.objects.link(sun)
sun.rotation_euler = B(info['sunDir']).to_track_quat('Z', 'Y').to_euler()
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (.62, .74, .92, 1); bg.inputs[1].default_value = .45

sc.render.engine = 'BLENDER_EEVEE'
ee = sc.eevee
for k, v in (('use_raytracing', True), ('use_shadows', True), ('shadow_resolution_scale', 1.0), ('taa_render_samples', 32), ('use_fast_gi', True)):
    if hasattr(ee, k):
        try: setattr(ee, k, v)
        except Exception as e: print('skip', k, e)
sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = .15
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.image_settings.file_format = 'PNG'
if 'diag' in args:  # ตรวจแดด: ปิดแสงฟ้า เหลือแดดอย่างเดียว
    bg.inputs[1].default_value = 0
    print('SUN -Z', sun.matrix_world.to_3x3() @ Vector((0, 0, -1)), 'shadow', sun_d.use_shadow)
    import collections
    print('METHOD', collections.Counter(getattr(m, 'surface_render_method', '?') for m in bpy.data.materials))
sc.render.filepath = os.path.join(HERE, '%s-%s-%d%s.png' % (name, view, W, '-diag' if 'diag' in args else ''))
bpy.ops.render.render(write_still=True)
print('RENDER', sc.render.filepath)
