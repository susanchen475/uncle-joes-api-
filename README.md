# Uncle-Joes-API-
uncle joes FastAPI backend

**Uncle Joe’s Coffee Club: Internal Pilot**

An integrated web application designed for Uncle Joe’s Coffee Company to modernize their digital apprearance. This internal pilot surfaces historical data from nearly 500 locations, allowing Coffee Club members to view their order history and loyalty rewards.

<br><br>

**Project Architecture**

1. Database (Storage): Google BigQuery housing 20+ years of historical order data across 5 relational tables.

2. Backend (Logic): FastAPI (Python) providing a RESTful API for secure data retrieval and member authentication.

3. Frontend (UI): A customer-facing Vue.js application (via CDN) for menu browsing and personalized account dashboards.

<br><br>

**Core Functionality**

The pilot is designed to answer these fundamental business questions:

- Menu Accessibility: Can customers see full item details (calories/price)?

- Store Locator: Can customers find a nearby coffee club location?

- Order History: Can a logged-in member see every order they've placed?

- Rewards Clarity: Is the Coffee Club points balance calculated accurately?

<br><br>

**Data Model**

The applications are build from the BigQuery tables:

- locations — 485 store locations (city, state, hours, amenities) 

- menu_items— 30 items (name, category, size, calories, price) 

- members— Coffee Club members (name, email, home_store, password hash) 

- orders — Order header records (member_id, store_id, order_date, order_total) 

- order_items — Line items per order (menu_item_id, item_name, quantity, price)

<br><br>

**Relationship Diagram**

Members & Locations: Each member has a home_store linked to locations.id.

Orders & Members: orders.member_id links to members.id (Nullable for guest orders).

Orders & Items: A one-to-many relationship between orders.order_id and order_items.order_id.

Items & Menu: order_items.menu_item_id links to menu_items.id.

<br><br>


**Tech Stack & Dependencies**

Runtime: Python 3.11+

Framework: FastAPI (Asynchronous REST API)

Package Management: Poetry

Data Warehouse: Google BigQuery (via google-cloud-bigquery)

Security & Auth: passlib[bcrypt] for password verification

Deployment: Docker containers on Google Cloud Run

<br>

**API Endpoint Map**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/menu` | Returns the full list of coffee and food items. |
| **GET** | `/menu/{item_id}` | Returns detailed data for a specific menu item. |
| **GET** | `/locations` | Lists all 485 Uncle Joe’s store locations. |
| **GET** | `/locations/{id}` | Returns details (hours, amenities) for a specific store. |
| **POST** | `/login` | Verifies member credentials against hashed passwords. |
| **GET** | `/members/{id}/orders` | Retrieves a member's full order history with line items. |
| **GET** | `/members/{id}/points` | Computes a member's loyalty points balance ($1 = 1pt). |
