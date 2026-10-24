# ฝังโมเดล + โลโก้เป็น data URI ให้ดับเบิลคลิกเปิดไฟล์ได้เลย (Chrome ไม่ให้ WebGL อ่านไฟล์ในเครื่องตรงๆ)
# ใช้: python build-assets.py  → assets.js (ใช้คู่กับ ผังโซนโคราช.html) + ผังโซนโคราช-ไฟล์เดียว.html (ส่งต่อได้ไฟล์เดียว)
import base64, glob, json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
MIME = {'.glb': 'model/gltf-binary', '.png': 'image/png', '.jpg': 'image/jpeg'}
# models/ar = โมเดล AR ของ ar.html (โหลดผ่านเว็บ ~12 MB) ไม่ฝัง
glbs = [f for f in glob.glob('models/*/*.glb') if os.path.basename(os.path.dirname(f)) != 'ar']
files = sorted(glbs + glob.glob('models/*/Textures/*.png') + glob.glob('logos/*.png') + glob.glob('photos/*.jpg'))
assets = {}
for f in files:
    p = f.replace('\\', '/')
    with open(f, 'rb') as fh:
        assets[p] = 'data:%s;base64,%s' % (MIME[os.path.splitext(f)[1]], base64.b64encode(fh.read()).decode())
js = 'window.ASSETS=' + json.dumps(assets, separators=(',', ':')) + ';\n'
with open('assets.js', 'w', encoding='utf-8') as fh:
    fh.write(js)
html = open('ผังโซนโคราช.html', encoding='utf-8').read()
tag = '<script src="assets.js"></script>'
assert tag in html, 'ไม่เจอ ' + tag
# เนื้อหา (content.js) ฝังด้วย — ไฟล์เดียวจึงเป็นภาพ ณ ตอน build · แก้ผ่านแอดมินแล้วต้อง build ใหม่ถึงจะตาม
ctag = '''<script>document.write('<script src="content.js?t='+Math.floor(Date.now()/6e4)+'"><\\/script>')</script>'''
assert ctag in html, 'ไม่เจอตัวโหลด content.js'
content = open('content.js', encoding='utf-8').read()
with open('ผังโซนโคราช-ไฟล์เดียว.html', 'w', encoding='utf-8', newline='') as fh:
    fh.write(html.replace(tag, '<script>' + js + '</script>').replace(ctag, '<script>' + content.replace('</', '<\\/') + '</script>'))
print(len(assets), 'files', round(len(js) / 1e6, 1), 'MB')
