'use client';

import { useEffect } from 'react';
import { getRedirectResult } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { authAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';
import GoogleSignIn from '@/components/GoogleSignIn';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    console.log('🚀 Home page loaded, checking for redirect result...');

    // Handle redirect result when user comes back from Google OAuth
    const handleRedirectResult = async () => {
      try {
        console.log('🔍 Checking redirect result...');
        const result = await getRedirectResult(auth);

        if (result?.user) {
          console.log('✅ Redirect result found:', {
            uid: result.user.uid,
            email: result.user.email,
            displayName: result.user.displayName
          });

          console.log('🔑 Getting ID token from redirect result...');
          const idToken = await result.user.getIdToken();
          console.log('✅ ID token obtained, length:', idToken.length);

          console.log('📡 Sending redirect result to backend...');
          const response = await authAPI.googleLogin(idToken);
          console.log('✅ Backend response for redirect:', response.data);

          // Check if user has phone number, if not redirect to phone collection
          if (!response.data.user.phone_number) {
            console.log('📞 No phone number found, redirecting to phone collection...');
            router.push('/collect-phone');
          } else {
            console.log('🎯 User has phone number, redirecting to dashboard from redirect result...');
            router.push('/dashboard');
          }
        } else {
          console.log('🚫 No redirect result found');
        }
      } catch (error: any) {
        console.error('❌ Redirect sign-in error:', {
          message: error.message,
          code: error.code,
          stack: error.stack
        });
      }
    };

    handleRedirectResult();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900">
            Sign in to your account
          </h2>
        </div>

        {/* Debug Info Panel - Remove in production */}
        <div className="bg-gray-100 p-3 rounded text-xs">
          <details>
            <summary className="cursor-pointer font-semibold">Debug Info (Click to expand)</summary>
            <div className="mt-2 space-y-1">
              <div>API URL: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</div>
              <div>Firebase Project: {process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || 'NOT SET'}</div>
              <div>Firebase API Key: {process.env.NEXT_PUBLIC_FIREBASE_API_KEY ? 'SET' : 'NOT SET'}</div>
              <div>Auth Domain: {process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || 'NOT SET'}</div>
            </div>
          </details>
        </div>

        {/* Phone Number Info Panel */}
        <div className="bg-blue-50 border border-blue-200 p-3 rounded text-xs">
          <div className="text-blue-800 font-semibold mb-1">📞 One-time Phone Collection:</div>
          <div className="text-blue-700 text-xs">
            After Google login, first-time users will be asked to provide their phone number. This is a one-time setup - returning users won't be asked again.
          </div>
        </div>

        <div className="space-y-6">
          <GoogleSignIn />
        </div>
      </div>
    </div>
  );
}