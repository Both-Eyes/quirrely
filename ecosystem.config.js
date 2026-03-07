module.exports = {
  apps: [{
    name: 'quirrely',
    script: '/opt/quirrely/quirrely_v313_integrated/backend/venv/bin/uvicorn',
    args: 'app:app --host 127.0.0.1 --port 8000 --workers 2',
    cwd: '/opt/quirrely/quirrely_v313_integrated/backend',
    interpreter: 'none',
    env: {
      APP_URL: 'https://quirrely.ca',
      DATABASE_URL: 'postgresql://quirrely:QuirrDB2026xK9m@localhost:5432/quirrely_prod',
      GOOGLE_CLIENT_ID: '1023940227750-0nn22gt9lt1gjjca7j398r6v66b3o9of.apps.googleusercontent.com',
      GOOGLE_CLIENT_SECRET: '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',
      FACEBOOK_CLIENT_ID: '4334298873522506',
      FACEBOOK_CLIENT_SECRET: '03ce79eb6bc34c63e4cd27dff78b46fb',
      LINKEDIN_CLIENT_ID: '7880dn5cjir12l',
      LINKEDIN_CLIENT_SECRET: 'WPL_AP1.GT9ycAmUn5aonC8c.Tnd/gg==',
      OAUTH_REDIRECT_BASE: 'https://quirrely.ca'
    }
  }]
}
