# Product Management Frontend

This is the frontend application for the Product Management System, built with Next.js, React, and TypeScript. It provides a complete admin dashboard for managing products and categories through the backend API.

## Features

- User authentication with Google Sign-In
- Phone number collection for new users
- Product management (CRUD operations)
- Category management (CRUD operations)
- Image upload for products and categories
- Responsive design with Tailwind CSS

## API Integration

The frontend is tightly integrated with the backend API endpoints:

### Authentication Endpoints
- `POST /auth/google-login` - Google authentication
- `POST /auth/update-phone` - Update user phone number
- `GET /auth/me` - Get current user information
- `POST /auth/logout` - Logout user

### Product Endpoints
- `GET /api/products` - Get all products (with filtering and pagination)
- `GET /api/products/{id}` - Get specific product
- `POST /api/products` - Create new product (multipart form data)
- `PUT /api/products/{id}` - Update existing product (multipart form data)
- `DELETE /api/products/{id}` - Delete product (soft delete)

### Category Endpoints
- `GET /api/categories` - Get all categories
- `GET /api/categories/{id}` - Get specific category
- `POST /api/categories` - Create new category (multipart form data)
- `PUT /api/categories/{id}` - Update existing category (multipart form data)

## Project Structure

```
src/
├── app/                 # Next.js app router pages
│   ├── dashboard/       # Admin dashboard pages
│   │   ├── products/    # Product management page
│   │   ├── categories/  # Category management page
│   │   ├── layout.tsx   # Dashboard layout
│   │   └── page.tsx     # Dashboard home page
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Home page
├── components/          # Reusable React components
├── lib/                 # Utility functions and API clients
│   ├── api.ts           # Authentication API client
│   └── productApi.ts    # Product/Category API client
└── utils/               # Helper functions
```

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env.local` file based on `.env.local.example`:
   ```bash
   cp .env.local.example .env.local
   ```
   
3. Update the environment variables with your Firebase configuration and API URL.

4. Run the development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

The following environment variables are required:

- `NEXT_PUBLIC_AUTH_API_URL` - The base URL for the authentication service (default: http://localhost:8001)
- `NEXT_PUBLIC_PRODUCT_API_URL` - The base URL for the product service (default: http://localhost:8002)
- `NEXT_PUBLIC_FIREBASE_API_KEY` - Firebase API key
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` - Firebase auth domain
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID` - Firebase project ID
- `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` - Firebase storage bucket
- `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` - Firebase messaging sender ID
- `NEXT_PUBLIC_FIREBASE_APP_ID` - Firebase app ID

## API Client Usage

The frontend uses two main API clients:

### Authentication API (`lib/api.ts`)
```typescript
import { authAPI } from '@/lib/api';

// Google login
const response = await authAPI.googleLogin(idToken);

// Get current user
const user = await authAPI.getCurrentUser();

// Update phone number
await authAPI.updatePhoneNumber(phoneNumber);

// Logout
await authAPI.logout();
```

### Product API (`lib/productApi.ts`)
```typescript
import { productAPI } from '@/lib/productApi';

// Get products
const products = await productAPI.getProducts({ category_id: 1 });

// Create product
const newProduct = await productAPI.createProduct({
  name: 'Product Name',
  price: 99.99,
  category_id: 1,
  image: file // optional
});

// Update product
const updatedProduct = await productAPI.updateProduct(1, {
  name: 'Updated Name',
  price: 89.99
});

// Delete product
await productAPI.deleteProduct(1);

// Similar functions for categories
const categories = await productAPI.getCategories();
const newCategory = await productAPI.createCategory({ name: 'Category Name' });
```

## Form Data Handling

All product and category creation/update operations use multipart form data as required by the backend API. The frontend automatically handles:

- Converting form fields to appropriate data types
- Attaching image files when provided
- Setting proper Content-Type headers

## Deployment

To deploy the frontend application:

1. Build the application:
   ```bash
   npm run build
   ```

2. Start the production server:
   ```bash
   npm start
   ```

Or deploy to platforms like Vercel, Netlify, or any static hosting service that supports Next.js.