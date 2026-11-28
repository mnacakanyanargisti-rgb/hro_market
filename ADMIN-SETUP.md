# Owner dashboard activation
The storefront continues using its original catalog until Supabase is configured.
1. Create a project at https://supabase.com/dashboard.
2. In Authentication > Users create and confirm an owner email/password (strong unique password, not 11111). Copy the user's UUID. Disable public signups if not needed.
3. In SQL Editor run supabase-setup.sql after replacing REPLACE_WITH_OWNER_UUID with that UUID.
4. Set url, key (publishable/anon only), and ownerEmail in store-config.js. Never commit a secret/service-role key or password.
5. Deploy and visit admin.html. Enter HroMarket and the owner's password. The first login loads the original 88 products. Save publishes the catalog.
6. Test price changes, adding/removing items, photo uploads, and unauthorized writes. Check storefront in another browser after each save. Restore original price after testing.
The catalog is saved as one JSON document; use one editing session at a time. Images are public and uploaded files are not automatically deleted. A network failure falls back to original catalog. The existing range-price and price-on-request behavior is preserved.
