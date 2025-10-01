I'm currently working with an application that has all its data in a single PostgreSQL database. The tables include users, products, categories, carts, cart_items, wishlists, promo_codes, and related junction tables. All services like Auth, Product, and Cart are accessing this same database directly, using foreign keys and joins.

I want to transition this system into a proper microservices architecture where each service owns its own data and there is no shared database between services.

so help me in transitioning, Since we can no longer use cross-service foreign keys or SQL joins, how do services safely reference data from other services (like user_id in cart or product_id in cart_items)
also tell me How should services communicate when one needs data from another?
also make sure that what are best practices for ensuring data consistency, performance, and fault tolerance in this new architecture