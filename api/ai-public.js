// Public AI endpoint for free tools (e.g. invoice generator).
//
// Security model: zero user input in system prompts. The client picks a
// task name; the server picks the prompt template; user input only goes
// into named variable slots. This prevents jailbreak / prompt-as-proxy abuse.
//
// Rate limiting: per-IP, per-day, via Upstash Redis REST API.
// Set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN in Vercel env.
// If Upstash is not configured, the endpoint will run without rate limiting
// (logs a warning) — fine for local dev, BAD for production. Fix by adding
// the env vars before launching publicly.

const DAILY_LIMIT = 5;             // AI calls per IP per day
const MAX_TOKENS  = 250;           // hard cap on output tokens
const MODEL       = 'claude-haiku-4-5-20251001';

// Allowlist of task names → prompt-template builders.
// Each builder takes a sanitized payload object and returns the user prompt
// string. Anything not in this map is rejected.
const PROMPTS = {
  polish_description: function(p) {
    var raw = String(p.description || '').slice(0, 200);
    return [
      "Rewrite this rough invoice line-item description as a clean, professional one.",
      "Rules:",
      "- Max 14 words",
      "- No marketing fluff, no emoji, no jargon",
      "- Preserve any specific deliverable, scope, or quantity in the original",
      "- Just return the rewritten text — no quotes, no labels, no explanation",
      "",
      "Original description:",
      raw
    ].join('\n');
  },

  generate_payment_terms: function(p) {
    var lateFee  = (p.late_fee_pct  != null) ? Number(p.late_fee_pct)  : 1.5;
    var dueLabel = String(p.due_label || 'on the due date').slice(0, 60);
    var bizName  = String(p.business_name || '').slice(0, 80);
    return [
      "Write a short payment terms paragraph for the bottom of an invoice.",
      "Rules:",
      "- 2 to 3 sentences only",
      "- Professional but warm tone",
      "- State payment is due " + dueLabel,
      "- Mention a " + lateFee + "% per month late fee on overdue balances",
      "- Mention bank transfer or credit card as accepted methods (don't promise specifics)",
      "- Do not invent contact info, links, or business names beyond what is given",
      bizName ? ("- Business name (use only if natural): " + bizName) : "",
      "- Just return the paragraph, no labels, no quotes"
    ].filter(Boolean).join('\n');
  },

  draft_reminder_email: function(p) {
    var clientName = String(p.client_name || 'there').slice(0, 80);
    var invNum     = String(p.invoice_number || '').slice(0, 40);
    var total      = String(p.total || '').slice(0, 30);
    var daysOver   = (p.days_overdue != null) ? Math.max(0, Math.min(365, parseInt(p.days_overdue, 10) || 0)) : 0;
    var bizName    = String(p.business_name || '').slice(0, 80);

    return [
      "Write a payment reminder email body. Polite but firm. No subject line.",
      "Rules:",
      "- 4 to 6 sentences",
      "- Open by name, address them as a real person, not a transaction",
      "- Include the invoice number and amount once",
      "- Acknowledge it may have been an oversight",
      "- Ask them to reply if there's a question or to send payment",
      "- Sign off warmly, no pushy 'final notice' language",
      "- Just return the email body. No subject. No 'Hi {name}' placeholders.",
      "",
      "Details:",
      "- Recipient: " + clientName,
      "- Invoice #: " + (invNum || 'unknown'),
      "- Amount: " + (total || 'unknown'),
      "- Days overdue: " + daysOver,
      bizName ? ("- Sender's business name: " + bizName) : ""
    ].filter(Boolean).join('\n');
  }
};

// ---------- Rate limiting (Upstash REST) ----------

function todayKey(ip) {
  var d = new Date();
  var date = d.toISOString().slice(0, 10); // YYYY-MM-DD
  // Hash-y to keep keys short; the IP itself is fine but URL-safe it.
  var safe = String(ip).replace(/[^a-zA-Z0-9.:_-]/g, '_').slice(0, 64);
  return 'ai-public:' + date + ':' + safe;
}

async function rateLimitCheck(ip) {
  var url   = process.env.UPSTASH_REDIS_REST_URL;
  var token = process.env.UPSTASH_REDIS_REST_TOKEN;

  if (!url || !token) {
    console.warn('[ai-public] Upstash not configured — running without rate limit. Set UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN in Vercel env.');
    return { allowed: true, remaining: -1, count: 0 };
  }

  var key = todayKey(ip);
  var headers = { 'Authorization': 'Bearer ' + token };

  try {
    // Atomic increment
    var incrRes = await fetch(url + '/incr/' + encodeURIComponent(key), {
      method: 'POST',
      headers: headers
    });
    if (!incrRes.ok) throw new Error('Upstash incr failed: ' + incrRes.status);
    var incrData = await incrRes.json();
    var count = Number(incrData.result || 0);

    // First request → set TTL to ~25h (covers timezone slop). Idempotent.
    if (count === 1) {
      await fetch(url + '/expire/' + encodeURIComponent(key) + '/90000', {
        method: 'POST',
        headers: headers
      }).catch(function(){});
    }

    return {
      allowed: count <= DAILY_LIMIT,
      remaining: Math.max(0, DAILY_LIMIT - count),
      count: count
    };
  } catch (e) {
    console.error('[ai-public] Rate limit check failed:', e.message);
    // Fail open on rate-limit infrastructure errors so a transient Upstash
    // outage doesn't take the tool offline. The hard caps below still apply.
    return { allowed: true, remaining: -1, count: 0 };
  }
}

// ---------- Handler ----------

function getClientIp(req) {
  var xff = (req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  if (xff) return xff;
  return req.headers['x-real-ip'] || req.socket && req.socket.remoteAddress || 'unknown';
}

export default async function handler(req, res) {
  // CORS — same-origin in production but be permissive for now
  res.setHeader('Cache-Control', 'no-store');

  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'POST');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(204).end();
  }
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'method_not_allowed' });
  }

  // Validate request body
  var body = req.body;
  if (!body || typeof body !== 'object') {
    return res.status(400).json({ error: 'invalid_body' });
  }
  var task = String(body.task || '');
  var payload = body.payload && typeof body.payload === 'object' ? body.payload : {};

  if (!Object.prototype.hasOwnProperty.call(PROMPTS, task)) {
    return res.status(400).json({ error: 'unknown_task' });
  }

  // Rate limit
  var ip = getClientIp(req);
  var limit = await rateLimitCheck(ip);
  if (!limit.allowed) {
    return res.status(429).json({
      error: 'rate_limited',
      remaining: 0,
      message: "You've hit the daily AI assist limit. It resets at midnight UTC, or sign up free for unlimited assists in the Operaite app."
    });
  }

  // Build the prompt server-side. User input never reaches the system role.
  var userPrompt;
  try {
    userPrompt = PROMPTS[task](payload);
  } catch (e) {
    return res.status(400).json({ error: 'invalid_payload' });
  }

  // Call Anthropic
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('[ai-public] ANTHROPIC_API_KEY missing');
    return res.status(500).json({ error: 'misconfigured' });
  }

  try {
    var anthropic = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        system: "You are a precise writing assistant for small business owners. Follow the user's rules exactly. Never invent facts. Return only the requested text — no preface, no explanation, no markdown unless asked.",
        messages: [{ role: 'user', content: userPrompt }]
      })
    });

    if (!anthropic.ok) {
      var errText = await anthropic.text();
      console.error('[ai-public] Anthropic error', anthropic.status, errText);
      return res.status(502).json({ error: 'ai_provider_error' });
    }

    var data = await anthropic.json();
    if (data.error) {
      return res.status(502).json({ error: 'ai_provider_error', detail: data.error.message });
    }

    var text = '';
    if (Array.isArray(data.content)) {
      for (var i = 0; i < data.content.length; i++) {
        if (data.content[i] && data.content[i].type === 'text') {
          text += data.content[i].text;
        }
      }
    }
    text = text.trim();

    return res.status(200).json({
      result: text,
      remaining: limit.remaining > 0 ? Math.max(0, limit.remaining - 1) : limit.remaining
    });
  } catch (e) {
    console.error('[ai-public] Request failed:', e.message);
    return res.status(500).json({ error: 'request_failed' });
  }
}
