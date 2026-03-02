#!/usr/bin/env python3
"""Inject auth-aware nav swap into all blog HTML files.
If quirrely_session exists in localStorage, replaces 'Take the Test' CTA
with 'Dashboard' link + small avatar circle."""
import glob, os

BLOG_DIR = "/opt/quirrely/quirrely_v313_integrated/blog"
AUTH_JS = '''<script>
(function(){
  var s=localStorage.getItem('quirrely_session');
  if(!s)return;
  var cta=document.querySelector('.nav .cta');
  if(cta){
    cta.textContent='Dashboard';
    cta.href='/dashboard';
  }
  var nav=document.querySelector('.nav');
  if(nav){
    var u=localStorage.getItem('quirrely_user');
    var av=document.createElement('a');
    av.href='/dashboard';
    av.style.cssText='width:28px;height:28px;border-radius:50%;background:#FF6B6B;display:inline-flex;align-items:center;justify-content:center;color:white;font-size:0.75rem;font-weight:600;text-decoration:none;margin-left:0.5rem;';
    try{var ud=JSON.parse(u);av.textContent=(ud.display_name||ud.email||'?')[0].toUpperCase();}catch(e){av.textContent='?';}
    nav.appendChild(av);
  }
})();
</script>'''

count = 0
for f in sorted(glob.glob(os.path.join(BLOG_DIR, "*.html"))):
    c = open(f).read()
    if 'quirrely_session' in c:
        print(f"  skip (already has auth): {os.path.basename(f)}")
        continue
    if '</body>' not in c:
        print(f"  skip (no </body>): {os.path.basename(f)}")
        continue
    c = c.replace('</body>', AUTH_JS + '\n</body>', 1)
    open(f, 'w').write(c)
    count += 1
    print(f"  ✅ {os.path.basename(f)}")

print(f"\nDone: {count} files patched")
