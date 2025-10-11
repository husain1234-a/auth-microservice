import OrderNavigation from '@/components/orders/OrderNavigation';

export default function OrdersLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-gray-50">
            <OrderNavigation />
            {children}
        </div>
    );
}