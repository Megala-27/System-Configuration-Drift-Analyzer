-- Run this script in MySQL before starting the application.
CREATE DATABASE IF NOT EXISTS drift_analyzer;
USE drift_analyzer;

CREATE TABLE IF NOT EXISTS config_baseline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_name VARCHAR(100) NOT NULL UNIQUE,
    expected_value VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS configurations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_name VARCHAR(100) NOT NULL,
    expected_value VARCHAR(100),
    current_value VARCHAR(100),
    drift_status VARCHAR(50),
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
