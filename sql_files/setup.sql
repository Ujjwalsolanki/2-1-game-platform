
CREATE DATABASE IF NOT EXISTS game_company;
USE game_company;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE games (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT COMMENT 'Small description of the game',
    html_code LONGTEXT NOT NULL COMMENT 'Contains the HTML structure of the game',
    file_url VARCHAR(255) COMMENT 'Local path where the combined file is saved',
    deployed_url VARCHAR(255) COMMENT 'Mock URL where the game is published',
    created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    game_id varchar(36) NOT NULL,
    payment_method VARCHAR(50),
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('paid', 'failed', 'refund') NOT NULL,
    created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints to link to other tables
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (game_id) REFERENCES games(id)
);

CREATE TABLE marketing_post (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id varchar(36) NOT NULL,
    platform VARCHAR(50) NOT NULL COMMENT 'e.g., Twitter, LinkedIn, Reddit',
    payload_json JSON NOT NULL COMMENT 'The generated text content, hashtags, etc.',
    post_url VARCHAR(255) COMMENT 'The mock URL of the posted content',
    status ENUM('draft', 'posted', 'failed') NOT NULL,
    created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint to link to the games table
    FOREIGN KEY (game_id) REFERENCES games(id)
);

CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level ENUM('debug', 'info', 'warning', 'error', 'critical') DEFAULT 'info',
    service VARCHAR(100) NOT NULL COMMENT 'The agent or module that generated the log (e.g., GameGenerator, BillingAgent, DB_Manager)',
    message TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);