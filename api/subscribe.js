import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { paymentMethodId, email, name } = req.body;
  if (!paymentMethodId || !email) return res.status(400).json({ error: 'Missing required fields' });

  try {
    // Create customer
    const customer = await stripe.customers.create({
      email,
      name,
      payment_method: paymentMethodId,
      invoice_settings: { default_payment_method: paymentMethodId }
    });

    // Create subscription with 7-day free trial
    const subscription = await stripe.subscriptions.create({
      customer: customer.id,
      items: [{ price: process.env.STRIPE_PRICE_ID }],
      trial_period_days: 7,
      expand: ['latest_invoice.payment_intent']
    });

    if (subscription.status === 'active' || subscription.status === 'trialing') {
      return res.status(200).json({ success: true, customerId: customer.id, subscriptionId: subscription.id });
    } else {
      return res.status(400).json({ error: 'Subscription could not be activated. Please check your card details.' });
    }
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
