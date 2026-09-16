(function () {
  "use strict";

  var config = window.AI_FACTORY_CONFIG || {};
  var apiBase = typeof config.revenueOsApiBase === "string"
    ? config.revenueOsApiBase.replace(/\/+$/, "")
    : "";
  var pageSlug = window.location.pathname.split("/").pop().replace(/\.html$/, "");
  var knownSlugs = new Set([
    "01-prompt-pack-th",
    "02-obsidian-student-kit",
    "03-freelance-pricing-calculator",
    "04-cold-email-template-pack",
    "05-ai-automation-workflow",
    "06-cv-international-template",
    "07-n8n-sme-workflow-pack",
    "08-content-calendar-90d",
    "09-finance-tracker-thb",
    "10-ai-agent-starter-github"
  ]);

  if (!knownSlugs.has(pageSlug)) return;

  function statusFor(anchor) {
    var status = anchor.parentElement.querySelector("[data-revenue-checkout-status]");
    if (status) return status;
    status = document.createElement("span");
    status.setAttribute("data-revenue-checkout-status", "");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    status.className = "block mt-3 text-sm text-red-700";
    anchor.insertAdjacentElement("afterend", status);
    return status;
  }

  function setBusy(anchor, value) {
    anchor.setAttribute("aria-busy", value ? "true" : "false");
    anchor.style.pointerEvents = value ? "none" : "";
    anchor.style.opacity = value ? "0.7" : "";
  }

  function isStripeCheckoutUrl(value) {
    try {
      var parsed = new URL(value);
      return parsed.protocol === "https:" &&
        (parsed.hostname === "checkout.stripe.com" || parsed.hostname.endsWith(".stripe.com"));
    } catch (_) {
      return false;
    }
  }

  async function startCheckout(event) {
    event.preventDefault();
    var anchor = event.currentTarget;
    var status = statusFor(anchor);
    status.textContent = "";
    if (!apiBase) {
      status.textContent = "Checkout ยังไม่ถูกตั้งค่า กรุณาติดต่อ support ก่อนชำระเงิน";
      return;
    }
    setBusy(anchor, true);
    var controller = new AbortController();
    var timeout = window.setTimeout(function () { controller.abort(); }, 15000);
    try {
      var response = await fetch(apiBase + "/checkout/session/by-slug", {
        method: "POST",
        credentials: "omit",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          product_slug: pageSlug,
          success_url: new URL("/thanks-" + pageSlug + ".html", window.location.origin).href,
          cancel_url: new URL("/" + pageSlug + ".html#buy", window.location.origin).href
        })
      });
      if (!response.ok) throw new Error("checkout unavailable");
      var payload = await response.json();
      if (!isStripeCheckoutUrl(payload.checkout_url)) throw new Error("invalid checkout target");
      window.location.assign(payload.checkout_url);
    } catch (_) {
      status.textContent = "เปิด checkout ไม่สำเร็จ กรุณาลองใหม่หรือติดต่อ support";
      setBusy(anchor, false);
    } finally {
      window.clearTimeout(timeout);
    }
  }

  document.querySelectorAll('a[data-revenue-product="' + pageSlug + '"]').forEach(function (anchor) {
    anchor.addEventListener("click", startCheckout);
  });
}());

