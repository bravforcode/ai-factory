# AI Factory

> 10-product digital marketplace with Stripe payments — static, serverless, ready to deploy.

## Overview

AI Factory is a one-week launch of 10 digital products targeting Thai office workers, freelancers, and SME owners. The store is 100% static — no backend, no database, no JS framework. Payment is handled by Stripe Payment Links.

## Products

| # | Product | Price (THB) |
|---|---------|-------------|
| 1 | Thai AI Prompt Pack | ฿299 |
| 2 | Obsidian Student Kit | ฿199 |
| 3 | Freelance Pricing Calculator | ฿149 |
| 4 | Cold Email Template Pack | ฿249 |
| 5 | AI Automation Workflow | ฿399 |
| 6 | CV International Template | ฿199 |
| 7 | n8n SME Workflow Pack | ฿499 |
| 8 | Content Calendar 90 Days | ฿299 |
| 9 | Finance Tracker THB | ฿349 |
| 10 | AI Agent Starter GitHub | ฿999 |

**Total addressable price points:** ฿4,191

## Architecture

```
┌─────────────────────────────────────────────┐
│  Static HTML Pages (10 products)            │
├─────────────────────────────────────────────┤
│  Stripe Payment Links                       │
├─────────────────────────────────────────────┤
│  Netlify (Hosting + Forms)                  │
├─────────────────────────────────────────────┤
│  Thank You Pages (Download/Delivery)        │
└─────────────────────────────────────────────┘
```

## Key Features

- **100% Static** — No backend, no database, no server
- **Stripe Payments** — Payment Links for each product
- **Responsive Design** — Mobile-first with TailwindCSS
- **SEO Optimized** — Meta tags, Open Graph, structured data
- **Analytics Ready** — UTM tracking, conversion pixels
- **Netlify Deploy** — One-click deployment

## Quick Start

```bash
# Clone
git clone https://github.com/bravforcode/ai-factory.git
cd ai-factory

# Open in browser
open index.html

# Or use Netlify CLI
npx netlify-cli dev
```

## Deployment

```bash
# Deploy to Netlify
npx netlify-cli deploy --prod
```

## Tech Stack

- **HTML5** — Semantic markup
- **CSS3** — TailwindCSS
- **JavaScript** — Vanilla JS (minimal)
- **Payments** — Stripe Payment Links
- **Hosting** — Netlify

## Live Demo

🔗 [ai-factory-omega.vercel.app](https://ai-factory-omega.vercel.app)

## License

MIT
