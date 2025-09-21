// Enhanced Paisabuddy Portfolio JavaScript
// Integrates with all backend enhanced features

// API Configuration
const API_BASE = 'http://127.0.0.1:8000';
const ENHANCED_API = {
    trading: `${API_BASE}/trading`,
    ai: `${API_BASE}/ai`,
    social: `${API_BASE}/social`,
    achievements: `${API_BASE}/achievements`,
    analytics: `${API_BASE}/analytics`,
    dashboard: `${API_BASE}/api/dashboard`,  // Updated to use new API endpoint
    market: `${API_BASE}/market`,
    health: `${API_BASE}/health`
};

// Global State
let currentUser = null;
let currentSimulation = null;
let currentTradingMode = 'intraday';
let portfolioChart = null;
let marketStocks = [];
let userAchievements = [];
let communityPosts = [];

// Authentication Functions
async function checkAuthentication() {
    try {
        const response = await fetch(`${API_BASE}/api/auth/me`, {
            credentials: 'include'
        });
        if (response.ok) {
            currentUser = await response.json();
            updateUserDisplay();
            return true;
        }
        return false;
    } catch (error) {
        console.error('Auth check error:', error);
        return false;
    }
}

async function demoLogin(username = 'demo') {
    try {
        const response = await fetch(`${API_BASE}/api/auth/demo-login/${username}`, {
            method: 'POST',
            credentials: 'include'
        });
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            updateUserDisplay();
            showToast('Demo login successful! Welcome to enhanced trading!', 'success');
            await initializeDashboard();
            return true;
        }
        throw new Error('Demo login failed');
    } catch (error) {
        showToast('Demo login failed: ' + error.message, 'error');
        return false;
    }
}

function updateUserDisplay() {
    if (currentUser) {
        document.getElementById('nav-username').textContent = currentUser.name;
        document.getElementById('user-nav').style.display = 'block';
        document.getElementById('logout-nav').style.display = 'block';
        document.getElementById('auth-nav').style.display = 'none';
    } else {
        document.getElementById('user-nav').style.display = 'none';
        document.getElementById('logout-nav').style.display = 'none';
        document.getElementById('auth-nav').style.display = 'block';
    }
}

async function logout() {
    try {
        const response = await fetch(`${API_BASE}/api/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            currentUser = null;
            currentSimulation = null;
            updateUserDisplay();
            showToast('Logged out successfully!', 'success');
            resetDashboard();
        } else {
            throw new Error('Logout failed');
        }
    } catch (error) {
        showToast('Logout failed', 'error');
    }
}

// Dashboard Navigation Functions
// Trading mode selection is now handled in portfolio.html
// This dashboard focuses on analytics and transaction history

// Enhanced API Functions

// Trading Simulation APIs
async function createSimulation(simulationData) {
    try {
        const response = await fetch(`${ENHANCED_API.trading}/create-simulation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(simulationData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create simulation');
        }
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Create simulation error:', error);
        throw error;
    }
}

async function getUserSimulations() {
    try {
        const response = await fetch(`${ENHANCED_API.trading}/user-simulations`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch simulations');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Get simulations error:', error);
        return [];
    }
}

async function executeTradeEnhanced(tradeData) {
    try {
        const response = await fetch(`${ENHANCED_API.trading}/execute-trade`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(tradeData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Trade execution failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Execute trade error:', error);
        throw error;
    }
}

// AI & Personalization APIs
async function getBehavioralAnalysis() {
    try {
        const response = await fetch(`${ENHANCED_API.ai}/behavioral-analysis`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            return { personality_insights: { risk_tolerance: 'moderate', trading_style: 'beginner' }, recommendations: [] };
        }
        
        return await response.json();
    } catch (error) {
        console.error('Behavioral analysis error:', error);
        return { personality_insights: { risk_tolerance: 'moderate', trading_style: 'beginner' }, recommendations: [] };
    }
}

async function getStockSuggestions(simulationId = null) {
    try {
        const url = simulationId ? 
            `${ENHANCED_API.ai}/stock-suggestions?simulation_id=${simulationId}` : 
            `${ENHANCED_API.ai}/stock-suggestions`;
            
        const response = await fetch(url, { credentials: 'include' });
        
        if (!response.ok) {
            return [
                { symbol: 'TCS', sector: 'IT', current_price: 3500, reason: 'Stable large cap stock', risk_level: 'low', confidence: 0.8 },
                { symbol: 'RELIANCE', sector: 'Energy', current_price: 2800, reason: 'Market leader in energy sector', risk_level: 'medium', confidence: 0.7 }
            ];
        }
        
        return await response.json();
    } catch (error) {
        console.error('Stock suggestions error:', error);
        return [];
    }
}

// Social Features APIs
async function createSocialPost(postData) {
    try {
        const response = await fetch(`${ENHANCED_API.social}/create-post`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(postData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create post');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Create post error:', error);
        throw error;
    }
}

async function getCommunityFeed(limit = 10) {
    try {
        const response = await fetch(`${ENHANCED_API.social}/community-feed?limit=${limit}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            return [];
        }
        
        return await response.json();
    } catch (error) {
        console.error('Community feed error:', error);
        return [];
    }
}

// Achievement APIs
async function getUserAchievements() {
    try {
        const response = await fetch(`${ENHANCED_API.achievements}/user-achievements`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            return { earned_achievements: [], total_earned: 0, total_points: 0, completion_percentage: 0 };
        }
        
        return await response.json();
    } catch (error) {
        console.error('Achievements error:', error);
        return { earned_achievements: [], total_earned: 0, total_points: 0, completion_percentage: 0 };
    }
}

// Analytics APIs
async function getPortfolioAnalytics(simulationId) {
    try {
        const response = await fetch(`${ENHANCED_API.analytics}/portfolio/${simulationId}`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            return { performance_metrics: {}, risk_metrics: {}, recommendations: [] };
        }
        
        return await response.json();
    } catch (error) {
        console.error('Portfolio analytics error:', error);
        return { performance_metrics: {}, risk_metrics: {}, recommendations: [] };
    }
}

// Dashboard API
async function getDashboardOverview() {
    try {
        const response = await fetch(`${ENHANCED_API.dashboard}/overview`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            return { user_stats: {}, achievements: {}, performance: {}, ai_insights: {} };
        }
        
        return await response.json();
    } catch (error) {
        console.error('Dashboard overview error:', error);
        return { user_stats: {}, achievements: {}, performance: {}, ai_insights: {} };
    }
}

// Market Data APIs
async function getAvailableStocks() {
    try {
        const response = await fetch(`${ENHANCED_API.market}/stocks`);
        
        if (!response.ok) {
            return [
                { symbol: 'TCS', sector: 'IT', current_price: 3500 },
                { symbol: 'RELIANCE', sector: 'Energy', current_price: 2800 },
                { symbol: 'HDFCBANK', sector: 'Banking', current_price: 1650 }
            ];
        }
        
        return await response.json();
    } catch (error) {
        console.error('Market data error:', error);
        return [];
    }
}

// UI Rendering Functions
function renderStocks(stocks) {
    const stockGrid = document.getElementById('stock-grid');
    
    if (!stocks || stocks.length === 0) {
        stockGrid.innerHTML = '<div class="loading"><span>No stocks available</span></div>';
        return;
    }
    
    stockGrid.innerHTML = stocks.map(stock => {
        const changeClass = (stock.change_percent || 0) >= 0 ? 'up' : 'down';
        const changeSymbol = (stock.change_percent || 0) >= 0 ? '+' : '';
        const changeIcon = (stock.change_percent || 0) >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
        
        return `
            <div class="stock-card">
                <div class="stock-header">
                    <div class="stock-info">
                        <h4>${stock.name || stock.symbol}</h4>
                        <div class="stock-symbol">${stock.symbol}</div>
                    </div>
                    <div class="stock-price">
                        <div class="price">₹${stock.current_price.toFixed(2)}</div>
                        <div class="change ${changeClass}">
                            <i class="fas ${changeIcon}"></i> ${changeSymbol}${(stock.change_percent || 0).toFixed(2)}%
                        </div>
                    </div>
                </div>
                <div class="stock-actions">
                    <button class="btn-trade btn-buy" onclick="openTradeModal('${stock.symbol}', 'buy', ${stock.current_price})">
                        <i class="fas fa-plus"></i> Buy
                    </button>
                    <button class="btn-trade btn-sell" onclick="openTradeModal('${stock.symbol}', 'sell', ${stock.current_price})">
                        <i class="fas fa-minus"></i> Sell
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function renderAIInsights(analysis) {
    const aiInsights = document.getElementById('ai-insights');
    const aiSuggestions = document.getElementById('ai-suggestions');
    
    // Render personality insights
    if (analysis.personality_insights) {
        aiInsights.innerHTML = `
            <div style="margin-bottom: 20px;">
                <h4 style="color: white; margin-bottom: 10px;">Your Trading Profile</h4>
                <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 12px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span>Risk Tolerance:</span>
                        <span style="font-weight: 600; text-transform: capitalize;">${analysis.personality_insights.risk_tolerance || 'Moderate'}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Trading Style:</span>
                        <span style="font-weight: 600; text-transform: capitalize;">${analysis.personality_insights.trading_style || 'Beginner'}</span>
                    </div>
                </div>
            </div>
        `;
    } else {
        aiInsights.innerHTML = '<div style="text-align: center; color: rgba(255,255,255,0.7);">Analyzing your portfolio...</div>';
    }
    
    // Render AI suggestions
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        aiSuggestions.innerHTML = analysis.recommendations.slice(0, 3).map(rec => `
            <div class="ai-suggestion">
                <div class="suggestion-stock">${rec.symbol || rec.title}</div>
                <div class="suggestion-reason">${rec.reason || rec.message}</div>
            </div>
        `).join('');
    } else {
        aiSuggestions.innerHTML = `
            <div class="ai-suggestion">
                <div class="suggestion-stock">Getting Started</div>
                <div class="suggestion-reason">Start trading to get personalized AI recommendations based on your behavior!</div>
            </div>
        `;
    }
}

function renderAchievements(achievements) {
    const achievementList = document.getElementById('achievement-list');
    
    if (achievements.earned_achievements && achievements.earned_achievements.length > 0) {
        achievementList.innerHTML = achievements.earned_achievements.slice(0, 4).map(achievement => `
            <div class="achievement-item">
                <div class="achievement-icon">
                    <i class="fas ${getAchievementIcon(achievement.achievement_type)}"></i>
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 2px;">${achievement.achievement_name}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">${achievement.description || 'Achievement unlocked!'}</div>
                </div>
            </div>
        `).join('');
    } else {
        achievementList.innerHTML = `
            <div class="achievement-item">
                <div class="achievement-icon">
                    <i class="fas fa-medal"></i>
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 2px;">First Steps</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">Start trading to unlock achievements!</div>
                </div>
            </div>
        `;
    }
}

function renderSocialFeed(posts) {
    const socialFeed = document.getElementById('social-feed');
    
    if (posts && posts.length > 0) {
        socialFeed.innerHTML = posts.slice(0, 5).map(post => {
            const postTime = new Date(post.created_at || Date.now()).toLocaleDateString('en-IN');
            const avatar = (post.author_name || 'A')[0].toUpperCase();
            
            return `
                <div class="social-post">
                    <div class="post-header">
                        <div class="post-avatar">${avatar}</div>
                        <div style="flex: 1;">
                            <div class="post-author">${post.author_name || 'Anonymous'}</div>
                            <div class="post-time">${postTime}</div>
                        </div>
                    </div>
                    <div class="post-content">
                        <div style="font-weight: 600; margin-bottom: 8px;">${post.title}</div>
                        <div>${post.content}</div>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        socialFeed.innerHTML = `
            <div class="social-post">
                <div class="post-header">
                    <div class="post-avatar">P</div>
                    <div style="flex: 1;">
                        <div class="post-author">Paisabuddy Team</div>
                        <div class="post-time">Welcome!</div>
                    </div>
                </div>
                <div class="post-content">
                    <div style="font-weight: 600; margin-bottom: 8px;">Welcome to the Community!</div>
                    <div>Share your trading insights and learn from other investors. Start by creating your first post!</div>
                </div>
            </div>
        `;
    }
}

function updatePortfolioSummary(dashboardData) {
    if (dashboardData.user_stats) {
        const stats = dashboardData.user_stats;
        document.getElementById('balance').textContent = `₹${(stats.balance || 100000).toLocaleString('en-IN')}`;
        document.getElementById('portfolio-value').textContent = `₹${(stats.portfolio_value || 100000).toLocaleString('en-IN')}`;
        
        const profitLoss = stats.profit_loss || 0;
        const profitLossElement = document.getElementById('profit-loss');
        profitLossElement.textContent = `${profitLoss >= 0 ? '+' : ''}₹${profitLoss.toLocaleString('en-IN')}`;
        profitLossElement.className = `value ${profitLoss >= 0 ? 'profit' : 'loss'}`;
        
        document.getElementById('total-trades').textContent = stats.total_trades || 0;
        document.getElementById('successful-trades').textContent = `${stats.successful_trades || 0} successful`;
    }
}

function initializePortfolioChart() {
    const ctx = document.getElementById('portfolioChart').getContext('2d');
    
    if (portfolioChart) {
        portfolioChart.destroy();
    }
    
    portfolioChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Today'],
            datasets: [{
                label: 'Portfolio Value',
                data: [100000, 101200, 100800, 102500, 103000, 104000, 104500],
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4,
                pointBackgroundColor: '#2563eb',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2.5,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { 
                    grid: { display: false },
                    ticks: { color: '#6b7280', font: { weight: '500' } }
                },
                y: { 
                    grid: { color: 'rgba(107, 114, 128, 0.1)' },
                    ticks: { color: '#6b7280', font: { weight: '500' } }
                }
            },
            layout: {
                padding: { top: 20, bottom: 20 }
            }
        }
    });
}

// Modal Functions
function goToPortfolio() {
    // Redirect to portfolio page for trading
    window.location.href = 'portfolio.html';
}

function closeCreateSimulationModal() {
    document.getElementById('create-simulation-modal').classList.remove('show');
}

function openTradeModal(symbol, type, price) {
    if (!currentUser) {
        showToast('Please login to start trading', 'error');
        return;
    }
    
    document.getElementById('trade-modal').classList.add('show');
    document.getElementById('stock-symbol').value = symbol;
    document.getElementById('trade-type').value = type.toUpperCase();
    document.getElementById('stock-price').value = price;
    document.getElementById('quantity').value = 1;
    document.getElementById('trade-notes').value = '';
    
    const tradeIcon = type === 'buy' ? 'fa-plus' : 'fa-minus';
    const tradeColor = type === 'buy' ? '#10b981' : '#ef4444';
    document.getElementById('trade-title').innerHTML = `<i class="fas ${tradeIcon}" style="color: ${tradeColor};"></i> ${type === 'buy' ? 'Buy' : 'Sell'} ${symbol}`;
}

function closeTradeModal() {
    document.getElementById('trade-modal').classList.remove('show');
}

function showCreatePostModal() {
    if (!currentUser) {
        showToast('Please login to create posts', 'error');
        return;
    }
    document.getElementById('create-post-modal').classList.add('show');
}

function closeCreatePostModal() {
    document.getElementById('create-post-modal').classList.remove('show');
}

// Event Handlers
document.getElementById('create-simulation-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentUser) {
        showToast('Please login to create simulations', 'error');
        return;
    }
    
    const formData = {
        simulation_name: document.getElementById('simulation-name').value,
        simulation_type: document.getElementById('simulation-type').value,
        start_year: parseInt(document.getElementById('start-year').value),
        settings: {}
    };
    
    try {
        const result = await createSimulation(formData);
        showToast(result.message, 'success');
        closeCreateSimulationModal();
        
        // Refresh simulations
        await initializeDashboard();
        
        // Reset form
        document.getElementById('create-simulation-form').reset();
    } catch (error) {
        showToast(error.message, 'error');
    }
});

document.getElementById('trade-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const tradeData = {
        simulation_id: currentSimulation?.simulation_id || 1, // Default simulation
        transaction_type: document.getElementById('trade-type').value.toLowerCase(),
        symbol: document.getElementById('stock-symbol').value,
        quantity: parseInt(document.getElementById('quantity').value),
        notes: document.getElementById('trade-notes').value || null
    };
    
    const submitBtn = document.getElementById('trade-submit');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    submitBtn.disabled = true;
    
    try {
        const result = await executeTradeEnhanced(tradeData);
        showToast(result.message || 'Trade executed successfully!', 'success');
        closeTradeModal();
        
        // Refresh dashboard
        await initializeDashboard();
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
});

document.getElementById('create-post-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const postData = {
        title: document.getElementById('post-title').value,
        content: document.getElementById('post-content').value,
        post_type: document.getElementById('post-type').value,
        tags: []
    };
    
    try {
        const result = await createSocialPost(postData);
        showToast('Post created successfully!', 'success');
        closeCreatePostModal();
        
        // Refresh social feed
        const posts = await getCommunityFeed();
        renderSocialFeed(posts);
        
        // Reset form
        document.getElementById('create-post-form').reset();
    } catch (error) {
        showToast(error.message, 'error');
    }
});

// Utility Functions
function getAchievementIcon(type) {
    const iconMap = {
        'first_trade': 'fa-handshake',
        'profit_maker': 'fa-chart-line',
        'portfolio_builder': 'fa-briefcase',
        'community_contributor': 'fa-users',
        'risk_manager': 'fa-shield-alt'
    };
    return iconMap[type] || 'fa-trophy';
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'info': 'fa-info-circle'
    }[type] || 'fa-check-circle';
    
    toast.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>`;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

function updateChart() {
    // Chart update logic based on selected period
    if (portfolioChart) {
        const period = document.getElementById('chart-period').value;
        // Update chart data based on period - would integrate with analytics API
        showToast(`Chart updated for ${period}`, 'info');
    }
}

// Dashboard Initialization
async function initializeDashboard() {
    try {
        showToast('Loading enhanced dashboard...', 'info');
        
        // Load all dashboard data
        const [
            dashboardOverview,
            stocks,
            behavioralAnalysis,
            achievements,
            communityPosts
        ] = await Promise.all([
            getDashboardOverview(),
            getAvailableStocks(),
            getBehavioralAnalysis(),
            getUserAchievements(),
            getCommunityFeed()
        ]);
        
        // Update UI components
        updatePortfolioSummary(dashboardOverview);
        renderStocks(stocks);
        renderAIInsights(behavioralAnalysis);
        renderAchievements(achievements);
        renderSocialFeed(communityPosts);
        
        // Initialize chart
        initializePortfolioChart();
        
        showToast('Dashboard loaded successfully!', 'success');
        
    } catch (error) {
        console.error('Dashboard initialization error:', error);
        showToast('Failed to load some dashboard components', 'error');
    }
}

async function refreshAllData() {
    await initializeDashboard();
}

function resetDashboard() {
    // Reset to default state for logged out users
    document.getElementById('balance').textContent = 'Login to view';
    document.getElementById('portfolio-value').textContent = 'Login to view';
    document.getElementById('profit-loss').textContent = 'Login to view';
    document.getElementById('total-trades').textContent = '0';
    document.getElementById('successful-trades').textContent = 'Login required';
    
    // Reset other components
    document.getElementById('stock-grid').innerHTML = '<div class="loading"><div class="spinner"></div><span>Login to start trading</span></div>';
    document.getElementById('ai-insights').innerHTML = '<div style="text-align: center; color: rgba(255,255,255,0.7);">Login for AI insights</div>';
    document.getElementById('achievement-list').innerHTML = '<div class="loading"><span>Login to view achievements</span></div>';
    document.getElementById('social-feed').innerHTML = '<div class="loading"><span>Login to join community</span></div>';
}

// Auto-demo login for testing
async function autoDemo() {
    if (!currentUser) {
        showToast('Starting demo mode...', 'info');
        await demoLogin('demo');
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Check authentication first
        const isAuthenticated = await checkAuthentication();
        
        if (isAuthenticated) {
            await initializeDashboard();
        } else {
            // Load basic data that doesn't require auth
            const stocks = await getAvailableStocks();
            renderStocks(stocks);
            
            // Show demo button
            showToast('Click "Create New Simulation" or login to start trading!', 'info');
            
            // Auto-demo after 3 seconds for testing
            setTimeout(autoDemo, 3000);
        }
        
        // Initialize chart regardless of auth status
        initializePortfolioChart();
        
    } catch (error) {
        console.error('App initialization error:', error);
        showToast('Application initialization failed', 'error');
    }
});

// Close modals when clicking outside
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    });
});

// Health check on app load
fetch(`${ENHANCED_API.health}`)
    .then(response => response.json())
    .then(data => {
        console.log('Backend services status:', data);
        if (data.status === 'healthy') {
            console.log('✅ All enhanced services are running properly');
        }
    })
    .catch(error => {
        console.warn('⚠️ Backend health check failed:', error);
        showToast('Some features may be limited due to server connectivity', 'error');
    });