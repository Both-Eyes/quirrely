// Quirrely Pricing Module v1.0
// Shared pricing data for billing pages

var COUNTRY_CURRENCY = {
  "US":"usd","CA":"cad","GB":"gbp","AU":"aud","NZ":"nzd"
};

var TZ_CURRENCY = {
  "America/Toronto":"cad","America/Vancouver":"cad","America/Edmonton":"cad",
  "America/Winnipeg":"cad","America/Halifax":"cad","America/St_Johns":"cad",
  "America/New_York":"usd","America/Chicago":"usd","America/Denver":"usd",
  "America/Los_Angeles":"usd","Europe/London":"gbp",
  "Australia/Sydney":"aud","Australia/Melbourne":"aud","Australia/Perth":"aud",
  "Pacific/Auckland":"nzd"
};

var PRICING = {
  cad: { symbol: "$", monthly: 2.99, annual: 29.99 },
  usd: { symbol: "$", monthly: 2.99, annual: 29.99 },
  gbp: { symbol: "\u00A3", monthly: 1.99, annual: 20.99 },
  aud: { symbol: "$", monthly: 4.99, annual: 29.99 },
  nzd: { symbol: "$", monthly: 3.99, annual: 39.99 }
};

function detectCurrency() {
  try {
    var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    return TZ_CURRENCY[tz] || "cad";
  } catch (e) {
    return "cad";
  }
}

// Preserve checkout_tier across auth redirects
function saveCheckoutTier(tier) {
  if (tier) sessionStorage.setItem("checkout_tier", tier);
}

function getCheckoutTier() {
  return sessionStorage.getItem("checkout_tier") ||
    new URLSearchParams(window.location.search).get("tier") || "";
}
