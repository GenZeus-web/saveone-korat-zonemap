# ตัวหนังสือไทยบนยอดป้าย → blender/sign-tower-th.png (พื้นโปร่ง) · รันด้วย Python เครื่อง (Blender ไม่มี PIL และวางสระบนไม่ถูก)
# python blender/sign-tower-text.py
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
TXT, COLOR = 'ตลาดเซฟวัน', (78, 224, 106, 255)
f = ImageFont.truetype('C:/Windows/Fonts/leelawdb.ttf', 200)
x0, y0, x1, y1 = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), TXT, font=f)
im = Image.new('RGBA', (x1 - x0 + 40, y1 - y0 + 40), (0, 0, 0, 0))
ImageDraw.Draw(im).text((20 - x0, 20 - y0), TXT, font=f, fill=COLOR)
im.save(os.path.join(HERE, 'sign-tower-th.png')); print(im.size)
