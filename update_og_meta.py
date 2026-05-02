"""
Update each page's <meta property="og:image"> + <meta name="twitter:image">
to point to the page-specific og.png we just generated.

One-shot script — run after generate_og_pages.py.
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
OLD_URL = 'https://operaite.net/og-image.png'

# (html_path, new_image_url, new_alt_text)
PAGES = [
    ('tools/index.html',
        'https://operaite.net/tools/og.png',
        'Operaite — Free AI tools for small business owners'),
    ('tools/free-invoice-generator/index.html',
        'https://operaite.net/tools/free-invoice-generator/og.png',
        'Operaite Free Invoice Generator'),
    ('features/ai-review-manager/index.html',
        'https://operaite.net/features/ai-review-manager/og.png',
        'Operaite AI Review Response Generator'),
    ('features/marketing-audit/index.html',
        'https://operaite.net/features/marketing-audit/og.png',
        'Operaite Small Business Marketing Audit'),
    ('features/social-media-ai/index.html',
        'https://operaite.net/features/social-media-ai/og.png',
        'Operaite AI Social Media Caption Generator'),
    ('features/client-proposals/index.html',
        'https://operaite.net/features/client-proposals/og.png',
        'Operaite Client Proposal Generator'),
    ('features/accounting/index.html',
        'https://operaite.net/features/accounting/og.png',
        'Operaite Simple Small Business Accounting'),
    ('features/scheduling/index.html',
        'https://operaite.net/features/scheduling/og.png',
        'Operaite Small Business Scheduling Software'),
    ('for/index.html',
        'https://operaite.net/for/og.png',
        'Operaite — AI tools by industry'),
    ('for/landscapers/index.html',
        'https://operaite.net/for/landscapers/og.png',
        'Operaite — AI tools for landscapers'),
    ('for/electricians/index.html',
        'https://operaite.net/for/electricians/og.png',
        'Operaite — AI tools for electricians'),
    ('for/plumbers/index.html',
        'https://operaite.net/for/plumbers/og.png',
        'Operaite — AI tools for plumbers'),
    ('for/contractors/index.html',
        'https://operaite.net/for/contractors/og.png',
        'Operaite — AI tools for general contractors'),
    ('for/hvac/index.html',
        'https://operaite.net/for/hvac/og.png',
        'Operaite — AI tools for HVAC businesses'),
    ('for/roofers/index.html',
        'https://operaite.net/for/roofers/og.png',
        'Operaite — AI tools for roofers'),
    ('for/cleaners/index.html',
        'https://operaite.net/for/cleaners/og.png',
        'Operaite — AI tools for cleaning businesses'),
    ('for/painters/index.html',
        'https://operaite.net/for/painters/og.png',
        'Operaite — AI tools for painters'),
    ('alternatives/index.html',
        'https://operaite.net/alternatives/og.png',
        'Operaite vs HoneyBook, Bonsai, Dubsado'),
    ('alternatives/honeybook/index.html',
        'https://operaite.net/alternatives/honeybook/og.png',
        'Operaite vs HoneyBook'),
    ('alternatives/bonsai/index.html',
        'https://operaite.net/alternatives/bonsai/og.png',
        'Operaite vs Bonsai'),
    ('alternatives/dubsado/index.html',
        'https://operaite.net/alternatives/dubsado/og.png',
        'Operaite vs Dubsado'),
]

def update(path, new_url, new_alt):
    full = os.path.join(ROOT, path.replace('/', os.sep))
    if not os.path.exists(full):
        print(f'  [skip] {path} (not found)')
        return
    with open(full, 'r', encoding='utf-8') as f:
        html = f.read()
    if OLD_URL not in html:
        print(f'  [skip] {path} (already updated or no og-image.png reference)')
        return
    # Replace the URL anywhere it appears (og:image + twitter:image)
    new = html.replace(OLD_URL, new_url)
    # Update og:image:alt + twitter:image:alt where present (best-effort regex)
    new = re.sub(
        r'(<meta property="og:image:alt" content=")[^"]*(" />)',
        rf'\1{new_alt}\2',
        new
    )
    new = re.sub(
        r'(<meta name="twitter:image:alt" content=")[^"]*(" />)',
        rf'\1{new_alt}\2',
        new
    )
    if new == html:
        print(f'  [no-change] {path}')
        return
    with open(full, 'w', encoding='utf-8', newline='') as f:
        f.write(new)
    print(f'  [ok] {path}')

if __name__ == '__main__':
    print(f'Updating og:image in {len(PAGES)} pages...')
    for path, url, alt in PAGES:
        update(path, url, alt)
    print('Done.')
