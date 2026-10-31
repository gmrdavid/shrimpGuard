-- ShrimpGuard MySQL schema
-- Import this file with a MySQL account that can create databases.

CREATE DATABASE IF NOT EXISTS shrimpguard
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE shrimpguard;

CREATE TABLE IF NOT EXISTS users (
    name VARCHAR(80) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    last_login DATETIME NULL,
    ntfy_topic VARCHAR(100) NULL,
    last_read_notifications DATETIME NULL,
    PRIMARY KEY (email),
    UNIQUE KEY uq_users_name (name),
    UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS roles (
    id INT NOT NULL AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_roles_role_name (role_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sensors (
    ph_level FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    `date` VARCHAR(45) NOT NULL,
    status VARCHAR(45) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS activity_logs (
    id INT NOT NULL AUTO_INCREMENT,
    user_email VARCHAR(255) NULL,
    user_name VARCHAR(80) NULL,
    role VARCHAR(50) NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT NULL,
    ip_address VARCHAR(45) NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_activity_logs_timestamp (timestamp),
    KEY idx_activity_logs_user_email (user_email)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS aquaculture_calculations (
    id INT NOT NULL AUTO_INCREMENT,
    user_email VARCHAR(255) NULL,
    user_name VARCHAR(80) NULL,
    notes VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 1. Biomass & Feed
    pond_area_m2 FLOAT NULL,
    pond_depth_m FLOAT NULL,
    stocking_density_pl_m2 FLOAT NULL,
    survival_rate_pct FLOAT NULL,
    abw_g FLOAT NULL,
    standing_biomass_kg FLOAT NULL,
    standing_biomass_tons FLOAT NULL,
    active_shrimp_count BIGINT NULL,

    -- 2. Temperature Feeding Adjustment
    water_temperature_c FLOAT NULL,
    base_feeding_rate_pct FLOAT NULL,
    temp_feeding_factor FLOAT NULL,
    adjusted_daily_feed_kg FLOAT NULL,
    feed_per_meal_kg FLOAT NULL,
    feedings_per_day INT NULL,

    -- 3. Eight Growth Equations (Eqs. 1–8)
    is_count BIGINT NULL,
    lhc_count BIGINT NULL,
    doc_days INT NULL,
    ibw_g FLOAT NULL,
    bulk_weight_kg FLOAT NULL,
    total_feed_given_kg FLOAT NULL,
    total_length_cm FLOAT NULL,
    eq1_sr_pct FLOAT NULL,
    eq1_mortality_count BIGINT NULL,
    eq2_fabw_g FLOAT NULL,
    eq2_count_per_kg FLOAT NULL,
    eq3_adwg_g_day FLOAT NULL,
    eq3_weekly_gain_g FLOAT NULL,
    eq4_sgr_pct_day FLOAT NULL,
    eq5_ib_kg FLOAT NULL,
    eq6_fb_kg FLOAT NULL,
    eq5_6_net_biomass_kg FLOAT NULL,
    eq7_fcr FLOAT NULL,
    eq7_feed_efficiency_pct FLOAT NULL,
    eq8_fulton_k FLOAT NULL,
    eq8_fulton_profile VARCHAR(100) NULL,

    -- 4. pH Liming Dosage
    lime_pond_vol_m3 FLOAT NULL,
    lime_current_ph FLOAT NULL,
    lime_target_ph FLOAT NULL,
    lime_chemical_type VARCHAR(100) NULL,
    lime_dosage_kg FLOAT NULL,
    lime_dosage_ppm FLOAT NULL,

    -- 5. Organic Carbon Dosing (Biofloc)
    molasses_daily_feed_kg FLOAT NULL,
    molasses_protein_pct FLOAT NULL,
    molasses_target_cn FLOAT NULL,
    molasses_carbon_source VARCHAR(100) NULL,
    molasses_dosage_kg FLOAT NULL,

    -- 6. Aerator Power
    aero_biomass_kg FLOAT NULL,
    aero_water_temp_c FLOAT NULL,
    aero_salinity_ppt FLOAT NULL,
    aero_target_do_ppm FLOAT NULL,
    aero_power_hp FLOAT NULL,
    aero_units_desc VARCHAR(100) NULL,

    -- 7. Unionized Ammonia
    ammonia_tan_ppm FLOAT NULL,
    ammonia_temp_c FLOAT NULL,
    ammonia_ph FLOAT NULL,
    ammonia_salinity_ppt FLOAT NULL,
    ammonia_factor_f FLOAT NULL,
    ammonia_nh3_ppm FLOAT NULL,
    ammonia_status VARCHAR(50) NULL,

    -- 8. Free Carbon Dioxide (CO2)
    co2_alkalinity_mg_l FLOAT NULL,
    co2_temp_c FLOAT NULL,
    co2_ph FLOAT NULL,
    co2_factor FLOAT NULL,
    co2_concentration_mg_l FLOAT NULL,
    co2_status VARCHAR(50) NULL,

    PRIMARY KEY (id),
    KEY idx_aqua_calc_created (created_at),
    KEY idx_aqua_calc_user (user_email)
) ENGINE=InnoDB;
