'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import { SecureStorage, UserData } from '@/lib/storage';

interface UserContextType {
    user: UserData | null;
    loading: boolean;
    login: (userData: UserData) => void;
    logout: () => void;
    updateUser: (userData: UserData) => void;
    hasRole: (roles: string | string[]) => boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<UserData | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        initializeUser();
    }, []);

    const initializeUser = async () => {
        try {
            // Check if we have stored user data and valid session
            const storedUser = SecureStorage.getUser();
            const isSessionValid = SecureStorage.isSessionValid();

            if (storedUser && isSessionValid) {
                console.log('🔄 Using stored user data');
                setUser(storedUser);
                SecureStorage.updateActivity();
            } else {
                console.log('📡 Fetching fresh user data from server');
                // Fetch fresh user data from server
                const response = await authAPI.getCurrentUser();
                const userData = response.data as UserData;

                setUser(userData);
                SecureStorage.setUser(userData);
                SecureStorage.updateActivity();
            }
        } catch (error) {
            console.error('❌ Failed to initialize user:', error);
            // Clear any corrupted data
            SecureStorage.clearUser();
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const login = (userData: UserData) => {
        setUser(userData);
        SecureStorage.setUser(userData);
        SecureStorage.updateActivity();
        console.log('✅ User logged in:', userData.role);
    };

    const logout = async () => {
        try {
            await authAPI.logout();
        } catch (error) {
            console.error('❌ Logout API error:', error);
        } finally {
            setUser(null);
            SecureStorage.clearUser();
            router.push('/');
            console.log('👋 User logged out');
        }
    };

    const updateUser = (userData: UserData) => {
        setUser(userData);
        SecureStorage.setUser(userData);
        SecureStorage.updateActivity();
        console.log('🔄 User data updated');
    };

    const hasRole = (roles: string | string[]): boolean => {
        if (!user) return false;

        const roleArray = Array.isArray(roles) ? roles : [roles];
        return roleArray.includes(user.role);
    };

    return (
        <UserContext.Provider value={{
            user,
            loading,
            login,
            logout,
            updateUser,
            hasRole
        }}>
            {children}
        </UserContext.Provider>
    );
}

export function useUser() {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
}