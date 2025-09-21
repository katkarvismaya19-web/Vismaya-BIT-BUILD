// Frontend Configuration for Paisabuddy
// This file contains non-sensitive configuration that can be publicly visible

const CONFIG = {
    // API Configuration
    API_BASE_URL: 'http://127.0.0.1:8000',
    
    // Google OAuth Configuration
    // Replace this with your actual Google Client ID
    GOOGLE_CLIENT_ID: 'your_google_client_id.apps.googleusercontent.com',
    
    // Other frontend settings
    APP_NAME: 'Paisabuddy',
    VERSION: '2.0.0',
    
    // Feature flags
    FEATURES: {
        GOOGLE_OAUTH: true,
        DEMO_MODE: true,
        OFFLINE_MODE: false
    },
    
    // UI Configuration
    THEME: {
        PRIMARY_COLOR: '#2563eb',
        BACKGROUND_GRADIENT: 'linear-gradient(-45deg, #89f7fe, #66a6ff, #a1c4fd, #c2e9fb)'
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}