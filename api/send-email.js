const { Resend } = require('resend');

module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const { email, product_name, product_slug, order_id } = req.body;
  
  if (!email || !product_name) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  
  const resend = new Resend(process.env.RESEND_API_KEY);
  
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { font-family: 'IBM Plex Sans Thai', system-ui, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; text-align: center; }
        .content { padding: 30px; }
        .btn { display: inline-block; background: #6366f1; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; }
        .footer { padding: 20px 30px; background: #f1f5f9; text-align: center; font-size: 12px; color: #64748b; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>⚡ Ai Factory</h1>
          <p>ขอบคุณสำหรับการสั่งซื้อ!</p>
        </div>
        <div class="content">
          <h2>สินค้า: ${product_name}</h2>
          <p>คำสั่งซื้อ #${order_id || 'N/A'}</p>
          <p>คุณสามารถดาวน์โหลดสินค้าได้จากลิงก์ด้านล่าง:</p>
          <p style="text-align: center; margin: 30px 0;">
            <a href="https://ai-factory-omega.vercel.app/${product_slug}" class="btn">ดาวน์โหลดสินค้า</a>
          </p>
          <h3>วิธีใช้งาน:</h3>
          <ol>
            <li>คลิกปุ่มดาวน์โหลดด้านบน</li>
            <li>ทำตามคำแนะนำในไฟล์</li>
            <li>เริ่มใช้งานได้ทันที!</li>
          </ol>
          <p><strong>ต้องการความช่วยเหลือ?</strong> ติดต่อเราได้ที่ <a href="mailto:hello@aifactory.store">hello@aifactory.store</a></p>
          <p>นโยบายrefund: หากไม่พอใจภายใน 7 วัน สามารถขอคืนเงินได้</p>
        </div>
        <div class="footer">
          <p>© 2026 Ai Factory · All rights reserved</p>
        </div>
      </div>
    </body>
    </html>
  `;
  
  try {
    const { data, error } = await resend.emails.send({
      from: 'Ai Factory <hello@aifactory.store>',
      to: [email],
      subject: `✅ ขอบคุณสำหรับการสั่งซื้อ ${product_name}`,
      html: html,
    });
    
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    
    return res.status(200).json({ success: true, id: data.id });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
};
