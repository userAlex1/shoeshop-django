# StepUp Shoes — Django Shoe Store with M-Pesa & Paystack

A shoe e-commerce site built in Django with:
- Product catalog with categories, sizes, images
- Session-based cart & checkout
- **M-Pesa STK Push** (Daraja API) — customer gets a payment prompt on their phone
- **Paystack** for card / bank payments
- Django admin to manage products and view orders

---

## 1. Install & run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then fill in real values (see below)

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the shop and `http://127.0.0.1:8000/admin/` to
add categories and products (upload shoe images there).

---

## 2. Getting M-Pesa Daraja sandbox credentials (since you don't have them yet)

1. Go to **https://developer.safaricom.co.ke** and create a free account.
2. Log in, go to **My Apps** → **Add a new App**. Name it anything (e.g. "StepUp Shoes").
   Select the **Lipa Na M-Pesa Sandbox** product when creating it.
3. Open the app — you'll see your **Consumer Key** and **Consumer Secret**. Put these in
   `.env` as `MPESA_CONSUMER_KEY` / `MPESA_CONSUMER_SECRET`.
4. Go to **APIs → M-Pesa Express (STK Push)** → **Test Credentials** page. This gives you:
   - `Shortcode`: `174379` (standard sandbox test shortcode — already set as the default)
   - `Passkey`: a long string — put this in `.env` as `MPESA_PASSKEY`
5. Test phone number for the sandbox is Safaricom's official test MSISDN
   **254708374149** — use this when testing checkout, since sandbox will not
   send a real prompt to your own phone.

### Callback URL (important)
Safaricom's servers must be able to reach your callback URL over the public internet —
`localhost` won't work. For local development, use **ngrok**:

```bash
ngrok http 8000
```

Copy the `https://xxxx.ngrok-free.app` URL it gives you, and set in `.env`:
```
MPESA_CALLBACK_URL=https://xxxx.ngrok-free.app/payments/mpesa/callback/
```
Restart `runserver` after changing `.env`.

### Going live
When ready for production: apply for **Go-Live** on the Daraja portal to get your real
Paybill/Till shortcode and production passkey, set `MPESA_ENV=production`, and point
`MPESA_CALLBACK_URL` at your real deployed domain.

---

## 3. Getting Paystack keys (for card / bank payments)

1. Sign up at **https://dashboard.paystack.com/#/signup** (Paystack supports Kenya).
2. Go to **Settings → API Keys & Webhooks**.
3. Copy the **Test Secret Key** and **Test Public Key** into `.env` as
   `PAYSTACK_SECRET_KEY` / `PAYSTACK_PUBLIC_KEY`.
4. Test card numbers are listed at https://paystack.com/docs/payments/test-payments —
   e.g. card `4084 0840 8408 4081`, any future expiry, CVV `408`.
5. When ready to accept real payments, switch to your **Live** keys and complete
   Paystack's business verification.

---

## 4. How the payment flows work

**M-Pesa:**
`checkout` → creates `Order` → redirects to `payments:mpesa_pay` → user confirms phone
→ `mpesa.stk_push()` calls Daraja → phone gets the STK prompt → customer enters PIN →
Safaricom POSTs the result to `payments:mpesa_callback` → order marked paid → the
"waiting" page (polling every 3s) detects this and redirects to the success page.

**Paystack:**
`checkout` → creates `Order` → redirects to `payments:paystack_pay` → Paystack's hosted
checkout page → customer pays by card/bank → redirected back to
`payments:paystack_verify` → we verify server-side with Paystack → order marked paid.

---

## 5. Project structure

```
shoeshop/
  shoeshop/        # settings, root urls
  store/           # products, cart, checkout, orders
  payments/        # mpesa.py (Daraja client), paystack.py, webhook views
  templates/        # base.html
  static/css/       # styling
```

---

## 6. Before deploying to production

- Set `DEBUG=False` and a real random `SECRET_KEY`.
- Set `ALLOWED_HOSTS` to your real domain.
- Move off SQLite to Postgres for anything beyond a demo.
- Serve `MEDIA` (product images) via S3 or similar in production.
- Make sure your callback/webhook URLs use HTTPS.
- Consider adding Paystack webhook signature verification for extra safety
  (currently we verify server-side via the verify endpoint, which is secure on its own).
