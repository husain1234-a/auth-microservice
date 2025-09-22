'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import PhoneCollection from '@/components/PhoneCollection';

export default function CollectPhonePage() {
    const [user, setUser] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        console.log('📱 Phone collection page loaded...');

        const fetchUser = async () => {
            try {
                console.log('📡 Fetching current user...');
                const response = await authAPI.getCurrentUser();
                console.log('✅ User data received:', response.data);

                // If user already has phone number, redirect to dashboard
                if (response.data.phone_number) {
                    console.log('📞 User already has phone number, redirecting to dashboard...');
                    router.push('/dashboard');
                    return;
                }

                setUser(response.data);
            } catch (error: any) {
                console.error('❌ Failed to fetch user:', error);
                console.log('🔄 Redirecting to login page...');
                router.push('/');
            } finally {
                setLoading(false);
            }
        };

        fetchUser();
    }, [router]);

    const handlePhoneComplete = (phoneNumber: string) => {
        console.log('✅ Phone collection completed:', phoneNumber);
        console.log('🎯 Redirecting to dashboard...');
        router.push('/dashboard');
    };

    const handleSkip = () => {
        console.log('⏭️ User skipped phone collection');
        console.log('🎯 Redirecting to dashboard...');
        router.push('/dashboard');
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-xl text-gray-600">Loading...</div>
            </div>
        );
    }

    if (!user) {
        return null; // Will redirect to login
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <PhoneCollection
                user={user}
                onComplete={handlePhoneComplete}
                onSkip={handleSkip}
            />
        </div>
    );
}