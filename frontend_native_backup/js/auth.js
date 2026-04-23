/** Author: Vishal Joshi (vishaljoshi9694@gmail.com) **/
const TOKEN_KEY = 'insight_token';
const USER_KEY = 'insight_user';

/**
 * Check if user is authenticated
 * @param {boolean} redirect - Whether to redirect to login if not authenticated
 * @returns {object|null} User data or null
 */
export function checkAuth(redirect = true) {
    const token = localStorage.getItem(TOKEN_KEY);
    const userStr = localStorage.getItem(USER_KEY);

    if (!token || !userStr) {
        if (redirect) {
            window.location.href = 'login.html';
        }
        return null;
    }

    try {
        return JSON.parse(userStr);
    } catch (e) {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        if (redirect) {
            window.location.href = 'login.html';
        }
        return null;
    }
}

/**
 * Save authentication data
 * @param {string} token - JWT token
 * @param {string} role - User role
 * @param {string} username - Username
 * @param {number} userId - User ID
 */
export function saveAuth(token, role, username, userId) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify({
        role,
        username,
        userId,
        loggedInAt: new Date().toISOString()
    }));
}

/**
 * Log out the current user
 */
export function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.href = 'index.html';
}

/**
 * Get the authorization header for API requests
 * @returns {object} Headers object
 */
export function getAuthHeaders() {
    const token = localStorage.getItem(TOKEN_KEY);
    return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
    };
}

/**
 * Check if user has admin role
 * @returns {boolean}
 */
export function isAdmin() {
    const user = checkAuth(false);
    return user && user.role === 'Admin';
}

/**
 * Get current user data
 * @returns {object|null}
 */
export function getCurrentUser() {
    return checkAuth(false);
}

/**
 * Check if token is expired (basic check)
 * @returns {boolean}
 */
export function isTokenExpired() {
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return true;

    try {
        const user = JSON.parse(userStr);
        const loggedIn = new Date(user.loggedInAt);
        const now = new Date();
        // Token expires after 30 minutes
        const diffMinutes = (now - loggedIn) / 1000 / 60;
        return diffMinutes > 30;
    } catch {
        return true;
    }
}
