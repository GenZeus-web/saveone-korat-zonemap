# รถเข็นขายอาหารแบบไทย + ร่มลายทาง — สร้างด้วย Blender แบบไม่เปิดหน้าจอ
# รัน: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup -P blender\food-cart.py
# ได้: models/blender/food-cart.glb (ใช้ในเว็บ) + blender/food-cart.png (ภาพตัวอย่าง)
import bpy, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def mat(name, rgb, rough=.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m

def srgb(h):  # '#rrggbb' → linear
    c = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c)

M = {k: mat(k, srgb(v[0]), *v[1:]) for k, v in {
    'steel': ('#c9ced6', .25, 1.0), 'glass': ('#cfe8f2', .05, 0.0), 'red': ('#d8322f', .45), 'white': ('#f6f4ef', .5),
    'orange': ('#f08a24', .5), 'tire': ('#26292e', .8), 'wood': ('#b98a5b', .7), 'pot': ('#5a5f66', .3, .9),
    'food': ('#e7a443', .6), 'blue': ('#2d6fd1', .4), 'yellow': ('#f6cf45', .5)}.items()}

def box(name, size, loc, m, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 2
    o.data.materials.append(M[m]); return o

def cyl(name, r, h, loc, m, rot=(0, 0, 0), v=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=v); o = bpy.context.object; o.name = name
    o.data.materials.append(M[m]); bpy.ops.object.shade_smooth(); return o

# ตัวรถเข็น (กว้าง 1.6 ลึก 0.7 สูงเคาน์เตอร์ 0.9 ม.)
box('cabinet', (1.6, .7, .75), (0, 0, .5), 'red')
box('counter', (1.7, .78, .04), (0, 0, .9), 'steel', .005)
box('stripe', (1.62, .72, .08), (0, 0, .78), 'white', 0)
# ตู้กระจกโชว์ของ
box('case_frame', (1.2, .5, .02), (-.1, 0, 1.38), 'steel', .004)
for x in (-.7, .5):
    for y in (-.24, .24):
        box('post', (.02, .02, .46), (x, y, 1.15), 'steel', 0)
g = box('case_glass', (1.18, .48, .44), (-.1, 0, 1.15), 'glass', 0)
gm = g.data.materials[0]; gm.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = .3
for k, v in (('surface_render_method', 'BLENDED'), ('blend_method', 'BLEND')):
    if hasattr(gm, k):
        try: setattr(gm, k, v)
        except Exception: pass
for i in range(5):  # ของในตู้ (ลูกชิ้น/ไก่ทอด)
    cyl(f'food{i}', .06, .05, (-.55 + i * .22, 0, .97), 'food')
# เตา + กระทะ + ถังแก๊ส
box('stove', (.36, .36, .08), (.6, 0, .96), 'pot', .01)
cyl('wok', .17, .06, (.6, 0, 1.03), 'pot')
cyl('gas', .13, .5, (.95, -.15, .25), 'blue')
# ล้อ + มือจับ
for x in (-.6, .6):
    for y in (-.38, .38):
        cyl('wheel', .16, .07, (x, y, .16), 'tire', (math.pi / 2, 0, 0))
cyl('handle', .02, .8, (-.95, 0, 1.0), 'steel', (math.pi / 2, 0, 0), 12)
# ป้ายร้าน
box('sign', (1.3, .03, .26), (-.1, -.26, 1.75), 'yellow', .01)
for x in (-.7, .5):
    cyl('signpole', .015, .36, (x, -.26, 1.56), 'steel', v=8)
# ร่มลายทาง (16 ช่อง สลับแดง/ขาว)
bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=1.25, radius2=0, depth=.45, location=(.2, .1, 2.35), end_fill_type='NOTHING')
u = bpy.context.object; u.name = 'umbrella'; u.data.materials.append(M['red']); u.data.materials.append(M['white'])
for i, f in enumerate(u.data.polygons): f.material_index = i % 2
sol = u.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = .015
cyl('umb_pole', .02, 2.3, (.2, .1, 1.17), 'steel', v=8)

# ส่งออกสำหรับเว็บ (ใช้ modifier จริง · +Y ขึ้นตามมาตรฐาน glTF)
out = os.path.join(ROOT, 'models', 'blender', 'food-cart.glb')
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_apply=True)
print('EXPORT', out, os.path.getsize(out))

# ภาพตัวอย่าง: แสงแดด + ท้องฟ้า + พื้น
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0)); fl = bpy.context.object; fl.data.materials.append(mat('ground', srgb('#9ea2a7'), .9))
bpy.ops.object.light_add(type='SUN', location=(3, -4, 6)); sun = bpy.context.object; sun.data.energy = 4; sun.rotation_euler = (math.radians(50), 0, math.radians(35))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (*srgb('#cfe3f5'), 1); w.node_tree.nodes['Background'].inputs[1].default_value = .9
bpy.ops.object.camera_add(location=(3.6, -4.2, 2.9)); cam = bpy.context.object; sc.camera = cam
tr = cam.constraints.new('TRACK_TO'); bpy.ops.object.empty_add(location=(0, 0, 1.0)); tr.target = bpy.context.object
cam.data.lens = 40
sc.render.resolution_x, sc.render.resolution_y = 900, 700
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    sc.render.engine = 'BLENDER_EEVEE'
sc.render.filepath = os.path.join(HERE, 'food-cart.png')
bpy.ops.render.render(write_still=True)
print('RENDER', sc.render.engine, sc.render.filepath)
