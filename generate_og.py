from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1200, 630

img = Image.new('RGB', (W, H), '#1e1b3a')
draw = ImageDraw.Draw(img)

# Background gradient (simulate with rectangles)
for i in range(H):
    ratio = i / H
    r = int(0x1e + (0x2d - 0x1e) * ratio)
    g = int(0x1b + (0x25 - 0x1b) * ratio)
    b = int(0x3a + (0x80 - 0x3a) * ratio)
    draw.line([(0, i), (W, i)], fill=(r, g, b))

# Decorative orbs
orb_color = (83, 74, 183, 60)
orb_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
orb_draw = ImageDraw.Draw(orb_img)
orb_draw.ellipse([800, -100, 1300, 400], fill=(83, 74, 183, 50))
orb_draw.ellipse([-100, 300, 350, 750], fill=(83, 74, 183, 40))
img = Image.alpha_composite(img.convert('RGBA'), orb_img).convert('RGB')
draw = ImageDraw.Draw(img)

# Fonts
try:
    font_xl = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 88)
    font_lg = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 36)
    font_md = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 28)
    font_sm = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 22)
except:
    font_xl = ImageFont.load_default()
    font_lg = font_xl
    font_md = font_xl
    font_sm = font_xl

# Purple accent bar on left
draw.rectangle([0, 0, 8, H], fill='#534AB7')

# Logo area — circle with "O"
logo_x, logo_y, logo_r = 90, 90, 42
draw.ellipse([logo_x - logo_r, logo_y - logo_r, logo_x + logo_r, logo_y + logo_r], fill='#534AB7')
bbox = draw.textbbox((0, 0), 'O', font=font_lg)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text((logo_x - tw // 2, logo_y - th // 2 - 2), 'O', font=font_lg, fill='white')

# Brand name
draw.text((148, 58), 'Operaite', font=font_xl, fill='white')

# Tagline
draw.text((148, 158), 'AI-Powered Tools for Small Business Owners', font=font_md, fill='#c4bfe8')

# Divider line
draw.rectangle([148, 205, 780, 208], fill='#534AB7')

# Feature pills
features = [
    ('📊', 'Accounting'),
    ('⭐', 'Review Manager'),
    ('📄', 'Invoicing'),
    ('📢', 'Marketing'),
    ('🤖', 'AI Writing'),
    ('📱', 'Social Media'),
]

pill_x = 148
pill_y = 235
pill_h = 46
pill_gap = 14
row_gap = 16

for i, (icon, label) in enumerate(features):
    col = i % 3
    row = i // 3
    text = f'{icon}  {label}'
    bbox = draw.textbbox((0, 0), text, font=font_sm)
    tw = bbox[2] - bbox[0]
    pw = tw + 32
    x = pill_x + col * (pw + pill_gap + 30)
    y = pill_y + row * (pill_h + row_gap)
    # pill bg
    draw.rounded_rectangle([x, y, x + pw + 30, y + pill_h], radius=23, fill='#2d2580')
    draw.rounded_rectangle([x, y, x + pw + 30, y + pill_h], radius=23, outline='#534AB7', width=1)
    draw.text((x + 16, y + 10), text, font=font_sm, fill='#e8e5ff')

# Bottom tagline / CTA
draw.text((148, H - 90), 'operaite.net', font=font_lg, fill='#534AB7')
draw.text((148, H - 50), 'Start your free trial · $29/month', font=font_sm, fill='#9b96cc')

# Right side illustration — dashboard mockup (simplified)
mock_x = 820
mock_y = 60
mock_w = 340
mock_h = 490

draw.rounded_rectangle([mock_x, mock_y, mock_x + mock_w, mock_y + mock_h], radius=16, fill='#2a2650', outline='#534AB7', width=2)
# header bar
draw.rounded_rectangle([mock_x, mock_y, mock_x + mock_w, mock_y + 44], radius=16, fill='#534AB7')
draw.text((mock_x + 16, mock_y + 10), '⬛ Operaite Dashboard', font=font_sm, fill='white')

# metric cards
card_colors = ['#534AB7', '#10B981', '#F59E0B', '#EF4444']
labels = ['Revenue', 'Clients', 'Invoices', 'Reviews']
vals = ['$12,400', '38', '14', '4.9★']
for j in range(4):
    cx = mock_x + 16 + (j % 2) * 158
    cy = mock_y + 62 + (j // 2) * 90
    draw.rounded_rectangle([cx, cy, cx + 145, cy + 72], radius=10, fill='#1e1b3a', outline=card_colors[j], width=2)
    draw.text((cx + 12, cy + 10), labels[j], font=font_sm, fill='#9b96cc')
    draw.text((cx + 12, cy + 36), vals[j], font=font_lg, fill='white')

# content rows
for k in range(4):
    ry = mock_y + 254 + k * 52
    draw.rounded_rectangle([mock_x + 16, ry, mock_x + mock_w - 16, ry + 38], radius=8, fill='#1e1b3a', outline='#3d3870', width=1)
    draw.rectangle([mock_x + 28, ry + 12, mock_x + 50, ry + 26], fill='#534AB7')
    draw.rectangle([mock_x + 60, ry + 12, mock_x + 160 - k * 20, ry + 20], fill='#3d3870')

img.save('C:/Users/bjusm/operaite/og-image.png', 'PNG', optimize=True)
print('og-image.png saved successfully')
