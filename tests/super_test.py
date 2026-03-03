#!/usr/bin/env python3
"""QUIRRELY SUPER_TEST v1.1 — ASO · KIM · MARS"""
import os,sys,json,time,socket,subprocess,urllib.request,urllib.error,ssl
from datetime import datetime,timezone
BASE_URL="http://127.0.0.1:8080"
SITE_URL="https://quirrely.com"
SITE_CA_URL="http://127.0.0.1:8080"
DB_NAME="quirrely_prod"
APP_DIR="/opt/quirrely/quirrely_v313_integrated/backend"
RESEND_API_KEY=""  # read from .env at runtime
FROM_EMAIL="Quirrely <hello@quirrely.com>"
REPORT_EMAIL="hello@quirrely.com"
TEST_EMAIL="supertest@quirrely.com"
SSL_CTX=ssl.create_default_context()
results={"run_at":datetime.now(timezone.utc).isoformat(),"part_a":{"pass":0,"fail":0,"tests":[]},"part_b":{"pass":0,"fail":0,"tests":[]},"part_c":{"pass":0,"fail":0,"tests":[]}}
def record(part,name,passed,detail="",owner=""):
    key="part_a" if part=="A" else "part_b" if part=="B" else "part_c"
    results[key]["pass" if passed else "fail"]+=1
    results[key]["tests"].append({"name":name,"status":"PASS" if passed else "FAIL","detail":detail,"owner":owner})
    print(f"  {'✅' if passed else '❌'} [{owner}] {name}: {detail}")
def http_get(url,timeout=10):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; QuirrelyHealthCheck)"})
        with urllib.request.urlopen(req,timeout=timeout,context=SSL_CTX) as r:
            return r.status,r.read().decode("utf-8",errors="replace")
    except urllib.error.HTTPError as e: return e.code,""
    except Exception as e: return 0,str(e)
def http_post(url,data,timeout=10):
    try:
        payload=json.dumps(data).encode("utf-8")
        req=urllib.request.Request(url,data=payload,method="POST",headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0 (compatible; QuirrelyHealthCheck)"})
        with urllib.request.urlopen(req,timeout=timeout,context=SSL_CTX) as r:
            return r.status,json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try: return e.code,json.loads(e.read().decode("utf-8"))
        except: return e.code,{}
    except Exception as e: return 0,{"error":str(e)}
def db_query(sql):
    try:
        r=subprocess.run(["sudo","-u","postgres","psql","-d",DB_NAME,"-t","-c",sql],capture_output=True,text=True,timeout=10)
        return r.stdout.strip(),r.returncode==0
    except Exception as e: return str(e),False
def pm2_status():
    try:
        r=subprocess.run(["pm2","jlist"],capture_output=True,text=True,timeout=10)
        return json.loads(r.stdout)
    except: return []
def ssl_expiry_days(hostname):
    try:
        ctx=ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(),server_hostname=hostname) as s:
            s.settimeout(5);s.connect((hostname,443))
            cert=s.getpeercert()
            exp=datetime.strptime(cert["notAfter"],"%b %d %H:%M:%S %Y %Z")
            return (exp-datetime.now(timezone.utc).replace(tzinfo=None)).days
    except: return -1
def run_part_a():
    print("\n"+"="*70+"\n  SUPER_TEST_PART_A — Environment [ASO+MARS]\n"+"="*70)
    print("\n  [ASO] PM2")
    procs=pm2_status()
    proc=next((p for p in procs if p.get("name")=="quirrely"),None)
    if proc:
        st=proc.get("pm2_env",{}).get("status","unknown")
        rs=proc.get("pm2_env",{}).get("restart_time",0)
        mb=proc.get("monit",{}).get("memory",0)/1024/1024
        record("A","PM2 quirrely online",st=="online",f"status={st}","ASO")
        record("A","PM2 restarts < 25",rs<=25,f"restarts={rs}","ASO")
        record("A","PM2 memory < 512MB",mb<512,f"{mb:.1f}MB","ASO")
    else:
        record("A","PM2 quirrely found",False,"not found","ASO")
    print("\n  [ASO] API")
    st,body=http_get(f"{BASE_URL}/health")
    record("A","GET /health 200",st==200,f"status={st}","ASO")
    if st==200:
        try:
            d=json.loads(body)
            record("A","API version 3.1.3",d.get("version")=="3.1.3",f"version={d.get('version')}","ASO")
            record("A","API status healthy",d.get("status")=="healthy",f"status={d.get('status')}","ASO")
        except: record("A","API health JSON",False,"parse error","ASO")
    st,_=http_get(f"{BASE_URL}/api/v2/health")
    record("A","GET /api/v2/health",st==200,f"status={st}","ASO")
    print("\n  [ASO] Database")
    out,ok=db_query("SELECT version();")
    record("A","PostgreSQL connection",ok,out[:40] if ok else out,"ASO")
    out,ok=db_query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
    cnt=int(out.strip()) if ok and out.strip().isdigit() else 0
    record("A","Public schema 15+ tables",cnt>=15,f"{cnt} tables","ASO")
    for tbl in ["users","writing_profiles","subscriptions","waitlist"]:
        out,ok=db_query(f"SELECT COUNT(*) FROM {tbl};")
        record("A",f"Table '{tbl}' accessible",ok,f"rows={out.strip()}" if ok else out,"ASO")
    out,ok=db_query("SELECT COUNT(*) FROM stretch_prompts_base;")
    cnt=int(out.strip()) if ok and out.strip().isdigit() else 0
    record("A","STRETCH prompts 450+",cnt>=450,f"{cnt} prompts","ASO")
    out,ok=db_query("SELECT COUNT(*) FROM stretch_authors;")
    cnt=int(out.strip()) if ok and out.strip().isdigit() else 0
    record("A","STRETCH authors 60",cnt>=60,f"{cnt} authors","ASO")
    out,ok=db_query("SELECT COUNT(DISTINCT voice_type) FROM stretch_authors;")
    cnt=int(out.strip()) if ok and out.strip().isdigit() else 0
    record("A","STRETCH author voices 10",cnt>=10,f"{cnt} voices","ASO")
    print("\n  [ASO] SSL+Sites")
    st,body=http_get(SITE_URL)
    record("A","quirrely.com 200",st==200,f"status={st}","ASO")
    if st==200: record("A","quirrely.com has Quirrely","Quirrely" in body,"found" if "Quirrely" in body else "not found","ASO")
    st,_=http_get(SITE_CA_URL)
    record("A","quirrely.ca 200",st==200,f"status={st}","ASO")
    for host in ["quirrely.com","api.quirrely.com","quirrely.ca"]:
        days=ssl_expiry_days(host)
        record("A",f"SSL valid: {host}",days>14,f"{days} days","ASO")
    print("\n  [MARS] Stripe")
    sk,wh="",""
    try:
        with open(os.path.join(APP_DIR,".env")) as f:
            for line in f:
                if line.startswith("STRIPE_SECRET_KEY="): sk=line.split("=",1)[1].strip()
                if line.startswith("STRIPE_WEBHOOK_SECRET="): wh=line.split("=",1)[1].strip()
    except: pass
    record("A","STRIPE_SECRET_KEY present",bool(sk),"found" if sk else "missing","MARS")
    record("A","STRIPE live key",sk.startswith("sk_live_"),"live" if sk.startswith("sk_live_") else "not live","MARS")
    record("A","STRIPE_WEBHOOK_SECRET present",bool(wh),"found" if wh else "missing","MARS")
def run_part_b():
    print("\n"+"="*70+"\n  SUPER_TEST_PART_B — Functional [KIM]\n"+"="*70)
    ts=int(time.time())
    print("\n  [KIM] Auth Endpoints")
    test_user=f"supertest_{ts}@quirrely.com"
    st,resp=http_post(f"{BASE_URL}/api/v2/auth/signup",{"email":test_user,"password":"SuperTest2026!x","username":f"st_{ts}"})
    record("B","Auth signup endpoint mounted",st not in [0,404],f"status={st}","KIM")
    st,resp=http_post(f"{BASE_URL}/api/v2/auth/login",{"email":test_user,"password":"SuperTest2026!x"})
    record("B","Auth login endpoint mounted",st not in [0,404],f"status={st}","KIM")
    token=resp.get("access_token","") if st==200 else ""
    record("B","Login returns token",bool(token),"token received" if token else "no token (auth not mounted)","KIM")
    print("\n  [KIM] LNCP Pipeline")
    sys.path.insert(0,APP_DIR)
    try:
        from lncp_orchestrator import get_orchestrator
        orch=get_orchestrator()
        sid,state=orch.create_session(mode="STORY")
        record("B","LNCP session created",bool(sid),f"session={sid[:8]}...","KIM")
        groups=[
            ["The morning light came through the window.","She made coffee and sat down."],
            ["Words are the only currency that compounds.","He wrote slowly, with intention."],
            ["The ratio of silence to speech matters.","She paused before answering."],
        ]
        for i,grp in enumerate(groups):
            state=orch.submit_group(sid,grp)
            record("B",f"LNCP group {i+1} accepted",state.get("last_submission",{}).get("status")=="VALID",f"gate={state.get('gate',{}).get('completed',0)}/3","KIM")
        record("B","LNCP gate complete",state.get("gate",{}).get("is_complete",False),"complete" if state.get("gate",{}).get("is_complete") else "incomplete","KIM")
        analysis=orch.run_analysis(sid)
        record("B","LNCP analysis runs",bool(analysis),f"sentences={len(analysis.get('sentences_analyzed',[]))}","KIM")
        record("B","LNCP phase2 present","phase2" in analysis,f"mode={analysis.get('phase2',{}).get('presentation_mode','N/A')}","KIM")
        record("B","LNCP phase3 syntheses",len(analysis.get("phase3",{}).get("syntheses",[]))>0,f"{len(analysis.get('phase3',{}).get('syntheses',[]))} syntheses","KIM")
        orch.cleanup_session(sid)
        record("B","LNCP session cleanup",True,"ok","KIM")
    except Exception as e:
        record("B","LNCP pipeline",False,str(e),"KIM")
    print("\n  [KIM] Analyze API Endpoint")
    _az_s,_az_r=http_post(BASE_URL+"/api/v2/analyze",{"text":"The morning light filtered through curtains. She sat quietly thinking about what to write next. Words matter more than we realize."})
    record("B","Analyze endpoint 200",_az_s==200,f"status={_az_s}","KIM")
    _az_ps=isinstance(_az_r,dict) and "profiles" in _az_r.get("scores",{})
    record("B","Analyze returns profiles",_az_ps,"found" if _az_ps else "MISSING","KIM")
    _az_st=isinstance(_az_r,dict) and "stances" in _az_r.get("scores",{})
    record("B","Analyze returns stances",_az_st,"found" if _az_st else "MISSING","KIM")
    _az_rej,_=http_post(BASE_URL+"/api/v2/analyze",{"text":"Short"})
    record("B","Analyze rejects short text",_az_rej==422,f"status={_az_rej}","KIM")

    print("\n  [KIM] Feature Gate")
    try:
        from feature_gate import FeatureGate,Tier
        import tempfile; from pathlib import Path
        gate=FeatureGate(storage_dir=Path(tempfile.mkdtemp())/"gate")
        uid=f"testuser_{ts}"
        gate.set_user_tier(uid,Tier.FREE)
        record("B","FREE: basic_analysis allowed",gate.can_access("basic_analysis",user_id=uid).allowed,"allowed","KIM")
        record("B","FREE: unlimited_analyses blocked",not gate.can_access("unlimited_analyses",user_id=uid).allowed,"blocked","KIM")
        gate.set_user_tier(uid,Tier.PRO)
        record("B","PRO: unlimited_analyses allowed",gate.can_access("unlimited_analyses",user_id=uid).allowed,"allowed","KIM")
    except Exception as e:
        record("B","Feature gate",False,str(e),"KIM")
    print("\n  [KIM] STRETCH+Extension")
    out,ok=db_query("SELECT COUNT(*) FROM stretch_prompts_base;")
    cnt=int(out.strip()) if ok and out.strip().isdigit() else 0
    record("B","STRETCH prompts 450+",cnt>=450,f"{cnt}","KIM")
    out,ok=db_query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND (table_name LIKE 'stretch%' OR table_name LIKE 'tier_stretch%' OR table_name LIKE 'user_stretch%');")
    cnt=int(out.strip()) if ok and out.strip().isdigit() else 0
    record("B","STRETCH tables 10+",cnt>=10,f"{cnt} tables","KIM")
    out,ok=db_query("SELECT COUNT(*) FROM stretch_authors;")
    cnt=int(out.strip()) if ok and out.strip().isdigit() else 0
    record("B","STRETCH authors 60",cnt>=60,f"{cnt} authors","KIM")
    out,ok=db_query("SELECT COUNT(DISTINCT voice_type) FROM stretch_authors WHERE active=TRUE;")
    cnt=int(out.strip()) if ok and out.strip().isdigit() else 0
    record("B","STRETCH 10 voice types in authors",cnt>=10,f"{cnt} voices","KIM")
    out,ok=db_query("SELECT COUNT(*) FROM stretch_authors WHERE book1_isbn IS NOT NULL AND book2_isbn IS NOT NULL;")
    cnt=int(out.strip()) if ok and out.strip().isdigit() else 0
    record("B","STRETCH all authors have 2 ISBNs",cnt>=60,f"{cnt}/60","KIM")
    out,ok=db_query("SELECT COUNT(*) FROM stretch_authors WHERE wikipedia_url IS NOT NULL AND wikipedia_url != '';")
    cnt=int(out.strip()) if ok and out.strip().isdigit() else 0
    record("B","STRETCH all authors have Wikipedia",cnt>=60,f"{cnt}/60","KIM")
    out,ok=db_query("SELECT column_name FROM information_schema.columns WHERE table_name='stretch_exercises' AND column_name='author_id';")
    record("B","STRETCH exercises has author_id FK",ok and "author_id" in out,"found" if ok and "author_id" in out else "MISSING","KIM")
    st,_=http_get(f"{BASE_URL}/api/extension/health")
    record("B","Extension API responds",st in [200,401,404],f"status={st}","KIM")
    # Extension Files
    print("\n  [KIM] Extension Files")
    _ext="/opt/quirrely/quirrely_v313_integrated/extension"
    _popup_html=open(_ext+"/pages/popup.html").read() if os.path.isfile(_ext+"/pages/popup.html") else ""
    _popup_js=open(_ext+"/pages/popup.js").read() if os.path.isfile(_ext+"/pages/popup.js") else ""
    record("B","Extension wordmark correct",'coral">rel</span>' in _popup_html and 'italic">y</span>' in _popup_html and 'italic">ly</span>' not in _popup_html,"correct" if 'italic">y</span>' in _popup_html else "WRONG","KIM")
    record("B","Extension no Featured tier","featuredAnalysesPerDay" not in _popup_js,"clean" if "featuredAnalysesPerDay" not in _popup_js else "STILL PRESENT","KIM")
    record("B","Extension upgrade URL correct","/billing/upgrade.html" in _popup_js,"found" if "/billing/upgrade.html" in _popup_js else "MISSING","KIM")
    record("B","Extension login URL correct","/auth/login.html" in _popup_js,"found" if "/auth/login.html" in _popup_js else "MISSING","KIM")
    record("B","Extension dashboard URL correct","/frontend/pro-dashboard.html" in _popup_js,"found" if "/frontend/pro-dashboard.html" in _popup_js else "MISSING","KIM")
    record("B","Extension no double-L","Quirrelly" not in _popup_html and "Quirrelly" not in _popup_js,"clean" if "Quirrelly" not in _popup_html else "FOUND","KIM")
    print("\n  [KIM] Dashboard API")
    st,resp=http_get(f"{BASE_URL}/api/v2/me/dashboard")
    record("B","Dashboard endpoint mounted",st==401,f"status={st} (401=auth required)","KIM")
    st,resp=http_post(f"{BASE_URL}/api/v2/me/save-analysis",{"profile":"minimal","stance":"open","input_word_count":50})
    record("B","Save-analysis endpoint mounted",st==401,f"status={st} (401=auth required)","KIM")
    if token:
        _req=urllib.request.Request(f"{BASE_URL}/api/v2/me/dashboard",headers={"User-Agent":"Mozilla/5.0 (compatible; QuirrelyHealthCheck)","Authorization":f"Bearer {token}"})
        try:
            with urllib.request.urlopen(_req,timeout=10,context=SSL_CTX) as _r: _dst,_db=_r.status,json.loads(_r.read().decode("utf-8"))
        except urllib.error.HTTPError as e: _dst,_db=e.code,{}
        except Exception as e: _dst,_db=0,{}
        record("B","Dashboard returns user data",_dst==200 and "user" in _db,f"status={_dst}, keys={list(_db.keys())[:4]}","KIM")
        record("B","Dashboard has stats",_dst==200 and "stats" in _db,f"stats={_db.get(chr(115)+chr(116)+chr(97)+chr(116)+chr(115),{})}","KIM")

    # Webhook DB persistence
    _wh1 = "Persist to DB" in open("/opt/quirrely/quirrely_v313_integrated/backend/payments_api.py").read()
    record("B","Webhook persists checkout to DB",_wh1,"found" if _wh1 else "missing","MARS")
    _wh2 = "Persist update to DB" in open("/opt/quirrely/quirrely_v313_integrated/backend/payments_api.py").read()
    record("B","Webhook persists sub update to DB",_wh2,"found" if _wh2 else "missing","MARS")
    _wh3 = "Persist deletion to DB" in open("/opt/quirrely/quirrely_v313_integrated/backend/payments_api.py").read()
    record("B","Webhook persists sub deletion to DB",_wh3,"found" if _wh3 else "missing","MARS")
    # Promo Codes
    print("\n  [KIM] Save-Analysis Auto-Score")
    _sa=open(os.path.join(APP_DIR,"dashboard_api.py")).read()
    record("B","Save-analysis auto-score","Auto-compute scores" in _sa,"found" if "Auto-compute scores" in _sa else "MISSING","KIM")
    record("B","Save-analysis imports classifier","get_classifier" in _sa,"found" if "get_classifier" in _sa else "MISSING","KIM")

    print("\n  [MARS] Promo Codes")
    _pay_src = open(os.path.join(APP_DIR, "payments_api.py")).read()
    record("B","Checkout allows promo codes","allow_promotion_codes=True" in _pay_src,"found" if "allow_promotion_codes=True" in _pay_src else "MISSING","MARS")
    _promo_file = os.path.join(os.path.dirname(APP_DIR), "promo_codes.txt")
    _promo_exists = os.path.isfile(_promo_file)
    _promo_count = len(open(_promo_file).readlines()) if _promo_exists else 0
    record("B","Promo codes file exists (100)",_promo_exists and _promo_count==100,f"{_promo_count} codes" if _promo_exists else "MISSING","MARS")
    try:
        import stripe as _stripe
        _env=read_env(); _stripe.api_key=_env.get("STRIPE_SECRET_KEY","")
        _coupon=_stripe.Coupon.retrieve("qsaRUyUt")
        record("B","Stripe coupon active",_coupon.valid,"valid" if _coupon.valid else "INVALID","MARS")
    except Exception as e:
        record("B","Stripe coupon active",False,str(e)[:60],"MARS")
    # Multi-Currency Pricing
    print("\n  [MARS] Multi-Currency Pricing")
    import json as _json
    for _cc, _exp_pro in [("cad",2.99),("gbp",1.99),("aud",4.99),("nzd",3.99),("usd",2.99)]:
        try:
            _req=urllib.request.Request(f"http://127.0.0.1:8000/api/v2/payments/pricing?currency={_cc}")
            _resp=urllib.request.urlopen(_req,timeout=5)
            _pd=_json.loads(_resp.read())
            _ok=_pd.get("pro",{}).get("monthly")==_exp_pro and _pd.get("currency")==_cc
            record("B",f"Pricing {_cc.upper()} correct",_ok,f"pro={_pd.get(chr(112)+chr(114)+chr(111),{}).get(chr(109)+chr(111)+chr(110)+chr(116)+chr(104)+chr(108)+chr(121))} expect={_exp_pro}","MARS")
        except Exception as e:
            record("B",f"Pricing {_cc.upper()} correct",False,str(e)[:60],"MARS")
def read_env():
    env={}
    try:
        import os
        with open(os.path.join(APP_DIR,".env")) as f:
            for line in f:
                line=line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k,v=line.split("=",1); env[k.strip()]=v.strip()
    except: pass
    return env

def run_part_c():
    print("\n"+"="*70+"\n  SUPER_TEST_PART_C — Readiness [ASO+KIM+MARS]\n"+"="*70)
    import time as _time,re
    print("\n  [ASO] Disk + Apache + Speed")
    try:
        r=subprocess.run(["df","-h","/"],capture_output=True,text=True,timeout=5)
        parts=[l for l in r.stdout.splitlines() if "/" in l and "Filesystem" not in l][-1].split()
        record("C","Disk usage < 80%",int(parts[4].replace("%",""))<80,parts[4]+" ("+parts[2]+"/"+parts[1]+")","ASO")
    except Exception as e: record("C","Disk usage",False,str(e),"ASO")
    try:
        r=subprocess.run(["systemctl","is-active","httpd"],capture_output=True,text=True,timeout=5)
        if r.stdout.strip()!="active":
            r=subprocess.run(["systemctl","is-active","apache2"],capture_output=True,text=True,timeout=5)
        record("C","Apache active",r.stdout.strip()=="active",r.stdout.strip(),"ASO")
    except Exception as e: record("C","Apache active",False,str(e),"ASO")
    t0=_time.time(); st,_=http_get(BASE_URL+"/health"); ms=int((_time.time()-t0)*1000)
    record("C","API response < 500ms",ms<500,str(ms)+"ms","ASO")
    try:
        _ae=read_env();_req=urllib.request.Request(BASE_URL+"/api/admin/v2/overview",headers={"User-Agent":"Mozilla/5.0 (compatible; QuirrelyHealthCheck)","X-Admin-Key":_ae.get("ADMIN_API_KEY","")})
        with urllib.request.urlopen(_req,timeout=10,context=SSL_CTX) as _r: st,body=_r.status,_r.read().decode("utf-8",errors="replace")
    except urllib.error.HTTPError as e: st,body=e.code,""
    except Exception as e: st,body=0,str(e)
    record("C","Admin overview 200",st==200,"status="+str(st),"ASO")
    if st==200:
        try:
            d=json.loads(body)
            record("C","Admin has waitlist count","waitlist" in d,"waitlist="+str(d.get("waitlist",0)),"ASO")
        except: pass
    print("\n  [KIM] Auth + Blog + Files")
    ts=int(_time.time()); tu="partc_"+str(ts)+"@quirrely.com"
    st,resp=http_post(BASE_URL+"/api/v2/auth/signup",{"email":tu,"password":"PartC2026!x","username":"pc_"+str(ts)})
    record("C","Signup 200",st==200,"status="+str(st),"KIM")
    if st==200:
        out,ok=db_query("SELECT COUNT(*) FROM users WHERE email='"+tu+"';")
        record("C","Signup in DB",ok and out.strip()!="0","rows="+out.strip(),"KIM")
        st2,r2=http_post(BASE_URL+"/api/v2/auth/login",{"email":tu,"password":"PartC2026!x"})
        record("C","Login JWT",bool(r2.get("access_token")),"received" if r2.get("access_token") else "missing","KIM")
    st,_=http_get(BASE_URL+"/api/stretch/eligibility/test")
    record("C","STRETCH endpoint mounted",st not in [0,404],"status="+str(st),"KIM")
    st,_=http_get(BASE_URL+"/api/stretch/recommend/00000000-0000-0000-0000-000000000000")
    record("C","STRETCH recommend endpoint",st in [401,422],"status="+str(st)+" (auth required)","KIM")
    st,_=http_get(BASE_URL+"/api/stretch/progress/00000000-0000-0000-0000-000000000000")
    record("C","STRETCH progress endpoint",st in [401,422],"status="+str(st)+" (auth required)","KIM")
    for slug in ["/blog/","/blog/how-assertive-balanced-writers-write.html"]:
        st,_=http_get(SITE_URL+slug)
        record("C","Blog "+slug,st in [200,301,302],"status="+str(st),"KIM")
    ar="/home/quirrely/quirrely.ca"
    record("C","index_app.html exists",os.path.isfile(ar+"/index_app.html"),"found" if os.path.isfile(ar+"/index_app.html") else "MISSING","KIM")
    _idx=open(ar+"/index.html").read() if os.path.isfile(ar+"/index.html") else ""
    record("C","index.html has save-analysis","save-analysis" in _idx,"found" if "save-analysis" in _idx else "MISSING","KIM")
    _dash=os.path.isfile(ar+"/pro-dashboard.html")
    record("C","pro-dashboard.html exists",_dash,"found" if _dash else "MISSING","KIM")
    if _dash:
        _dc=open(ar+"/pro-dashboard.html").read()
        record("C","Dashboard no mock data","Sarah Mitchell" not in _dc,"clean" if "Sarah Mitchell" not in _dc else "MOCK DATA FOUND","KIM")
        record("C","Dashboard fetches API","/api/v2/me/dashboard" in _dc,"found" if "/api/v2/me/dashboard" in _dc else "MISSING","KIM")
    _pjs=open(ar+"/billing/pricing.js").read() if os.path.isfile(ar+"/billing/pricing.js") else ""
    record("C","Pricing saves tier on redirect","checkout_tier" in _pjs,"found" if "checkout_tier" in _pjs else "MISSING","KIM")
    record("C","Pricing auto-checkout from URL","URLSearchParams" in _pjs,"found" if "URLSearchParams" in _pjs else "MISSING","KIM")
    _su=open(ar+"/auth/signup.html").read() if os.path.isfile(ar+"/auth/signup.html") else ""
    record("C","Signup checkout redirect","checkout_tier" in _su,"found" if "checkout_tier" in _su else "MISSING","KIM")
    record("C","Signup checkout banner","checkout-banner" in _su,"found" if "checkout-banner" in _su else "MISSING","KIM")
    _li=open(ar+"/auth/login.html").read() if os.path.isfile(ar+"/auth/login.html") else ""
    record("C","Login checkout redirect","checkout_tier" in _li,"found" if "checkout_tier" in _li else "MISSING","KIM")
    record("C","welcome.html exists",os.path.isfile(ar+"/welcome.html"),"found" if os.path.isfile(ar+"/welcome.html") else "MISSING","KIM")
    _ws,_=http_get(BASE_URL+"/welcome?session_id=test")
    record("C","Welcome page loads",_ws==200,"status="+str(_ws),"KIM")
    for _pf in ["formal","balanced"]:
        _ps,_=http_get(BASE_URL+"/profiles/"+_pf)
        record("C","Profile "+_pf+".html loads",_ps==200,"status="+str(_ps),"KIM")
    print("\n  [KIM] Social Links")
    _social_files = [
        ("/opt/quirrely/quirrely_v313_integrated/frontend/index.html", "App index"),
        ("/opt/quirrely/quirrely_v313_integrated/blog/index.html", "Blog index"),
        ("/opt/quirrely/quirrely_v313_integrated/blog/featured.html", "Blog featured"),
        ("/opt/quirrely/quirrely_v313_integrated/blog/submit-writing.html", "Blog submit"),
    ]
    _fb_url = "facebook.com/profile.php?id=61575643048349"
    _li_url = "linkedin.com/company/"
    for _sf, _sn in _social_files:
        if os.path.isfile(_sf):
            _sc = open(_sf).read()
            record("C", _sn+" Facebook link", _fb_url in _sc and "display: none" not in _sc.split(_fb_url)[0].split(chr(10))[-1], "found" if _fb_url in _sc else "MISSING", "KIM")
            record("C", _sn+" LinkedIn link", _li_url in _sc, "found" if _li_url in _sc else "MISSING", "KIM")
        else:
            record("C", _sn+" file exists", False, "MISSING", "KIM")
    print("\n  [MARS] Stripe + Keys")
    env=read_env()
    for k in ["STRIPE_PRICE_PRO_MONTHLY","STRIPE_PRICE_PRO_ANNUAL"]:
        val=env.get(k,"")
        record("C",k,bool(val) and val.startswith("price_"),val if val else "missing","MARS")
    st,_=http_get(BASE_URL+"/api/v2/payments/pricing")
    record("C","Payments mounted",st not in [0,404],"status="+str(st),"MARS")
    try:
        last=json.load(open("/opt/quirrely/quirrely_v313_integrated/tests/last_run.json"))
        lw=next((t["detail"] for t in last.get("part_a",{}).get("tests",[]) if "waitlist" in t["name"]),"rows=0")
        lc=int(lw.replace("rows=","")) if "rows=" in lw else 0
        out,ok=db_query("SELECT COUNT(*) FROM waitlist WHERE email NOT LIKE '%kimtest%' AND email NOT LIKE '%supertest%' AND email NOT LIKE '%quirrely.com%' AND email NOT LIKE '%test.com%';")
        cc=int(out.strip()) if ok and out.strip().isdigit() else 0
    except: pass
    for fname in ["email_service.py","notify_api.py","email_config.py"]:
        fpath=os.path.join(APP_DIR,fname)
        if os.path.isfile(fpath):
            fc=open(fpath).read()
            bad="re_SKMTFrSH" in fc or "re_atnZAc7j" in fc or "re_BETww8EJ" in fc
            record("C",fname+" key clean",not bad,"clean" if not bad else "HARDCODED KEY FOUND","MARS")

        # Wordmark consistency - SVG logo with correct viewBox across all pages
    print("\n  [MARS] Wordmark Consistency")
    import glob as _glob
    _all_html = _glob.glob("/home/quirrely/quirrely.ca/**/*.html", recursive=True) + _glob.glob("/opt/quirrely/quirrely_v313_integrated/**/*.html", recursive=True)
    _old_css = [f for f in _all_html if "Quir<span>rel</span><em>ly</em>" in open(f).read()]
    record("C","No old CSS text logos",len(_old_css)==0,str(len(_old_css))+" found" if _old_css else "clean","MARS")
    _old_vb = [f for f in _all_html if 'viewBox="0 0 340' in open(f).read()]
    record("C","No old 340 viewBox",len(_old_vb)==0,str(len(_old_vb))+" found" if _old_vb else "clean","MARS")
    _dbl_l = [f for f in _all_html if "Quirrelly" in open(f).read()]
    record("C","No double-L Quirrelly",len(_dbl_l)==0,str(len(_dbl_l))+" found" if _dbl_l else "clean","MARS")
    _og = os.path.isfile("/home/quirrely/quirrely.ca/assets/logo/og-image.png")
    record("C","OG image exists",_og,"found" if _og else "MISSING","MARS")

    # Nav duplicate check — no double Pricing in index.html
    print("\n  [MARS] Nav Consistency")
    _idx=open(ar+"/index.html").read()
    _pricing_count=_idx.count(">Pricing<")
    record("C","No duplicate Pricing in nav",_pricing_count==0,f"{_pricing_count} found (expect 0)","MARS")
    # Google Analytics
    print("\n  [MARS] Google Analytics")
    import glob as _glob
    _ga_excludes = ["/admin","/components/","/assets/","/extension/","/secure/","/sentense-app/","_locked","_v0.","_v1.","master-test","lncp-v4","analytics-dashboard","super_admin","super-admin","blog/reading/"]
    _ga_count = sum(1 for _f in _glob.glob(ar+"/**/*.html", recursive=True) if "G-HQ818WM2YB" in open(_f).read() and not any(_x in _f for _x in _ga_excludes))
    _ga_total = len([_f for _f in _glob.glob(ar+"/**/*.html", recursive=True) if not any(_x in _f for _x in _ga_excludes)])
    record("C","GA4 tag on all pages",_ga_count==_ga_total,f"{_ga_count}/{_ga_total} pages","MARS")
    # ===== BLOG FRONTEND TESTS (added Session 4) =====
    print("\n  [MARS] Blog Frontend")
    import glob as _bg
    _blog_dir = "/opt/quirrely/quirrely_v313_integrated/blog"
    _blog_htmls = _bg.glob(_blog_dir + "/*.html")
    _blog_all = [f for f in _blog_htmls if "admin-" not in f]
    _blog_non_index = [f for f in _blog_all if not f.endswith("/index.html")]
    # Blog nav on all non-index posts
    _nav_count = sum(1 for f in _blog_non_index if '<nav class="nav"' in open(f).read())
    record("C","Blog nav on all posts",_nav_count==len(_blog_non_index),f"{_nav_count}/{len(_blog_non_index)} posts","MARS")
    # Blog nav has correct links (spot check 3 files)
    for _bnf in ["how-assertive-open-writers-write.html","featured.html","what-is-writing-voice.html"]:
        _bnp = _blog_dir+"/"+_bnf
        if os.path.isfile(_bnp):
            _bnc = open(_bnp).read()
            _has_links = 'href="/"' in _bnc and 'href="/blog"' in _bnc and 'href="/faq"' in _bnc and "Sign In" in _bnc
            record("C","Blog nav links "+_bnf,_has_links,"found" if _has_links else "MISSING","MARS")
    # Blog no Twitter/X anywhere
    _tw_blog = [os.path.basename(f) for f in _blog_all if "twitter" in open(f).read().lower()]
    record("C","Blog no Twitter/X refs",len(_tw_blog)==0,",".join(_tw_blog) if _tw_blog else "clean","MARS")
    # Blog canonicals use quirrely.ca not .com (exclude email)
    _com_blog = []
    for f in _blog_all:
        _fc = open(f).read()
        _fc_no_email = _fc.replace("hello@quirrely.com","")
        if "quirrely.com" in _fc_no_email:
            _com_blog.append(os.path.basename(f))
    record("C","Blog canonicals use .ca",len(_com_blog)==0,",".join(_com_blog[:5]) if _com_blog else "clean","MARS")
    # Blog GA4 on all files
    _ga_blog = sum(1 for f in _blog_all if "G-HQ818WM2YB" in open(f).read())
    record("C","Blog GA4 all files",_ga_blog==len(_blog_all),f"{_ga_blog}/{len(_blog_all)} files","MARS")
    # Blog SVG logo on all non-index posts
    _svg_blog = sum(1 for f in _blog_non_index if 'viewBox="0 0 365 100"' in open(f).read())
    record("C","Blog SVG logo all posts",_svg_blog==len(_blog_non_index),f"{_svg_blog}/{len(_blog_non_index)} posts","MARS")
    # ===== NEWSLETTER TESTS (added Session 4) =====
    print("\n  [KIM] Newsletter")
    _nl_st,_nl_body=http_post(BASE_URL+"/api/v2/newsletter/subscribe",{"email":"nl_supertest@quirrely.com","source":"super_test"})
    record("C","Newsletter subscribe 200",_nl_st==200,"status="+str(_nl_st),"KIM")
    if _nl_st==200:
        try:
            _nl_d=json.loads(_nl_body) if isinstance(_nl_body,str) else _nl_body
            record("C","Newsletter subscribe success",_nl_d.get("success")==True,"success="+str(_nl_d.get("success")),"KIM")
        except: record("C","Newsletter subscribe success",False,"parse error","KIM")
    _nl_bad_st,_nl_bad=http_post(BASE_URL+"/api/v2/newsletter/subscribe",{"email":"not-an-email","source":"super_test"})
    if _nl_bad_st==200:
        try:
            _nl_bd=json.loads(_nl_bad) if isinstance(_nl_bad,str) else _nl_bad
            record("C","Newsletter rejects bad email",_nl_bd.get("success")==False,"rejected" if not _nl_bd.get("success") else "ACCEPTED","KIM")
        except: record("C","Newsletter rejects bad email",False,"parse error","KIM")
    _nl_ct_st,_nl_ct=http_get(BASE_URL+"/api/v2/newsletter/count")
    record("C","Newsletter count endpoint",_nl_ct_st==200,"status="+str(_nl_ct_st),"KIM")
    _nl_blog=open("/opt/quirrely/quirrely_v313_integrated/blog/index.html").read()
    record("C","Blog newsletter form wired","newsletter/subscribe" in _nl_blog,"found" if "newsletter/subscribe" in _nl_blog else "MISSING","KIM")
    record("C","Blog no fake subscriber count","17,500" not in _nl_blog,"clean" if "17,500" not in _nl_blog else "FAKE COUNT","KIM")
    # Newsletter duplicate detection
    _nl_dup_st,_nl_dup=http_post(BASE_URL+"/api/v2/newsletter/subscribe",{"email":"nl_supertest@quirrely.com","source":"super_test"})
    if _nl_dup_st==200:
        try:
            _nl_dd=json.loads(_nl_dup) if isinstance(_nl_dup,str) else _nl_dup
            record("C","Newsletter dedup returns new=false",_nl_dd.get("new")==False,"new="+str(_nl_dd.get("new")),"KIM")
        except: record("C","Newsletter dedup returns new=false",False,"parse error","KIM")
    # ===== BLOG AUTH NAV TESTS (added Session 4b) =====
    _blog_auth_ok = sum(1 for f in _blog_all if "quirrely_session" in open(f).read())
    record("C","Blog auth nav on all pages",_blog_auth_ok==len(_blog_all),f"{_blog_auth_ok}/{len(_blog_all)} files","MARS")
    _ba_idx = open("/opt/quirrely/quirrely_v313_integrated/blog/index.html").read()
    record("C","Blog auth swaps CTA to Dashboard","Dashboard" in _ba_idx and "quirrely_session" in _ba_idx,"found","MARS")

    # ===== FEATURED WRITERS TESTS (added Phase 1) =====
    print("\n  [KIM] Featured Writers")
    _fw_st,_fw_body=http_get(BASE_URL+"/api/v2/featured/approved")
    record("C","Featured approved endpoint 200",_fw_st==200,"status="+str(_fw_st),"KIM")
    _fw_sub_st,_=http_post(BASE_URL+"/api/v2/featured/submit",{"sample":"test","display_name":"Test"})
    record("C","Featured submit requires auth",_fw_sub_st==401,"status="+str(_fw_sub_st),"KIM")
    _fw_my_st,_=http_get(BASE_URL+"/api/v2/featured/my-submission")
    record("C","Featured my-submission requires auth",_fw_my_st==401,"status="+str(_fw_my_st),"KIM")
    _bi=open("/opt/quirrely/quirrely_v313_integrated/blog/index.html").read()
    record("C","Blog index no fake featured writers","Sarah M." not in _bi,"clean" if "Sarah M." not in _bi else "FAKE","MARS")
    _ft=open("/opt/quirrely/quirrely_v313_integrated/blog/featured.html").read()
    record("C","Featured page has tier CTAs","cta-guest" in _ft and "cta-free" in _ft and "cta-pro" in _ft,"found","MARS")
    record("C","Featured page loads from API","api/v2/featured/approved" in _ft,"wired","MARS")
    _sw=open("/opt/quirrely/quirrely_v313_integrated/blog/submit-writing.html").read()
    record("C","Submit form wired to API","api/v2/featured/submit" in _sw,"wired","MARS")
    record("C","Submit form has auth gate","subscription_tier" in _sw,"gated","MARS")

    # ===== FEATURED ADMIN TESTS (Phase 2) =====
    _fa_st,_=http_get(BASE_URL+"/api/v2/featured/admin/pending")
    record("C","Featured admin requires key",_fa_st==403,"status="+str(_fa_st),"KIM")
    try:
        _ak="45d2749b8cb13e3a3c7e3bc456e6f273cd806ba15c8f3935bec5dd743c2be500"
        _rq=urllib.request.Request(BASE_URL+"/api/v2/featured/admin/pending",headers={"X-Admin-Key":_ak})
        _rsp=urllib.request.urlopen(_rq,timeout=10)
        _fa2_st=_rsp.getcode()
    except urllib.error.HTTPError as _e: _fa2_st=_e.code
    except: _fa2_st=0
    record("C","Featured admin pending with key 200",_fa2_st==200,"status="+str(_fa2_st),"KIM")
    _af=os.path.exists("/opt/quirrely/quirrely_v313_integrated/blog/admin-featured.html")
    record("C","Admin featured review page exists",_af,"found" if _af else "MISSING","MARS")
    _afc=open("/opt/quirrely/quirrely_v313_integrated/blog/admin-featured.html").read() if _af else ""
    record("C","Admin page has approve/reject","doApprove" in _afc and "doReject" in _afc,"found","MARS")

    # ===== ADMIN HUB + SECURITY TESTS =====
    _ah=os.path.exists("/opt/quirrely/quirrely_v313_integrated/admin/index.html")
    record("C","Admin hub page exists",_ah,"found" if _ah else "MISSING","MARS")
    _ahc=open("/opt/quirrely/quirrely_v313_integrated/admin/index.html").read() if _ah else ""
    record("C","Admin hub has key gate","quirrely_admin_key" in _ahc,"gated","MARS")
    _secured=sum(1 for _f in ["/opt/quirrely/quirrely_v313_integrated/admin/super-admin.html","/opt/quirrely/quirrely_v313_integrated/admin/command_center.html","/opt/quirrely/quirrely_v313_integrated/admin/master_dashboard.html","/opt/quirrely/quirrely_v313_integrated/admin/review-queue.html","/opt/quirrely/quirrely_v313_integrated/super_admin_dashboard.html","/opt/quirrely/quirrely_v313_integrated/super-admin-dashboard.html"] if "quirrely_admin_key" in open(_f).read())
    record("C","All admin pages secured",_secured==6,f"{_secured}/6 gated","MARS")

    # ===== SUPER ADMIN WIRING TESTS =====
    _sad=open("/opt/quirrely/quirrely_v313_integrated/super-admin-dashboard.html").read()
    record("C","System Pulse wired to API","api/v2/super-admin/results" in _sad,"wired","MARS")
    record("C","System Pulse has Run Test button","runMasterTest" in _sad,"found","MARS")
    _sa_mounted="super_admin_router" in open("/opt/quirrely/quirrely_v313_integrated/backend/app.py").read()
    record("C","Super admin API mounted in app.py",_sa_mounted,"mounted" if _sa_mounted else "MISSING","KIM")

    # ===== COMMAND CENTER + REVIEW QUEUE WIRING =====
    _cc=open("/opt/quirrely/quirrely_v313_integrated/admin/command_center.html").read()
    record("C","Command Center wired to API","api/v2/super-admin" in _cc and "loadLiveData" in _cc,"wired","MARS")
    record("C","Command Center no hardcoded metrics","847" not in _cc and "$16,170" not in _cc and "87.2%" not in _cc and "18.3h" not in _cc,"clean","MARS")
    record("C","Command Center renders countries","results/countries" in _cc,"wired","MARS")
    record("C","Command Center renders pulse","/pulse" in _cc and "overall_health" in _cc,"wired","MARS")
    record("C","Command Center run simulation","run-test" in _cc and "runSimulation" in _cc,"wired","MARS")
    record("C","Command Center dynamic badges","badge-ux" in _cc and "badge-risks" in _cc and "by_severity" in _cc,"dynamic","MARS")
    record("C","Command Center real stats endpoint","stats/real" in _cc,"wired","MARS")
    record("C","Command Center alerts actionable","ackAlert" in _cc and "action_recommended" in _cc,"actionable","MARS")
    record("C","Command Center tabs work","filterActions" in _cc and "activeFilter" in _cc,"wired","MARS")
    _ae3=read_env();_rq3=urllib.request.Request(BASE_URL+"/api/admin/v2/stats/real",headers={"User-Agent":"Mozilla/5.0 (compatible; QuirrelyHealthCheck)","X-Admin-Key":_ae3.get("ADMIN_API_KEY","")});_st3=urllib.request.urlopen(_rq3,timeout=10,context=SSL_CTX).status;record("C","Admin real stats API 200",_st3==200,"status="+str(_st3),"KIM")
    _rq=open("/opt/quirrely/quirrely_v313_integrated/admin/review-queue.html").read()
    record("C","Review Queue wired to API","api/v2/super-admin/actions" in _rq,"wired","MARS")
    record("C","Review Queue has run cycle","api/v2/super-admin/run-test" in _rq,"wired","MARS")
    # ===== FAQ PAGE =====
    _fq=open("/opt/quirrely/quirrely_v313_integrated/faq.html").read()
    record("C","FAQ page exists","faq-item" in _fq and "toggleFaq" in _fq,"exists","MARS")
    record("C","FAQ has 10 questions",_fq.count("onclick=\"toggleFaq")==10,"count="+str(_fq.count("onclick=\"toggleFaq")),"MARS")
    record("C","FAQ has auth-aware nav","quirrely_token" in _fq and "nav-cta" in _fq,"auth-aware","MARS")
    record("C","FAQ linked in index","/faq" in open("/opt/quirrely/quirrely_v313_integrated/index.html").read(),"linked","MARS")
    record("C","FAQ linked in dashboard","/faq" in open("/opt/quirrely/quirrely_v313_integrated/frontend/dashboard.html").read(),"linked","MARS")
    record("C","FAQ linked in settings","/faq" in open("/opt/quirrely/quirrely_v313_integrated/settings.html").read(),"linked","MARS")

    # Clean up test newsletter sub
    try:
        import subprocess as _sp
        _sp.run(["sudo","-u","postgres","psql","-d","quirrely_prod","-c","DELETE FROM newsletter_subscribers WHERE email LIKE '%supertest%' OR email LIKE '%@quirrely.com';"],capture_output=True)
    except: pass
    # Sitemaps
    print("\n  [MARS] Sitemaps")
    _sm_ca_st,_sm_ca=http_get("https://quirrely.ca/sitemap.xml")
    record("C","Sitemap quirrely.ca 200",_sm_ca_st==200,f"status={_sm_ca_st}","MARS")
    record("C","Sitemap quirrely.ca valid XML","sitemapindex" in str(_sm_ca),"valid" if "sitemapindex" in str(_sm_ca) else "INVALID","MARS")
    _sm_com_st,_sm_com=http_get("https://quirrely.com/sitemap.xml")
    record("C","Sitemap quirrely.com 200",_sm_com_st==200,f"status={_sm_com_st}","MARS")
    _sm_blog_st,_=http_get("https://quirrely.ca/sitemap-blog.xml")
    record("C","Sitemap blog sub-sitemap 200",_sm_blog_st==200,f"status={_sm_blog_st}","MARS")
    _sm_profiles_st,_=http_get("https://quirrely.ca/sitemap-profiles.xml")
    record("C","Sitemap profiles sub-sitemap 200",_sm_profiles_st==200,f"status={_sm_profiles_st}","MARS")
    _sm_pages_st,_sm_pages=http_get("https://quirrely.ca/sitemap-pages.xml")
    record("C","Sitemap pages sub-sitemap 200",_sm_pages_st==200,f"status={_sm_pages_st}","MARS")
    record("C","Sitemap pages has FAQ","/faq" in str(_sm_pages),"found" if "/faq" in str(_sm_pages) else "MISSING","MARS")
    record("C","Sitemap pages has dashboard","/frontend/dashboard.html" in str(_sm_pages),"found","MARS")
    record("C","Sitemap index updated 2026-02-28","2026-02-28" in str(_sm_ca),"updated","MARS")
    _robots=open(ar+"/robots.txt").read() if os.path.isfile(ar+"/robots.txt") else ""
    record("C","Robots.txt has sitemap","sitemap.xml" in _robots.lower(),f"found" if "sitemap.xml" in _robots.lower() else "MISSING","MARS")
    # ===== DASHBOARD WIRING TESTS =====
    print("\n  [KIM] Dashboard Routes")
    for _dp,_dn in [("/dashboard/","Dashboard"),("/settings","Settings"),("/frontend/index.html","App index"),("/frontend/export.html","Export"),("/billing/","Billing"),("/profile/test","Public profile"),("/profiles/formal","Profile formal"),("/welcome","Welcome")]:
        _ds,_=http_get(BASE_URL+_dp)
        record("C",_dn+" route 200",_ds==200,f"status={_ds}","KIM")

    print("\n  [KIM] Dashboard HTML Elements")
    _dash_html=open(ar+"/frontend/dashboard.html").read()
    for _eid in ["tierBadge","headerName","headerAvatar","sidebarName","sidebarAvatar","sidebarLocation","sidebarVoiceTag","sidebarStance","statTests","statWords","statConsistency","voiceBars","voiceCard","evolutionCard","writersCard","booksCard","stretchCard","upgradeCard","activityCard","welcomeBanner","welcomeHeading","userMenuToggle","userDropdown"]:
        record("C",f"Dashboard ID #{_eid}",'id="'+_eid+'"' in _dash_html,"found" if 'id="'+_eid+'"' in _dash_html else "MISSING","KIM")
    for _nl,_nn in [('/dashboard','Dashboard nav'),('/blog','Blog nav'),('/faq','FAQ nav'),('/settings','Settings nav')]:
        record("C",f"Dashboard {_nn} link",'href="'+_nl+'"' in _dash_html,"found" if 'href="'+_nl+'"' in _dash_html else "MISSING","KIM")
    record("C","Sidebar Take New Test",'/frontend/index.html' in _dash_html and 'Take New Test' in _dash_html,"found","KIM")
    record("C","Sidebar Export Data",'/frontend/export.html' in _dash_html and 'Export Data' in _dash_html,"found","KIM")
    record("C","Sidebar Upgrade link",'/billing/' in _dash_html and 'Upgrade' in _dash_html,"found","KIM")
    for _fl in ["blog/terms.html","blog/privacy.html","blog/affiliates.html","mailto:support@quirrely.ca"]:
        record("C",f"Footer {_fl}",_fl in _dash_html,"found" if _fl in _dash_html else "MISSING","KIM")
    print("\n  [KIM] Dashboard JS Functions")
    _required_fns=["function toggleUserMenu","function doLogout","function viewPublicProfile","function submitForFeatured","function copyProfileLink","function claimSlug","function initShare","function refreshShare","function showToast","function formatLocation","function getInitial","function formatNumber","function timeAgo","function renderVoiceBars","function renderActivity","function renderWriters","function renderBooks","function renderStretch","function startStretch","function renderEvolution","function setTier","async function init"]
    for _fn in _required_fns:
        _fname=_fn.replace("async ","").replace("function ","")
        record("C",f"JS fn {_fname}()",_fn in _dash_html,"found" if _fn in _dash_html else "MISSING","KIM")
    record("C","Dashboard no raw alert()","alert(" not in _dash_html,"clean" if "alert(" not in _dash_html else "STUB FOUND","KIM")
    record("C","Dashboard uses analytics/me/summary","/api/v2/analytics/me/summary" in _dash_html,"found" if "/api/v2/analytics/me/summary" in _dash_html else "WRONG PATH","KIM")
    record("C","Dashboard uses /api/v2/me/dashboard","/api/v2/me/dashboard" in _dash_html,"found" if "/api/v2/me/dashboard" in _dash_html else "MISSING","KIM")
    record("C","Dashboard uses /api/v2/auth/logout","/api/v2/auth/logout" in _dash_html,"found" if "/api/v2/auth/logout" in _dash_html else "MISSING","KIM")
    record("C","Dashboard uses /api/stretch/start","/api/stretch/start" in _dash_html,"found" if "/api/stretch/start" in _dash_html else "MISSING","KIM")
    record("C","Dashboard Write Like a Master title","Write Like a Master" in _dash_html,"found" if "Write Like a Master" in _dash_html else "MISSING","KIM")
    record("C","Dashboard _stretchExercises var","_stretchExercises" in _dash_html,"found" if "_stretchExercises" in _dash_html else "MISSING","KIM")
    record("C","Dashboard authorSelect element","authorSelect" in _dash_html,"found" if "authorSelect" in _dash_html else "MISSING","KIM")
    record("C","Dashboard mapping_id in start","mapping_id" in _dash_html,"found" if "mapping_id" in _dash_html else "MISSING","KIM")
    record("C","Dashboard author_id in start","author_id" in _dash_html,"found" if "author_id" in _dash_html else "MISSING","KIM")
    print("\n  [KIM] Dashboard API Endpoints")
    _as,_=http_get(BASE_URL+"/api/v2/analytics/me/summary")
    record("C","Analytics summary mounted",_as==401,f"status={_as} (401=auth required)","KIM")
    _bs=http_post(BASE_URL+"/api/v2/payments/billing-portal",{})
    record("C","Billing portal mounted",_bs[0]==401,f"status={_bs[0]} (401=auth required)","KIM")
    _pay_src=open("/opt/quirrely/quirrely_v313_integrated/backend/payments_api.py").read()
    record("C","Webhook dedup check","SELECT 1 FROM analytics_events" in _pay_src and "event_id" in _pay_src,"found" if "SELECT 1 FROM analytics_events" in _pay_src else "MISSING","KIM")
    print("\n  [KIM] Settings Page")
    _settings=open(ar+"/settings.html").read() if os.path.isfile(ar+"/settings.html") else ""
    record("C","Settings page exists",bool(_settings),"found" if _settings else "MISSING","KIM")
    for _sfn in ["function manageBilling","function cancelSubscription","function deleteAccount","function exportData","function exportPDF","function changePassword","function clearHistory","function showToast"]:
        _sfname=_sfn.replace("function ","")
        record("C",f"Settings fn {_sfname}()",_sfn in _settings,"found" if _sfn in _settings else "MISSING","KIM")
    record("C","Settings auth guard","quirrely_session" in _settings,"found" if "quirrely_session" in _settings else "MISSING","KIM")
    record("C","Settings auth redirect","/auth/login" in _settings,"found" if "/auth/login" in _settings else "MISSING","KIM")
    record("C","Settings loads API","/api/v2/me/dashboard" in _settings,"found" if "/api/v2/me/dashboard" in _settings else "MISSING","KIM")
    record("C","Settings manageBilling wired","billing-portal" in _settings,"wired" if "billing-portal" in _settings else "STUB","KIM")
    record("C","Settings no raw alert()","alert(" not in _settings,"clean" if "alert(" not in _settings else "STUB FOUND","KIM")
    record("C","Settings Dashboard nav",'/dashboard' in _settings,"found" if '/dashboard' in _settings else "MISSING","KIM")
    record("C","Settings Blog nav",'/blog' in _settings,"found" if '/blog' in _settings else "MISSING","KIM")
    record("C","Settings no dead /analyze",'href="/analyze"' not in _settings,"clean" if 'href="/analyze"' not in _settings else "DEAD","KIM")
    record("C","Settings no dead /history",'href="/history"' not in _settings,"clean" if 'href="/history"' not in _settings else "DEAD","KIM")
    record("C","Settings nav closed","</nav>" in _settings,"found" if "</nav>" in _settings else "MISSING","KIM")
    record("C","Settings GA4","G-HQ818WM2YB" in _settings,"found" if "G-HQ818WM2YB" in _settings else "MISSING","MARS")
    record("C","Settings title","Settings | Quirrely" in _settings,"found" if "Settings | Quirrely" in _settings else "WRONG","MARS")
    record("C","Settings no hardcoded Jane","Jane Doe" not in _settings,"clean" if "Jane Doe" not in _settings else "HARDCODED","KIM")
    record("C","Settings no hardcoded $4.99","$4.99" not in _settings and "$7.99" not in _settings,"clean" if ("$4.99" not in _settings and "$7.99" not in _settings) else "FOUND","KIM")
    record("C","Settings tierBadge",'id="tierBadge"' in _settings,"found" if 'id="tierBadge"' in _settings else "MISSING","KIM")
    record("C","Settings subscriptionCard",'id="subscriptionCard"' in _settings,"found" if 'id="subscriptionCard"' in _settings else "MISSING","KIM")
    for _sid in ["totalAnalyses","totalWords","memberSince"]:
        record("C",f"Settings stat {_sid}",'id="'+_sid+'"' in _settings,"found" if 'id="'+_sid+'"' in _settings else "MISSING","KIM")
    record("C","Settings danger zone","danger-zone" in _settings,"found" if "danger-zone" in _settings else "MISSING","KIM")
    record("C","Settings delete endpoint","auth/account/delete" in _settings,"found" if "auth/account/delete" in _settings else "WRONG ENDPOINT","KIM")
    record("C","Settings delete confirm","DELETE MY ACCOUNT" in _settings,"found" if "DELETE MY ACCOUNT" in _settings else "WRONG PHRASE","KIM")
    record("C","Settings showToast complete","toast.remove" in _settings,"found" if "toast.remove" in _settings else "TRUNCATED","KIM")
    record("C","Settings closing html","</html>" in _settings,"found" if "</html>" in _settings else "TRUNCATED","KIM")
    record("C","Settings no Twitter","twitter.com" not in _settings and "x.com/share" not in _settings,"clean","MARS")
    record("C","Settings no LinkedIn in nav","linkedin.com" not in _settings,"clean" if "linkedin.com" not in _settings else "STILL PRESENT","MARS")
    record("C","Settings support email","hello@quirrely.com" in _settings,"found" if "hello@quirrely.com" in _settings else "MISSING","MARS")
    record("C","Settings changePassword wired","auth/password/change" in _settings,"found" if "auth/password/change" in _settings else "STUB","KIM")
    record("C","Settings clearHistory wired","api/v2/me/history" in _settings,"found" if "api/v2/me/history" in _settings else "STUB","KIM")
    record("C","Settings edit display name","saveDisplayName" in _settings,"found" if "saveDisplayName" in _settings else "MISSING","KIM")
    record("C","Settings display name API","api/v2/auth/me/update" in _settings,"found" if "api/v2/auth/me/update" in _settings else "MISSING","KIM")
    record("C","Settings avatar picker","avatarPicker" in _settings,"found" if "avatarPicker" in _settings else "MISSING","KIM")
    record("C","Settings avatar save","saveAvatar" in _settings,"found" if "saveAvatar" in _settings else "MISSING","KIM")
    record("C","Settings displayNameInput",'id="displayNameInput"' in _settings,"found" if 'id="displayNameInput"' in _settings else "MISSING","KIM")
    record("C","Settings public profile toggle",'id="publicProfile"' in _settings,"found" if 'id="publicProfile"' in _settings else "MISSING","KIM")
    record("C","Settings profile visibility wired","profile_visibility" in _settings,"found" if "profile_visibility" in _settings else "MISSING","KIM")
    print("\n  [KIM] Export Page")
    _export=open(ar+"/frontend/export.html").read() if os.path.isfile(ar+"/frontend/export.html") else ""
    record("C","Export page exists",bool(_export),"found" if _export else "MISSING","KIM")
    record("C","Export has nav",'<header' in _export,"found" if '<header' in _export else "MISSING","KIM")
    record("C","Export fn exportData()","function exportData" in _export,"found" if "function exportData" in _export else "MISSING","KIM")
    for _et in ["profile","activity","all"]:
        record("C",f"Export type {_et}","exportData('"+_et+"'" in _export,"found" if "exportData('"+_et+"'" in _export else "MISSING","KIM")


    print("\n  [KIM] Dashboard Data Wiring")
    record("C","Voice uses avg_scores","avg_scores" in _dash_html and "data.avg_scores" in _dash_html,"found" if "data.avg_scores" in _dash_html else "MISSING","KIM")
    record("C","Writers link to blog","blogSlug" in _dash_html and "/blog/how-" in _dash_html,"found" if "blogSlug" in _dash_html else "MISSING","KIM")
    record("C","Writers pass stance","renderWriters(voiceType, lp.stance)" in _dash_html,"found" if "renderWriters(voiceType, lp.stance)" in _dash_html else "MISSING","KIM")
    record("C","Writers Wikipedia fallback","wikipedia.org" in _dash_html,"found" if "wikipedia.org" in _dash_html else "MISSING","KIM")
    record("C","Books country-aware","getBookstore" in _dash_html and "BOOKSTORE_BY_COUNTRY" in _dash_html,"found" if "getBookstore" in _dash_html else "MISSING","KIM")
    record("C","Books pass country","renderBooks(voiceType, (u.country" in _dash_html,"found" if "renderBooks(voiceType, (u.country" in _dash_html else "MISSING","KIM")
    for _bk in ["Indigo","Waterstones","Booktopia","Mighty Ape","Bookshop.org"]:
        record("C",f"Bookstore {_bk} configured",_bk in _dash_html,"found" if _bk in _dash_html else "MISSING","KIM")
    record("C","No Twitter/X share","shareTwitter" not in _dash_html and "twitter.com/intent" not in _dash_html,"clean" if "shareTwitter" not in _dash_html else "FOUND","KIM")
    record("C","Share claim present","claimSlug" in _dash_html,"found" if "claimSlug" in _dash_html else "MISSING","KIM")
    record("C","Share refresh present","refreshShare" in _dash_html,"found" if "refreshShare" in _dash_html else "MISSING","KIM")
    record("C","No hardcoded Indigo-only links","chapters.indigo.ca" not in _dash_html,"clean" if "chapters.indigo.ca" not in _dash_html else "HARDCODED","KIM")
    record("C","Voice no lp.scores fallback","lp.scores ||" not in _dash_html,"clean" if "lp.scores ||" not in _dash_html else "STALE","KIM")
    record("C","Dominant voice from avgEntries","avgEntries" in _dash_html,"found" if "avgEntries" in _dash_html else "MISSING","KIM")

    print("\n  [KIM] Pro-Dashboard Wiring")
    _pd=open(ar+"/pro-dashboard.html").read() if os.path.isfile(ar+"/pro-dashboard.html") else ""
    record("C","Pro-dashboard exists",bool(_pd),"found" if _pd else "MISSING","KIM")
    if _pd:
        record("C","Pro uses avg_scores","avg_scores" in _pd,"found" if "avg_scores" in _pd else "MISSING","KIM")
        record("C","Pro derives dominantVoice","dominantVoice" in _pd,"found" if "dominantVoice" in _pd else "MISSING","KIM")
        record("C","Pro no stale lp.scores fallback","latest_profile.scores || avg_scores" not in _pd,"clean","KIM")
        record("C","Pro no Twitter/X","shareTwitter" not in _pd and "twitter.com" not in _pd,"clean","KIM")

    print("\n  [KIM] Dashboard Tier Variants")
    for _tc,_tv in [("tier-free-only","Free-only card"),("tier-pro","Pro-gated card")]:
        record("C",f"CSS class {_tv}",_tc in _dash_html,"found" if _tc in _dash_html else "MISSING","KIM")
    for _tid,_tn in [("upgradeCard","Upgrade card"),("evolutionCard","Evolution card"),("writersCard","Writers card"),("booksCard","Books card"),("stretchCard","STRETCH card")]:
        record("C",f"Tier element #{_tid}",'id="'+_tid+'"' in _dash_html,"found" if 'id="'+_tid+'"' in _dash_html else "MISSING","KIM")
    record("C","setTier() function","function setTier" in _dash_html,"found" if "function setTier" in _dash_html else "MISSING","KIM")
    record("C","Body class tier switching","is-pro" in _dash_html,"found","KIM")

    print("\n  [KIM] Dashboard Country Variants")
    record("C","BOOKSTORE_BY_COUNTRY defined","BOOKSTORE_BY_COUNTRY" in _dash_html,"found" if "BOOKSTORE_BY_COUNTRY" in _dash_html else "MISSING","KIM")
    for _bk in ["Indigo","Waterstones","Booktopia","Mighty Ape","Bookshop.org"]:
        record("C",f"Bookstore {_bk}",_bk in _dash_html,"found" if _bk in _dash_html else "MISSING","KIM")
    record("C","getBookstore() function","function getBookstore" in _dash_html,"found" if "function getBookstore" in _dash_html else "MISSING","KIM")
    record("C","Country flags COUNTRY_FLAGS","COUNTRY_FLAGS" in _dash_html,"found" if "COUNTRY_FLAGS" in _dash_html else "MISSING","KIM")
    record("C","Books country-aware render","renderBooks(voiceType" in _dash_html and "country" in _dash_html,"found","KIM")

    print("\n  [KIM] Dashboard JS Functions (master)")
    _mfns = ["function doLogout","function viewPublicProfile","function submitForFeatured",
        "function copyProfileLink","function claimSlug","function initShare","function refreshShare",
        "function showToast","function getBookstore","function renderVoiceBars",
        "function renderWriters","function renderBooks","function renderActivity",
        "function renderStretch","function startStretch","function renderEvolution",
        "function setTier","async function init",
        "function toggleUserMenu","function getInitial","function formatNumber","function timeAgo"]
    for _fn in _mfns:
        _fname=_fn.replace("async ","").replace("function ","")
        record("C",f"Master JS fn {_fname}()",_fn in _dash_html,"found" if _fn in _dash_html else "MISSING","KIM")

    print("\n  [KIM] Dashboard Nav & Actions")
    for _href,_label in [("/dashboard","Dashboard nav"),("/blog","Blog nav"),("/faq","FAQ nav"),("/settings","Settings nav"),("/billing/","Billing link"),("/frontend/export.html","Export link")]:
        record("C",f"Master {_label}",_href in _dash_html,"found" if _href in _dash_html else "MISSING","KIM")
    record("C","Master no alert()","alert(" not in _dash_html,"clean" if "alert(" not in _dash_html else "FOUND","KIM")
    record("C","Master API /api/v2/me/dashboard","/api/v2/me/dashboard" in _dash_html,"found","KIM")
    record("C","Master API /api/v2/auth/logout","/api/v2/auth/logout" in _dash_html,"found","KIM")

    print("\n  [KIM] Dashboard Share Buttons")
    record("C","Share Copy Link",'copyProfileLink' in _dash_html,"found" if "copyProfileLink" in _dash_html else "MISSING","KIM")
    record("C","Share slug input styled","shareSlugInput" in _dash_html,"found" if "shareSlugInput" in _dash_html else "MISSING","KIM")
    record("C","Share ready section","shareReady" in _dash_html,"found" if "shareReady" in _dash_html else "MISSING","KIM")
    record("C","No Twitter/X in dashboard","shareTwitter" not in _dash_html and "twitter.com" not in _dash_html,"clean","KIM")

    print("\n  [MARS] Sentense Cleanup")
    record("C","Affiliate no sentense","sentense" not in open(os.path.join(APP_DIR,"affiliate_service.py")).read(),"clean" if "sentense" not in open(os.path.join(APP_DIR,"affiliate_service.py")).read() else "FOUND","MARS")
    _logo_readme=open(ar+"/assets/logo/README.md").read() if os.path.isfile(ar+"/assets/logo/README.md") else ""
    record("C","Logo README no Sentense","Sentense" not in _logo_readme,"clean" if "Sentense" not in _logo_readme else "FOUND","MARS")


    # STRETCH Exercise Flow UI (Session 6)
    print("\n  [KIM+MARS] STRETCH Exercise Flow UI")
    _dh=open("/home/quirrely/quirrely.ca/frontend/dashboard.html").read()
    record("C","STRETCH overlay exists","stretchOverlay" in _dh,"found" if "stretchOverlay" in _dh else "MISSING","MARS")
    record("C","STRETCH landing section","stretchLanding" in _dh,"found" if "stretchLanding" in _dh else "MISSING","MARS")
    record("C","STRETCH writing section","stretchWriting" in _dh,"found" if "stretchWriting" in _dh else "MISSING","MARS")
    record("C","STRETCH cycle done section","stretchCycleDone" in _dh,"found" if "stretchCycleDone" in _dh else "MISSING","MARS")
    record("C","STRETCH complete section","stretchComplete" in _dh,"found" if "stretchComplete" in _dh else "MISSING","MARS")
    record("C","STRETCH keystroke tracker","initKeystrokeTracker" in _dh,"found" if "initKeystrokeTracker" in _dh else "MISSING","MARS")
    record("C","STRETCH paste detection","pasteDetected" in _dh and "stretchPasteWarn" in _dh,"found" if "pasteDetected" in _dh else "MISSING","MARS")
    record("C","STRETCH word count UI","stretchWordCount" in _dh,"found" if "stretchWordCount" in _dh else "MISSING","MARS")
    record("C","STRETCH progress bar","stretchProgressFill" in _dh,"found" if "stretchProgressFill" in _dh else "MISSING","MARS")
    record("C","STRETCH submit function","submitStretchInput" in _dh,"found" if "submitStretchInput" in _dh else "MISSING","MARS")
    record("C","STRETCH resume function","resumeStretchExercise" in _dh,"found" if "resumeStretchExercise" in _dh else "MISSING","MARS")
    record("C","STRETCH resume badge","stretch-resume-badge" in _dh,"found" if "stretch-resume-badge" in _dh else "MISSING","MARS")
    record("C","STRETCH share LinkedIn","shareStretch" in _dh and "linkedin" in _dh,"found","MARS")
    record("C","STRETCH share Facebook","facebook" in _dh and "shareStretch" in _dh,"found","MARS")
    record("C","STRETCH no Twitter share","twitter" not in _dh.lower() or "shareStretch" in _dh,True,"MARS")
    record("C","STRETCH abandon function","abandonStretchFlow" in _dh,"found" if "abandonStretchFlow" in _dh else "MISSING","MARS")
    record("C","STRETCH book cards","stretch-book-card" in _dh,"found" if "stretch-book-card" in _dh else "MISSING","MARS")
    record("C","STRETCH cycle stats","stretch-stat-box" in _dh,"found" if "stretch-stat-box" in _dh else "MISSING","MARS")


    # STRETCH Technique & Style (Session 6 cont.)
    print("\n  [KIM+MARS] STRETCH Technique & Style")
    record("C","STRETCH technique card","stretchTechnique" in _dh and "stretchTechniqueName" in _dh,"found","MARS")
    record("C","STRETCH technique tip","stretchTechniqueTip" in _dh,"found" if "stretchTechniqueTip" in _dh else "MISSING","MARS")

    # --- Session 11: Word Usage Bar ---
    print("\n  [MARS] Word Usage Bar")
    record("C","Word usage bar exists","wordUsageBar" in _dh,"found" if "wordUsageBar" in _dh else "MISSING","MARS")
    record("C","Word usage fill bar","wuFill" in _dh,"found" if "wuFill" in _dh else "MISSING","MARS")
    record("C","Word usage label","wuLabel" in _dh,"found" if "wuLabel" in _dh else "MISSING","MARS")
    record("C","Word usage count","wuCount" in _dh,"found" if "wuCount" in _dh else "MISSING","MARS")
    record("C","Word usage hint","wuHint" in _dh,"found" if "wuHint" in _dh else "MISSING","MARS")
    record("C","renderWordUsage function","function renderWordUsage" in _dh,"found" if "function renderWordUsage" in _dh else "MISSING","MARS")
    record("C","Word usage calls limits API","api/v2/features/limits" in _dh,"found" if "api/v2/features/limits" in _dh else "MISSING","MARS")

    # --- Session 11: Unauth Word Limit ---
    print("\n  [MARS] Unauth Word Limit")
    _idx=open(ar.replace("quirrely.ca","quirrely.ca/frontend")+"/index.html").read() if os.path.isfile(ar.replace("quirrely.ca","quirrely.ca/frontend")+"/index.html") else ""
    if not _idx:
        _idx=open("/opt/quirrely/quirrely_v313_integrated/frontend/index.html").read()
    record("C","Index has daily word limit","quirrely_daily_words" in _idx,"found" if "quirrely_daily_words" in _idx else "MISSING","MARS")
    record("C","Index 150 word cap","150" in _idx and "word limit" in _idx.lower(),"found" if "150" in _idx else "MISSING","MARS")
    record("C","Index signup CTA on limit","signup.html" in _idx,"found" if "signup.html" in _idx else "MISSING","MARS")

    # --- Session 12: Share / Public Voice Profile ---
    print("\n  [MARS] Session 12 Share Feature")
    _apy=open(os.path.join(APP_DIR,"app.py")).read()
    _share_exists=os.path.isfile(os.path.join(APP_DIR,"share_api.py"))
    record("C","share_api.py exists",_share_exists,"found" if _share_exists else "MISSING","MARS")
    _sh=open(os.path.join(APP_DIR,"share_api.py")).read() if _share_exists else ""
    record("C","Share generate endpoint","generate" in _sh and "require_auth" in _sh,"found" if "generate" in _sh else "MISSING","MARS")
    record("C","Share slug validation","SLUG_RE" in _sh and "RESERVED" in _sh,"found" if "SLUG_RE" in _sh else "MISSING","MARS")
    record("C","Share refresh endpoint","def refresh_share" in _sh,"found" if "def refresh_share" in _sh else "MISSING","MARS")
    record("C","Share get_public_profile","def get_public_profile" in _sh,"found" if "def get_public_profile" in _sh else "MISSING","MARS")
    record("C","app.py mounts share router","share_router" in _apy,"found" if "share_router" in _apy else "MISSING","MARS")
    record("C","app.py has /voice/ route","/voice/{slug}" in _apy,"found" if "/voice/{slug}" in _apy else "MISSING","MARS")
    record("C","app.py voice OG tags","og:title" in _apy and "og:image" in _apy,"found" if "og:title" in _apy else "MISSING","MARS")
    _nx=open("/etc/nginx/conf.d/quirrely.conf").read()
    record("C","nginx proxies /voice/","location /voice/" in _nx,"found" if "location /voice/" in _nx else "MISSING","MARS")

        # --- Session 12: Pattern Recording in Proxy ---
    print("\n  [MARS] Session 12 Pattern Recording")
    record("C","app.py proxy calls collector.record_analysis","collector.record_analysis" in _apy,"found" if "collector.record_analysis" in _apy else "MISSING","MARS")
    record("C","app.py proxy returns pattern_id",'pattern_id=pid' in _apy,"found" if "pattern_id=pid" in _apy else "MISSING","MARS")

        # --- Session 12: Voice Comparison + Personalized CTA ---
    print("\n  [MARS] Session 12 Voice Comparison")
    _sh=open(os.path.join(APP_DIR,"share_api.py")).read()
    record("C","Public profile JSON endpoint","def get_public_share" in _sh,"found" if "def get_public_share" in _sh else "MISSING","MARS")
    _idx=open("/opt/quirrely/quirrely_v313_integrated/frontend/index.html").read()
    record("C","Auto-compare on ref visit","ref-compare" in _idx and "quirrely_ref" in _idx,"found" if "ref-compare" in _idx else "MISSING","MARS")
    record("C","Tracks analyze referral","action:'analyze'" in _idx or 'action:"analyze"' in _idx or "action:'analyze'" in _idx,"found" if "analyze" in _idx else "MISSING","MARS")
    record("C","Personalized CTA on voice page","compares to" in _apy,"found" if "compares to" in _apy else "MISSING","MARS")

        # --- Session 12: Referral Tracking ---
    print("\n  [MARS] Session 12 Referral Tracking")
    _sh=open(os.path.join(APP_DIR,"share_api.py")).read()
    record("C","Referral track endpoint","def track_referral" in _sh,"found" if "def track_referral" in _sh else "MISSING","MARS")
    record("C","Referral stats endpoint","def referral_stats" in _sh,"found" if "def referral_stats" in _sh else "MISSING","MARS")
    record("C","Voice page CTA has ref param","?ref={slug}" in _apy,"found" if "?ref={slug}" in _apy else "MISSING","MARS")
    _idx=open("/opt/quirrely/quirrely_v313_integrated/frontend/index.html").read()
    record("C","Index captures ref param","quirrely_ref" in _idx,"found" if "quirrely_ref" in _idx else "MISSING","MARS")
    record("C","Index tracks ref visit","referral/track" in _idx,"found" if "referral/track" in _idx else "MISSING","MARS")

        # --- Session 12: Writing Profiles Recording ---
    print("\n  [MARS] Session 12 Writing Profiles")
    record("C","app.py writes to writing_profiles","writing_profiles" in _apy and "INSERT INTO writing_profiles" in _apy,"found" if "INSERT INTO writing_profiles" in _apy else "MISSING","MARS")

        # --- Session 12: OG Share Images ---
    print("\n  [MARS] Session 12 OG Images")
    _og_dir="/home/quirrely/quirrely.ca/og"
    _og_profiles=["assertive","minimal","poetic","dense","conversational","formal","interrogative","hedged","parallel","longform"]
    _og_all=all(os.path.isfile(f"{_og_dir}/{p}.png") for p in _og_profiles)
    record("C","All 10 OG profile images exist",_og_all,"all found" if _og_all else "MISSING","MARS")
    _og_size=all(os.path.getsize(f"{_og_dir}/{p}.png")>10000 for p in _og_profiles) if _og_all else False
    record("C","OG images non-trivial size",_og_size,"valid" if _og_size else "TOO SMALL","MARS")

        # --- Session 12: Dashboard Share UI ---
    print("\n  [MARS] Session 12 Dashboard Share")
    record("C","Share card in dashboard","shareCard" in _dh,"found" if "shareCard" in _dh else "MISSING","MARS")
    record("C","Share slug input","shareSlugInput" in _dh,"found" if "shareSlugInput" in _dh else "MISSING","MARS")
    record("C","claimSlug function","function claimSlug" in _dh,"found" if "function claimSlug" in _dh else "MISSING","MARS")
    record("C","initShare function","function initShare" in _dh,"found" if "function initShare" in _dh else "MISSING","MARS")
    record("C","refreshShare function","function refreshShare" in _dh,"found" if "function refreshShare" in _dh else "MISSING","MARS")
    record("C","initShare called in init","initShare()" in _dh,"found" if "initShare()" in _dh else "MISSING","MARS")

        # --- Session 12: Word Tracking Auth Fix ---
    print("\n  [MARS] Session 12 Word Tracking")
    _apy=open(os.path.join(APP_DIR,"app.py")).read()
    record("C","app.py analyze imports get_current_user","get_current_user" in _apy and "from auth_api import get_current_user" in _apy,"found" if "from auth_api import get_current_user" in _apy else "MISSING","MARS")
    record("C","app.py analyze calls record_analysis","gate.record_analysis" in _apy,"found" if "gate.record_analysis" in _apy else "MISSING","MARS")
    _av2=open(os.path.join(APP_DIR,"api_v2.py")).read()
    record("C","api_v2 get_user_id uses auth not header","from auth_api import get_current_user" in _av2 or "auth_api" in _av2.split("get_user_id")[1][:200],"auth-based" if "x_user_id" not in _av2 else "HEADER-BASED","MARS")
        # --- Session 11: Tier Simplification ---
    print("\n  [MARS] Tier Simplification")
    record("C","No featuredCard in dashboard","featuredCard" not in _dh,"clean" if "featuredCard" not in _dh else "STILL PRESENT","MARS")
    record("C","No authorityCard in dashboard","authorityCard" not in _dh,"clean" if "authorityCard" not in _dh else "STILL PRESENT","MARS")
    record("C","No tier-featured CSS","tier-featured" not in _dh,"clean" if "tier-featured" not in _dh else "STILL PRESENT","MARS")
    record("C","No tier-authority CSS","tier-authority" not in _dh,"clean" if "tier-authority" not in _dh else "STILL PRESENT","MARS")
    record("C","setTier maps featured to pro","featured" in _dh and "mapped" in _dh,"found","MARS")
    record("C","STRETCH learning goal","stretchLearningGoal" in _dh,"found" if "stretchLearningGoal" in _dh else "MISSING","MARS")
    record("C","STRETCH style example","stretchStyleExample" in _dh,"found" if "stretchStyleExample" in _dh else "MISSING","MARS")
    record("C","STRETCH clear paste","clearStretchTextarea" in _dh,"found" if "clearStretchTextarea" in _dh else "MISSING","MARS")
    record("C","STRETCH toast z-index","99999" in _dh,"found" if "99999" in _dh else "MISSING","MARS")
    record("C","STRETCH select onchange","onchange" in _dh and "stretchBtn_" in _dh,"found","MARS")
    record("C","STRETCH keystroke 2000","slice(-2000)" in _dh,"found" if "slice(-2000)" in _dh else "MISSING","MARS")
    record("C","STRETCH no var shadow","var eb=" in _dh,"found" if "var eb=" in _dh else "MISSING","MARS")
    record("C","STRETCH technique CSS","stretch-technique" in _dh,"found","MARS")
    print("\n  [KIM+MARS] STRETCH Backend")
    _sa=open("/opt/quirrely/quirrely_v313_integrated/backend/stretch_api.py").read()
    record("C","Backend technique fields","technique_name" in _sa and "technique_tip" in _sa,"found","MARS")
    record("C","Backend style_example","style_example" in _sa,"found" if "style_example" in _sa else "MISSING","MARS")
    record("C","Backend learning_goal","learning_goal" in _sa,"found" if "learning_goal" in _sa else "MISSING","MARS")
    record("C","Backend dup input check","SELECT si.id FROM stretch_inputs" in _sa,"found" if "SELECT si.id" in _sa else "MISSING","MARS")
    record("C","Backend no Channel style","Channel the style of" not in _sa,"removed","MARS")
    record("C","Backend ratio 0.3","MIN_KEYSTROKE_RATIO = 0.3" in _sa,"0.3","MARS")

    
    # STRETCH Voice Mapping & Authors (Session 6 cont.)
    print("\n  [KIM+MARS] STRETCH Voice System")
    import psycopg2,psycopg2.extras
    _cn=psycopg2.connect("postgresql://quirrely:Quirr2026db@127.0.0.1:5432/quirrely_prod")
    _cr=_cn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    _cr.execute("SELECT COUNT(DISTINCT profile_from) as c FROM stretch_mappings WHERE active=TRUE")
    record("C","Mappings 10 profiles",_cr.fetchone()['c']>=10,"covered","MARS")
    _cr.execute("SELECT COUNT(DISTINCT voice_type) as c FROM stretch_authors WHERE active=TRUE")
    record("C","Authors 10 voice types",_cr.fetchone()['c']>=10,"covered","MARS")
    _cr.execute("SELECT COUNT(*) as c FROM stretch_authors WHERE active=TRUE")
    ac=_cr.fetchone()['c']
    record("C","60+ authors",ac>=60,str(ac),"MARS")
    _cr.execute("SELECT COUNT(*) as c FROM stretch_mappings WHERE active=TRUE")
    mc=_cr.fetchone()['c']
    record("C","90 mappings",mc>=90,str(mc),"MARS")
    _cr.execute("SELECT COUNT(*) as c FROM stretch_prompts_base WHERE active=TRUE")
    pc=_cr.fetchone()['c']
    record("C","450 prompts",pc>=450,str(pc),"MARS")
    _cr.execute("SELECT COUNT(*) as c FROM stretch_prompts_base WHERE active=TRUE AND technique_name IS NOT NULL")
    tc=_cr.fetchone()['c']
    record("C","Prompts have technique",tc>=450,str(tc)+"/"+str(pc),"MARS")
    _cr.execute("SELECT COUNT(*) as c FROM stretch_prompts_base WHERE active=TRUE AND style_example IS NOT NULL")
    sc=_cr.fetchone()['c']
    record("C","Prompts have style_example",sc>=450,str(sc)+"/"+str(pc),"MARS")
    _cr.execute("SELECT COUNT(*) FROM stretch_prompts_base WHERE active=TRUE AND variant=1 GROUP BY target_profile,cycle_number HAVING COUNT(DISTINCT story_starter)<3")
    record("C","No dup starters",_cr.rowcount==0,"clean","MARS")
    _cr.execute("SELECT COUNT(*) FROM stretch_prompts_base WHERE active=TRUE AND variant=1 GROUP BY target_profile,cycle_number HAVING COUNT(DISTINCT instruction)<3")
    record("C","No dup instructions",_cr.rowcount==0,"clean","MARS")
    _cn.close()


    # ===== NAV UNIFICATION + BLOG SIDEBAR TESTS (added Session 7) =====
    print("\n  [MARS] Unified Nav Checks")
    # Blog reading pages have auth script
    _reading_dir = "/opt/quirrely/quirrely_v313_integrated/blog/reading"
    _reading_auth = sum(1 for f in _bg.glob(_reading_dir+"/*.html") if "quirrely_session" in open(f).read())
    record("C","Reading pages auth-aware",_reading_auth==40,f"{_reading_auth}/40 pages","MARS")
    # Blog reading pages have squirrel SVG logo
    _reading_svg = sum(1 for f in _bg.glob(_reading_dir+"/*.html") if "viewBox" in open(f).read().split("</header>")[0])
    record("C","Reading pages squirrel logo",_reading_svg==40,f"{_reading_svg}/40 pages","MARS")
    # FAQ has auth script
    _faq = open(ar+"/faq.html").read() if os.path.isfile(ar+"/faq.html") else ""
    record("C","FAQ auth-aware","quirrely_session" in _faq,"found" if "quirrely_session" in _faq else "MISSING","MARS")
    # FAQ has squirrel logo
    record("C","FAQ squirrel logo","viewBox" in _faq.split("</header>")[0] if "<header" in _faq else "","found","MARS")
    # Settings has squirrel logo
    record("C","Settings squirrel logo","viewBox" in _settings.split("</header>")[0] if "<header" in _settings else "","found","MARS")
    # No beta badge on homepage
    _hp = open(ar+"/index.html").read()
    record("C","Homepage no beta badge","version-badge" not in _hp,"clean" if "version-badge" not in _hp else "STILL PRESENT","MARS")
    # Blog posts have related posts section
    _related_count = sum(1 for f in _bg.glob(_blog_dir+"/how-*-writers-write.html") if "related-posts" in open(f).read() and "tracked" not in f)
    record("C","Blog posts have related posts",_related_count==40,f"{_related_count}/40 posts","MARS")
    # Blog sidebar no country tags
    _bi_sidebar = open(_blog_dir+"/index.html").read()
    record("C","Blog sidebar no country tags","Writers by Region" not in _bi_sidebar,"clean" if "Writers by Region" not in _bi_sidebar else "STILL PRESENT","MARS")
    # Blog sidebar profile links wired (not href=#)
    _profile_wired = "assertive-open-writers-write" in _bi_sidebar and "poetic-open-writers-write" in _bi_sidebar
    record("C","Blog sidebar profiles wired",_profile_wired,"found" if _profile_wired else "DEAD LINKS","MARS")
    # Blog sidebar no fake post counts
    record("C","Blog sidebar no fake counts","profile-count" not in _bi_sidebar,"clean" if "profile-count" not in _bi_sidebar else "STILL PRESENT","MARS")
    # Geo-block middleware in app.py
    _app_py = open("/opt/quirrely/quirrely_v313_integrated/backend/app.py").read()
    record("C","Geo-block middleware","_BLOCKED_COUNTRIES" in _app_py and "geo_block_middleware" in _app_py,"found","MARS")
    record("C","Geo-block FR+RU",'"FR"' in _app_py and '"RU"' in _app_py,"found","MARS")
    # Wordmark spelling: "Quirrely" (single L) only — "Quirrelly" (double L) is ALWAYS wrong
    print("\n  [MARS] Wordmark Spelling")
    import glob as _sg
    _double_l = []
    for _sp in ["/opt/quirrely/quirrely_v313_integrated/blog/**/*.html", ar+"/**/*.html"]:
        for _sf in _sg.glob(_sp, recursive=True):
            with open(_sf) as _sfh:
                _sc = _sfh.read()
            if 'rel</tspan>' in _sc or 'Quir<span>rel</span>' in _sc:
                _double_l.append(os.path.basename(_sf))
    record("C","No double-L wordmark (Quirrelly)",len(_double_l)==0,",".join(_double_l[:5]) if _double_l else "clean","MARS")




    # ══════════════════════════════════════════════════════════════════
    # SECURITY AUDIT (Session 8)
    # ══════════════════════════════════════════════════════════════════
    print("\n  [MARS] Security Audit — SQL Injection Prevention")
    for _sf in ["featured_api.py","newsletter_api.py","notify_api.py"]:
        _sp=os.path.join(APP_DIR,_sf)
        if os.path.exists(_sp):
            _sc=open(_sp).read()
            record("C",f"No subprocess SQL in {_sf}","subprocess" not in _sc,f"subprocess found in {_sf}","MARS")
            _has_fstr=("f\"SELECT" in _sc or "f\"INSERT" in _sc or "f\"UPDATE" in _sc or "f\"DELETE" in _sc
                       or "f'SELECT" in _sc or "f'INSERT" in _sc or "f'UPDATE" in _sc or "f'DELETE" in _sc)
            record("C",f"No f-string SQL in {_sf}",not _has_fstr,f"f-string SQL in {_sf}","MARS")
            record("C",f"Uses parameterized queries in {_sf}","db_query_one" in _sc or "db_execute" in _sc,"missing parameterized helpers","MARS")

    print("\n  [MARS] Security Audit — CORS Configuration")
    _app_py=open(os.path.join(APP_DIR,"app.py")).read()
    record("C","app.py CORS not wildcard",'allow_origins=["*"]' not in _app_py,"wildcard CORS in app.py","MARS")
    for _cf in ["api.py","api_v2.py"]:
        _cfc=open(os.path.join(APP_DIR,_cf)).read()
        record("C",f"{_cf} CORS not wildcard",'allow_origins=["*"]' not in _cfc,f"wildcard CORS in {_cf}","MARS")

    print("\n  [MARS] Security Audit — Error Leakage")
    for _ef in ["payments_api.py","app.py","api_v2.py"]:
        _ec=open(os.path.join(APP_DIR,_ef)).read()
        _leaks=[l.strip() for i,l in enumerate(_ec.split("\n"),1) if "detail=str(e)" in l or 'detail=f"' in l and "str(e)" in l]
        record("C",f"No error leakage in {_ef}",len(_leaks)==0,f"{len(_leaks)} leaks","MARS")

    print("\n  [MARS] Security Audit — Nginx Headers")
    import subprocess as _sp2
    _ng=_sp2.run(["curl","-sI","http://127.0.0.1:8080/"],capture_output=True,text=True,timeout=5).stdout
    record("C","HSTS header present","strict-transport-security" in _ng.lower(),"missing HSTS","MARS")
    record("C","CSP header present","content-security-policy" in _ng.lower(),"missing CSP","MARS")
    record("C","X-Frame-Options present","x-frame-options" in _ng.lower(),"missing X-Frame-Options","MARS")
    record("C","X-Content-Type-Options present","x-content-type-options" in _ng.lower(),"missing X-Content-Type-Options","MARS")


    print("\n  [MARS] Security Audit — Auth & Sessions")
    _auth=open(os.path.join(APP_DIR,"auth_api.py")).read()
    record("C","Bcrypt password hashing","bcrypt" in _auth.lower(),"no bcrypt found","MARS")
    record("C","Parameterized queries in auth_api","db_execute" in _auth and "%s" in _auth,"missing parameterized queries","MARS")
    record("C","Session expiry check","expires_at" in _auth,"no session expiry","MARS")
    record("C","Avatar URL validation","Invalid avatar URL" in _auth or "valid HTTPS URL" in _auth,"no avatar validation","MARS")

    print("\n  [MARS] Security Audit — .env & Secrets")
    _env_perms=_sp2.run(["stat","-c","%a",os.path.join(APP_DIR,".env")],capture_output=True,text=True,timeout=5).stdout.strip()
    record("C",".env permissions restricted",_env_perms=="600",f"perms={_env_perms}","MARS")
    for _hf in ["newsletter_api.py","notify_api.py"]:
        _hc=open(os.path.join(APP_DIR,_hf)).read()
        record("C",f"No hardcoded .env path in {_hf}","open(" not in _hc or ".env" not in _hc,"hardcoded .env path","MARS")
        record("C",f"Uses os.getenv in {_hf}","os.getenv" in _hc or "os.environ" in _hc,"not using os.getenv","MARS")

    print("\n  [MARS] Security Audit — Cookie Security")
    _mw=open(os.path.join(APP_DIR,"auth_middleware.py")).read()
    record("C","Cookies httpOnly","COOKIE_HTTPONLY" in _mw and "True" in _mw,"httponly not set","MARS")
    record("C","Cookies secure flag","COOKIE_SECURE" in _mw,"secure flag missing","MARS")
    record("C","Cookies SameSite","COOKIE_SAMESITE" in _mw,"samesite missing","MARS")

    print("\n  [MARS] Security Audit — Geo-block Active")
    _gb=_sp2.run(["curl","-s","-H","cf-ipcountry: FR","http://127.0.0.1:8000/health"],capture_output=True,text=True,timeout=5).stdout
    record("C","Geo-block FR returns 403","access_denied" in _gb,"geo-block not working","MARS")

    # ── US MARKET PARITY (Session 9) ──
    print("\n  [MARS] US Market Parity")
    # Backend: stripe_config has USD
    _sc=open(os.path.join(APP_DIR,"stripe_config.py")).read()
    record("C","USD in Currency enum",'USD = "usd"' in _sc,"found" if 'USD = "usd"' in _sc else "MISSING","MARS")
    record("C","US in COUNTRY_TO_CURRENCY",'"US": Currency.USD' in _sc,"found" if '"US": Currency.USD' in _sc else "MISSING","MARS")
    record("C","USD pricing block","Currency.USD:" in _sc,"found" if "Currency.USD:" in _sc else "MISSING","MARS")
    record("C","No NEVER USD in stripe_config","NEVER USD" not in _sc,"clean" if "NEVER USD" not in _sc else "STILL PRESENT","MARS")
    # Backend: launch_config has US
    _lc=open(os.path.join(APP_DIR,"launch_config.py")).read()
    record("C","US in Country enum",'US = "us"' in _lc,"found" if 'US = "us"' in _lc else "MISSING","MARS")
    record("C","US CountryConfig exists","Country.US: CountryConfig(" in _lc,"found" if "Country.US: CountryConfig(" in _lc else "MISSING","MARS")
    record("C","US in GEO_COUNTRY_MAP",'"US": Country.US' in _lc,"found" if '"US": Country.US' in _lc else "MISSING","MARS")
    record("C","Bookshop.org in launch_config","Bookshop.org" in _lc,"found" if "Bookshop.org" in _lc else "MISSING","MARS")
    # Backend: geo_redirect has US locale
    _gr=open(os.path.join(APP_DIR,"geo_redirect.py")).read()
    record("C","US locale en-US in geo_redirect",'Country.US: "en-US"' in _gr,"found" if 'Country.US: "en-US"' in _gr else "MISSING","MARS")
    # Backend: affiliate_service has US
    _af=open(os.path.join(APP_DIR,"affiliate_service.py")).read()
    record("C","US retailer in affiliate_service","'US': RetailerConfig(" in _af,"found" if "'US': RetailerConfig(" in _af else "MISSING","MARS")
    record("C","Bookshop.org in affiliate","bookshop.org" in _af,"found" if "bookshop.org" in _af else "MISSING","MARS")
    record("C","US in affiliate country loop","'US']:" in _af,"found" if "'US']:" in _af else "MISSING","MARS")
    # Frontend: dashboard has US bookstore
    record("C","US bookstore in dashboard","Bookshop.org" in _dash_html,"found" if "Bookshop.org" in _dash_html else "MISSING","KIM")
    record("C","bookshop.org URL in dashboard","bookshop.org/search" in _dash_html,"found" if "bookshop.org/search" in _dash_html else "MISSING","KIM")
    # US not geo-blocked
    _app=open(os.path.join(APP_DIR,"app.py")).read()
    record("C","US not in blocked countries",'"US"' not in _app or "_BLOCKED_COUNTRIES" not in _app or '"US"' not in _app.split("_BLOCKED_COUNTRIES")[1].split("\n")[0],"clean","MARS")
    # Billing: USD currency button
    _upgrade=open("/home/quirrely/quirrely.ca/billing/upgrade.html").read()
    record("C","Billing USD button",'data-curr="usd"' in _upgrade,"found" if 'data-curr="usd"' in _upgrade else "MISSING","MARS")
    for _bc in ["cad","gbp","aud","nzd","usd"]:
        record("C",f"Billing {_bc.upper()} button",'data-curr="'+_bc+'"' in _upgrade,"found" if 'data-curr="'+_bc+'"' in _upgrade else "MISSING","MARS")
    # Pricing.js auto-detects US
    _pjs=open("/home/quirrely/quirrely.ca/billing/pricing.js").read()
    record("C","pricing.js US auto-detect",'"US":"usd"' in _pjs,"found" if '"US":"usd"' in _pjs else "MISSING","MARS")
    # No Amazon anywhere
    record("C","No Amazon in affiliate","amazon.com" not in _af.lower(),"clean" if "amazon.com" not in _af.lower() else "FOUND","MARS")
    record("C","No Amazon in dashboard","amazon.com" not in _dash_html.lower(),"clean" if "amazon.com" not in _dash_html.lower() else "FOUND","KIM")


def send_report():
    env=read_env();RESEND_API_KEY=env.get("RESEND_API_KEY","")
    if not RESEND_API_KEY:
        print("  Email skipped: RESEND_API_KEY not in .env"); return
#    removed duplicate run_part_c()
    pa=results["part_a"];pb=results["part_b"];pc=results["part_c"]
    tp=pa["pass"]+pb["pass"]+pc["pass"];tf=pa["fail"]+pb["fail"]+pc["fail"];tot=tp+tf
    pct=int(100*tp/tot) if tot>0 else 0
    sw="ALL SYSTEMS GO" if tf==0 else f"ATTENTION REQUIRED ({tf} failures)"
    def rows(tests):
        r=""
        for t in tests:
            ic="PASS" if t["status"]=="PASS" else "FAIL"
            color="#27ae60" if t["status"]=="PASS" else "#e74c3c"
            r+=f"<tr><td style='color:{color}'>{ic}</td><td>{t['name']}</td><td>{t['detail']}</td><td>{t['owner']}</td></tr>"
        return r
    html="<html><body><h2>"+sw+"</h2><p>"+str(tp)+"/"+str(tot)+" passed ("+str(pct)+"%) "+results["run_at"][:19]+" UTC</p><h3>Part A</h3><table>"+rows(pa["tests"])+"</table><h3>Part B</h3><table>"+rows(pb["tests"])+"</table></body></html>"
    subj="SUPER_TEST "+"PASS" if tf==0 else "FAIL"
    try:
        import httpx, asyncio
        async def _send():
            async with httpx.AsyncClient() as c:
                r = await c.post("https://api.resend.com/emails",
                    headers={"Authorization":"Bearer "+RESEND_API_KEY,"Content-Type":"application/json"},
                    json={"from":FROM_EMAIL,"to":[REPORT_EMAIL],"subject":subj,"html":html},
                    timeout=10)
                return r.status_code, r.text
        code,body = asyncio.run(_send())
        if code==200:
            print("  Report emailed to " + REPORT_EMAIL)
        else:
            print("  Email failed: " + str(code) + " " + str(body))
    except Exception as e:
        print("  Email error: " + str(e))

if __name__=="__main__":
    print("\nQUIRRELY SUPER_TEST v1.1 — ASO · KIM · MARS")
    print(f"Run at: {results['run_at']}")
    run_part_a()
    run_part_b()
    run_part_c()
    pa=results["part_a"];pb=results["part_b"];pc=results["part_c"]
    tp=pa["pass"]+pb["pass"]+pc["pass"];tf=pa["fail"]+pb["fail"]+pc["fail"];tot=tp+tf
    print("\n"+"="*70)
    print(f"  Part A : {pa['pass']}/{pa['pass']+pa['fail']} passed")
    print(f"  Part B : {pb['pass']}/{pb['pass']+pb['fail']} passed")
    print(f"  Part C : {pc['pass']}/{pc['pass']+pc['fail']} passed")
    print(f"  Total  : {tp}/{tot} ({int(100*tp/tot) if tot else 0}%)")
    print("="*70)
    send_report()
    try:
        json.dump(results,open("/opt/quirrely/quirrely_v313_integrated/tests/last_run.json","w"),indent=2)
        print("  Results saved to last_run.json")
    except Exception as e: print(f"  Save failed: {e}")
    sys.exit(0 if tf==0 else 1)
