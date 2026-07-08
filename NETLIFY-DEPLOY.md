# Netlify Deploy Guide

**Backup deployment for sales_pages (primary: Vercel)**

---

## Quick Deploy (Drag & Drop)

1. Go to **https://app.netlify.com/drop**
2. Open `C:\Users\menum\sales_pages` in Explorer
3. Drag the **entire folder** onto the Netlify page
4. Wait for upload → get your URL (e.g. `https://random-name.netlify.app`)

---

## Custom Domain Setup

1. Go to **Site settings → Domain management**
2. Click **Add custom domain**
3. Enter: `aitoolshop.co` (or your domain)
4. Update DNS:
   - Add CNAME record: `www` → `your-site.netlify.app`
   - Or use Netlify DNS (nameservers)

---

## Netlify CLI Deploy (if installed later)

```powershell
# Install
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd "C:\Users\menum\sales_pages"
netlify deploy --prod --dir .
```

---

## Configuration

The `netlify.toml` in this folder includes:
- Static site config (no build step)
- Pretty URLs via redirects
- Short-links: `/t/<slug>` rewrites
- Security headers (CSP, HSTS, X-Frame-Options)
- Cache rules (1 year for assets, 5 min for HTML)
- Stripe checkout allowed in CSP `form-action`

---

## Vercel ↔ Netlify Parity

| Feature | Vercel | Netlify |
|---------|--------|---------|
| Deploy | `vercel --prod` | Drag & Drop / CLI |
| Custom domain | ✅ | ✅ |
| HTTPS | Auto | Auto |
| netlify.toml redirects | N/A | ✅ |
| vercel.json rewrites | ✅ | N/A |

**Note:** Short-links (`/t/*`) only work on Netlify. Vercel uses direct URLs.
