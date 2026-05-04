from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 1600, 1200
SIDEBAR_W = 230
TOPBAR_H = 0
PURPLE = (83, 74, 183)
DARK = (30, 27, 58)
LIGHT_BG = (244, 243, 248)
WHITE = (255, 255, 255)
BORDER = (220, 216, 240)
TEXT_DARK = (26, 26, 26)
TEXT_MID = (100, 100, 120)
TEXT_LIGHT = (160, 155, 190)
GREEN = (16, 185, 129)
AMBER = (245, 158, 11)
RED = (239, 68, 68)
BLUE = (59, 130, 246)

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ''
    for word in words:
        test = (current + ' ' + word).strip()
        w = draw.textbbox((0,0), test, font=font)[2]
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def fonts():
    try:
        return {
            'bold':  ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 28),
            'bold_lg': ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 40),
            'bold_xl': ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 56),
            'bold_sm': ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 22),
            'bold_xs': ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 18),
            'reg':   ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 24),
            'reg_sm': ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 20),
            'reg_xs': ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 17),
        }
    except:
        f = ImageFont.load_default()
        return {k: f for k in ['bold','bold_lg','bold_xl','bold_sm','bold_xs','reg','reg_sm','reg_xs']}

F = fonts()

def new_img():
    img = Image.new('RGB', (W, H), LIGHT_BG)
    draw = ImageDraw.Draw(img)
    return img, draw

def draw_sidebar(draw, active_label):
    draw.rectangle([0, 0, SIDEBAR_W, H], fill=DARK)
    # Brand
    box_x, box_y = 20, 22
    draw.rounded_rectangle([box_x, box_y, box_x+40, box_y+40], radius=10, fill=PURPLE)
    cx, cy = box_x+20, box_y+20
    draw.ellipse([cx-8, cy-8, cx+8, cy+8], outline=WHITE, width=2)
    for dx, dy in [(0,-14),(0,14),(-14,0),(14,0)]:
        draw.line([(cx+dx//2, cy+dy//2),(cx+dx,cy+dy)], fill=WHITE, width=2)
    draw.text((box_x+50, box_y+4), 'Operaite', font=F['bold'], fill=WHITE)

    nav_items = [
        ('📊', 'Dashboard'),
        ('⭐', 'AI Reviews'),
        ('📝', 'Proposals'),
        ('📄', 'Invoicing'),
        ('💰', 'Accounting'),
        ('📢', 'Marketing'),
        ('📱', 'Social Media'),
        ('✉️', 'Email Templates'),
        ('👤', 'Bio Writer'),
        ('💼', 'Job Postings'),
        ('❓', 'FAQ Generator'),
        ('😤', 'Complaints'),
        ('🏢', 'Business Profile'),
    ]
    y = 100
    for icon, label in nav_items:
        is_active = label == active_label
        if is_active:
            draw.rounded_rectangle([10, y-4, SIDEBAR_W-10, y+34], radius=8, fill=(60, 54, 120))
            draw.rectangle([3, y-4, 6, y+34], fill=(*PURPLE, 255))
        color = WHITE if is_active else (160, 155, 195)
        draw.text((24, y), icon, font=F['reg_sm'], fill=color)
        draw.text((56, y+1), label, font=F['bold_xs'] if is_active else F['reg_sm'], fill=color)
        y += 46

def draw_hero(draw, img, title, subtitle, color1, color2, icon):
    x0, y0 = SIDEBAR_W, 0
    x1, y1 = W, 160
    # Gradient
    for i in range(x1 - x0):
        ratio = i / (x1 - x0)
        r = int(color1[0] + (color2[0]-color1[0])*ratio)
        g = int(color1[1] + (color2[1]-color1[1])*ratio)
        b = int(color1[2] + (color2[2]-color1[2])*ratio)
        draw.line([(x0+i, y0), (x0+i, y1)], fill=(r,g,b))
    # Orb
    orb = Image.new('RGBA', (W, H), (0,0,0,0))
    od = ImageDraw.Draw(orb)
    od.ellipse([W-200, -80, W+100, 220], fill=(*color1, 30))
    img.paste(Image.alpha_composite(Image.new('RGBA', (W,H),(0,0,0,0)), orb).convert('RGB'), mask=orb.split()[3])
    draw = ImageDraw.Draw(img)
    draw.text((x0+36, 28), icon, font=F['bold_xl'], fill=(255,255,255,200))
    draw.text((x0+110, 22), title, font=F['bold_xl'], fill=WHITE)
    draw.text((x0+112, 82), subtitle, font=F['reg'], fill=(220,215,255))
    return draw

def card(draw, x, y, w, h, title, value, sub, accent):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=14, fill=WHITE, outline=BORDER, width=2)
    draw.rounded_rectangle([x, y, x+w, y+5], radius=14, fill=accent)
    draw.rectangle([x, y+2, x+w, y+5], fill=accent)
    draw.text((x+20, y+22), title, font=F['reg_xs'], fill=TEXT_MID)
    draw.text((x+20, y+50), value, font=F['bold_lg'], fill=TEXT_DARK)
    draw.text((x+20, y+100), sub, font=F['reg_xs'], fill=TEXT_MID)

def pill(draw, x, y, text, bg, fg):
    bbox = draw.textbbox((0,0), text, font=F['reg_xs'])
    tw = bbox[2]-bbox[0]
    draw.rounded_rectangle([x, y, x+tw+20, y+26], radius=13, fill=bg)
    draw.text((x+10, y+4), text, font=F['reg_xs'], fill=fg)
    return tw+28

def row_line(draw, x, y, w):
    draw.line([(x, y), (x+w, y)], fill=BORDER, width=1)

# ─── SCREEN 1: Dashboard ───────────────────────────────────────────────────────
def screen_dashboard():
    img, draw = new_img()
    draw_sidebar(draw, 'Dashboard')
    draw = draw_hero(draw, img, 'Dashboard', 'Good morning — here\'s your business at a glance', PURPLE, (45, 37, 128), '📊')

    mx = SIDEBAR_W + 30
    my = 185
    cw, ch = 295, 130

    card(draw, mx,      my, cw, ch, 'Total Revenue',   '$12,400', '▲ 18% vs last month', GREEN)
    card(draw, mx+325,  my, cw, ch, 'Active Clients',  '38',       '4 new this month', BLUE)
    card(draw, mx+650,  my, cw, ch, 'Open Invoices',   '6',        '$4,200 outstanding', AMBER)
    card(draw, mx+975,  my, cw, ch, 'Avg Review',      '4.8 ★',    '24 reviews total', (*PURPLE,))

    # Recent transactions
    ty = my + 160
    draw.rounded_rectangle([mx, ty, W-30, ty+360], radius=14, fill=WHITE, outline=BORDER, width=2)
    draw.text((mx+24, ty+20), 'Recent Transactions', font=F['bold'], fill=TEXT_DARK)
    draw.text((W-160, ty+22), 'View all →', font=F['reg_xs'], fill=PURPLE)

    headers = ['Description', 'Client', 'Date', 'Amount', 'Status']
    hx = [mx+24, mx+350, mx+640, mx+830, mx+1020]
    row_line(draw, mx+16, ty+60, W-30-mx-32)
    for i, h in enumerate(headers):
        draw.text((hx[i], ty+68), h, font=F['bold_xs'], fill=TEXT_MID)
    row_line(draw, mx+16, ty+95, W-30-mx-32)

    rows = [
        ('Web Design Package',    'Johnson Co.',   'Apr 14', '$2,400', 'Paid',    GREEN),
        ('Monthly Retainer',      'Acme Corp',     'Apr 12', '$1,800', 'Pending', AMBER),
        ('Logo Package',          'Rivera LLC',    'Apr 10', '$850',   'Paid',    GREEN),
        ('SEO Audit',             'Bright Ideas',  'Apr 8',  '$600',   'Paid',    GREEN),
        ('Brand Guidelines',      'NovaTech',      'Apr 5',  '$1,200', 'Overdue', RED),
    ]
    for i, (desc, client, date, amt, status, scol) in enumerate(rows):
        ry = ty + 110 + i * 48
        bg = (249, 248, 253) if i % 2 == 0 else WHITE
        draw.rectangle([mx+1, ry-6, W-31, ry+34], fill=bg)
        draw.text((hx[0], ry), desc,   font=F['reg_sm'], fill=TEXT_DARK)
        draw.text((hx[1], ry), client, font=F['reg_sm'], fill=TEXT_MID)
        draw.text((hx[2], ry), date,   font=F['reg_sm'], fill=TEXT_MID)
        draw.text((hx[3], ry), amt,    font=F['bold_sm'], fill=TEXT_DARK)
        pill(draw, hx[4], ry+1, status, (*scol, 30), scol)

    img.save('C:/Users/bjusm/operaite/screenshot_dashboard.png')
    print('Dashboard saved')

# ─── SCREEN 2: AI Review Manager ───────────────────────────────────────────────
def screen_reviews():
    img, draw = new_img()
    draw_sidebar(draw, 'AI Reviews')
    draw = draw_hero(draw, img, 'AI Review Manager', 'Paste a review and get a professional response instantly', (180, 120, 20), (140, 80, 10), '⭐')

    mx = SIDEBAR_W + 30
    my = 185

    # Left panel — input
    lw = 580
    draw.rounded_rectangle([mx, my, mx+lw, my+500], radius=14, fill=WHITE, outline=BORDER, width=2)
    draw.text((mx+24, my+22), 'Customer Review', font=F['bold'], fill=TEXT_DARK)
    draw.text((mx+24, my+58), 'Paste the review text below', font=F['reg_xs'], fill=TEXT_MID)

    # Review text box
    review_text = [
        '"The team at this company was absolutely outstanding.',
        'From start to finish, they were professional,',
        'responsive, and delivered exactly what they promised.',
        'The quality of work exceeded my expectations and I',
        'could not be happier with the results. Will definitely',
        'be recommending them to everyone I know!"',
        '',
        '— Posted on Google  ★★★★★',
    ]
    draw.rounded_rectangle([mx+20, my+90, mx+lw-20, my+310], radius=10, fill=LIGHT_BG, outline=BORDER, width=1)
    for i, line in enumerate(review_text):
        col = TEXT_MID if line.startswith('—') else TEXT_DARK
        draw.text((mx+36, my+106+i*26), line, font=F['reg_xs'], fill=col)

    draw.text((mx+24, my+330), 'Tone', font=F['bold_xs'], fill=TEXT_MID)
    for i, tone in enumerate(['Professional', 'Friendly', 'Grateful']):
        bx = mx+24+i*160
        active = i == 1
        bg = PURPLE if active else (240,239,252)
        fg = WHITE if active else TEXT_MID
        draw.rounded_rectangle([bx, my+354, bx+140, my+386], radius=20, fill=bg)
        draw.text((bx+20, my+360), tone, font=F['reg_xs'], fill=fg)

    draw.rounded_rectangle([mx+20, my+410, mx+lw-20, my+462], radius=10, fill=PURPLE)
    draw.text((mx+lw//2-90, my+424), '✨  Generate AI Response', font=F['bold_sm'], fill=WHITE)

    # Right panel — output
    rx = mx + lw + 30
    rw = W - rx - 30
    draw.rounded_rectangle([rx, my, rx+rw, my+500], radius=14, fill=WHITE, outline=BORDER, width=2)
    draw.text((rx+24, my+22), 'AI Response', font=F['bold'], fill=TEXT_DARK)
    pill(draw, rx+200, my+24, 'Ready to copy', (220,255,235), GREEN)

    response_lines = [
        'Thank you so much for your incredibly kind words!',
        'It truly means the world to our entire team to hear',
        'such wonderful feedback. We put a great deal of care',
        'into every project we take on, and knowing that it',
        'showed in your experience is so rewarding.',
        '',
        'We\'re so glad we could deliver results that exceeded',
        'your expectations — that\'s always our goal! Thank you',
        'for the referral as well; word-of-mouth means',
        'everything to a small business like ours.',
        '',
        'We look forward to working with you again!',
    ]
    draw.rounded_rectangle([rx+20, my+70, rx+rw-20, my+400], radius=10, fill=LIGHT_BG, outline=BORDER, width=1)
    for i, line in enumerate(response_lines):
        draw.text((rx+36, my+86+i*26), line, font=F['reg_xs'], fill=TEXT_DARK)

    draw.rounded_rectangle([rx+20, my+420, rx+rw//2-10, my+472], radius=10, fill=(220,255,235))
    draw.text((rx+44, my+434), '📋  Copy Response', font=F['bold_xs'], fill=GREEN)
    draw.rounded_rectangle([rx+rw//2+10, my+420, rx+rw-20, my+472], radius=10, fill=LIGHT_BG, outline=BORDER, width=1)
    draw.text((rx+rw//2+34, my+434), '🔄  Regenerate', font=F['bold_xs'], fill=TEXT_MID)

    img.save('C:/Users/bjusm/operaite/screenshot_reviews.png')
    print('Reviews saved')

# ─── SCREEN 3: Invoicing ───────────────────────────────────────────────────────
def screen_invoicing():
    img, draw = new_img()
    draw_sidebar(draw, 'Invoicing')
    draw = draw_hero(draw, img, 'Invoicing', 'Create professional invoices in under a minute', (37, 99, 235), (29, 78, 216), '📄')

    mx = SIDEBAR_W + 30
    my = 185

    # Form side
    fw = 540
    draw.rounded_rectangle([mx, my, mx+fw, my+680], radius=14, fill=WHITE, outline=BORDER, width=2)
    draw.text((mx+24, my+22), 'Invoice Details', font=F['bold'], fill=TEXT_DARK)

    fields = [
        ('Client Name', 'Johnson Co.'),
        ('Client Email', 'contact@johnsonce.com'),
        ('Invoice #', '1042'),
        ('Due Date', 'May 1, 2026'),
    ]
    for i, (label, val) in enumerate(fields):
        fy = my + 70 + i * 80
        draw.text((mx+24, fy), label, font=F['reg_xs'], fill=TEXT_MID)
        draw.rounded_rectangle([mx+20, fy+22, mx+fw-20, fy+58], radius=8, fill=LIGHT_BG, outline=BORDER, width=1)
        draw.text((mx+36, fy+32), val, font=F['reg_sm'], fill=TEXT_DARK)

    draw.text((mx+24, my+400), 'Line Items', font=F['bold_sm'], fill=TEXT_DARK)
    items = [
        ('Web Design — 10 hrs', '$150/hr', '$1,500'),
        ('SEO Setup', 'flat', '$500'),
        ('Hosting (annual)', 'flat', '$200'),
    ]
    for i, (desc, rate, total) in enumerate(items):
        iy = my + 432 + i * 56
        draw.rounded_rectangle([mx+20, iy, mx+fw-20, iy+44], radius=8, fill=LIGHT_BG, outline=BORDER, width=1)
        draw.text((mx+36, iy+11), desc, font=F['reg_xs'], fill=TEXT_DARK)
        draw.text((mx+fw-160, iy+11), rate,  font=F['reg_xs'], fill=TEXT_MID)
        draw.text((mx+fw-80,  iy+11), total, font=F['bold_xs'], fill=TEXT_DARK)

    draw.rounded_rectangle([mx+20, my+612, mx+fw-20, my+644], radius=8, fill=(235,233,255), outline=BORDER, width=1)
    draw.text((mx+36, my+622), '+ Add line item', font=F['reg_xs'], fill=PURPLE)

    # Preview side
    px = mx + fw + 30
    pw = W - px - 30
    draw.rounded_rectangle([px, my, px+pw, my+680], radius=14, fill=WHITE, outline=BORDER, width=2)

    # Invoice header
    draw.rounded_rectangle([px, my, px+pw, my+90], radius=14, fill=DARK)
    draw.rectangle([px, my+70, px+pw, my+90], fill=DARK)
    draw.text((px+24, my+18), 'INVOICE', font=F['bold_lg'], fill=WHITE)
    draw.text((px+24, my+62), '#1042', font=F['reg_sm'], fill=TEXT_LIGHT)
    draw.text((px+pw-180, my+18), 'Due: May 1, 2026', font=F['reg_xs'], fill=TEXT_LIGHT)

    draw.text((px+24, my+110), 'Bill To:', font=F['bold_xs'], fill=TEXT_MID)
    draw.text((px+24, my+134), 'Johnson Co.', font=F['bold_sm'], fill=TEXT_DARK)
    draw.text((px+24, my+160), 'contact@johnsonce.com', font=F['reg_xs'], fill=TEXT_MID)

    row_line(draw, px+16, my+196, pw-32)
    draw.text((px+24,      my+208), 'Description',  font=F['bold_xs'], fill=TEXT_MID)
    draw.text((px+pw-200,  my+208), 'Qty/Rate',     font=F['bold_xs'], fill=TEXT_MID)
    draw.text((px+pw-80,   my+208), 'Total',        font=F['bold_xs'], fill=TEXT_MID)
    row_line(draw, px+16, my+232, pw-32)

    for i, (desc, rate, total) in enumerate(items):
        ry = my + 248 + i * 44
        draw.text((px+24,     ry), desc,  font=F['reg_xs'], fill=TEXT_DARK)
        draw.text((px+pw-200, ry), rate,  font=F['reg_xs'], fill=TEXT_MID)
        draw.text((px+pw-90,  ry), total, font=F['bold_xs'], fill=TEXT_DARK)

    row_line(draw, px+16, my+388, pw-32)
    draw.text((px+pw-200, my+400), 'Subtotal', font=F['reg_xs'], fill=TEXT_MID)
    draw.text((px+pw-90,  my+400), '$2,200', font=F['reg_xs'], fill=TEXT_DARK)
    draw.text((px+pw-200, my+426), 'Tax (8%)', font=F['reg_xs'], fill=TEXT_MID)
    draw.text((px+pw-90,  my+426), '$176', font=F['reg_xs'], fill=TEXT_DARK)
    row_line(draw, px+16, my+452, pw-32)
    draw.text((px+pw-200, my+464), 'Total Due', font=F['bold_sm'], fill=TEXT_DARK)
    draw.text((px+pw-110, my+460), '$2,376', font=F['bold_lg'], fill=PURPLE)

    draw.rounded_rectangle([px+20, my+620, px+pw//2-10, my+662], radius=10, fill=PURPLE)
    draw.text((px+44, my+634), '⬇  Download PDF', font=F['bold_xs'], fill=WHITE)
    draw.rounded_rectangle([px+pw//2+10, my+620, px+pw-20, my+662], radius=10, fill=LIGHT_BG, outline=BORDER, width=1)
    draw.text((px+pw//2+34, my+634), '✉  Send Invoice', font=F['bold_xs'], fill=TEXT_DARK)

    img.save('C:/Users/bjusm/operaite/screenshot_invoicing.png')
    print('Invoicing saved')

# ─── SCREEN 4: Social Media AI ─────────────────────────────────────────────────
def screen_social():
    img, draw = new_img()
    draw_sidebar(draw, 'Social Media')
    draw = draw_hero(draw, img, 'Social Media AI', 'Generate on-brand content for every platform in seconds', (124, 58, 237), (109, 40, 217), '📱')

    mx = SIDEBAR_W + 30
    my = 185

    # Input panel
    lw = 520
    draw.rounded_rectangle([mx, my, mx+lw, my+600], radius=14, fill=WHITE, outline=BORDER, width=2)
    draw.text((mx+24, my+22), 'Content Brief', font=F['bold'], fill=TEXT_DARK)

    draw.text((mx+24, my+68), 'Platform', font=F['reg_xs'], fill=TEXT_MID)
    platforms = ['Instagram', 'LinkedIn', 'Facebook', 'Twitter/X']
    for i, p in enumerate(platforms):
        bx = mx+24+(i%2)*230
        by = my+92+(i//2)*50
        active = i == 0
        bg = PURPLE if active else (240,239,252)
        fg = WHITE if active else TEXT_MID
        draw.rounded_rectangle([bx, by, bx+210, by+36], radius=18, fill=bg)
        draw.text((bx+20, by+8), p, font=F['reg_xs'], fill=fg)

    draw.text((mx+24, my+212), 'What do you want to post about?', font=F['reg_xs'], fill=TEXT_MID)
    draw.rounded_rectangle([mx+20, my+236, mx+lw-20, my+330], radius=8, fill=LIGHT_BG, outline=BORDER, width=1)
    draw.text((mx+36, my+252), 'We just launched our new residential cleaning', font=F['reg_xs'], fill=TEXT_DARK)
    draw.text((mx+36, my+276), 'service! Want to announce it and drive bookings.', font=F['reg_xs'], fill=TEXT_DARK)

    draw.text((mx+24, my+350), 'Tone', font=F['reg_xs'], fill=TEXT_MID)
    for i, tone in enumerate(['Excited', 'Professional', 'Casual']):
        bx = mx+24+i*155
        active = i == 0
        bg = PURPLE if active else (240,239,252)
        fg = WHITE if active else TEXT_MID
        draw.rounded_rectangle([bx, my+374, bx+135, my+406], radius=18, fill=bg)
        draw.text((bx+16, my+380), tone, font=F['reg_xs'], fill=fg)

    draw.text((mx+24, my+428), 'Include hashtags?', font=F['reg_xs'], fill=TEXT_MID)
    draw.rounded_rectangle([mx+24, my+452, mx+64, my+480], radius=6, fill=PURPLE)
    draw.text((mx+34, my+458), '✓', font=F['reg_xs'], fill=WHITE)
    draw.text((mx+76, my+458), 'Yes', font=F['reg_xs'], fill=TEXT_DARK)

    draw.rounded_rectangle([mx+20, my+530, mx+lw-20, my+578], radius=10, fill=PURPLE)
    draw.text((mx+lw//2-80, my+546), '✨  Generate Post', font=F['bold_sm'], fill=WHITE)

    # Output panel
    rx = mx + lw + 30
    rw = W - rx - 30
    draw.rounded_rectangle([rx, my, rx+rw, my+600], radius=14, fill=WHITE, outline=BORDER, width=2)
    draw.text((rx+24, my+22), 'Generated Post', font=F['bold'], fill=TEXT_DARK)
    pill(draw, rx+260, my+24, '📋 Copy', (235,233,255), PURPLE)

    # Phone mockup
    ph_x, ph_y = rx + rw//2 - 120, my + 70
    ph_w, ph_h = 240, 420
    draw.rounded_rectangle([ph_x-3, ph_y-3, ph_x+ph_w+3, ph_y+ph_h+3], radius=34, fill=(220,216,240))
    draw.rounded_rectangle([ph_x, ph_y, ph_x+ph_w, ph_y+ph_h], radius=32, fill=WHITE)
    # Instagram header
    draw.rounded_rectangle([ph_x, ph_y, ph_x+ph_w, ph_y+50], radius=32, fill=(250,249,255))
    draw.rectangle([ph_x, ph_y+30, ph_x+ph_w, ph_y+50], fill=(250,249,255))
    draw.ellipse([ph_x+12, ph_y+8, ph_x+44, ph_y+40], fill=(*PURPLE,255))
    draw.text((ph_x+52, ph_y+14), 'yourbusiness', font=F['reg_xs'], fill=TEXT_DARK)
    draw.text((ph_x+ph_w-60, ph_y+14), '•••', font=F['bold'], fill=TEXT_MID)
    # Post image placeholder
    draw.rectangle([ph_x, ph_y+50, ph_x+ph_w, ph_y+200], fill=(*PURPLE, 255))
    draw.text((ph_x+ph_w//2-40, ph_y+108), '🏠✨', font=F['bold_lg'], fill=WHITE)
    # Caption
    cap_lines = [
        '🚨 Big news — we now offer',
        'residential cleaning! 🏠✨',
        '',
        'Deep clean or regular upkeep,',
        "we've got you covered.",
        'Book your first session today!',
        '',
        '#SmallBusiness #Cleaning',
        '#HomeClean #BookNow',
    ]
    for i, line in enumerate(cap_lines):
        col = PURPLE if line.startswith('#') else TEXT_DARK
        draw.text((ph_x+12, ph_y+210+i*22), line, font=F['reg_xs'], fill=col)

    img.save('C:/Users/bjusm/operaite/screenshot_social.png')
    print('Social saved')

# ─── SCREEN 5: Marketing Audit ─────────────────────────────────────────────────
def screen_marketing():
    img, draw = new_img()
    draw_sidebar(draw, 'Marketing')
    draw = draw_hero(draw, img, 'Marketing Audit', 'Score your online presence and get a prioritized action plan', (5, 150, 105), (4, 120, 87), '📢')

    mx = SIDEBAR_W + 30
    my = 185

    # Score card
    sw = 340
    draw.rounded_rectangle([mx, my, mx+sw, my+300], radius=14, fill=WHITE, outline=BORDER, width=2)
    draw.text((mx+24, my+22), 'Overall Score', font=F['bold'], fill=TEXT_DARK)
    # Big score
    draw.text((mx+sw//2-54, my+70), '72', font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 100) if True else F['bold_xl'], fill=PURPLE)
    draw.text((mx+sw//2-20, my+172), '/ 100', font=F['bold'], fill=TEXT_MID)
    # Score bar
    bar_x, bar_y = mx+30, my+230
    bar_w = sw-60
    draw.rounded_rectangle([bar_x, bar_y, bar_x+bar_w, bar_y+16], radius=8, fill=LIGHT_BG)
    draw.rounded_rectangle([bar_x, bar_y, bar_x+int(bar_w*0.72), bar_y+16], radius=8, fill=PURPLE)
    draw.text((mx+24, my+260), 'Good — room to grow', font=F['reg_xs'], fill=TEXT_MID)

    # Category scores
    cx2 = mx + sw + 30
    cw2 = W - cx2 - 30
    draw.rounded_rectangle([cx2, my, cx2+cw2, my+300], radius=14, fill=WHITE, outline=BORDER, width=2)
    draw.text((cx2+24, my+22), 'Category Breakdown', font=F['bold'], fill=TEXT_DARK)

    cats = [
        ('Google Business Profile', 88, GREEN),
        ('Website SEO',             64, AMBER),
        ('Social Media Presence',   45, RED),
        ('Online Reviews',          82, GREEN),
        ('Local Citations',         71, AMBER),
    ]
    for i, (label, score, col) in enumerate(cats):
        ry = my + 68 + i * 46
        draw.text((cx2+24, ry), label, font=F['reg_xs'], fill=TEXT_DARK)
        bx = cx2 + 300
        bw = cw2 - 340
        draw.rounded_rectangle([bx, ry+2, bx+bw, ry+18], radius=6, fill=LIGHT_BG)
        draw.rounded_rectangle([bx, ry+2, bx+int(bw*score/100), ry+18], radius=6, fill=col)
        draw.text((bx+bw+12, ry), f'{score}', font=F['bold_xs'], fill=col)

    # Action plan
    ay = my + 326
    draw.rounded_rectangle([mx, ay, W-30, ay+500], radius=14, fill=WHITE, outline=BORDER, width=2)
    draw.text((mx+24, ay+22), 'Prioritized Action Plan', font=F['bold'], fill=TEXT_DARK)
    pill(draw, mx+310, ay+24, 'AI-generated', (235,233,255), PURPLE)

    actions = [
        (1, RED,   'Add 15+ photos to your Google Business Profile — listings with photos get 42% more requests for directions.'),
        (2, RED,   'Write unique meta descriptions for your top 5 website pages to improve search click-through rates.'),
        (3, AMBER, 'Post on Instagram at least 3x per week — consistent posting drives 3x more profile visits.'),
        (4, AMBER, 'Respond to all Google reviews within 24 hours — businesses that respond earn 12% more reviews.'),
        (5, GREEN, 'Set up Google Alerts for your business name to monitor your online reputation effortlessly.'),
        (6, GREEN, 'List your business on 3 more local directories: Yelp, Bing Places, and Apple Maps.'),
    ]
    max_text_w = W - 30 - (mx + 70) - 30
    ry = ay + 68
    for num, col, text in actions:
        lines = wrap_text(draw, text, F['reg_xs'], max_text_w)
        row_h = max(44, len(lines) * 22 + 16)
        draw.ellipse([mx+24, ry+6, mx+48, ry+30], fill=col)
        draw.text((mx+30, ry+8), str(num), font=F['bold_xs'], fill=WHITE)
        for j, line in enumerate(lines):
            draw.text((mx+66, ry+8+j*22), line, font=F['reg_xs'], fill=TEXT_DARK if j==0 else TEXT_MID)
        ry += row_h

    img.save('C:/Users/bjusm/operaite/screenshot_marketing.png')
    print('Marketing saved')

screen_dashboard()
screen_reviews()
screen_invoicing()
screen_social()
screen_marketing()
print('\nAll 5 screenshots generated at 1600x1200 (4:3)')
