import { Resend } from 'resend';

// Sends transactional emails for the booking flow.
// Events:
//   request_received   → customer confirmation + owner notification
//   request_approved   → customer confirmation
//   request_declined   → customer apology with redirect to direct contact
//
// Trust model: client-supplied data. Spoofing risk is real but mitigated by:
//   - Email format validation
//   - Length caps on every text field (prevents header injection / oversized payloads)
//   - Resend rate limits at the API key level
// Server-side booking_id verification is a v1.1 add (would require Supabase
// service role key in env).

const FROM = 'Operaite <notifications@operaite.net>';
const SITE = 'https://operaite.net';
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const DAILY_LIMIT_PER_IP = 50;

// ===== Rate limiting (Upstash REST) — same pattern as /api/ai-public =====
function getClientIp(req) {
  var xff = (req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  if (xff) return xff;
  return req.headers['x-real-ip'] || (req.socket && req.socket.remoteAddress) || 'unknown';
}
function todayKey(ip) {
  var date = new Date().toISOString().slice(0, 10);
  var safe = String(ip).replace(/[^a-zA-Z0-9.:_-]/g, '_').slice(0, 64);
  return 'booking-notify:' + date + ':' + safe;
}
async function rateLimitCheck(ip) {
  var url = process.env.UPSTASH_REDIS_REST_URL;
  var token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) {
    console.warn('[booking-notify] Upstash not configured — running without rate limit.');
    return { allowed: true, count: 0 };
  }
  var key = todayKey(ip);
  var headers = { 'Authorization': 'Bearer ' + token };
  try {
    var incrRes = await fetch(url + '/incr/' + encodeURIComponent(key), { method: 'POST', headers: headers });
    if (!incrRes.ok) throw new Error('Upstash incr failed: ' + incrRes.status);
    var incrData = await incrRes.json();
    var count = Number(incrData.result || 0);
    if (count === 1) {
      await fetch(url + '/expire/' + encodeURIComponent(key) + '/90000', { method: 'POST', headers: headers }).catch(function(){});
    }
    return { allowed: count <= DAILY_LIMIT_PER_IP, count: count };
  } catch (e) {
    console.error('[booking-notify] Rate limit check failed:', e.message);
    return { allowed: true, count: 0 }; // fail open on infrastructure errors
  }
}

function clampStr(s, max) {
  return String(s == null ? '' : s).slice(0, max);
}
function escapeHtml(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}
function fmtDate(iso) {
  if (!iso) return '';
  var d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
}
function fmtTime(t) {
  if (!t) return '';
  var p = String(t).split(':');
  var h = +p[0]; var ampm = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12;
  return h + ':' + p[1] + ' ' + ampm;
}

// ===== Email shells =====
function shell(innerHtml) {
  return [
    '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Operaite</title></head>',
    '<body style="margin:0;padding:0;background:#f9f9f8;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#1a1a1a;">',
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f9f9f8;padding:32px 16px;">',
    '<tr><td align="center">',
    '<table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background:#fff;border:1px solid #ececea;border-radius:14px;overflow:hidden;">',
    '<tr><td style="padding:24px 28px 0;">',
    '<a href="' + SITE + '" style="text-decoration:none;color:inherit;">',
    '<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>',
    '<td style="padding:0 10px 0 0;vertical-align:middle;"><img src="' + SITE + '/logo_option1.png" alt="Operaite" width="32" height="32" style="display:block;border:0;border-radius:9px;" /></td>',
    '<td style="vertical-align:middle;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;font-size:18px;font-weight:700;color:#1a1a1a;">Opera<span style="color:#534AB7;">ite</span></td>',
    '</tr></table>',
    '</a>',
    '</td></tr>',
    '<tr><td style="padding:18px 28px 28px;">',
    innerHtml,
    '</td></tr>',
    '</table>',
    '<table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;margin-top:16px;">',
    '<tr><td align="center" style="font-size:11.5px;color:#888;line-height:1.5;">',
    'Sent by <a href="' + SITE + '" style="color:#888;">Operaite</a> on behalf of the business above.<br>',
    'Reply directly to this email to reach the business.',
    '</td></tr>',
    '</table>',
    '</td></tr></table></body></html>'
  ].join('');
}

function detailRow(label, value) {
  if (!value) return '';
  return '<tr><td style="padding:6px 0;font-size:13.5px;color:#666;width:130px;">' + escapeHtml(label) + '</td>' +
    '<td style="padding:6px 0;font-size:14px;color:#1a1a1a;font-weight:600;">' + escapeHtml(value) + '</td></tr>';
}

// ===== Templates =====
function customerReceivedHtml(d) {
  var details =
    '<table role="presentation" cellpadding="0" cellspacing="0" style="margin:16px 0 20px;border-collapse:collapse;">' +
    detailRow('Service', d.service_type) +
    detailRow('Date', fmtDate(d.requested_date)) +
    detailRow('Time', fmtTime(d.requested_time)) +
    '</table>';
  return shell(
    '<h1 style="font-size:20px;font-weight:700;margin:0 0 12px;">We got your request</h1>' +
    '<p style="font-size:14.5px;line-height:1.6;color:#444;margin:0 0 12px;">Hi ' + escapeHtml(d.customer_name) + ',</p>' +
    '<p style="font-size:14.5px;line-height:1.6;color:#444;margin:0 0 12px;">' +
    'Thanks for reaching out to <strong>' + escapeHtml(d.business_name) + '</strong>. We&rsquo;ve received your appointment request:' +
    '</p>' + details +
    '<p style="font-size:14.5px;line-height:1.6;color:#444;margin:0 0 12px;">' +
    '<strong>' + escapeHtml(d.business_name) + '</strong> will confirm by email within 1 business day. If they need to suggest a different time, they&rsquo;ll let you know directly.' +
    '</p>' +
    '<p style="font-size:13px;color:#888;line-height:1.5;margin:16px 0 0;">Need to reach them now? Reply to this email and it&rsquo;ll go straight to the business owner.</p>'
  );
}
function customerReceivedText(d) {
  return [
    'Hi ' + d.customer_name + ',',
    '',
    'Thanks for reaching out to ' + d.business_name + '. We received your appointment request:',
    '',
    '  Service: ' + (d.service_type || '—'),
    '  Date: ' + fmtDate(d.requested_date),
    '  Time: ' + fmtTime(d.requested_time),
    '',
    d.business_name + ' will confirm by email within 1 business day.',
    '',
    'Reply to this email to reach the business directly.',
    '— Sent by Operaite'
  ].join('\n');
}

function ownerNotifyHtml(d) {
  var notesBlock = d.notes ? '<div style="margin:12px 0 16px;padding:10px 12px;background:#f9f9f8;border-left:2px solid #d8d8d4;font-size:13.5px;color:#555;line-height:1.5;white-space:pre-wrap;">' + escapeHtml(d.notes) + '</div>' : '';
  var details =
    '<table role="presentation" cellpadding="0" cellspacing="0" style="margin:16px 0 20px;border-collapse:collapse;">' +
    detailRow('Customer', d.customer_name) +
    detailRow('Email', d.customer_email) +
    detailRow('Phone', d.customer_phone) +
    detailRow('Service', d.service_type) +
    detailRow('Requested', fmtDate(d.requested_date) + ' at ' + fmtTime(d.requested_time)) +
    '</table>';
  return shell(
    '<h1 style="font-size:20px;font-weight:700;margin:0 0 6px;">New booking request</h1>' +
    '<p style="font-size:13px;color:#888;margin:0 0 16px;">For ' + escapeHtml(d.business_name) + '</p>' +
    details + notesBlock +
    '<a href="' + SITE + '/book-admin" style="display:inline-block;padding:11px 20px;background:#534AB7;color:#fff;text-decoration:none;border-radius:8px;font-size:14px;font-weight:600;">Approve or decline →</a>' +
    '<p style="font-size:13px;color:#888;line-height:1.5;margin:18px 0 0;">Reply to this email to message the customer directly.</p>'
  );
}
function ownerNotifyText(d) {
  return [
    'New booking request for ' + d.business_name,
    '',
    '  Customer: ' + d.customer_name,
    '  Email: ' + d.customer_email,
    '  Phone: ' + (d.customer_phone || '—'),
    '  Service: ' + (d.service_type || '—'),
    '  Requested: ' + fmtDate(d.requested_date) + ' at ' + fmtTime(d.requested_time),
    d.notes ? '\n  Notes: ' + d.notes : '',
    '',
    'Approve or decline: ' + SITE + '/book-admin',
    '',
    'Reply to this email to message the customer directly.',
    '— Sent by Operaite'
  ].filter(Boolean).join('\n');
}

function customerApprovedHtml(d) {
  var contactLines = '';
  if (d.owner_email) contactLines += detailRow('Email', d.owner_email);
  if (d.owner_phone) contactLines += detailRow('Phone', d.owner_phone);
  var contactBlock = contactLines ? '<p style="font-size:13.5px;color:#666;margin:16px 0 6px;">If you need to reach ' + escapeHtml(d.business_name) + ' directly:</p>' +
    '<table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">' + contactLines + '</table>' : '';
  var details =
    '<table role="presentation" cellpadding="0" cellspacing="0" style="margin:16px 0 20px;border-collapse:collapse;">' +
    detailRow('Service', d.service_type) +
    detailRow('Date', fmtDate(d.requested_date)) +
    detailRow('Time', fmtTime(d.requested_time)) +
    detailRow('Business', d.business_name) +
    '</table>';
  return shell(
    '<h1 style="font-size:20px;font-weight:700;margin:0 0 12px;color:#065f46;">Your appointment is confirmed</h1>' +
    '<p style="font-size:14.5px;line-height:1.6;color:#444;margin:0 0 12px;">Hi ' + escapeHtml(d.customer_name) + ',</p>' +
    '<p style="font-size:14.5px;line-height:1.6;color:#444;margin:0 0 12px;">' +
    '<strong>' + escapeHtml(d.business_name) + '</strong> has confirmed your appointment:' +
    '</p>' + details + contactBlock +
    '<p style="font-size:13.5px;color:#666;line-height:1.5;margin:16px 0 0;">If anything changes on your end, reply to this email or contact the business directly.</p>'
  );
}
function customerApprovedText(d) {
  return [
    'Hi ' + d.customer_name + ',',
    '',
    d.business_name + ' has confirmed your appointment:',
    '',
    '  Service: ' + (d.service_type || '—'),
    '  Date: ' + fmtDate(d.requested_date),
    '  Time: ' + fmtTime(d.requested_time),
    '  Business: ' + d.business_name,
    '',
    d.owner_email ? '  Reach the business: ' + d.owner_email : '',
    d.owner_phone ? '  Or call: ' + d.owner_phone : '',
    '',
    'Reply to this email if anything changes.',
    '— Sent by Operaite'
  ].filter(Boolean).join('\n');
}

function customerDeclinedHtml(d) {
  var contactLines = '';
  if (d.owner_email) contactLines += detailRow('Email', d.owner_email);
  if (d.owner_phone) contactLines += detailRow('Phone', d.owner_phone);
  var contactBlock = contactLines ? '<p style="font-size:13.5px;color:#666;margin:16px 0 6px;">To find another time:</p>' +
    '<table role="presentation" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">' + contactLines + '</table>' : '';
  return shell(
    '<h1 style="font-size:20px;font-weight:700;margin:0 0 12px;">We couldn&rsquo;t fit your requested time</h1>' +
    '<p style="font-size:14.5px;line-height:1.6;color:#444;margin:0 0 12px;">Hi ' + escapeHtml(d.customer_name) + ',</p>' +
    '<p style="font-size:14.5px;line-height:1.6;color:#444;margin:0 0 12px;">' +
    'Thanks for reaching out to <strong>' + escapeHtml(d.business_name) + '</strong>. Unfortunately the time you requested isn&rsquo;t available. ' +
    'Please contact the business directly to find an alternative — they&rsquo;d like to help.' +
    '</p>' + contactBlock +
    '<p style="font-size:13px;color:#888;line-height:1.5;margin:16px 0 0;">You can also reply to this email and it will go straight to the business.</p>'
  );
}
function customerDeclinedText(d) {
  return [
    'Hi ' + d.customer_name + ',',
    '',
    'Thanks for reaching out to ' + d.business_name + '. Unfortunately the time you requested isn\'t available.',
    '',
    'Please contact the business directly to find an alternative:',
    d.owner_email ? '  Email: ' + d.owner_email : '',
    d.owner_phone ? '  Phone: ' + d.owner_phone : '',
    '',
    'You can also reply to this email and it goes straight to the business.',
    '— Sent by Operaite'
  ].filter(Boolean).join('\n');
}

// ===== Handler =====
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  if (!process.env.RESEND_API_KEY) {
    console.warn('RESEND_API_KEY not set — booking emails disabled');
    return res.status(200).json({ ok: false, reason: 'email_disabled' });
  }

  // Rate limit by IP — anti-spam for the public booking submit endpoint
  var ip = getClientIp(req);
  var rl = await rateLimitCheck(ip);
  if (!rl.allowed) {
    return res.status(429).json({ error: 'rate_limited', message: 'Too many booking notifications from this IP today.' });
  }

  const resend = new Resend(process.env.RESEND_API_KEY);

  let body;
  try { body = req.body && typeof req.body === 'object' ? req.body : JSON.parse(req.body || '{}'); }
  catch (e) { return res.status(400).json({ error: 'Invalid JSON' }); }

  const event = String(body.event || '');
  const data = {
    customer_name: clampStr(body.customer_name, 200).trim(),
    customer_email: clampStr(body.customer_email, 320).trim(),
    customer_phone: clampStr(body.customer_phone, 30).trim() || null,
    service_type: clampStr(body.service_type, 200).trim() || null,
    requested_date: clampStr(body.requested_date, 12).trim(),
    requested_time: clampStr(body.requested_time, 8).trim(),
    notes: clampStr(body.notes, 2000).trim() || null,
    business_name: clampStr(body.business_name, 200).trim(),
    owner_email: clampStr(body.owner_email, 320).trim() || null,
    owner_phone: clampStr(body.owner_phone, 30).trim() || null,
  };

  if (data.customer_email && !EMAIL_RE.test(data.customer_email)) {
    return res.status(400).json({ error: 'Invalid customer email' });
  }
  if (data.owner_email && !EMAIL_RE.test(data.owner_email)) {
    data.owner_email = null;
  }
  if (!data.business_name) {
    return res.status(400).json({ error: 'Missing business_name' });
  }

  try {
    if (event === 'request_received') {
      // Customer confirmation
      await resend.emails.send({
        from: FROM,
        to: data.customer_email,
        reply_to: data.owner_email || undefined,
        subject: 'We got your request — ' + data.business_name,
        html: customerReceivedHtml(data),
        text: customerReceivedText(data),
      });

      // Owner notification (only if owner contact email is set on profile)
      if (data.owner_email) {
        await resend.emails.send({
          from: FROM,
          to: data.owner_email,
          reply_to: data.customer_email,
          subject: 'New booking request: ' + data.customer_name + (data.service_type ? ' — ' + data.service_type : ''),
          html: ownerNotifyHtml(data),
          text: ownerNotifyText(data),
        });
      }
      return res.status(200).json({ ok: true, sent: data.owner_email ? 2 : 1 });
    }

    if (event === 'request_approved') {
      await resend.emails.send({
        from: FROM,
        to: data.customer_email,
        reply_to: data.owner_email || undefined,
        subject: 'Confirmed: ' + (data.service_type || 'your appointment') + ' on ' + fmtDate(data.requested_date) + ' — ' + data.business_name,
        html: customerApprovedHtml(data),
        text: customerApprovedText(data),
      });
      return res.status(200).json({ ok: true, sent: 1 });
    }

    if (event === 'request_declined') {
      await resend.emails.send({
        from: FROM,
        to: data.customer_email,
        reply_to: data.owner_email || undefined,
        subject: data.business_name + " couldn't fit your requested time",
        html: customerDeclinedHtml(data),
        text: customerDeclinedText(data),
      });
      return res.status(200).json({ ok: true, sent: 1 });
    }

    return res.status(400).json({ error: 'Unknown event: ' + event });
  } catch (err) {
    console.error('booking-notify error:', err);
    return res.status(500).json({ error: err.message || 'send failed' });
  }
}
