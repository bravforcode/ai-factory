const fs = require('fs');
const path = require('path');

const baseDir = 'C:\\Users\\menum\\sales_pages';

const langToggleButton = `<button id="lang-toggle" class="lang-toggle" aria-label="Switch language">
      <span class="lang-th">\u{1F1F9}\u{1F1ED}</span>
      <span class="lang-en" style="display:none">\u{1F1FA}\u{1F1F8}</span>
    </button>`;

// Get all thanks HTML files
const files = fs.readdirSync(baseDir).filter(f => f.startsWith('thanks-') && f.endsWith('.html'));

for (const filename of files) {
  const filePath = path.join(baseDir, filename);
  console.log(`Processing: ${filename}`);
  
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Check if already has lang-toggle
  if (content.includes('id="lang-toggle"')) {
    console.log(`  SKIP: Already has lang-toggle`);
    continue;
  }
  
  // Add lang toggle before <!-- Success Hero -->
  content = content.replace(
    '<!-- Success Hero -->',
    `${langToggleButton}\n\n  <!-- Success Hero -->`
  );
  
  fs.writeFileSync(filePath, content, 'utf8');
  console.log(`  DONE: ${filename}`);
}

console.log(`\n=== Fixed ${files.length} thanks pages! ===`);
