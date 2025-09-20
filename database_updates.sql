-- Database updates for Virtual Trading Simulator
USE paisabuddy;

-- Update Users table to add balance column if it doesn't exist
ALTER TABLE Users ADD COLUMN IF NOT EXISTS balance DECIMAL(15,2) DEFAULT 100000.00;

-- Create Portfolio table (different from VirtualPortfolio for trading simulator)
CREATE TABLE IF NOT EXISTS Portfolio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_symbol (user_id, symbol)
);

-- Create TradeHistory table
CREATE TABLE IF NOT EXISTS TradeHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    trade_type ENUM('BUY', 'SELL') NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    total_value DECIMAL(15,2) GENERATED ALWAYS AS (quantity * price) STORED,
    trade_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_user_date (user_id, trade_date DESC),
    INDEX idx_symbol (symbol)
);

-- Create Stocks table for available stocks information
CREATE TABLE IF NOT EXISTS Stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    sector VARCHAR(50),
    base_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol)
);

-- Insert sample stock data
INSERT IGNORE INTO Stocks (symbol, name, sector, base_price, current_price) VALUES
('RELIANCE', 'Reliance Industries', 'Energy & Petrochemicals', 2500.00, 2500.00),
('TCS', 'Tata Consultancy Services', 'Information Technology', 3200.00, 3200.00),
('HDFCBANK', 'HDFC Bank', 'Banking', 1600.00, 1600.00),
('INFY', 'Infosys', 'Information Technology', 1400.00, 1400.00),
('ICICIBANK', 'ICICI Bank', 'Banking', 950.00, 950.00),
('SBIN', 'State Bank of India', 'Banking', 520.00, 520.00),
('AXISBANK', 'Axis Bank', 'Banking', 1100.00, 1100.00),
('BAJFINANCE', 'Bajaj Finance', 'Financial Services', 6800.00, 6800.00),
('TATAMOTORS', 'Tata Motors', 'Automotive', 650.00, 650.00),
('WIPRO', 'Wipro', 'Information Technology', 400.00, 400.00),
('MARUTI', 'Maruti Suzuki', 'Automotive', 9500.00, 9500.00),
('HINDUNILVR', 'Hindustan Unilever', 'FMCG', 2400.00, 2400.00);

-- Create UserSessions table for simple session management
CREATE TABLE IF NOT EXISTS UserSessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    INDEX idx_token (session_token),
    INDEX idx_user_active (user_id, is_active)
);

-- Create sample user for testing (password is 'password123' hashed)
INSERT IGNORE INTO Users (id, name, username, email, password_hash, balance) VALUES 
(1, 'Demo User', 'demo', 'demo@paisabuddy.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewUWTSUWrqjBNQgu', 100000.00);

-- Show tables to verify creation
SHOW TABLES;

-- Show sample data
SELECT 'Users Table:' as Info;
SELECT id, name, username, balance FROM Users LIMIT 5;

SELECT 'Stocks Table:' as Info;
SELECT symbol, name, sector, base_price FROM Stocks LIMIT 5;