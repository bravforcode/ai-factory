/* Public, non-secret storefront configuration.
 * Set revenueOsApiBase to the deployed Revenue OS API + /api before launch.
 * An empty value intentionally disables checkout instead of falling back to a
 * direct Stripe payment link that would bypass Revenue OS fulfillment.
 */
window.AI_FACTORY_CONFIG = Object.freeze({
  revenueOsApiBase: "",
});

