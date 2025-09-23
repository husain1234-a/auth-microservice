import type { Metadata } from 'next';
import './globals.css';

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
        {children}
      </body>
    </html>
  );
}