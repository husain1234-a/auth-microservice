/**
 * Secure storage utility for sensitive user data
 * Uses sessionStorage for temporary data and localStorage for persistent data
 * All data is encrypted before storage
 */

// Simple encryption/decryption using base64 and a key
const STORAGE_KEY = 'grofast_secure_';
const ENCRYPTION_KEY = 'gf_2024_secure_key';

// Simple XOR encryption (for demo purposes - use proper encryption in production)
function encrypt(text: string): string {
    let result = '';
    for (let i = 0; i < text.length; i++) {
        result += String.fromCharCode(
            text.charCodeAt(i) ^ ENCRYPTION_KEY.charCodeAt(i % ENCRYPTION_KEY.length)
        );
    }
    return btoa(result);
}

function decrypt(encryptedText: string): string {
    try {
        const text = atob(encryptedText);
        let result = '';
        for (let i = 0; i < text.length; i++) {
            result += String.fromCharCode(
                text.charCodeAt(i) ^ ENCRYPTION_KEY.charCodeAt(i % ENCRYPTION_KEY.length)
            );
        }
        return result;
    } catch (error) {
        console.error('Failed to decrypt data:', error);
        return '';
    }
}

export const secureStorage = {
    // Store data securely in sessionStorage (cleared when tab closes)
    setSession: (key: string, value: any): void => {
        try {
            const serialized = JSON.stringify(value);
            const encrypted = encrypt(serialized);
            sessionStorage.setItem(STORAGE_KEY + key, encrypted);
        } catch (error) {
            console.error('Failed to store session data:', error);
        }
    },

    // Get data from sessionStorage
    getSession: <T>(key: string): T | null => {
        try {
            const encrypted = sessionStorage.getItem(STORAGE_KEY + key);
            if (!encrypted) return null;

            const decrypted = decrypt(encrypted);
            if (!decrypted) return null;

            return JSON.parse(decrypted) as T;
        } catch (error) {
            console.error('Failed to retrieve session data:', error);
            return null;
        }
    },

    // Store data securely in localStorage (persistent)
    setPersistent: (key: string, value: any): void => {
        try {
            const serialized = JSON.stringify(value);
            const encrypted = encrypt(serialized);
            localStorage.setItem(STORAGE_KEY + key, encrypted);
        } catch (error) {
            console.error('Failed to store persistent data:', error);
        }
    },

    // Get data from localStorage
    getPersistent: <T>(key: string): T | null => {
        try {
            const encrypted = localStorage.getItem(STORAGE_KEY + key);
            if (!encrypted) return null;

            const decrypted = decrypt(encrypted);
            if (!decrypted) return null;

            return JSON.parse(decrypted) as T;
        } catch (error) {
            console.error('Failed to retrieve persistent data:', error);
            return null;
        }
    },

    // Remove data from sessionStorage
    removeSession: (key: string): void => {
        try {
            sessionStorage.removeItem(STORAGE_KEY + key);
        } catch (error) {
            console.error('Failed to remove session data:', error);
        }
    },

    // Remove data from localStorage
    removePersistent: (key: string): void => {
        try {
            localStorage.removeItem(STORAGE_KEY + key);
        } catch (error) {
            console.error('Failed to remove persistent data:', error);
        }
    },

    // Clear all secure storage
    clearAll: (): void => {
        try {
            // Clear sessionStorage
            Object.keys(sessionStorage).forEach(key => {
                if (key.startsWith(STORAGE_KEY)) {
                    sessionStorage.removeItem(key);
                }
            });

            // Clear localStorage
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith(STORAGE_KEY)) {
                    localStorage.removeItem(key);
                }
            });
        } catch (error) {
            console.error('Failed to clear secure storage:', error);
        }
    }
};

// User-specific storage functions
export const userStorage = {
    // Store user data securely
    setUser: (user: any): void => {
        secureStorage.setSession('user', user);
        // Also store in localStorage for persistence across sessions
        secureStorage.setPersistent('user_backup', {
            uid: user.uid,
            email: user.email,
            role: user.role,
            display_name: user.display_name,
            // Don't store sensitive data in persistent storage
        });
    },

    // Get user data
    getUser: (): any | null => {
        // Try session storage first
        let user = secureStorage.getSession('user');
        if (user) return user;

        // Fallback to persistent storage backup
        const backup = secureStorage.getPersistent('user_backup');
        return backup;
    },

    // Remove user data
    removeUser: (): void => {
        secureStorage.removeSession('user');
        secureStorage.removePersistent('user_backup');
    },

    // Store user preferences
    setPreferences: (preferences: any): void => {
        secureStorage.setPersistent('user_preferences', preferences);
    },

    // Get user preferences
    getPreferences: (): any | null => {
        return secureStorage.getPersistent('user_preferences');
    }
};

// Authentication token storage
export const authStorage = {
    // Store auth token securely (session only for security)
    setToken: (token: string): void => {
        secureStorage.setSession('auth_token', token);
    },

    // Get auth token
    getToken: (): string | null => {
        return secureStorage.getSession('auth_token');
    },

    // Remove auth token
    removeToken: (): void => {
        secureStorage.removeSession('auth_token');
    }
};