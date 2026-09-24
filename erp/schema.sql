DROP VIEW IF EXISTS erp.v_sales_target_day;
DROP TABLE IF EXISTS erp.user_access, erp.city_geo, erp.sales_target_month, erp.weekday_weight,
    erp.item_price, erp.store_profile, erp.state_region, erp.region;
IF SCHEMA_ID('erp') IS NULL EXEC('CREATE SCHEMA erp');
CREATE TABLE erp.region (
    region_id int PRIMARY KEY,
    region_name nvarchar(50) NOT NULL UNIQUE);
CREATE TABLE erp.state_region (
    state nvarchar(60) PRIMARY KEY,
    region_id int NOT NULL REFERENCES erp.region (region_id));
CREATE TABLE erp.store_profile (
    store_nbr int PRIMARY KEY,
    selling_area_m2 int NOT NULL CHECK (selling_area_m2 > 0));
CREATE TABLE erp.item_price (
    item_nbr int PRIMARY KEY,
    unit_price decimal(10, 2) NOT NULL,
    unit_cost decimal(10, 2) NOT NULL,
    CHECK (unit_cost > 0 AND unit_price > unit_cost));
CREATE TABLE erp.weekday_weight (
    store_nbr int NOT NULL REFERENCES erp.store_profile (store_nbr),
    weekday_num tinyint NOT NULL CHECK (weekday_num BETWEEN 1 AND 7),
    weight float NOT NULL CHECK (weight > 0),
    PRIMARY KEY (store_nbr, weekday_num));
CREATE TABLE erp.sales_target_month (
    store_nbr int NOT NULL REFERENCES erp.store_profile (store_nbr),
    month_start date NOT NULL CHECK (DAY(month_start) = 1),
    target_value decimal(14, 2) NOT NULL CHECK (target_value > 0),
    PRIMARY KEY (store_nbr, month_start));
CREATE TABLE erp.city_geo (
    city nvarchar(60) PRIMARY KEY,
    latitude float NOT NULL,
    longitude float NOT NULL,
    admin1 nvarchar(80) NOT NULL);
CREATE TABLE erp.user_access (
    user_principal_name nvarchar(256) NOT NULL,
    store_nbr int NOT NULL REFERENCES erp.store_profile (store_nbr),
    PRIMARY KEY (user_principal_name, store_nbr));
