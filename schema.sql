-- Agritech database schema

CREATE DATABASE IF NOT EXISTS agritech;
USE agritech;

CREATE TABLE IF NOT EXISTS farmers (
    farmer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    village VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crops (
    crop_id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    season ENUM('Kharif', 'Rabi', 'Zaid') NOT NULL,
    area_acres DECIMAL(6,2) NOT NULL,
    sowing_date DATE,
    expected_yield_kg DECIMAL(10,2),
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS market_prices (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL,
    price_per_kg DECIMAL(8,2) NOT NULL,
    updated_on DATE NOT NULL
);
