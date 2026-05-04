from PIL import Image, ImageDraw, ImageFont
import math

W, H = 400, 400
BG = '#f4f3f8'
PURPLE = '#534AB7'
DARK = '#1e1b3a'
WHITE = '#ffffff'

def get_fonts():
    try:
        bold = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 72)
        bold_lg = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 120)
        bold_sm = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 48)
    except:
        bold = ImageFont.load_default()
        bold_lg = bold
        bold_sm = bold
    return bold, bold_lg, bold_sm

# ── Option 1: O with lightning bolt ──────────────────────────────────────────
def logo1():
    img = Image.new('RGBA', (W, H), BG)
    draw = ImageDraw.Draw(img)

    cx, cy, r = W//2, H//2, 130
    # Outer circle fill
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=PURPLE)
    # Inner circle cutout (ring)
    ir = 90
    draw.ellipse([cx-ir, cy-ir, cx+ir, cy+ir], fill=BG)
    # Lightning bolt polygon (white)
    bolt = [
        (cx+18, cy-100),   # top right
        (cx-10, cy-10),    # mid left notch
        (cx+22, cy-10),    # mid right notch
        (cx-18, cy+100),   # bottom left
        (cx+8,  cy+15),    # lower mid right
        (cx-18, cy+15),    # lower mid left
    ]
    draw.polygon(bolt, fill=WHITE)
    # Mask the bolt outside the ring area so it sits inside cleanly
    # Redraw the outer ring border clean
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=PURPLE, width=3)

    img.save('C:/Users/bjusm/operaite/logo_option1.png')
    print('Logo 1 saved')

# ── Option 2: Rounded square dashboard grid ───────────────────────────────────
def logo2():
    img = Image.new('RGBA', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Rounded square
    pad = 70
    draw.rounded_rectangle([pad, pad, W-pad, H-pad], radius=48, fill=DARK)

    # 3x2 grid of rounded rects (dashboard tiles)
    tile_w, tile_h = 68, 52
    gap = 16
    start_x = W//2 - (3*tile_w + 2*gap)//2
    start_y = H//2 - (2*tile_h + gap)//2

    colors = [PURPLE, '#7c75d4', PURPLE, '#7c75d4', PURPLE, '#7c75d4']
    for row in range(2):
        for col in range(3):
            x = start_x + col * (tile_w + gap)
            y = start_y + row * (tile_h + gap)
            c = colors[row * 3 + col]
            draw.rounded_rectangle([x, y, x+tile_w, y+tile_h], radius=10, fill=c)
            # Small white bar inside each tile
            draw.rounded_rectangle([x+10, y+tile_h-16, x+tile_w-10, y+tile_h-8], radius=3, fill=WHITE)

    img.save('C:/Users/bjusm/operaite/logo_option2.png')
    print('Logo 2 saved')

# ── Option 3: Oi monogram with sparkle ────────────────────────────────────────
def logo3():
    img = Image.new('RGBA', (W, H), BG)
    draw = ImageDraw.Draw(img)
    _, bold_lg, _ = get_fonts()

    try:
        font_o = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 200)
        font_i = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 200)
    except:
        font_o = ImageFont.load_default()
        font_i = font_o

    # Draw "O"
    draw.text((52, 70), 'O', font=font_o, fill=PURPLE)
    # Draw "i" without dot (we'll add custom dot)
    draw.text((222, 70), 'i', font=font_i, fill=DARK)
    # Cover the dot of 'i' with bg color
    draw.ellipse([252, 72, 292, 112], fill=BG)

    # Sparkle / 4-point star at top of i
    sx, sy = 272, 62
    star_size = 24
    # 4-point star
    points = []
    for k in range(8):
        angle = math.radians(k * 45 - 90)
        radius = star_size if k % 2 == 0 else star_size * 0.4
        points.append((sx + radius * math.cos(angle), sy + radius * math.sin(angle)))
    draw.polygon(points, fill=PURPLE)

    img.save('C:/Users/bjusm/operaite/logo_option3.png')
    print('Logo 3 saved')

# ── Option 4: Split O with spark gap ──────────────────────────────────────────
def logo4():
    img = Image.new('RGBA', (W, H), BG)
    draw = ImageDraw.Draw(img)

    cx, cy = W//2, H//2
    r_outer = 130
    r_inner = 78
    line_width = r_outer - r_inner  # = 52

    # Draw arc ring: full circle minus a gap at top-right
    # We'll draw a thick arc using a series of line segments
    gap_start = -55   # degrees (top right)
    gap_end   = -10

    # Draw the ring as filled annulus then cut gap with bg
    draw.ellipse([cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer], fill=PURPLE)
    draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], fill=BG)

    # Cut the gap (top-right sector) by drawing a pie slice in BG color
    gap_s = -70
    gap_e = -5
    draw.pieslice([cx-r_outer-2, cy-r_outer-2, cx+r_outer+2, cy+r_outer+2],
                  start=gap_s, end=gap_e, fill=BG)

    # Redraw inner circle clean
    draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], fill=BG)

    # Spark at the gap — 3 lines radiating out
    spark_cx = cx + int(r_outer * math.cos(math.radians(-37)))
    spark_cy = cy + int(r_outer * math.sin(math.radians(-37)))

    for angle_offset in [-30, 0, 30]:
        angle = math.radians(-37 + angle_offset)
        x1 = spark_cx + int(18 * math.cos(angle))
        y1 = spark_cy + int(18 * math.sin(angle))
        x2 = spark_cx + int(42 * math.cos(angle))
        y2 = spark_cy + int(42 * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=PURPLE, width=5)

    # Small dot at center of spark
    draw.ellipse([spark_cx-7, spark_cy-7, spark_cx+7, spark_cy+7], fill=PURPLE)

    img.save('C:/Users/bjusm/operaite/logo_option4.png')
    print('Logo 4 saved')

logo1()
logo2()
logo3()
logo4()
print('All 4 logos generated.')
