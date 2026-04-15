import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { prompt, customerId } = req.body;
  if (!prompt) return res.status(400).json({ error: 'No prompt provided' });
  if (!customerId) return res.status(401).json({ error: 'Not authorized' });

  if (customerId !== 'admin') {
    try {
      const subscriptions = await stripe.subscriptions.list({ customer: customerId, status: 'active', limit: 1 });
      if (subscriptions.data.length === 0) {
        return res.status(403).json({ error: 'No active subscription found.' });
      }
    } catch (e) {
      return res.status(403).json({ error: 'Could not verify subscription.' });
    }
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    const data = await response.json();
    if (data.error) return res.status(500).json({ error: data.error.message });
    return res.status(200).json({ result: data.content[0].text });
  } catch (e) {
    return res.status(500).json({ error: 'AI request failed. Please try again.' });
  }
}
