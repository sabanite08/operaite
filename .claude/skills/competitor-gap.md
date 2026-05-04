---
name: competitor-gap
description: Find bottom-of-funnel keyword gaps for Operaite. Use when planning new blog posts, landing pages, or feature pages. Outputs a ranked list of high-buyer-intent searches in small-business operations that Operaite could rank for.
---

# Operaite Competitor Gap Research

## What this skill does
Find keyword gaps where (a) small-business owners are searching, (b) competitors have a page, (c) Operaite has no page yet — focused on **bottom-of-funnel** searches where the user is one step from solving an operations problem (and one step from needing a tool like Operaite).

## Inputs the user must provide
- A topic, problem area, or competitor URL (e.g., "invoicing", "responding to bad reviews", "honeybook.com/blog/invoice-templates")
- Optional: their existing blog list (read from `blog/` directory)

If no input, default to surveying gaps across Operaite's pillar topics: invoicing, customer communication, online reputation/reviews, marketing for small business, hiring, pricing, social media for SMBs, proposals, basic accounting.

## Competitors to check
Direct SaaS competitors (their blogs are the goldmine):
- honeybook.com/blog — wedding/creative SMB ops
- jobber.com/academy — home service SMBs
- squareup.com/us/en/townsquare — broad SMB
- waveapps.com/blog — accounting/invoicing
- freshbooks.com/blog — invoicing/accounting
- gusto.com/resources — payroll/people but covers SMB ops broadly

Indirect editorial competitors:
- shopify.com/blog (small-business sections)
- buffer.com/library (social media)
- hootsuite.com/resources (social)
- getapp.com / capterra.com (review-style comparison content)

Authoritative .gov/.org for trust signals (don't compete with — link to):
- sba.gov, irs.gov

## Filters to apply
For each candidate keyword:

1. **Intent type.** Reject pure informational ("what is invoicing"). Keep:
   - **Template/checklist intent**: "what to include on professional invoice", "client onboarding checklist"
   - **How-to-with-stakes intent**: "how to respond to negative google review", "how to write price increase letter"
   - **Decision intent**: "cash vs accrual for small business", "when to hire first employee"
   - **Audit/diagnostic intent**: "small business marketing audit", "is my pricing too low"
2. **Page status.** Check `blog/` directory for existing slugs. If covered, mark as "expand" or skip.
3. **Niche fit.** Operaite serves small-business owners (likely solo to ~20 employees) doing operations themselves. Reject enterprise topics, deep accounting (CPA-level), or anything that needs a license to advise on (legal, medical, tax filing specifics).
4. **CTA-ability.** The post must have a natural place to mention Operaite — invoicing, marketing, reviews, social posting, proposals. If a topic exists in a vacuum (e.g., "best Excel formulas for accountants"), skip.

## Output format
Markdown table:

| Rank | Keyword | Intent type | Evidence (URL) | Operaite gap | Suggested page type | Operaite CTA hook |
|------|---------|-------------|----------------|--------------|---------------------|-------------------|
| 1 | invoice late fee wording | Template | jobber.com/academy/late-fees | No post yet | 1500-word checklist post | Invoicing module auto-applies late fees |

Cap at 15 rows. Rank by: (a) clarity of buyer intent, (b) thinness of top-ranking competitor page, (c) ability to plug an Operaite feature naturally.

## Honest limits to surface
End every report with "What I couldn't verify":
- Search volume (no Ahrefs/SEMrush — recommend Ubersuggest free or Google Trends spot-check)
- Difficulty (same)
- Whether the user's CTA placement is natural — flag any where the Operaite tie-in feels forced

Do NOT invent search volume or "people also ask" data without citing the source.
