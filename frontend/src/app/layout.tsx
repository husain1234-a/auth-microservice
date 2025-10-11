import type { Metadata } from 'next';
import './globals.css';
import './skeleton.css';
import { CartProvider } from '@/contexts/CartContext';
import { UserProvider } from '@/contexts/UserContext';
import { OrderProvider } from '@/contexts/OrderContext';

export const metadata: Metadata = {
  title: 'Product Management System',
  description: 'Admin dashboard for product and category management',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning={true} className="min-h-screen bg-gray-50">
        <UserProvider>
          <CartProvider>
            <OrderProvider>
              {children}
            </OrderProvider>
          </CartProvider>
        </UserProvider>
      </body>
    </html>
  );
}