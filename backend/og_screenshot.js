
const puppeteer = require('puppeteer');
const slug = process.argv[2];
const out  = process.argv[3];
(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage']
  });
  const page = await browser.newPage();
  await page.setViewport({width:1200, height:630});
  await page.goto(`http://127.0.0.1:8080/user/${slug}`, {waitUntil:'networkidle0', timeout:20000});
  // Wait for radar SVG to render
  await page.waitForSelector('#vsr svg, #vsr', {timeout:5000}).catch(()=>{});
  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({path: out, clip:{x:0,y:0,width:1200,height:630}});
  await browser.close();
  console.log('OK');
})();
