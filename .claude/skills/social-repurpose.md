---
name: social-repurpose
description: Turn an Operaite blog post into platform-specific social posts. Use when promoting a new post or filling a social calendar. Outputs ready-to-paste posts for X/Twitter, LinkedIn, Facebook, and Instagram.
---

# Operaite Social Repurpose

## What this skill does
Take one published Operaite blog post and produce 4 platform-tailored posts plus image suggestions. Audience: small-business owners (solo to ~20 employees) — service businesses, freelancers, creators, e-commerce sellers.

## Inputs
- URL or slug of the post (e.g., `/blog/professional-invoice-checklist`)
- Optional: a specific angle or stat from the post to lead with

If only a slug given, read `blog/[slug]/index.html` to pull the actual content. Don't paraphrase blind.

## Audience tone per platform
- **X/Twitter**: One sharp claim with a number, then the URL. ≤280 chars total. 0-1 hashtag (none preferred). Tone is "operator sharing what works."
- **LinkedIn**: 120–200 words, line-break heavy, opens with the most counterintuitive insight from the post. End with a question to drive comments. 0-2 hashtags. Tone is peer-to-peer, not "personal brand guru."
- **Facebook**: 80–120 words for SMB-owner Facebook groups. Frame as "if you're doing X, here's the gotcha." No links until end (FB depriotizes link posts; mention "link in comments" pattern works well).
- **Instagram caption**: Hook in first 125 chars (caption preview), then 100–150 words. 4–6 hashtags at the end mixing broad (#smallbusiness) and niche (#freelancetips, #servicebusiness). Pair with carousel-style image suggestions.

## What to NOT do
- No emoji spam (one MAX per post if any).
- No "Are you struggling with X?" hook patterns.
- No fake stats. Pull only from the source post.
- No "DM me for the link" growth-hack patterns.
- No "Hot take:" or "Unpopular opinion:" openings — overused.
- No claiming Operaite has features it doesn't. Stick to: invoicing, marketing tools, reviews, social posts, proposals, $29/mo.

## Output format
Four code blocks, labeled, ready to paste:

```
### X / Twitter (≤280 chars)
[post]

### LinkedIn
[post]

### Facebook
[post]

### Instagram caption
[caption + hashtags]

### Image suggestions (3 options)
1. [description with concrete subject + style + text overlay if any]
2. ...
3. ...
```

Image suggestions should be concrete enough to brief a Canva/AI step. Best-converting Operaite assets historically are: text-on-solid-background quote cards with the strongest stat from the post, screenshots of real invoices/responses (anonymized), and side-by-side before/after.

## Link
Always use canonical: `https://operaite.net/blog/[slug]`.

## What to leave to the human
End the response with one line: "Eyeball the stat I led with against the source post — I pulled from the file but didn't recompute anything."
