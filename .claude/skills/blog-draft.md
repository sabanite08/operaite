---
name: blog-draft
description: Draft an Operaite blog post in the house voice. Use when adding a new post to the daily-blog routine or filling a content gap. Outputs a complete static HTML file ready to save under blog/[slug]/index.html.
---

# Operaite Blog Draft

## What this skill does
Write an Operaite blog post as a complete static `index.html` file matching the existing pattern under `blog/`. Voice: practical, checklist-driven, specific numbers, written for a small-business owner doing the work themselves.

## Inputs
- Target slug (e.g., `late-fee-wording-for-invoices`)
- Title and target keyword
- Optional: the angle or specific gotcha to lead with

## House voice — non-negotiables
Before writing, read 2 reference posts (e.g., `blog/professional-invoice-checklist/index.html` and `blog/respond-to-negative-google-reviews/index.html`) to match patterns:

1. **Lede paragraph** opens with a concrete claim with a number ("There's a 30% gap in payment speed between…"). No "In this post, we'll cover…"
2. **Sections use `<h2>` and `<h3>`**, not `<h1>` (the title is already h1).
3. **Numbered lists for checklist items**, with `<strong>` lead-in for each item, then explanation.
4. **Plain language** — write like talking to a contractor or a freelance designer who has 15 min to read this between jobs. No "leverage", "synergy", "stakeholder."
5. **Specific numbers wherever possible.** "2x faster", "$600 1099 threshold", "30 days late." Vague claims kill trust.
6. **Use HTML entities for apostrophes/quotes**: `&rsquo;` `&ldquo;` `&rdquo;` — match existing posts.
7. **Word count: 800–1500.** The reference posts run long-form. No artificial shortening.

## Structure to follow
The reference posts use this exact HTML scaffold — copy it and swap content. The wrapping nav, article shell, footer, and structured data should match `professional-invoice-checklist/index.html` byte-for-byte except for:
- `<title>` and meta description
- All `og:` and `twitter:` meta tags
- Canonical URL
- JSON-LD `headline`, `datePublished`, `dateModified`, `mainEntityOfPage`
- The `<article>` body content
- Reading time in `.meta` (estimate: ~250 words/min)

## Operaite CTA placement
Every post needs ONE natural Operaite mention, not a sales pitch. Pattern:
> If you're writing these manually every time, [Operaite](https://operaite.net) generates [invoices/responses/posts] from your business profile in under a minute — useful when you have 15 of these to send before end of day.

Place it 2/3 of the way through the post, NOT at the top, and NOT as the final paragraph. The final paragraph should be a practical takeaway, not a CTA.

## Encoding
**Critical:** Operaite's blog HTML files contain non-ASCII characters (smart quotes, em dashes). Per project memory: PowerShell 5.1 Get/Set-Content corrupts UTF-8. Use the Write tool (not PowerShell) to create the file. If editing later, use the Edit tool, not Get-Content/Set-Content round-trips.

## File path
Save to `blog/[slug]/index.html`. Create the directory if needed (use `mkdir -p` via Bash, or rely on Write to create parent dirs).

## After writing — what to remind the user
1. Add the post to the blog index page (`blog/index.html`) — find where existing posts are listed and copy the pattern.
2. Add the post URL to `sitemap.xml`.
3. Verify the OG image still resolves (uses `/og-image.png` by default; custom only if user provides one).

## What NOT to do
- No emojis.
- No fake stats. If you cite a percentage, name the source or write "in our experience" / "broadly" — don't fabricate "according to a 2024 SBA study" if you didn't read one.
- No filler conclusion ("In summary…"). Last paragraph is a practical takeaway or a question that prompts action.
- No tables of contents.
- No AI-tells: avoid "delve", "navigate the complexities", "in today's fast-paced world", "robust solutions."
