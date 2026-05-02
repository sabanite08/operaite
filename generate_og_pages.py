"""
Generate per-page OG images (1200x630) for every indexable URL.

Run from the repo root:
    python generate_og_pages.py

Outputs `og.png` in each page's directory. Update each page's
<meta property="og:image"> + <meta name="twitter:image"> to point at
its own og.png (e.g. https://operaite.net/features/ai-review-manager/og.png).
"""
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1200, 630
BRAND = '#534AB7'
BRAND_RGB = (83, 74, 183)
TEXT_LIGHT = '#c4bfe8'
SUB_GREY = '#9b96cc'

# ---------- Fonts ----------
def load_fonts():
    candidates = [
        'C:/Windows/Fonts/segoeuib.ttf',
        'C:/Windows/Fonts/segoeui.ttf',
    ]
    bold_path = candidates[0] if os.path.exists(candidates[0]) else None
    reg_path  = candidates[1] if os.path.exists(candidates[1]) else None
    def f(path, size):
        try:
            return ImageFont.truetype(path or '', size)
        except Exception:
            return ImageFont.load_default()
    return {
        'wordmark': f(bold_path, 36),
        'badge':    f(bold_path, 17),
        'title':    f(bold_path, 64),
        'title_sm': f(bold_path, 56),
        'sub':      f(reg_path, 26),
        'url':      f(bold_path, 30),
        'tag':      f(reg_path, 19),
        'logo':     f(bold_path, 32),
    }

# ---------- Helpers ----------
def text_wrap(draw, text, font, max_w):
    """Greedy wrap to fit max_w."""
    words = text.split()
    lines = []
    cur = []
    for w in words:
        test = ' '.join(cur + [w])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(' '.join(cur))
            cur = [w]
    if cur:
        lines.append(' '.join(cur))
    return lines

def text_w(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

# ---------- Renderer ----------
def make_og(out_path, badge, title, subtitle, fonts):
    # Background gradient
    img = Image.new('RGB', (W, H), '#1e1b3a')
    draw = ImageDraw.Draw(img)
    for i in range(H):
        ratio = i / H
        r = int(0x1e + (0x2d - 0x1e) * ratio)
        g = int(0x1b + (0x25 - 0x1b) * ratio)
        b = int(0x3a + (0x80 - 0x3a) * ratio)
        draw.line([(0, i), (W, i)], fill=(r, g, b))

    # Decorative purple orbs
    orb = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(orb)
    od.ellipse([900, -120, 1500, 480], fill=(83, 74, 183, 70))
    od.ellipse([-150, 350, 420, 800], fill=(83, 74, 183, 55))
    od.ellipse([700, 380, 1100, 720], fill=(139, 92, 246, 35))
    img = Image.alpha_composite(img.convert('RGBA'), orb).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Left accent bar
    draw.rectangle([0, 0, 10, H], fill=BRAND)

    # Logo: purple disc + wordmark
    logo_cx, logo_cy, logo_r = 105, 80, 28
    draw.ellipse(
        [logo_cx - logo_r, logo_cy - logo_r, logo_cx + logo_r, logo_cy + logo_r],
        fill=BRAND
    )
    o_w = text_w(draw, 'O', fonts['logo'])
    draw.text(
        (logo_cx - o_w // 2 - 1, logo_cy - 22),
        'O', font=fonts['logo'], fill='white'
    )
    draw.text((logo_cx + 50, logo_cy - 22), 'Operaite', font=fonts['wordmark'], fill='white')

    # Category badge
    badge_y = 155
    badge_x = 95
    bw = text_w(draw, badge, fonts['badge'])
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + bw + 32, badge_y + 36],
        radius=18, fill=BRAND
    )
    draw.text((badge_x + 16, badge_y + 9), badge, font=fonts['badge'], fill='white')

    # Title (max 3 lines, swap to smaller font if title is long)
    title_font = fonts['title']
    lines = text_wrap(draw, title, title_font, 1010)
    if len(lines) > 2:
        title_font = fonts['title_sm']
        lines = text_wrap(draw, title, title_font, 1010)
    lines = lines[:3]
    line_h = 78 if title_font is fonts['title'] else 68
    title_y = 218
    for i, line in enumerate(lines):
        draw.text((95, title_y + i * line_h), line, font=title_font, fill='white')

    # Subtitle (max 3 lines)
    sub_y = title_y + len(lines) * line_h + 16
    sub_lines = text_wrap(draw, subtitle, fonts['sub'], 1010)[:3]
    for i, line in enumerate(sub_lines):
        draw.text((95, sub_y + i * 36), line, font=fonts['sub'], fill=TEXT_LIGHT)

    # Bottom row: URL + tagline
    draw.text((95, H - 80), 'operaite.net', font=fonts['url'], fill=BRAND)
    draw.text((95, H - 42), '$29/mo · 7-day free trial · cancel anytime', font=fonts['tag'], fill=SUB_GREY)

    # Save
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, 'PNG', optimize=True)
    print(f'  [ok] {os.path.relpath(out_path, ROOT)}')

# ---------- Page list ----------
PAGES = [
    # Tools
    ('tools/og.png',
        'FREE TOOLS',
        'Free AI tools for small business owners',
        'No signup. No watermark. Just useful.'),
    ('tools/free-invoice-generator/og.png',
        'FREE TOOL',
        'Free invoice generator',
        '3 templates. Vector PDF. Logo upload. No signup, no watermark.'),

    # Features
    ('features/ai-review-manager/og.png',
        'FEATURE',
        'AI review response generator',
        'Reply to every Google review in seconds, in your voice.'),
    ('features/marketing-audit/og.png',
        'FEATURE',
        'Small business marketing audit',
        'Score your online presence and get a 3-item fix list.'),
    ('features/social-media-ai/og.png',
        'FEATURE',
        'AI social media caption generator',
        'Captions, hashtags, and post ideas in your voice.'),
    ('features/client-proposals/og.png',
        'FEATURE',
        'Client proposal generator',
        'Win-ready proposals auto-filled from your business profile.'),
    ('features/accounting/og.png',
        'FEATURE',
        'Simple small business accounting',
        'Track income and expenses. See net profit at a glance.'),
    ('features/scheduling/og.png',
        'FEATURE',
        'Small business scheduling software',
        'Book jobs, send branded confirmations, avoid double-bookings.'),

    # Industry verticals
    ('for/og.png',
        'BY INDUSTRY',
        'AI tools tuned for your trade',
        'Sample content in your trade\'s language. Built for owner-operators.'),
    ('for/landscapers/og.png',
        'FOR LANDSCAPERS',
        'AI tools for landscaping businesses',
        'Spring cleanups, hardscape, recurring contracts. In your trade\'s language.'),
    ('for/electricians/og.png',
        'FOR ELECTRICIANS',
        'AI tools for electrical contractors',
        'Service calls, panel upgrades, EV chargers. Permit-aware.'),
    ('for/plumbers/og.png',
        'FOR PLUMBERS',
        'AI tools for plumbing businesses',
        'Emergency calls, repairs, fixture installs. Trip-charge invoicing.'),
    ('for/contractors/og.png',
        'FOR CONTRACTORS',
        'AI tools for general contractors',
        'Remodels, additions, milestone-based proposals and draws.'),
    ('for/hvac/og.png',
        'FOR HVAC',
        'AI tools for HVAC businesses',
        'Service contracts, install jobs, seasonal promo content.'),
    ('for/roofers/og.png',
        'FOR ROOFERS',
        'AI tools for roofing contractors',
        'Insurance-claim friendly invoices and storm-season scheduling.'),
    ('for/cleaners/og.png',
        'FOR CLEANERS',
        'AI tools for cleaning businesses',
        'Recurring contracts, per-visit invoices, AI review replies.'),
    ('for/painters/og.png',
        'FOR PAINTERS',
        'AI tools for painting contractors',
        'Sq-ft proposals, paint-coat invoicing, weather-flexible scheduling.'),

    # Alternatives
    ('alternatives/og.png',
        'COMPARE',
        'HoneyBook vs Bonsai vs Operaite',
        'Honest comparisons. Where each one wins.'),
    ('alternatives/honeybook/og.png',
        'VS HONEYBOOK',
        'Operaite vs HoneyBook',
        'Where Operaite wins, where HoneyBook wins. No fluff.'),
    ('alternatives/bonsai/og.png',
        'VS BONSAI',
        'Operaite vs Bonsai',
        'Where Operaite wins, where Bonsai wins. No fluff.'),
    ('alternatives/dubsado/og.png',
        'VS DUBSADO',
        'Operaite vs Dubsado',
        'Where Operaite wins, where Dubsado wins. No fluff.'),
]

# ---------- Run ----------
if __name__ == '__main__':
    fonts = load_fonts()
    print(f'Generating {len(PAGES)} OG images...')
    for path, badge, title, subtitle in PAGES:
        full = os.path.join(ROOT, path.replace('/', os.sep))
        make_og(full, badge, title, subtitle, fonts)
    print('Done.')
