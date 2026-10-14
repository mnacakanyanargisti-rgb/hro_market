# Hro Market — Original Emergent frontend recovery

This is the actual React + original CSS frontend from the user-supplied browser-captured webpack bundle, not a newly redesigned store. The two store photos and 66 saved product/category images are stored locally in `assets/`.

## Files

- `index.html` — browser entrypoint; loads the compiled React frontend.
- `bundle.js` — preserved application bundle. Removed the Emergent developer overlay and hot-reloading startup. Checkout was changed from Emergent-only `/api/orders` to customer-composed WhatsApp order messages.
- `assets/` — recovered photographs.
- `.nojekyll` — optional for static GitHub hosting.

## Static hosting

Upload the contents of this folder, preserving relative paths, to any static host. This does NOT require Node/npm or a build step. The app uses `assets/…` relative paths, so it works on a GitHub project subdirectory too.

GitHub stores the source files; for an active online shop, check your host's policy. GitHub Pages has commerce-related restrictions. Cloudflare Pages or Netlify are alternate static hosts that can deploy from a GitHub repository.

## Functional scope

- Original page layout and typography, products, category filters, language UI, search, quantity/cart and checkout form.
- Order submission opens a filled-in WhatsApp message to the store. The customer must press Send inside WhatsApp. No backend database is deployed and no automatic acknowledgement is implied.
- Some products have `null` prices in the original bundle; they continue to show the original *price on request* UI. Verify every real price with the shop owner.
- Seven original product images were NOT present in the saved ZIP, so their existing Unsplash image URLs remain remote. All other 68 recovered images are local.
- English/Russian product names are based on the original site's simplified translations and may need copyediting.
- Original remote Google fonts and social-link endpoints may depend on third-party availability.

## Validation

Tested using browser execution of the compiled JS: homepage renders, search filters products, language buttons switch copy, product button adds an item to the cart, cart opens and checkout form is displayed. Visual match is based on the supplied compiled frontend code; the live Emergent preview is blocked from this environment, so pixel-perfect comparison could not be verified.
