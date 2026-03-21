# ShopFast — Full-Stack E-Commerce App

A full-stack e-commerce application built with **FastAPI** (Python) on the backend and **React + TypeScript** (Vite) on the frontend.

---

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python, FastAPI, SQLite, Uvicorn    |
| Frontend  | React 19, TypeScript, Vite, Axios   |
| Routing   | React Router v7                     |
| Styling   | Plain CSS (global stylesheet)       |

---

## Project Structure

```
LearnClaudeCode/
├── main.py                  # FastAPI application (all API endpoints)
├── requirements.txt         # Python dependencies
├── pytest.ini               # Pytest configuration
├── ecommerce.db             # SQLite database (auto-generated)
├── tests/
│   ├── test_main.py         # General API tests
│   └── test_cart.py         # Cart-specific tests
└── frontend/                # React + TypeScript frontend
    ├── src/
    │   ├── api/             # Axios API service layer
    │   ├── components/      # Reusable UI components
    │   ├── hooks/           # Custom React hooks
    │   ├── pages/           # Page-level components
    │   └── types/           # Shared TypeScript interfaces
    └── vite.config.ts
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+

### Backend Setup

```bash
# Install Python dependencies
pip install fastapi uvicorn

# Run the development server (auto-reloads on changes)
uvicorn main:app --reload
```

API runs at: **http://127.0.0.1:8000**
Interactive docs: **http://127.0.0.1:8000/docs**

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

### Run Both Servers Together

```bash
cd frontend
npm run dev:all
```

---

## API Endpoints

| Method   | Endpoint                  | Description                        |
|----------|---------------------------|------------------------------------|
| `GET`    | `/`                       | Welcome message                    |
| `GET`    | `/health`                 | Health check                       |
| `GET`    | `/products`               | List all products                  |
| `GET`    | `/products/search?q=`     | Search products by name            |
| `GET`    | `/products/{id}`          | Get a single product               |
| `POST`   | `/products`               | Create a new product               |
| `GET`    | `/cart`                   | Get cart items and total           |
| `POST`   | `/cart`                   | Add item to cart                   |
| `DELETE` | `/cart/{product_id}`      | Remove item from cart              |

---

## Frontend Pages

| Route      | Page           | Description                                  |
|------------|----------------|----------------------------------------------|
| `/login`   | Login          | Stylish sign-in form with email & password   |
| `/`        | Products       | Product grid with live search (300ms debounce)|
| `/cart`    | Cart           | Cart items, line totals, and order total     |

---

## Running Tests

```bash
# Run all backend tests
pytest

# Run a specific test
pytest tests/test_main.py::test_name -v
```

---

## Default Seed Data

The database is seeded automatically on first run:

| Product             | Price   | Stock |
|---------------------|---------|-------|
| Wireless Mouse      | $29.99  | 50    |
| Mechanical Keyboard | $89.99  | 30    |
| USB-C Hub           | $49.99  | 100   |
