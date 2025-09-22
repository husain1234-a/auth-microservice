'use client';

import { useState } from 'react';
import { signInWithPopup, signInWithRedirect, getRedirectResult } from 'firebase/auth';
import { auth, googleProvider } from '@/lib/firebase';
import { authAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';

export default function GoogleSignIn() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [usePopup, setUsePopup] = useState(true);

  const handleGoogleSignIn = async () => {
    try {
      console.log('🚀 Starting Google sign-in process...');
      console.log('📱 Using popup method:', usePopup);

      setIsLoading(true);
      setError(null);

      let result;

      if (usePopup) {
        console.log('🔄 Attempting popup sign-in...');
        try {
          result = await signInWithPopup(auth, googleProvider);
          console.log('✅ Popup sign-in successful:', result.user.uid);
        } catch (popupError: any) {
          console.warn('⚠️ Popup sign-in failed, falling back to redirect:', popupError.message);

          // Fall back to redirect if popup fails
          console.log('🔄 Switching to redirect method...');
          await signInWithRedirect(auth, googleProvider);
          // The redirect will handle the rest
          return;
        }
      } else {
        console.log('🔄 Using redirect sign-in...');
        await signInWithRedirect(auth, googleProvider);
        // The redirect will handle the rest
        return;
      }

      if (result?.user) {
        console.log('👤 User authenticated:', {
          uid: result.user.uid,
          email: result.user.email,
          displayName: result.user.displayName,
          phoneNumber: result.user.phoneNumber,
          photoURL: result.user.photoURL
        });

        // Log additional user metadata
        console.log('📋 User metadata:', {
          creationTime: result.user.metadata.creationTime,
          lastSignInTime: result.user.metadata.lastSignInTime
        });

        // Log provider data
        console.log('🔗 Provider data:', result.user.providerData);

        console.log('🔑 Getting ID token...');
        const idToken = await result.user.getIdToken();
        console.log('✅ ID token obtained, length:', idToken.length);

        // Decode and log token claims (for debugging - remove in production)
        try {
          const tokenPayload = JSON.parse(atob(idToken.split('.')[1]));
          console.log('🎫 Token claims:', {
            iss: tokenPayload.iss,
            aud: tokenPayload.aud,
            email: tokenPayload.email,
            phone_number: tokenPayload.phone_number,
            name: tokenPayload.name,
            picture: tokenPayload.picture
          });
        } catch (e) {
          console.warn('⚠️ Could not decode token payload');
        }

        console.log('📡 Sending to backend...');
        const response = await authAPI.googleLogin(idToken);
        console.log('✅ Backend response:', response.data);

        // Check if user has phone number, if not redirect to phone collection
        if (!response.data.user.phone_number) {
          console.log('📞 No phone number found, redirecting to phone collection...');
          router.push('/collect-phone');
        } else {
          console.log('🎯 User has phone number, redirecting to dashboard...');
          router.push('/dashboard');
        }
      }
    } catch (error: any) {
      console.error('❌ Google sign-in error:', {
        message: error.message,
        code: error.code,
        stack: error.stack
      });
      setError(error.message || 'Failed to sign in with Google');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full space-y-3">
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>Authentication method:</span>
        <button
          onClick={() => setUsePopup(!usePopup)}
          className="text-blue-600 hover:text-blue-700 underline"
          type="button"
        >
          {usePopup ? 'Switch to Redirect' : 'Switch to Popup'}
        </button>
      </div>

      <button
        onClick={handleGoogleSignIn}
        disabled={isLoading}
        className="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          usePopup ? 'Opening Google Popup...' : 'Redirecting to Google...'
        ) : (
          `Sign in with Google (${usePopup ? 'Popup' : 'Redirect'})`
        )}
      </button>

      {error && (
        <div className="text-red-500 text-sm mt-2 p-2 bg-red-50 rounded">
          <div className="font-semibold">Error:</div>
          <div>{error}</div>
        </div>
      )}
    </div>
  );
}