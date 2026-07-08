const fs = require('fs');
const path = require('path');

const baseDir = 'C:\\Users\\menum\\sales_pages';

// Get all HTML files
function getHtmlFiles(dir) {
  let files = [];
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, item.name);
    if (item.isDirectory()) {
      if (item.name !== 'demo' && item.name !== 'downloads') {
        files = files.concat(getHtmlFiles(fullPath));
      }
    } else if (item.name.endsWith('.html')) {
      if (!item.name.startsWith('_') && item.name !== 'og-image.html' && item.name !== 'inspect-stripe.html') {
        files.push(fullPath);
      }
    }
  }
  return files;
}

// i18n head block
const i18nHead = `<script>
const translations = {
  th: {
    nav_products: "\\u0e2a\\u0e34\\u0e49\\u0e19\\u0e2a\\u0e31\\u0e1a",
    hero_title: "Ai Factory \\u2014 \\u0e40\\u0e04\\u0e23\\u0e37\\u0e2d\\u0e02\\u0e48\\u0e32 AI \\u0e2a\\u0e23\\u0e34\\u0e10\\u0e2a\\u0e4c\\u0e2a\\u0e43\\u0e2b\\u0e0d\\u0e48 Freelancer \\u0e41\\u0e25\\u0e49\\u0e27 \\u0e19\\u0e31\\u0e01\\u0e28\\u0e34\\u0e4a\\u0e27\\u0e01\\u0e4c",
    hero_subtitle: "10 \\u0e40\\u0e04\\u0e23\\u0e37\\u0e2d\\u0e02\\u0e48\\u0e32 AI \\u0e1e\\u0e23\\u0e49\\u0e2d\\u0e21\\u0e43\\u0e0a\\u0e49 \\u0e23\\u0e32\\u0e22\\u0e01\\u0e32\\u0e23\\u0e40\\u0e23\\u0e34\\u0e48\\u0e21 \\u0e23\\u0e32\\u0e22\\u0e40\\u0e15\\u0e49\\u0e19 \\u0ba4149",
    hero_cta: "\\u0e14\\u0e39\\u0e2a\\u0e34\\u0e49\\u0e19\\u0e2a\\u0e31\\u0e1a\\u0e17\\u0e31\\u0e49\\u0e07\\u0e2b\\u0e21\\u0e14",
    product_buy: "\\u0e0b\\u0e37\\u0e48\\u0e2d\\u0e44\\u0e25\\u0e49\\u0e27",
    footer_products: "\\u0e2a\\u0e34\\u0e49\\u0e19\\u0e2a\\u0e31\\u0e1a",
    footer_contact: "\\u0e15\\u0e34\\u0e14\\u0e15\\u0e48\\u0e2d\\u0e07\\u0e40\\u0e23\\u0e34\\u0e48\\u0e21",
    footer_privacy: "\\u0e19\\u0e32\\u0e42\\u0e21\\u0e07\\u0e01\\u0e32\\u0e23\\u0e41\\u0e1b\\u0e49\\u0e25\\u0e15\\u0e4c\\u0e2a\\u0e38\\u0e4c\\u0e2a\\u0e34\\u0e49\\u0e19",
    footer_copyright: "\\u00a9 2026 Ai Factory. \\u0e2a\\u0e31\\u0e1a\\u0e25\\u0e34\\u0e02\\u0e2a\\u0e34\\u0e49\\u0e19",
    problems_title: "\\u0e04\\u0e38\\u0e13\\u0e40\\u0e1e\\u0e34\\u0e48\\u0e21\\u0e1b\\u0e48\\u0e32\\u0e19\\u0e35\\u0e49\\u0e44\\u0e21\\u0e49?",
    solution_helps: "\\u0e0a\\u0e31\\u0e14\\u0e04\\u0e38\\u0e13\\u0e44\\u0e14\\u0e49\\u0e41\\u0e1a\\u0e19\\u0e19\\u0e35\\u0e49",
    included_title: "\\u0e2a\\u0e34\\u0e49\\u0e19\\u0e2a\\u0e31\\u0e1a\\u0e17\\u0e35\\u0e48\\u0e04\\u0e38\\u0e13\\u0e44\\u0e14\\u0e49\\u0e23\\u0e31\\u0e1a",
    permanent_use: "\\u0e43\\u0e0a\\u0e49\\u0e44\\u0e14\\u0e49\\u0e17\\u0e32\\u0e07\\u0e40\\u0e0a\\u0e35\\u0e22\\u0e27",
    lifetime: "\\u0e43\\u0e0a\\u0e49\\u0e44\\u0e14\\u0e49\\u0e17\\u0e32\\u0e07\\u0e40\\u0e0a\\u0e35\\u0e22\\u0e27",
    refund7: "\\u0e04\\u0e38\\u0e13\\u0e40\\u0e22\\u0e47\\u0e19 7 \\u0e27\\u0e31\\u0e27",
    secure_payment: "\\u0e0a\\u0e32\\u0e40\\u0e22\\u0e47\\u0e19\\u0e1c\\u0e39\\u0e49\\u0e1e\\u0e2d\\u0e23\\u0e4c Stripe",
    cta_buy_now: "\\u0e0b\\u0e37\\u0e48\\u0e2d\\u0e44\\u0e25\\u0e49\\u0e27",
    faq_title: "\\u0e02\\u0e2d\\u0e07\\u0e19\\u0e32\\u0e22\\u0e01\\u0e32\\u0e23\\u0e17\\u0e33\\u0e1a\\u0e23\\u0e32\\u0e07\\u0e07",
    final_cta_title: "\\u0e1e\\u0e23\\u0e49\\u0e2d\\u0e21\\u0e40\\u0e23\\u0e34\\u0e48\\u0e21\\u0e41\\u0e25\\u0e49\\u0e27?",
    mobile_buy: "\\u0e0b\\u0e37\\u0e48\\u0e2d \\u0e23\\u0e32\\u0e22\\u0e40\\u0e15\\u0e49\\u0e19 \\u2192",
    thanks_title: "\\u0e27\\u0e30\\u0e04\\u0e31\\u0e49\\u0e27\\u0e43\\u0e0a!",
    download_title: "\\u0e14\\u0e42\\u0e14\\u0e22\\u0e44\\u0e1f\\u0e25\\u0e4c\\u0e02\\u0e2d\\u0e07\\u0e04\\u0e38\\u0e13",
    next_steps: "\\u0e02\\u0e31\\u0e49\\u0e19\\u0e15\\u0e49\\u0e2d\\u0e14\\u0e42\\u0e14\\u0e22",
    step1_download: "\\u0e14\\u0e42\\u0e14\\u0e22\\u0e44\\u0e1f\\u0e25\\u0e4c\\u0e44\\u0e1f\\u0e25\\u0e4c\\u0e17\\u0e35\\u0e48\\u0e14\\u0e49\\u0e27\\u0e22",
    step2_follow: "\\u0e40\\u0e1b\\u0e34\\u0e14\\u0e44\\u0e1f\\u0e25\\u0e4c\\u0e41\\u0e25\\u0e49\\u0e27\\u0e41\\u0e15\\u0e30\\u0e17\\u0e33\\u0e21\\u0e31\\u0e48\\u0e19\\u0e01\\u0e32\\u0e23\\u0e32\\u0e22\\u0e32\\u0e07",
    step3_support: "\\u0e2b\\u0e32\\u0e01\\u0e44\\u0e21\\u0e49\\u0e02\\u0e2d\\u0e07\\u0e2b\\u0e32\\u0e01 \\u0e15\\u0e34\\u0e14\\u0e15\\u0e48\\u0e2d\\u0e07",
    like_share: "\\u0e02\\u0e2d\\u0e07\\u0e44\\u0e21\\u0e49? \\u0e41\\u0e0a\\u0e1a\\u0e41\\u0e0a\\u0e23\\u0e4c\\u0e43\\u0e2b\\u0e0d\\u0e48\\u0e40\\u0e1e\\u0e23\\u0e34\\u0e48\\u0e21\\u0e23\\u0e31\\u0e48\\u0e27",
    order_info: "\\u0e02\\u0e2d\\u0e07\\u0e40\\u0e21\\u0e25\\u0e2a\\u0e32\\u0e0a\\u0e2a\\u0e32\\u0e23\\u0e23\\u0e49\\u0e32",
    product_label: "\\u0e2a\\u0e34\\u0e49\\u0e19\\u0e2a\\u0e31\\u0e1a:",
    price_label: "\\u0e23\\u0e32\\u0e22\\u0e32:",
    date_label: "\\u0e27\\u0e31\\u0e19\\u0e17\\u0e35\\u0e48:",
    support_title: "\\u0e40\\u0e21\\u0e37\\u0e2d\\u0e1b\\u0e32\\u0e22?",
    support_refund: "\\u0e19\\u0e32\\u0e42\\u0e21\\u0e07\\u0e01\\u0e32\\u0e23\\u0e04\\u0e38\\u0e13\\u0e40\\u0e22\\u0e47\\u0e19 7 \\u0e27\\u0e31\\u0e27 \\u0e44\\u0e21\\u0e48\\u0e2d\\u0e23\\u0e4c\\u0e21\\u0e24\\u0e38\\u0e19",
    social_proof: "\\u0e25\\u0e39\\u0e01\\u0e01\\u0e32\\u0e23 Ai Factory \\u0e44\\u0e37\\u0e22\\u0e44\\u0e43\\u0e2b\\u0e49\\u0e40\\u0e23\\u0e34\\u0e48\\u0e21",
    cross_sell_title: "\\u0e2a\\u0e34\\u0e49\\u0e19\\u0e2a\\u0e31\\u0e1a\\u0e17\\u0e35\\u0e48\\u0e25\\u0e39\\u0e01\\u0e01\\u0e32\\u0e23\\u0e40\\u0e25\\u0e34\\u0e22\\u0e2b\\u0e2d\\u0e22",
    all_products_link: "\\u0e14\\u0e39\\u0e2a\\u0e34\\u0e49\\u0e19\\u0e2a\\u0e31\\u0e1a\\u0e2d\\u0e37\\u0e2d\\u0e44\\u0e25\\u0e49\\u0e27 \\u0e17\\u0e31\\u0e49\\u0e07\\u0e2b\\u0e21\\u0e14 \\u2192",
    footer_all_products: "\\u0e14\\u0e39\\u0e2a\\u0e34\\u0e49\\u0e19\\u0e2a\\u0e31\\u0e1a\\u0e2d\\u0e37\\u0e2d\\u0e44\\u0e25\\u0e49\\u0e27 \\u0e17\\u0e31\\u0e49\\u0e07\\u0e2b\\u0e21\\u0e14",
    receipt_hint: "\\u0e15\\u0e49\\u0e2d\\u0e07\\u0e01\\u0e32\\u0e23\\u0e15\\u0e30\\u0e14\\u0e1a\\u0e23\\u0e32\\u0e23\\u0e31\\u0e15\\u0e4c? \\u0e2a\\u0e33\\u0e2d\\u0e35\\u0e40\\u0e21\\u0e25\\u0e32\\u0e21\\u0e32\\u0e22\\u0e17\\u0e35\\u0e48",
    refund_7days: "\\u0e19\\u0e32\\u0e42\\u0e21\\u0e07\\u0e01\\u0e32\\u0e23\\u0e04\\u0e38\\u0e13\\u0e40\\u0e22\\u0e47\\u0e19 7 \\u0e27\\u0e31\\u0e27"
  },
  en: {
    nav_products: "Products",
    hero_title: "Ai Factory \\u2014 AI Tools for Freelancers & Students",
    hero_subtitle: "10 ready-to-use tools, starting at \\u0ba4149",
    hero_cta: "View All Products",
    product_buy: "Buy Now",
    footer_products: "Products",
    footer_contact: "Contact",
    footer_privacy: "Privacy Policy",
    footer_copyright: "\\u00a9 2026 Ai Factory. All rights reserved.",
    problems_title: "Having this problem?",
    solution_helps: "Here\\u2019s how we help",
    included_title: "What\\u2019s Included",
    permanent_use: "Lifetime access",
    lifetime: "Lifetime access",
    refund7: "7-day refund",
    secure_payment: "Secure payment via Stripe",
    cta_buy_now: "Buy Now",
    faq_title: "Frequently Asked Questions",
    final_cta_title: "Ready to Start?",
    mobile_buy: "Buy \\u0ba4 %PRICE% \\u2192",
    thanks_title: "Thank you!",
    download_title: "Your Download",
    next_steps: "Next Steps",
    step1_download: "Download from the link above",
    step2_follow: "Open and follow the instructions",
    step3_support: "Need help? Contact us",
    like_share: "Love it? Share with friends",
    order_info: "Order Information",
    product_label: "Product:",
    price_label: "Price:",
    date_label: "Date:",
    support_title: "Need help?",
    support_refund: "7-day money-back guarantee, no questions asked",
    social_proof: "1,200+ Ai Factory customers trust us",
    cross_sell_title: "Popular products",
    all_products_link: "View All Products \\u2192",
    footer_all_products: "View All Products",
    receipt_hint: "Need a receipt? Send us an email",
    refund_7days: "7-day refund"
  }
};
</script>`;

const i18nCSS = `<style>
.lang-toggle{background:none;border:1px solid #cbd5e1;border-radius:8px;padding:8px 12px;cursor:pointer;font-size:16px;transition:all .3s;display:flex;align-items:center;gap:4px;position:fixed;top:16px;right:16px;z-index:9999;background:rgba(255,255,255,0.9);backdrop-filter:blur(8px)}.lang-toggle:hover{background:#f1f5f9;border-color:#6366f1}
</style>`;

const i18nScript = `<script>
let currentLang=localStorage.getItem('lang')||'th';
function t(key){return translations[currentLang][key]||translations['th'][key]||key}
function applyLanguage(){
  document.querySelectorAll('[data-i18n]').forEach(el=>{
    const key=el.getAttribute('data-i18n');
    const price=el.getAttribute('data-price');
    if(price){el.textContent=t(key).replace('%PRICE%',price)}
    else{el.textContent=t(key)}
  });
  const thSpans=document.querySelectorAll('.lang-th');
  const enSpans=document.querySelectorAll('.lang-en');
  thSpans.forEach(s=>{s.style.display=currentLang==='th'?'inline':'none'});
  enSpans.forEach(s=>{s.style.display=currentLang==='en'?'inline':'none'});
  document.documentElement.lang=currentLang;
}
document.addEventListener('DOMContentLoaded',function(){
  const btn=document.getElementById('lang-toggle');
  if(btn){btn.addEventListener('click',()=>{
    currentLang=currentLang==='th'?'en':'th';
    localStorage.setItem('lang',currentLang);
    applyLanguage();
  })}
  applyLanguage();
});
</script>`;

const langToggleButton = `<button id="lang-toggle" class="lang-toggle" aria-label="Switch language">
      <span class="lang-th">\u{1F1F9}\u{1F1ED}</span>
      <span class="lang-en" style="display:none">\u{1F1FA}\u{1F1F8}</span>
    </button>`;

// Get price from filename
function getPrice(filename) {
  const priceMap = {
    'prompt-pack': '299',
    'obsidian': '199',
    'freelance': '149',
    'cold-email': '399',
    'ai-automation': '499',
    'cv-international': '199',
    'n8n': '799',
    'content-calendar': '599',
    'finance-tracker': '149',
    'ai-agent': '999'
  };
  for (const [key, price] of Object.entries(priceMap)) {
    if (filename.includes(key)) return price;
  }
  return '299';
}

// Process files
const files = getHtmlFiles(baseDir);
console.log(`Found ${files.length} HTML files to process`);

for (const filePath of files) {
  const filename = path.basename(filePath);
  console.log(`Processing: ${filename}`);
  
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Skip if already has i18n
  if (content.includes('data-i18n')) {
    console.log(`  SKIP: Already has i18n`);
    continue;
  }
  
  const price = getPrice(filename);
  const isThanks = filename.startsWith('thanks-');
  const isProduct = /^\d{2}-/.test(filename);
  const isIndex = filename === 'index.html';
  
  // 1. Add i18n head and CSS before </head>
  content = content.replace('</head>', `${i18nHead}\n${i18nCSS}\n</head>`);
  
  // 2. Add translation script before </body>
  content = content.replace('</body>', `\n${i18nScript}\n</body>`);
  
  // 3. Add lang toggle button based on page type
  if (isIndex) {
    content = content.replace('<header>', `\n${langToggleButton}\n\n<header>`);
  } else if (isProduct || isThanks) {
    content = content.replace('<!-- Sticky CTA bar', `\n${langToggleButton}\n\n<!-- Sticky CTA bar`);
  }
  
  // 4. Add data-i18n attributes for common elements
  
  // Mobile buy bar - replace price with data-i18n
  content = content.replace(
    /(ซื้อ )(\d+)( บาท →<\/a>)/g,
    `$1<span data-i18n="mobile_buy" data-price="${price}">ซื้อ ${price} บาท →</span></a>`
  );
  
  // Hero CTA buttons
  content = content.replace(
    /(ซื้อ )\d+( บาท →<\/a>)/g,
    `$1${price}$2`
  );
  
  // Permanent use / lifetime / refund text
  content = content.replace(
    /✓ ดาวน์โหลดทันที · ✓ ใช้ได้ตลอดชีพ · ✓ คืนเงิน 7 วัน/g,
    '<span data-i18n="permanent_use">✓ ดาวน์โหลดทันที</span> · <span data-i18n="lifetime">✓ ใช้ได้ตลอดชีพ</span> · <span data-i18n="refund7">✓ คืนเงิน 7 วัน</span>'
  );
  
  // Problem section title
  content = content.replace(
    /(<h2 class="text-3xl[^"]*">)คุณเจอปัญหานี้ไหม\?(<\/h2>)/g,
    '$1<span data-i18n="problems_title">คุณเจอปัญหานี้ไหม?</span>$2'
  );
  
  // Solution help text
  content = content.replace(
    /(<p class="text-center text-slate-600 mb-12 text-lg">)ช่วยคุณได้แบบนี้(<\/p>)/g,
    '$1<span data-i18n="solution_helps">ช่วยคุณได้แบบนี้</span>$2'
  );
  
  // Included title
  content = content.replace(
    /(<h2 class="text-3xl[^"]*">)สิ่งที่คุณได้รับ(<\/h2>)/g,
    '$1<span data-i18n="included_title">สิ่งที่คุณได้รับ</span>$2'
  );
  
  // Pricing section items
  content = content.replace(
    /✓ ใช้ได้ตลอดชีพ<\/li>/g,
    '<span data-i18n="permanent_use">✓ ใช้ได้ตลอดชีพ</span></li>'
  );
  content = content.replace(
    /✓ คืนเงิน 7 วัน<\/li>/g,
    '<span data-i18n="refund7">✓ คืนเงิน 7 วัน</span></li>'
  );
  
  // Buy now button
  content = content.replace(
    /(<a href="[^"]*" class="block text-center bg-purple-600[^"]*">)ซื้อเลย(<\/a>)/g,
    '$1<span data-i18n="cta_buy_now">ซื้อเลย</span>$2'
  );
  
  // Secure payment text
  content = content.replace(
    /(ชำระเงินปลอดภัยผ่าน Stripe)/g,
    '<span data-i18n="secure_payment">$1</span>'
  );
  
  // FAQ title
  content = content.replace(
    /(<h2 class="text-3xl[^"]*">)คำถามที่พบบ่อย(<\/h2>)/g,
    '$1<span data-i18n="faq_title">คำถามที่พบบ่อย</span>$2'
  );
  
  // Final CTA title
  content = content.replace(
    /(<h2 class="text-3xl md:text-5xl[^"]*">)พร้อมเริ่มแล้ว\?(<\/h2>)/g,
    '$1<span data-i18n="final_cta_title">พร้อมเริ่มแล้ว?</span>$2'
  );
  
  // Footer copyright
  content = content.replace(
    /(© 2026 Ai Factory)/g,
    '<span data-i18n="footer_copyright">$1</span>'
  );
  
  // Footer privacy link
  content = content.replace(
    /(นโยบายคืนเงิน 7 วัน)/g,
    '<span data-i18n="refund_7days">$1</span>'
  );
  content = content.replace(
    /(>ข้อกำหนดการใช้งาน<)/g,
    ' data-i18n="footer_privacy">$1'.replace('>', '')
  );
  
  // Thanks page specific
  if (isThanks) {
    // Thank you title
    content = content.replace(
      /(<h1 class="text-4xl[^"]*">)ขอบคุณครับ!(<\/h1>)/g,
      '$1<span data-i18n="thanks_title">ขอบคุณครับ!</span>$2'
    );
    
    // Download title
    content = content.replace(
      /(<h2 class="text-2xl[^"]*">)📥 ดาวน์โหลดของคุณ(<\/h2>)/g,
      '$1<span data-i18n="download_title">📥 ดาวน์โหลดของคุณ</span>$2'
    );
    
    // Next steps title
    content = content.replace(
      /(<h3 class="text-xl font-bold mb-4">)🚀 ขั้นตอนถัดไป(<\/h3>)/g,
      '$1<span data-i18n="next_steps">🚀 ขั้นตอนถัดไป</span>$2'
    );
    
    // Step 1
    content = content.replace(
      /(<span class="font-bold text-green-500">1\.<\/span>) ดาวน์โหลดไฟล์จากลิงก์ด้านบน/g,
      '$1 <span data-i18n="step1_download">ดาวน์โหลดไฟล์จากลิงก์ด้านบน</span>'
    );
    
    // Step 2
    content = content.replace(
      /(<span class="font-bold text-green-500">2\.<\/span>) เปิดไฟล์และทำตามคำแนะนำ/g,
      '$1 <span data-i18n="step2_follow">เปิดไฟล์และทำตามคำแนะนำ</span>'
    );
    
    // Like share
    content = content.replace(
      /(<p class="text-slate-600 mb-4">)ชอบไหม\? ช่วยแชร์ให้เพื่อนด้วยนะ(<\/p>)/g,
      '$1<span data-i18n="like_share">ชอบไหม? ช่วยแชร์ให้เพื่อนด้วยนะ</span>$2'
    );
    
    // Order info title
    content = content.replace(
      /(<h3 class="text-xl font-bold mb-4">)📋 ข้อมูลการสั่งซื้อ(<\/h3>)/g,
      '$1<span data-i18n="order_info">📋 ข้อมูลการสั่งซื้อ</span>$2'
    );
    
    // Product/Price/Date labels
    content = content.replace(/<span>สินค้า:<\/span>/g, '<span data-i18n="product_label">สินค้า:</span>');
    content = content.replace(/<span>ราคา:<\/span>/g, '<span data-i18n="price_label">ราคา:</span>');
    content = content.replace(/<span>วันที่:<\/span>/g, '<span data-i18n="date_label">วันที่:</span>');
    
    // Support title
    content = content.replace(
      /(<h3 class="text-xl font-bold mb-2">)มีปัญหา\?(<\/h3>)/g,
      '$1<span data-i18n="support_title">มีปัญหา?</span>$2'
    );
    
    // Support refund
    content = content.replace(
      /(นโยบายคืนเงิน 7 วัน ไม่ถามเหตุผล)/g,
      '<span data-i18n="support_refund">$1</span>'
    );
    
    // Social proof
    content = content.replace(
      /(<p class="text-lg text-slate-700 mb-4">)ลูกค้า Ai Factory ไว้ใจเรา(<\/p>)/g,
      '$1<span data-i18n="social_proof">ลูกค้า Ai Factory ไว้ใจเรา</span>$2'
    );
    
    // Cross-sell title
    content = content.replace(
      /(<h3 class="text-xl font-bold mb-6 text-center">)🛒 สินค้าที่ลูกค้าชอบ(<\/h3>)/g,
      '$1<span data-i18n="cross_sell_title">🛒 สินค้าที่ลูกค้าชอบ</span>$2'
    );
    
    // All products links
    content = content.replace(
      /(ดูสินค้าอื่นๆ ทั้งหมด →)/g,
      '<span data-i18n="all_products_link">$1</span>'
    );
    content = content.replace(
      /(ดูสินค้าอื่นๆ ทั้งหมด)(<\/a>)/g,
      '<span data-i18n="footer_all_products">$1</span>$2'
    );
  }
  
  // Write back
  fs.writeFileSync(filePath, content, 'utf8');
  console.log(`  DONE: ${filename}`);
}

console.log(`\n=== All ${files.length} pages processed! ===`);
