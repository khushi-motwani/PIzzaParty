-- Portfolio Manager Database Population Script
-- Data sourced from Yahoo Finance API via yfinance
-- 32 Financial Products + Sample Portfolios & Transactions

USE Portfolio;

-- =====================================================
-- ADJUST FIELD SIZES
-- =====================================================
ALTER TABLE Assets MODIFY COLUMN asset_name varchar(100);
ALTER TABLE Assets MODIFY COLUMN asset_industry varchar(50);

-- =====================================================
-- INSERT FINANCIAL ASSETS (32 products)
-- =====================================================

-- MEGA CAP TECH (7)
INSERT INTO Assets (asset_id, asset_name, asset_type, asset_sector, asset_industry) VALUES
('AAPL', 'Apple Inc.', 'EQUITY', 'Technology', 'Consumer Electronics'),
('MSFT', 'Microsoft Corporation', 'EQUITY', 'Technology', 'Software - Infrastructure'),
('GOOG', 'Alphabet Inc.', 'EQUITY', 'Communication Services', 'Internet Content & Info'),
('NVDA', 'NVIDIA Corporation', 'EQUITY', 'Technology', 'Semiconductors'),
('TSLA', 'Tesla, Inc.', 'EQUITY', 'Consumer Cyclical', 'Auto Manufacturers'),
('META', 'Meta Platforms, Inc.', 'EQUITY', 'Communication Services', 'Internet Content & Info'),
('AMZN', 'Amazon.com, Inc.', 'EQUITY', 'Consumer Cyclical', 'Internet Retail');

-- FINANCIAL & BANKING (6)
INSERT INTO Assets (asset_id, asset_name, asset_type, asset_sector, asset_industry) VALUES
('JPM', 'JPMorgan Chase & Co.', 'EQUITY', 'Financial Services', 'Banks - Diversified'),
('BAC', 'Bank of America Corporation', 'EQUITY', 'Financial Services', 'Banks - Diversified'),
('GS', 'The Goldman Sachs Group, Inc.', 'EQUITY', 'Financial Services', 'Capital Markets'),
('BLK', 'BlackRock, Inc.', 'EQUITY', 'Financial Services', 'Asset Management'),
('V', 'Visa Inc.', 'EQUITY', 'Financial Services', 'Credit Services'),
('MA', 'Mastercard Incorporated', 'EQUITY', 'Financial Services', 'Credit Services');

-- HEALTHCARE & PHARMA (4)
INSERT INTO Assets (asset_id, asset_name, asset_type, asset_sector, asset_industry) VALUES
('JNJ', 'Johnson & Johnson', 'EQUITY', 'Healthcare', 'Drug Manufacturers'),
('UNH', 'UnitedHealth Group Incorporated', 'EQUITY', 'Healthcare', 'Healthcare Plans'),
('PFE', 'Pfizer Inc.', 'EQUITY', 'Healthcare', 'Drug Manufacturers'),
('ABBV', 'AbbVie Inc.', 'EQUITY', 'Healthcare', 'Drug Manufacturers');

-- ENERGY & UTILITIES (3)
INSERT INTO Assets (asset_id, asset_name, asset_type, asset_sector, asset_industry) VALUES
('XOM', 'ExxonMobil Holdings Corporation', 'EQUITY', 'Energy', 'Oil & Gas Integrated'),
('CVX', 'Chevron Corporation', 'EQUITY', 'Energy', 'Oil & Gas Integrated'),
('NEE', 'NextEra Energy, Inc.', 'EQUITY', 'Utilities', 'Utilities - Regulated Electric');

-- CONSUMER & RETAIL (3)
INSERT INTO Assets (asset_id, asset_name, asset_type, asset_sector, asset_industry) VALUES
('WMT', 'Walmart Inc.', 'EQUITY', 'Consumer Defensive', 'Discount Stores'),
('MCD', "McDonald's Corporation", 'EQUITY', 'Consumer Cyclical', 'Restaurants'),
('SBUX', 'Starbucks Corporation', 'EQUITY', 'Consumer Cyclical', 'Restaurants');

-- INDUSTRIAL & MANUFACTURING (2)
INSERT INTO Assets (asset_id, asset_name, asset_type, asset_sector, asset_industry) VALUES
('BA', 'The Boeing Company', 'EQUITY', 'Industrials', 'Aerospace & Defense'),
('CAT', 'Caterpillar Inc.', 'EQUITY', 'Industrials', 'Heavy Machinery');

-- ETFs - DIVERSIFIED BASKETS (5)
INSERT INTO Assets (asset_id, asset_name, asset_type, asset_sector, asset_industry) VALUES
('SPY', 'State Street SPDR S&P 500 ETF Trust', 'ETF', 'Index Funds', 'Broad Market'),
('QQQ', 'Invesco QQQ Trust', 'ETF', 'Index Funds', 'Tech-Heavy Index'),
('IWM', 'iShares Russell 2000 ETF', 'ETF', 'Index Funds', 'Small-Cap'),
('GLD', 'SPDR Gold Shares', 'ETF', 'Commodities', 'Gold Bullion'),
('TLT', 'iShares 20+ Year Treasury Bond ETF', 'ETF', 'Fixed Income', 'Government Bonds');

-- CRYPTOCURRENCIES (2)
INSERT INTO Assets (asset_id, asset_name, asset_type, asset_sector, asset_industry) VALUES
('BTC-USD', 'Bitcoin', 'CRYPTOCURRENCY', 'Digital Currency', 'Decentralized'),
('ETH-USD', 'Ethereum', 'CRYPTOCURRENCY', 'Digital Currency', 'Smart Contracts');

-- =====================================================
-- INSERT SAMPLE PORTFOLIOS
-- =====================================================

INSERT INTO Portfolios (portfolio_name, portfolio_balance) VALUES
('Growth Portfolio', 100000.00),
('Conservative Portfolio', 50000.00),
('Tech-Focused Portfolio', 75000.00),
('Dividend Income Portfolio', 60000.00),
('Emerging Investor Portfolio', 25000.00);

-- =====================================================
-- INSERT SAMPLE TRANSACTIONS
-- =====================================================

-- Growth Portfolio (portfolio_id = 1) - Starting balance: 100,000
INSERT INTO Transactions (portfolio_id, asset_id, transaction_type, transaction_quantity, transaction_price, transaction_date, transaction_total, balance_after_transaction) VALUES
(1, NULL, 'DEPOSIT', NULL, NULL, '2026-01-15 10:00:00', 100000.00, 100000.00),
(1, 'MSFT', 'BUY', 100, 389.46, '2026-01-15 10:30:00', 38946.00, 61054.00),
(1, 'NVDA', 'BUY', 150, 208.59, '2026-01-20 11:00:00', 31288.50, 29765.50),
(1, 'GOOG', 'BUY', 50, 346.86, '2026-02-05 14:15:00', 17343.00, 12422.50),
(1, 'TSLA', 'BUY', 25, 377.03, '2026-02-10 09:45:00', 9425.75, 2996.75),
(1, 'MSFT', 'SELL', 30, 389.46, '2026-03-01 13:20:00', 11683.80, 14680.55),
(1, NULL, 'WITHDRAW', NULL, NULL, '2026-01-15 10:00:00', 10000.00, 90000.00);

-- Conservative Portfolio (portfolio_id = 2) - Starting balance: 50,000
INSERT INTO Transactions (portfolio_id, asset_id, transaction_type, transaction_quantity, transaction_price, transaction_date, transaction_total, balance_after_transaction) VALUES
(2, Null, 'DEPOSIT', Null, Null, '2026-01-10 08:00:00', 50000.00, 50000.00),
(2, 'SPY', 'BUY', 35, 747.46, '2026-01-10 10:00:00', 26161.10, 23838.90),
(2, 'TLT', 'BUY', 300, 83.59, '2026-01-15 11:30:00', 25077.00, -1238.10),
(2, 'JNJ', 'BUY', 75, 254.93, '2026-02-01 15:00:00', 19119.75, -20357.85),
(2, 'WMT', 'BUY', 100, 109.52, '2026-02-20 09:30:00', 10952.00, -31309.85);

-- Tech-Focused Portfolio (portfolio_id = 3) - Starting balance: 75,000
INSERT INTO Transactions (portfolio_id, asset_id, transaction_type, transaction_quantity, transaction_price, transaction_date, transaction_total, balance_after_transaction) VALUES
(3, Null, 'DEPOSIT', Null, Null, '2026-01-10 08:00:00', 75000.00, 75000.00),
(3, 'AAPL', 'BUY', 120, 325.13, '2026-01-12 09:00:00', 39015.60, 35984.40),
(3, 'META', 'BUY', 60, 629.70, '2026-01-18 10:30:00', 37782.00, -1797.60),
(3, 'NVDA', 'BUY', 75, 208.59, '2026-02-03 14:00:00', 15644.25, -17441.85),
(3, 'QQQ', 'BUY', 40, 706.47, '2026-02-15 11:15:00', 28258.80, -45700.65);

-- Dividend Income Portfolio (portfolio_id = 4) - Starting balance: 60,000
INSERT INTO Transactions (portfolio_id, asset_id, transaction_type, transaction_quantity, transaction_price, transaction_date, transaction_total, balance_after_transaction) VALUES
(4, Null, 'DEPOSIT', Null, Null, '2026-01-12 16:15:00', 60000.00, 60000.00),
(4, 'V', 'BUY', 85, 355.14, '2026-01-14 10:00:00', 30186.90, 29813.10),
(4, 'MCD', 'BUY', 110, 263.88, '2026-01-22 12:00:00', 29026.80, 786.30),
(4, 'SBUX', 'BUY', 200, 104.36, '2026-02-08 13:45:00', 20872.00, -20085.70),
(4, 'MA', 'BUY', 40, 535.26, '2026-02-25 09:30:00', 21410.40, -41496.10);

-- Emerging Investor Portfolio (portfolio_id = 5) - Starting balance: 25,000
INSERT INTO Transactions (portfolio_id, asset_id, transaction_type, transaction_quantity, transaction_price, transaction_date, transaction_total, balance_after_transaction) VALUES
(4, Null, 'DEPOSIT', Null, Null, '2026-01-12 16:15:00', 25000.00, 25000.00),
(5, 'SPY', 'BUY', 20, 747.46, '2026-01-20 09:00:00', 14949.20, 10050.80),
(5, 'AMZN', 'BUY', 40, 244.19, '2026-02-05 10:30:00', 9767.60, 283.20),
(5, 'GLD', 'BUY', 30, 380.37, '2026-03-01 14:00:00', 11411.10, -11127.90);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Run these queries to verify the data was inserted correctly:
-- SELECT COUNT(*) as total_assets FROM Assets;
-- SELECT COUNT(*) as total_portfolios FROM Portfolios;
-- SELECT COUNT(*) as total_transactions FROM Transactions;
--
-- SELECT * FROM Assets ORDER BY asset_type, asset_id;
-- SELECT * FROM Portfolios;
-- SELECT * FROM Transactions ORDER BY portfolio_id, transaction_date;

