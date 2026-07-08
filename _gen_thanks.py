import json
import re
import urllib.parse
from pathlib import Path

# Read products.json
with open(r'C:\Users\menum\sales_pages\products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Read template
template_path = Path(r'C:\Users\menum\sales_pages\_thanks_template.html')
template = template_path.read_text(encoding='utf-8')

# URL-encode helper
def url_encode_share(name_th):
    text = 'ฉันเพิ่งซื้อ ' + name_th + ' แนะนำเลย!'
    return urllib.parse.quote(text, safe='')

# Process each product
for p in data['products']:
    slug = p['slug']
    slug_upper = slug.upper()
    product = p

    download_link = 'https://drive.google.com/REPLACE_WITH_ACTUAL_DOWNLOAD_LINK_FOR_' + slug_upper
    order_id = 'ord_' + slug.replace('-', '_')
    page_url = 'https://yourdomain.com/thanks/' + slug
    share_text = url_encode_share(product['name_th'])

    replacements = {
        '{{NAME_TH}}': product['name_th'],
        '{{TAGLINE}}': product['tagline'],
        '{{INCLUDED_1_TITLE}}': product['included'][0]['title'],
        '{{INCLUDED_2_TITLE}}': product['included'][1]['title'],
        '{{INCLUDED_3_TITLE}}': product['included'][2]['title'],
        '{{INCLUDED_4_TITLE}}': product['included'][3]['title'],
        '{{PRICE_THB}}': str(product['price_thb']),
        '{{EMAIL}}': data['default_email'],
        '{{BRAND}}': data['default_brand'],
        '{{DOWNLOAD_LINK}}': download_link,
        '{{CUSTOMER_EMAIL}}': '<span id="customer-email" class="text-slate-700 font-semibold">อีเมลของคุณ</span><script>try{var e=new URLSearchParams(location.search).get("email")||new URLSearchParams(location.search).get("customer_email")||"อีเมลของคุณ";document.getElementById("customer-email").textContent=e}catch(x){}</script>',
        '{{ORDER_DATE}}': '2026-06-05',
        '{{ORDER_ID}}': order_id,
        '{{PAGE_URL}}': page_url,
        '{{SHARE_TEXT}}': share_text,
    }
    content = template
    for key, value in replacements.items():
        content = content.replace(key, value)

    # Verify no placeholders remain
    remaining = re.findall(r'\{\{[^}]+\}\}', content)
    if remaining:
        print('WARNING: ' + slug + ' still has: ' + str(remaining))

    out_path = Path(r'C:\Users\menum\sales_pages') / ('thanks-' + slug + '.html')
    out_path.write_text(content, encoding='utf-8')
    print('Wrote ' + out_path.name + ' (' + str(len(content)) + ' bytes)')

print('Done.')
