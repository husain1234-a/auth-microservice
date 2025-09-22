import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Auth Microservice',
  description: 'Secure authentication with Firebase',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning={true}>{children}</body>
    </html>
  );
}