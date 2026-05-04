from PIL import Image, ImageDraw, ImageFont
import math

# Generate at 3x resolution for crispness, then save
SCALE = 3
W, H = 400 * SCALE, 120 * SCALE

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

PURPLE = '#534AB7'
DARK = '#1a1a1a'

# Icon box
box_size = 72 * SCALE
box_x, box_y = 16 * SCALE, (H - box_size) // 2
radius = 18 * SCALE
draw.rounded_rectangle([box_x, box_y, box_x + box_size, box_y + box_size], radius=radius, fill=PURPLE)

# Draw icon: circle with cross (same as SVG in nav)
cx = box_x + box_size // 2
cy = box_y + box_size // 2
r = 14 * SCALE
lw = 4 * SCALE
arm = 10 * SCALE
draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline='white', width=lw)
draw.line([(cx, cy - r - arm), (cx, cy - r)], fill='white', width=lw)
draw.line([(cx, cy + r), (cx, cy + r + arm)], fill='white', width=lw)
draw.line([(cx - r - arm, cy), (cx - r, cy)], fill='white', width=lw)
draw.line([(cx + r, cy), (cx + r + arm, cy)], fill='white', width=lw)

# Wordmark text
try:
    font = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 62 * SCALE)
except:
    font = ImageFont.load_default()

text = 'Operaite'
text_x = box_x + box_size + 20 * SCALE
bbox = draw.textbbox((0, 0), text, font=font)
text_h = bbox[3] - bbox[1]
text_y = (H - text_h) // 2 - bbox[1]
draw.text((text_x, text_y), text, font=font, fill=DARK)

# Crop to content
content_w = text_x + (bbox[2] - bbox[0]) + 16 * SCALE
img = img.crop([0, 0, content_w, H])

# Downscale to final size (anti-aliased)
final_w = content_w // SCALE
final_h = H // SCALE
img = img.resize((final_w, final_h), Image.LANCZOS)

# Save transparent PNG
img.save('C:/Users/bjusm/operaite/operaite-logo.png', 'PNG')

# Also save on white background JPG
bg = Image.new('RGB', (final_w, final_h), 'white')
bg.paste(img, mask=img.split()[3])
bg.save('C:/Users/bjusm/operaite/operaite-logo-white.jpg', 'JPEG', quality=95)

print(f'Saved operaite-logo.png ({final_w}x{final_h}) — transparent background')
print(f'Saved operaite-logo-white.jpg ({final_w}x{final_h}) — white background')
