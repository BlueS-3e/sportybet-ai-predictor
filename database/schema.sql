-- SportyBet AI Predictor - PostgreSQL Database Schema
-- Version: 1.0
-- Date: January 2026

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_expires_at TIMESTAMP,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    total_spent DECIMAL(10, 2) DEFAULT 0.00,
    
    -- Age verification & compliance
    age_verified BOOLEAN DEFAULT FALSE,
    age_verification_date TIMESTAMP,
    date_of_birth DATE,
    country_code VARCHAR(3),
    
    -- Gamification
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    
    -- Daily limits
    daily_predictions_left INTEGER DEFAULT 3,
    last_reset_date DATE DEFAULT CURRENT_DATE,
    
    -- Responsible gambling limits
    daily_deposit_limit DECIMAL(10, 2) DEFAULT 100.00,
    daily_loss_limit DECIMAL(10, 2) DEFAULT 50.00,
    session_time_limit INTEGER DEFAULT 120,
    is_self_excluded BOOLEAN DEFAULT FALSE,
    self_exclusion_until TIMESTAMP,
    
    -- Session tracking
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_start_at TIMESTAMP,
    total_session_time INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_banned BOOLEAN DEFAULT FALSE,
    ban_reason TEXT,
    
    -- Indexes
    CONSTRAINT chk_balance CHECK (balance >= 0),
    CONSTRAINT chk_tier CHECK (subscription_tier IN ('free', 'premium', 'pro', 'enterprise')),
    CONSTRAINT chk_age CHECK (date_of_birth IS NULL OR date_of_birth <= CURRENT_DATE - INTERVAL '18 years')
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_subscription ON users(subscription_tier, subscription_expires_at);
CREATE INDEX idx_users_active ON users(is_active, last_activity_at);

-- ============================================
-- PREDICTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    -- Match information
    match_id VARCHAR(100) NOT NULL,
    home_team VARCHAR(255) NOT NULL,
    away_team VARCHAR(255) NOT NULL,
    league VARCHAR(255),
    match_time TIMESTAMP,
    
    -- Prediction details
    prediction_type VARCHAR(50) NOT NULL, -- 'home', 'draw', 'away', 'over', 'under', 'btts'
    predicted_outcome VARCHAR(255) NOT NULL,
    confidence DECIMAL(5, 2), -- 0.00 to 100.00
    odds DECIMAL(10, 2),
    stake DECIMAL(10, 2),
    potential_return DECIMAL(10, 2),
    
    -- ML model info
    ml_confidence DECIMAL(5, 2),
    model_version VARCHAR(50),
    features_used TEXT, -- JSON string
    
    -- Result tracking
    actual_outcome VARCHAR(255),
    is_correct BOOLEAN,
    is_settled BOOLEAN DEFAULT FALSE,
    settled_at TIMESTAMP,
    profit_loss DECIMAL(10, 2),
    
    -- Metadata
    prediction_category VARCHAR(50) DEFAULT 'pre-match', -- 'pre-match', 'in-play'
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_prediction_type CHECK (prediction_type IN ('home', 'draw', 'away', 'over', 'under', 'btts', 'both_score')),
    CONSTRAINT chk_confidence CHECK (confidence >= 0 AND confidence <= 100),
    CONSTRAINT chk_category CHECK (prediction_category IN ('pre-match', 'in-play'))
);

CREATE INDEX idx_predictions_user ON predictions(user_id, created_at DESC);
CREATE INDEX idx_predictions_match ON predictions(match_id);
CREATE INDEX idx_predictions_settled ON predictions(is_settled, settled_at);
CREATE INDEX idx_predictions_correct ON predictions(is_correct, user_id);

-- ============================================
-- LIVE MATCHES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS live_matches (
    id BIGSERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Match details
    home_team VARCHAR(255) NOT NULL,
    away_team VARCHAR(255) NOT NULL,
    league VARCHAR(255),
    country VARCHAR(100),
    
    -- Status
    status VARCHAR(50) NOT NULL, -- 'scheduled', 'live', 'halftime', 'finished', 'postponed', 'cancelled'
    match_time TIMESTAMP NOT NULL,
    
    -- Live data
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    current_minute INTEGER,
    half VARCHAR(20), -- 'first', 'second', 'extra', 'penalty'
    
    -- Statistics (JSON)
    live_stats JSONB,
    
    -- Odds tracking
    home_odds DECIMAL(10, 2),
    draw_odds DECIMAL(10, 2),
    away_odds DECIMAL(10, 2),
    over_25_odds DECIMAL(10, 2),
    under_25_odds DECIMAL(10, 2),
    
    -- Events
    events JSONB, -- Goals, cards, substitutions
    
    -- Metadata
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100),
    
    CONSTRAINT chk_status CHECK (status IN ('scheduled', 'live', 'halftime', 'finished', 'postponed', 'cancelled'))
);

CREATE INDEX idx_live_matches_status ON live_matches(status, match_time);
CREATE INDEX idx_live_matches_time ON live_matches(match_time);
CREATE INDEX idx_live_matches_external ON live_matches(external_id);
CREATE INDEX idx_live_matches_updated ON live_matches(last_updated_at);

-- ============================================
-- LIVE ODDS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS live_odds (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES live_matches(id) ON DELETE CASCADE,
    
    -- Bookmaker info
    bookmaker VARCHAR(100) NOT NULL,
    market_type VARCHAR(50) NOT NULL, -- 'h2h', 'spreads', 'totals'
    
    -- Odds values
    home_odds DECIMAL(10, 2),
    draw_odds DECIMAL(10, 2),
    away_odds DECIMAL(10, 2),
    
    -- Alternative markets
    over_odds DECIMAL(10, 2),
    under_odds DECIMAL(10, 2),
    handicap DECIMAL(5, 2),
    
    -- Tracking
    odds_change_percent DECIMAL(5, 2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_market_type CHECK (market_type IN ('h2h', 'spreads', 'totals', 'btts'))
);

CREATE INDEX idx_live_odds_match ON live_odds(match_id, timestamp DESC);
CREATE INDEX idx_live_odds_bookmaker ON live_odds(bookmaker);
CREATE INDEX idx_live_odds_timestamp ON live_odds(timestamp);

-- ============================================
-- USER ALERTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_alerts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    -- Alert configuration
    alert_type VARCHAR(50) NOT NULL, -- 'odds_change', 'match_start', 'goal', 'arbitrage', 'prediction_result'
    match_id BIGINT REFERENCES live_matches(id) ON DELETE CASCADE,
    
    -- Alert conditions
    target_odds DECIMAL(10, 2),
    odds_threshold DECIMAL(10, 2),
    team_name VARCHAR(255),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMP,
    
    -- Notification
    notification_sent BOOLEAN DEFAULT FALSE,
    notification_sent_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    CONSTRAINT chk_alert_type CHECK (alert_type IN ('odds_change', 'match_start', 'goal', 'red_card', 'arbitrage', 'prediction_result'))
);

CREATE INDEX idx_user_alerts_user ON user_alerts(user_id, is_active);
CREATE INDEX idx_user_alerts_match ON user_alerts(match_id, is_active);
CREATE INDEX idx_user_alerts_active ON user_alerts(is_active, is_triggered);

-- ============================================
-- ARBITRAGE OPPORTUNITIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES live_matches(id) ON DELETE CASCADE,
    
    -- Opportunity details
    best_home_odds DECIMAL(10, 2) NOT NULL,
    best_home_bookmaker VARCHAR(100),
    best_draw_odds DECIMAL(10, 2),
    best_draw_bookmaker VARCHAR(100),
    best_away_odds DECIMAL(10, 2) NOT NULL,
    best_away_bookmaker VARCHAR(100),
    
    -- Profit calculation
    arbitrage_percent DECIMAL(10, 5) NOT NULL,
    profit_percent DECIMAL(10, 5) NOT NULL,
    required_stakes JSONB, -- Calculated stakes for each outcome
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Notifications
    users_notified INTEGER DEFAULT 0,
    
    CONSTRAINT chk_profit CHECK (profit_percent > 0)
);

CREATE INDEX idx_arbitrage_match ON arbitrage_opportunities(match_id, is_active);
CREATE INDEX idx_arbitrage_profit ON arbitrage_opportunities(profit_percent DESC, is_active);
CREATE INDEX idx_arbitrage_discovered ON arbitrage_opportunities(discovered_at DESC);

-- ============================================
-- TRANSACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    -- Transaction details
    transaction_type VARCHAR(50) NOT NULL, -- 'deposit', 'withdrawal', 'subscription', 'bet_stake', 'bet_return', 'refund'
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Payment info
    payment_method VARCHAR(50),
    payment_provider VARCHAR(50),
    external_transaction_id VARCHAR(255),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'refunded'
    
    -- Related entities
    prediction_id BIGINT REFERENCES predictions(id),
    
    -- Metadata
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    CONSTRAINT chk_transaction_type CHECK (transaction_type IN ('deposit', 'withdrawal', 'subscription', 'bet_stake', 'bet_return', 'refund')),
    CONSTRAINT chk_status CHECK (status IN ('pending', 'completed', 'failed', 'refunded'))
);

CREATE INDEX idx_transactions_user ON transactions(user_id, created_at DESC);
CREATE INDEX idx_transactions_status ON transactions(status, created_at);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);

-- ============================================
-- ACHIEVEMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(50), -- 'predictions', 'streak', 'social', 'spending'
    icon VARCHAR(50),
    requirement_type VARCHAR(50), -- 'total_predictions', 'streak', 'accuracy', 'profit'
    requirement_value INTEGER,
    xp_reward INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, achievement_id)
);

CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);

-- ============================================
-- SESSIONS TABLE (for session time limits)
-- ============================================
CREATE TABLE IF NOT EXISTS user_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    duration_seconds INTEGER,
    actions_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_sessions_user ON user_sessions(user_id, session_start DESC);
CREATE INDEX idx_sessions_active ON user_sessions(is_active);

-- ============================================
-- AUDIT LOG TABLE (for compliance)
-- ============================================
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    action_type VARCHAR(100) NOT NULL,
    action_details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_audit_log_action ON audit_log(action_type);
CREATE INDEX idx_audit_log_timestamp ON audit_log(created_at DESC);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_predictions_updated_at BEFORE UPDATE ON predictions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Reset daily prediction limits
CREATE OR REPLACE FUNCTION reset_daily_predictions()
RETURNS void AS $$
BEGIN
    UPDATE users
    SET 
        daily_predictions_left = CASE 
            WHEN subscription_tier = 'free' THEN 3
            WHEN subscription_tier = 'premium' THEN 50
            WHEN subscription_tier = 'pro' THEN 999
            WHEN subscription_tier = 'enterprise' THEN 9999
            ELSE 3
        END,
        last_reset_date = CURRENT_DATE
    WHERE last_reset_date < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- SAMPLE DATA (for testing)
-- ============================================

-- Insert default achievements
INSERT INTO achievements (name, description, category, icon, requirement_type, requirement_value, xp_reward) VALUES
('First Prediction', 'Make your first prediction', 'predictions', '🎯', 'total_predictions', 1, 10),
('Streak Master', 'Get 5 predictions correct in a row', 'streak', '🔥', 'streak', 5, 50),
('Century Club', 'Make 100 predictions', 'predictions', '💯', 'total_predictions', 100, 200),
('Sharp Bettor', 'Achieve 70% accuracy with 50+ predictions', 'predictions', '🎓', 'accuracy', 70, 300),
('Early Adopter', 'Join in the first month', 'social', '⭐', 'early_user', 1, 100),
('Premium Member', 'Subscribe to premium tier', 'spending', '👑', 'subscription', 1, 150),
('Profit Master', 'Earn $1000 in profit', 'predictions', '💰', 'profit', 1000, 500);

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- User statistics view
CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    u.id,
    u.telegram_id,
    u.username,
    u.subscription_tier,
    u.total_predictions,
    u.correct_predictions,
    CASE 
        WHEN u.total_predictions > 0 
        THEN ROUND((u.correct_predictions::DECIMAL / u.total_predictions) * 100, 2)
        ELSE 0 
    END as accuracy_percent,
    u.current_streak,
    u.longest_streak,
    u.level,
    u.xp,
    COUNT(DISTINCT ua.achievement_id) as achievements_unlocked,
    COALESCE(SUM(CASE WHEN t.transaction_type = 'deposit' THEN t.amount ELSE 0 END), 0) as total_deposits,
    COALESCE(SUM(CASE WHEN p.profit_loss > 0 THEN p.profit_loss ELSE 0 END), 0) as total_profit,
    COALESCE(SUM(CASE WHEN p.profit_loss < 0 THEN ABS(p.profit_loss) ELSE 0 END), 0) as total_loss
FROM users u
LEFT JOIN user_achievements ua ON u.id = ua.user_id
LEFT JOIN transactions t ON u.id = t.user_id AND t.status = 'completed'
LEFT JOIN predictions p ON u.id = p.user_id AND p.is_settled = TRUE
GROUP BY u.id;

-- Daily analytics view
CREATE OR REPLACE VIEW daily_analytics AS
SELECT 
    DATE(created_at) as date,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN is_correct = TRUE THEN 1 ELSE 0 END) as correct_predictions,
    ROUND(AVG(confidence), 2) as avg_confidence,
    COUNT(CASE WHEN prediction_category = 'in-play' THEN 1 END) as inplay_predictions
FROM predictions
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ============================================
-- GRANT PERMISSIONS (adjust as needed)
-- ============================================
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sportybet_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sportybet_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO sportybet_user;
