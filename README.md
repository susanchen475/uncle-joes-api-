# uncle-joes-api-
uncle joes FastAPI backend

**Uncle Joe’s Coffee Club: Internal Pilot**

An integrated web application designed for Uncle Joe’s Coffee Company to modernize their digital apprearance. This internal pilot surfaces historical data from nearly 500 locations, allowing Coffee Club members to view their order history and loyalty rewards.

**Project Architecture**

1. Database (Storage): Google BigQuery housing 20+ years of historical order data across 5 relational tables.

2. Backend (Logic): FastAPI (Python) providing a RESTful API for secure data retrieval and member authentication.

3. Frontend (UI): A customer-facing Vue.js application (via CDN) for menu browsing and personalized account dashboards.


**Core Functionality**

The pilot is designed to answer these fundamental business questions:

- Menu Accessibility: Can customers see full item details (calories/price)?

- Store Locator: Can customers find a nearby coffee club location?

- Order History: Can a logged-in member see every order they've placed?

- Rewards Clarity: Is the Coffee Club points balance calculated accurately?


**Data Model**

The applications are build from the BigQuery tables:

- locations — 485 store locations (city, state, hours, amenities) 

- menu_items— 30 items (name, category, size, calories, price) 

- members— Coffee Club members (name, email, home_store, password hash) 

- orders — Order header records (member_id, store_id, order_date, order_total) 

- order_items — Line items per order (menu_item_id, item_name, quantity, price) 
