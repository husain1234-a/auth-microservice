'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import PhoneCollection from '@/components/PhoneCollection';

export default function CollectPhonePage() {
    const { user, loading: userLoading } = useUser();
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        console.log('📱 Phone collection page loaded - using UserContext...');

        const checkUser = () => {
            if (!userLoading) {
                if (!user) {
                    console.log('🔄 No user found, redirecting to login...');
                    router.push('/');
                    return;
                }

                // If user already has phone number, redirect to dashboard
                if (user.phone_number) {
                    console.log('📞 User already has phone number, redirecting to dashboard...');
                    router.push('/dashboard');
                    return;
                }

                setLoading(false);
            }
        };

        checkUser();
    }, [user, userLoading, router]);

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