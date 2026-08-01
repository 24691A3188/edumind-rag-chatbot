# E-Commerce Admin & Order Management System - Technical Design Document

This document defines the architectural, database, and UI/UX design specifications for the E-Commerce Admin & Order Management System. It is built to translate the Product Requirements Document (PRD) into a concrete, developer-ready blueprint for a full-stack web application using React.js, Tailwind CSS, Framer Motion, Recharts, and Supabase.

---

## 1. Visual Identity & Design System

To achieve a **modern, colorful, and glassmorphic** user interface, the application utilizes a dark-mode-first aesthetic. Glassmorphism relies on high-contrast background gradients, blurred container layers, and subtle border highlights to create depth.

### 1.1 Color Palette & Theme Tokens

Beneath the glassmorphic surfaces, dynamic linear and radial gradients provide vibrant backdrops.

| Token | CSS Variable / Tailwind | Hex/RGBA Value | Usage |
| :--- | :--- | :--- | :--- |
| **Dark Background** | `--bg-deep` / `bg-slate-950` | `#030712` | Main page background |
| **Glass Panel** | `--glass-bg` | `rgba(17, 24, 39, 0.45)` | Card and modal containers |
| **Glass Border** | `--glass-border` | `rgba(255, 255, 255, 0.08)` | Thin container borders |
| **Glass Glow** | `--glass-glow` | `rgba(255, 255, 255, 0.03)` | Top highlight highlight |
| **Primary Accent** | `--accent-violet` / `from-indigo-500 to-purple-600` | `#6366f1` to `#9333ea` | Primary buttons, headers |
| **Secondary Accent**| `--accent-cyan` / `from-cyan-400 to-blue-500` | `#22d3ee` to `#3b82f6` | Charts, highlights, secondary CTAs |
| **Accent Emerald** | `--accent-emerald` | `#10b981` | Positive indicators, Success status |
| **Accent Rose** | `--accent-rose` | `#f43f5e` | Low stock, Cancelled status, alerts |
| **Text Primary** | `--text-primary` | `#f9fafb` | Primary titles, body text |
| **Text Secondary** | `--text-secondary` | `#9ca3af` | Secondary labels, captions |

### 1.2 Glassmorphism Core CSS (`src/index.css`)

Copy this core CSS definition into the root stylesheet to establish the utility classes for glassmorphic elements:

```css
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

:root {
  --bg-deep: #030712;
  --glass-bg: rgba(17, 24, 39, 0.45);
  --glass-border: rgba(255, 255, 255, 0.08);
  --glass-glow: rgba(255, 255, 255, 0.03);
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
}

body {
  background-color: var(--bg-deep);
  color: var(--text-primary);
  font-family: 'Outfit', 'Inter', sans-serif;
  overflow-x: hidden;
  background-image: 
    radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(34, 211, 238, 0.12) 0px, transparent 50%),
    radial-gradient(at 50% 50%, rgba(147, 51, 234, 0.08) 0px, transparent 50%);
  background-attachment: fixed;
}

/* Glassmorphism Utility Card */
.glass-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--glass-border);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

.glass-panel-hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-panel-hover:hover {
  background: rgba(17, 24, 39, 0.55);
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
  transform: translateY(-2px);
}

/* Neon Glow effects */
.glow-indigo {
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.25);
}

.glow-cyan {
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.25);
}

.glow-emerald {
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.25);
}

.glow-rose {
  box-shadow: 0 0 20px rgba(244, 63, 94, 0.25);
}

/* Custom Scrollbar for Glass UI */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}
```

---

## 2. Animation & Interaction Specifications

Animations are powered by **Framer Motion** for React. They are intentionally designed to be smooth, physics-based (springs), and lightweight.

### 2.1 Motion Standards
*   **Staggered Lists**: Products, orders, and customer lists fade and slide up sequentially.
*   **Page Transitions**: Slide-and-fade animations between route changes.
*   **Hover Scales**: Interactive items (Product Cards, Nav Links, Dashboard Cards) scale by `1.02x` or `1.03x` with smooth spring transitions (`type: "spring", stiffness: 300, damping: 20`).
*   **Micro-interactions**:
    *   **Cart Count Badge**: Bounces (`scale: [1, 1.3, 1]`) when a product is added.
    *   **Payment Success Modal**: Celebration checkmark draw-in animation + confetti burst.
    *   **Order Tracking Progress**: Line fill animation as order moves through stages (Pending $\rightarrow$ Packed $\rightarrow$ Shipped $\rightarrow$ Delivered).

### 2.2 Reusable Motion Framer Snippets
```javascript
// Fade & Slide Entrance (for Cards / Modals)
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] }
};

// Stagger Parent Container
export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.05
    }
  }
};

// Button Press / Hover
export const pressable = {
  whileHover: { scale: 1.02, y: -1 },
  whileTap: { scale: 0.98 }
};
```

---

## 3. Database Schema & RLS Rules (Supabase)

Below is the complete SQL structure to initialize the PostgreSQL database in Supabase, setup the profiles auto-generation, configure Row Level Security (RLS) policies, and handles tables structure.

### 3.1 SQL Database DDL Scripts

Execute this code block in the Supabase SQL editor:

```sql
-- Enable UUID generation
create extension if not exists "uuid-ossp";

-- 1. USERS Table (Syncs with auth.users)
create table public.users (
  id uuid references auth.users on delete cascade primary key,
  name text not null,
  email text unique not null,
  role text check (role in ('admin', 'customer')) default 'customer',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS on users
alter table public.users enable row level security;

-- 2. CATEGORIES Table
create table public.categories (
  id uuid default uuid_generate_v4() primary key,
  name text unique not null
);

alter table public.categories enable row level security;

-- 3. PRODUCTS Table
create table public.products (
  id uuid default uuid_generate_v4() primary key,
  name text not null,
  description text,
  price numeric(10, 2) not null check (price > 0),
  stock integer not null check (stock >= 0),
  category_id uuid references public.categories(id) on delete set null,
  image_url text,
  status text not null check (status in ('Available', 'Out of Stock')) default 'Available',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.products enable row level security;

-- 4. CUSTOMERS Table (Profile info for customer users)
create table public.customers (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.users(id) on delete cascade unique not null,
  phone text,
  address text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.customers enable row level security;

-- 5. CART Table (Transient storage of items in cart)
create table public.cart (
  id uuid default uuid_generate_v4() primary key,
  customer_id uuid references public.users(id) on delete cascade not null,
  product_id uuid references public.products(id) on delete cascade not null,
  quantity integer not null check (quantity > 0),
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  unique(customer_id, product_id)
);

alter table public.cart enable row level security;

-- 6. ORDERS Table
create table public.orders (
  id uuid default uuid_generate_v4() primary key,
  customer_id uuid references public.users(id) on delete set null not null,
  total_amount numeric(10, 2) not null check (total_amount >= 0),
  payment_status text not null check (payment_status in ('Pending', 'Paid', 'Failed')) default 'Paid',
  order_status text not null check (order_status in ('Pending', 'Packed', 'Shipped', 'Delivered', 'Cancelled')) default 'Pending',
  payment_method text not null check (payment_method in ('Dummy Credit Card', 'Cash on Delivery', 'UPI (Dummy)')),
  transaction_id text unique not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.orders enable row level security;

-- 7. ORDER_ITEMS Table
create table public.order_items (
  id uuid default uuid_generate_v4() primary key,
  order_id uuid references public.orders(id) on delete cascade not null,
  product_id uuid references public.products(id) on delete set null,
  quantity integer not null check (quantity > 0),
  price numeric(10, 2) not null check (price >= 0)
);

alter table public.order_items enable row level security;

-- 8. AUTOMATION FUNCTION & TRIGGER (Auto-create custom user entry when sign up occurs)
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.users (id, name, email, role)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'name', 'New User'),
    new.email,
    coalesce(new.raw_user_meta_data->>'role', 'customer')
  );
  
  -- If customer role, also seed empty customer profile
  if coalesce(new.raw_user_meta_data->>'role', 'customer') = 'customer' then
    insert into public.customers (user_id) values (new.id);
  end if;
  
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
```

### 3.2 Row Level Security (RLS) Policies

To protect sensitive datasets, implement these declarative RLS policies:

#### Users Table RLS
- **Enable Read Access**: Admins can read all profiles. Customers can only read their own profile.
- **Enable Write Access**: Admins can update any profile. Customers can only update their own `name`.
```sql
create policy "Allow users to read their own profile or admins to read all" on public.users
  for select using (auth.uid() = id or (select role from public.users where id = auth.uid()) = 'admin');

create policy "Allow users to update own profile or admins all" on public.users
  for update using (auth.uid() = id or (select role from public.users where id = auth.uid()) = 'admin');
```

#### Products & Categories RLS
- **Public Read Access**: Anyone (even unauthenticated users) can view products and categories.
- **Write Access Restrict**: Only users with the role `admin` can INSERT, UPDATE, or DELETE.
```sql
create policy "Allow public read access to products" on public.products
  for select using (true);

create policy "Allow admins full access to products" on public.products
  for all using ((select role from public.users where id = auth.uid()) = 'admin');

create policy "Allow public read access to categories" on public.categories
  for select using (true);

create policy "Allow admins full access to categories" on public.categories
  for all using ((select role from public.users where id = auth.uid()) = 'admin');
```

#### Cart Table RLS
- Customers can only perform operations on their own cart. Admins cannot interact with carts.
```sql
create policy "Allow users to manage own cart" on public.cart
  for all using (auth.uid() = customer_id);
```

#### Orders & Order Items RLS
- **Admins**: Can read, update and delete all orders.
- **Customers**: Can insert orders (checkout) and read/update their own orders. Can read their own order items.
```sql
create policy "Allow admins full access to orders" on public.orders
  for all using ((select role from public.users where id = auth.uid()) = 'admin');

create policy "Allow users to view own orders" on public.orders
  for select using (auth.uid() = customer_id);

create policy "Allow users to insert own orders" on public.orders
  for insert with check (auth.uid() = customer_id);

create policy "Allow admins full access to order items" on public.order_items
  for all using ((select role from public.users where id = auth.uid()) = 'admin');

create policy "Allow users to view own order items" on public.order_items
  for select using (
    exists (
      select 1 from public.orders 
      where orders.id = order_items.order_id 
      and orders.customer_id = auth.uid()
    )
  );
```

---

## 4. Frontend Route Architecture & Page Mockups

The app has distinct layouts for the **Customer Interface** and **Admin Dashboard**.

### 4.1 Route Declarations (`src/App.jsx`)
Configure routes using `react-router-dom`:

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute'; // Checks auth & roles

// Layouts
import CustomerLayout from './components/CustomerLayout';
import AdminLayout from './components/AdminLayout';

// Public pages
import Login from './pages/auth/Login';
import Signup from './pages/auth/Signup';
import Home from './pages/customer/Home';
import ProductDetails from './pages/customer/ProductDetails';

// Customer protected
import Cart from './pages/customer/Cart';
import Checkout from './pages/customer/Checkout';
import MyOrders from './pages/customer/MyOrders';

// Admin protected
import AdminDashboard from './pages/admin/Dashboard';
import AdminProducts from './pages/admin/Products';
import AdminAddProduct from './pages/admin/AddProduct';
import AdminEditProduct from './pages/admin/EditProduct';
import AdminOrders from './pages/admin/Orders';
import AdminCustomers from './pages/admin/Customers';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Customer Route Wrapper */}
        <Route element={<CustomerLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/product/:id" element={<ProductDetails />} />
          <Route path="/cart" element={<ProtectedRoute role="customer"><Cart /></ProtectedRoute>} />
          <Route path="/checkout" element={<ProtectedRoute role="customer"><Checkout /></ProtectedRoute>} />
          <Route path="/my-orders" element={<ProtectedRoute role="customer"><MyOrders /></ProtectedRoute>} />
        </Route>

        {/* Admin Route Wrapper */}
        <Route path="/admin" element={<ProtectedRoute role="admin"><AdminLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="dashboard" />} />
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="products" element={<AdminProducts />} />
          <Route path="products/add" element={<AdminAddProduct />} />
          <Route path="products/edit/:id" element={<AdminEditProduct />} />
          <Route path="orders" element={<AdminOrders />} />
          <Route path="customers" element={<AdminCustomers />} />
        </Route>

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

## 5. UI Components Details

### 5.1 Main Dashboards & User Pages

#### Customer Homepage (Product Catalog)
*   **Visual Structure**:
    *   **Hero Section**: Interactive parallax banner. Moving mesh gradient bg behind a large glassmorphic search input and horizontal list of category pills.
    *   **Responsive Grid**: Product cards utilizing `.glass-panel` and `.glass-panel-hover`.
    *   **Product Card**:
        *   An image container with a slight scale zoom on hover.
        *   Vibrant accent color tag representing category.
        *   Product name in bold and price highlighted with neon cyan text shadow.
        *   *Add to Cart* button: Radial hover glow. Triggers a Framer Motion bounce on the Navbar's Cart icon.
    *   **Filters Sidebar**: A sliding glass panel drawer from the right containing filters (Category checkboxes, Availability switch, Price range slider, and Sort by dropdown).

#### Product Details Page
*   **Visual Structure**:
    *   Split-column layout (50/50) on desktop.
    *   **Left Column**: High-resolution image card wrapped in a thick glass frame. Click-to-zoom feature.
    *   **Right Column**: Floating glass panel card. Product Title in large typography. Rating stars. Description text. In-stock/Out-of-stock badge with pulse-animation (green/red). Quantity stepper controls. *Add to Cart* & *Buy Now* gradient buttons.

#### Customer Cart Page
*   **Visual Structure**:
    *   List of line items on the left side, Order summary on the right.
    *   Items are rendered as horizontal glass bars. Staggered list entrance animation.
    *   Each item contains a thumbnail, name, unit price, quantity increment/decrement controls, and a garbage icon. Removing an item initiates a slide-left exit animation.
    *   **Order Summary**: Glass container with line items for Subtotal, Tax, Shipping (Free), and a bold Grand Total. *Proceed to Checkout* button with sliding gradient animation.

#### Checkout Page (Dummy Checkout)
*   **Visual Structure**:
    *   Interactive multi-step form (Shipping Details $\rightarrow$ Payment Details $\rightarrow$ Review & Submit).
    *   **Payment Option Selectors**: Custom radio buttons styled as glass cards. Features choices for: *Dummy Credit Card*, *UPI (Dummy)*, and *Cash on Delivery*. Icons illuminate with neon glowing colors when selected.
    *   **Pay Now Button**: Interactive, displays a full-screen loading backdrop blur when clicked, which fades into a beautiful checkmark success screen.
    *   **Success Component**: Triggered via local state. Uses a confetti package and an animated SVG checkmark drawing itself in, followed by a redirect button.

#### Customer Order History & Tracking
*   **Visual Structure**:
    *   Expandable accordions. Each accordion head represents an Order (ID, Date, Total, Status).
    *   Inside the accordion is the invoice breakdown alongside a **Visual Order Tracker**.
    *   **Order Tracker**: A progress bar showing step points (Pending $\rightarrow$ Packed $\rightarrow$ Shipped $\rightarrow$ Delivered). Active stages light up with neon emerald shadows. The line connecting completed stages animates from left to right.

---

### 5.2 Admin Dashboard UI (Featuring Recharts & Analytics)

#### Analytics Cards (Grid of 5)
1.  **Total Products**: Cobalt gradient background behind glass, displays count with a product icon.
2.  **Total Orders**: Violet gradient background, displays orders completed.
3.  **Total Revenue**: Emerald gradient, large font size of total sales (e.g., `₹1,24,500`), with an upward trend indicator.
4.  **Total Customers**: Orange gradient, count of registered customer accounts.
5.  **Low Stock Warning**: Crimson pulsing glow card, displays quantity of items with stock $< 5$. Clicking redirects to the product management filter.

#### Graphical Reports Section (Recharts Integration)
*   **Grid layout**: 2 columns on desktop.
*   **Left Chart (Area Chart)**: *Revenue over Time* (Monthly/Daily). Fill opacity gradient under the curve (Indigo/Cyan), custom glassmorphic hover tooltip showing values.
*   **Right Chart (Bar Chart)**: *Orders per Month*. Semi-transparent bars with rounded corners (`radius={[4, 4, 0, 0]}`) that animate up on page load.
*   **Bottom Chart (Pie Chart / Doughnut)**: *Category Distribution*. Concentric donut chart with glowing slice segments representing sales shares per category.

```javascript
// Recharts Glassmorphic Tooltip Component Example
const GlassTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-panel p-3 border border-white/10 rounded-xl shadow-xl">
        <p className="text-xs text-gray-400 font-semibold mb-1">{label}</p>
        <p className="text-sm font-bold text-cyan-400">
          Value: {`₹${payload[0].value.toLocaleString()}`}
        </p>
      </div>
    );
  }
  return null;
};
```

#### Recent Orders & Low Stock Tables
*   Tables are built using borderless layouts inside glass panels.
*   Alternating row backgrounds on hover.
*   Status pills are color-coded (Pending = Yellow/Orange, Packed = Purple, Shipped = Blue, Delivered = Green, Cancelled = Red) with subtle background transparency and glowing indicators.

---

## 6. Frontend Core Architecture

### 6.1 State Management (Contexts)

Two core React contexts manage global states: `AuthContext` and `CartContext`.

#### AuthContext (`src/hooks/useAuth.jsx`)
Handles interaction with Supabase Auth:
- `user`: Holds current authenticated user data.
- `profile`: Extends user data with database profile details (name, role).
- `loading`: Boolean state indicating active auth checks.
- `login(email, password)`: Call to `supabase.auth.signInWithPassword`.
- `signup(email, password, name, role)`: Sign up with meta data.
- `logout()`: Signs out the user and clears local state.

#### CartContext (`src/hooks/useCart.jsx`)
Synchronizes cart state between UI and Database (only for customers):
- `cartItems`: Array of active items `{ product_id, name, price, quantity, image_url }`.
- `addToCart(productId, quantity)`: Syncs with Supabase database (Upsert quantity on conflict).
- `removeFromCart(productId)`: Deletes product row from the cart.
- `updateQuantity(productId, quantity)`: Increments/decrements and updates database.
- `clearCart()`: Triggers upon successful checkout.

---

## 7. Crucial Workflows

### 7.1 Checkout & Stock Decrement Transaction Workflow
When a customer clicks "Pay Now" during checkout:

```
[UI] Checkout Page 
       │
       ▼
1. Validate Form (React Hook Form)
       │
       ▼
2. Call Database Function (RPC) via Supabase Client
   ├─ Insert into public.orders (Transaction ID created)
   ├─ Insert array of items into public.order_items
   ├─ Loop through items and decrement stock in public.products
   │  └─ IF stock drops below 0: RAISE EXCEPTION (Aborts Transaction)
   └─ Delete customer's cart rows in public.cart
       │
       ▼ (Database Transaction Success)
3. Return Transaction ID to Frontend
       │
       ▼
4. Render Confetti & Success Animation Screen
```

#### Supabase Database RPC function for Transactions
Deploy this SQL block to handle the checkout process atomically within PostgreSQL:

```sql
create or replace function public.process_checkout(
  p_customer_id uuid,
  p_total_amount numeric,
  p_payment_method text,
  p_transaction_id text,
  p_cart_items jsonb -- Array of {product_id, quantity, price}
) returns text as $$
declare
  v_order_id uuid;
  item record;
  v_current_stock integer;
begin
  -- 1. Create Order
  insert into public.orders (customer_id, total_amount, payment_method, transaction_id, payment_status, order_status)
  values (p_customer_id, p_total_amount, p_payment_method, p_transaction_id, 'Paid', 'Pending')
  returning id into v_order_id;

  -- 2. Process each item from cart
  for item in select * from jsonb_to_recordset(p_cart_items) as x(product_id uuid, quantity integer, price numeric) loop
    -- Check current stock before deducting
    select stock into v_current_stock from public.products where id = item.product_id for update;
    
    if v_current_stock < item.quantity then
      raise exception 'Product ID % is out of stock. Available: %', item.product_id, v_current_stock;
    end if;

    -- Decrement stock and update availability if 0
    update public.products 
    set 
      stock = stock - item.quantity,
      status = case when (stock - item.quantity) = 0 then 'Out of Stock' else 'Available' end
    where id = item.product_id;

    -- Insert into order items
    insert into public.order_items (order_id, product_id, quantity, price)
    values (v_order_id, item.product_id, item.quantity, item.price);
  end loop;

  -- 3. Clear user's cart
  delete from public.cart where customer_id = p_customer_id;

  return v_order_id::text;
exception
  when others then
    raise;
end;
$$ language plpgsql security definer;
```

---

## 8. Development Implementation Plan & File Tree

### 8.1 Suggested File Structure

Use this folder layout during project initialization:

```
src/
├── assets/                  # SVG assets, static design blobs
├── components/
│   ├── ui/
│   │   ├── Button.jsx       # Custom glassmorphic button component
│   │   ├── Card.jsx         # Wrapper for Glass Panel cards
│   │   ├── Table.jsx        # Glassmorphic Table wrapper
│   │   └── Loader.jsx       # Glowing spinner
│   ├── AdminLayout.jsx      # Left sidebar navigation structure
│   ├── CustomerLayout.jsx   # Topbar menu navigation layout
│   ├── Navbar.jsx           # Customer header with cart indicator
│   └── ProtectedRoute.jsx   # Role based Route guard
├── hooks/
│   ├── useAuth.jsx          # Context provider/hook for users & auth
│   └── useCart.jsx          # Context provider/hook for shopping cart
├── pages/
│   ├── auth/
│   │   ├── Login.jsx        # Login with moving background animations
│   │   └── Signup.jsx       # Signup page
│   ├── admin/
│   │   ├── Dashboard.jsx    # Analytics cards & graphs
│   │   ├── Products.jsx     # Manage products list view
│   │   ├── AddProduct.jsx   # Product creation form
│   │   ├── EditProduct.jsx  # Edit existing products
│   │   ├── Orders.jsx       # Admin order management
│   │   └── Customers.jsx    # Customers directory view
│   └── customer/
│       ├── Home.jsx         # Catalog page with filter/search
│       ├── ProductDetails.jsx # Detailed single-item view
│       ├── Cart.jsx         # Shopping cart page
│       ├── Checkout.jsx     # Form multi-step + payment success
│       └── MyOrders.jsx     # Order history and progress tracking
├── services/
│   └── supabaseClient.js    # Client connection configurations
├── utils/
│   └── format.js            # Currency & date formatters
├── App.jsx                  # Main route mapping definitions
├── index.css                # Base Tailwind + Glassmorphism system
└── main.jsx                 # Entrypoint attaching App.jsx
```

### 8.2 Build Order & Verification Checklist

When initiating development, follow this chronological schedule:

1.  **Backend Initialisation**: Setup a Supabase project, execute the SQL schema script in Section 3, and add demo product records via database insertions. Setup a Storage bucket named `product-images` with public read access.
2.  **Styles and Theme Injection**: Add dependencies (`framer-motion`, `recharts`, `react-router-dom`, `react-icons`, `@supabase/supabase-js`, `react-hook-form`, `axios`). Inject Section 1.2 code into `src/index.css`.
3.  **Client Configurations**: Build `src/services/supabaseClient.js`. Establish environment variables for `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.
4.  **Auth Implementation**: Write `useAuth.jsx` context. Build `Login.jsx` and `Signup.jsx` pages using glassmorphic panels positioned over rotating mesh background divs.
5.  **Admin Base**: Assemble `AdminLayout.jsx` and `AdminDashboard.jsx`. Integrate `recharts` for visual revenue and order graphs. Include glassmorphic tooltips in the charts.
6.  **Product CRUD**: Build product list tables, product creation/editing pages. Hook image uploads to Supabase Storage.
7.  **Customer Portal**: Build `Home.jsx` with search, sorting, and categories. Create the `ProductDetails` view.
8.  **Cart & Orders Transactions**: Implement the checkout step flow, hook up the `process_checkout` database RPC function, and display the payment success screen with appropriate animation.
9.  **Verification**: Test user flows to ensure checkout automatically decrements inventory stock and restricts invalid purchases (e.g., negative stock, out of stock status triggers). Verify that RLS prevents customer access to admin interfaces and blocks unauthenticated write access.
