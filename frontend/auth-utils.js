// auth-utils.js - Reusable authentication utilities

const AUTH_BASE = 'http://localhost:8000/api/auth';

// Global authentication state
let currentUser = null;

// Check if user is authenticated
async function checkAuth() {
    try {
        const response = await fetch(`${AUTH_BASE}/me`, {
            credentials: 'include'
        });
        if (response.ok) {
            currentUser = await response.json();
            return currentUser;
        }
        return null;
    } catch (error) {
        console.error('Auth check error:', error);
        return null;
    }
}

// Logout function
async function logoutUser() {
    try {
        const response = await fetch(`${AUTH_BASE}/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            currentUser = null;
            // Redirect to home page after logout
            window.location.href = 'index.html';
            return true;
        }
        throw new Error('Logout failed');
    } catch (error) {
        console.error('Logout error:', error);
        return false;
    }
}

// Update page with user information
function updateAuthDisplay(options = {}) {
    const {
        userBadgeSelector = '.user-badge',
        navUsernameSelector = '#nav-username',
        userNavSelector = '#user-nav',
        authNavSelector = '#auth-nav',
        logoutNavSelector = '#logout-nav'
    } = options;
    
    if (currentUser) {
        // Update user badge if exists
        const userBadge = document.querySelector(userBadgeSelector);
        if (userBadge) {
            userBadge.innerHTML = `<i class="fas fa-user-graduate"></i> Welcome, ${currentUser.name}!`;
        }
        
        // Update navbar username if exists
        const navUsername = document.querySelector(navUsernameSelector);
        if (navUsername) {
            navUsername.textContent = currentUser.name;
        }
        
        // Show/hide navigation elements
        const userNav = document.querySelector(userNavSelector);
        const authNav = document.querySelector(authNavSelector);
        const logoutNav = document.querySelector(logoutNavSelector);
        
        if (userNav) userNav.style.display = 'block';
        if (authNav) authNav.style.display = 'none';
        if (logoutNav) logoutNav.style.display = 'block';
        
    } else {
        // Reset user badge
        const userBadge = document.querySelector(userBadgeSelector);
        if (userBadge) {
            userBadge.innerHTML = '<i class="fas fa-user-graduate"></i> Welcome, Visitor!';
        }
        
        // Hide/show navigation elements
        const userNav = document.querySelector(userNavSelector);
        const authNav = document.querySelector(authNavSelector);
        const logoutNav = document.querySelector(logoutNavSelector);
        
        if (userNav) userNav.style.display = 'none';
        if (authNav) authNav.style.display = 'block';
        if (logoutNav) logoutNav.style.display = 'none';
    }
}

// Initialize authentication for any page
async function initAuth(options = {}) {
    try {
        const user = await checkAuth();
        updateAuthDisplay(options);
        return user;
    } catch (error) {
        console.error('Auth initialization error:', error);
        return null;
    }
}

// Add this to make logout available globally
window.logout = logoutUser;