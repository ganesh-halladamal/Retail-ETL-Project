-- ===========================================
-- Retail ETL Project - Source OLTP Database
-- File: sample_data.sql
-- Purpose: Insert realistic sample data
-- Maintains referential integrity via insert order
-- IMPORTANT: This file uses DELIMITER blocks for
--   stored procedures. It must be executed via:
--   - MySQL Workbench (open and execute)
--   - mysql command-line client
--   It CANNOT be executed via SQLAlchemy or
--   mysql-connector-python directly.
-- Requires: MySQL 8.0.16+
-- Reset: Run create_database.sql first
-- ===========================================

USE retail_oltp;

-- ===========================================
-- CATEGORIES (10 records)
-- ===========================================
INSERT INTO categories (category_name, description) VALUES
('Electronics', 'Smartphones, laptops, tablets and accessories'),
('Clothing', 'Men and women apparel, fashion wear'),
('Home & Kitchen', 'Kitchen appliances, cookware, home decor'),
('Books', 'Fiction, non-fiction, academic and reference'),
('Sports & Fitness', 'Gym equipment, sportswear, outdoor gear'),
('Beauty & Personal Care', 'Skincare, haircare, grooming products'),
('Toys & Games', 'Kids toys, board games, puzzles'),
('Groceries', 'Daily essentials, snacks, beverages'),
('Furniture', 'Office furniture, home furniture, storage'),
('Automotive', 'Car accessories, bike accessories, tools');

-- ===========================================
-- SUPPLIERS (10 records)
-- ===========================================
INSERT INTO suppliers (supplier_name, contact_person, email, phone, city, country) VALUES
('TechVision India Pvt Ltd', 'Rajesh Kumar', 'rajesh@techvision.in', '9876543210', 'Mumbai', 'India'),
('Fashion Hub Exports', 'Priya Sharma', 'priya@fashionhub.in', '9876543211', 'Delhi', 'India'),
('HomeStyle Suppliers', 'Amit Patel', 'amit@homestyle.in', '9876543212', 'Ahmedabad', 'India'),
('BookWorld Distributors', 'Sneha Reddy', 'sneha@bookworld.in', '9876543213', 'Hyderabad', 'India'),
('FitGear Industries', 'Vikram Singh', 'vikram@fitgear.in', '9876543214', 'Pune', 'India'),
('GlowCare Cosmetics', 'Neha Gupta', 'neha@glowcare.in', '9876543215', 'Bangalore', 'India'),
('ToyLand Manufacturing', 'Ravi Verma', 'ravi@toyland.in', '9876543216', 'Jaipur', 'India'),
('FreshMart Supplies', 'Anita Desai', 'anita@freshmart.in', '9876543217', 'Chennai', 'India'),
('WoodCraft Furniture', 'Suresh Nair', 'suresh@woodcraft.in', '9876543218', 'Kochi', 'India'),
('AutoParts Global', 'Manoj Tiwari', 'manoj@autoparts.in', '9876543219', 'Lucknow', 'India');

-- ===========================================
-- STORES (5 records)
-- ===========================================
INSERT INTO stores (store_name, city, state, manager_name, opened_date) VALUES
('RetailMart Mumbai Central', 'Mumbai', 'Maharashtra', 'Arun Mehta', '2019-03-15'),
('RetailMart Delhi Plaza', 'Delhi', 'Delhi', 'Kavita Joshi', '2019-07-20'),
('RetailMart Bangalore Tech Park', 'Bangalore', 'Karnataka', 'Deepak Rao', '2020-01-10'),
('RetailMart Hyderabad Hub', 'Hyderabad', 'Telangana', 'Lakshmi Iyer', '2020-06-25'),
('RetailMart Chennai Square', 'Chennai', 'Tamil Nadu', 'Karthik Subramanian', '2021-02-14');

-- ===========================================
-- PRODUCTS (50 records)
-- ===========================================
INSERT INTO products (category_id, supplier_id, product_name, brand, unit_price, cost_price, created_date, status) VALUES
(1, 1, 'iPhone 15 Pro Max 256GB', 'Apple', 159900.00, 130000.00, '2023-09-22', 'Active'),
(1, 1, 'Samsung Galaxy S24 Ultra', 'Samsung', 134999.00, 105000.00, '2024-01-17', 'Active'),
(1, 1, 'OnePlus 12 5G', 'OnePlus', 64999.00, 50000.00, '2024-01-23', 'Active'),
(1, 1, 'MacBook Air M3 15-inch', 'Apple', 139900.00, 115000.00, '2024-03-08', 'Active'),
(1, 1, 'Sony WH-1000XM5 Headphones', 'Sony', 29990.00, 22000.00, '2023-05-15', 'Active'),
(2, 2, 'Levi\'s 511 Slim Fit Jeans', 'Levi\'s', 2999.00, 1800.00, '2023-06-10', 'Active'),
(2, 2, 'Nike Dri-FIT Running T-Shirt', 'Nike', 1995.00, 1200.00, '2023-07-22', 'Active'),
(2, 2, 'Allen Solly Formal Blazer', 'Allen Solly', 5999.00, 3500.00, '2023-08-14', 'Active'),
(2, 2, 'Adidas Ultraboost Running Shoes', 'Adidas', 16999.00, 12000.00, '2023-04-30', 'Active'),
(2, 2, 'Zara Women Floral Dress', 'Zara', 3990.00, 2400.00, '2023-09-05', 'Active');

INSERT INTO products (category_id, supplier_id, product_name, brand, unit_price, cost_price, created_date, status) VALUES
(3, 3, 'Prestige Induction Cooktop', 'Prestige', 3499.00, 2200.00, '2023-03-18', 'Active'),
(3, 3, 'Philips Air Fryer HD9252', 'Philips', 7999.00, 5800.00, '2023-05-25', 'Active'),
(3, 3, 'Borosil Stainless Steel Casserole', 'Borosil', 1899.00, 1100.00, '2023-07-12', 'Active'),
(3, 3, 'Dyson V12 Vacuum Cleaner', 'Dyson', 52900.00, 40000.00, '2023-08-20', 'Active'),
(3, 3, 'Milton Thermosteel Flask 1L', 'Milton', 899.00, 550.00, '2023-02-14', 'Active'),
(4, 4, 'Atomic Habits by James Clear', 'Penguin', 599.00, 350.00, '2023-01-10', 'Active'),
(4, 4, 'The Psychology of Money', 'Jaico', 399.00, 220.00, '2023-01-15', 'Active'),
(4, 4, 'Clean Code by Robert Martin', 'Pearson', 2999.00, 1800.00, '2023-03-20', 'Active'),
(4, 4, 'System Design Interview Vol 2', 'ByteByteGo', 1999.00, 1200.00, '2023-04-10', 'Active'),
(4, 4, 'Data Structures Using Python', 'McGraw Hill', 899.00, 500.00, '2023-05-05', 'Active');

INSERT INTO products (category_id, supplier_id, product_name, brand, unit_price, cost_price, created_date, status) VALUES
(5, 5, 'PowerMax Treadmill TDM-100S', 'PowerMax', 34999.00, 26000.00, '2023-06-15', 'Active'),
(5, 5, 'Nivia Pro Cricket Bat', 'Nivia', 2499.00, 1500.00, '2023-07-01', 'Active'),
(5, 5, 'Boldfit Resistance Bands Set', 'Boldfit', 699.00, 400.00, '2023-04-20', 'Active'),
(5, 5, 'Yonex Badminton Racket Nanoray', 'Yonex', 4999.00, 3200.00, '2023-08-10', 'Active'),
(5, 5, 'Fitbit Charge 6 Fitness Tracker', 'Fitbit', 14999.00, 11000.00, '2023-10-12', 'Active'),
(6, 6, 'Lakme Absolute Skin Serum', 'Lakme', 799.00, 450.00, '2023-03-22', 'Active'),
(6, 6, 'Nivea Men All-in-One Face Wash', 'Nivea', 299.00, 170.00, '2023-04-05', 'Active'),
(6, 6, 'Biotique Bio Neem Face Wash', 'Biotique', 249.00, 140.00, '2023-05-18', 'Active'),
(6, 6, 'Philips Body Groomer BG3006', 'Philips', 2495.00, 1800.00, '2023-06-28', 'Active'),
(6, 6, 'Forest Essentials Night Cream', 'Forest Essentials', 2975.00, 1900.00, '2023-07-15', 'Active');

INSERT INTO products (category_id, supplier_id, product_name, brand, unit_price, cost_price, created_date, status) VALUES
(7, 7, 'LEGO Technic Racing Car 42153', 'LEGO', 4999.00, 3500.00, '2023-08-05', 'Active'),
(7, 7, 'Funskool Monopoly Board Game', 'Funskool', 899.00, 550.00, '2023-02-28', 'Active'),
(7, 7, 'Hot Wheels Track Builder Set', 'Mattel', 1999.00, 1300.00, '2023-09-10', 'Active'),
(7, 7, 'Rubik\'s Cube 3x3 Speed Edition', 'Rubik\'s', 599.00, 350.00, '2023-03-15', 'Active'),
(7, 7, 'Nerf Elite 2.0 Blaster', 'Hasbro', 2499.00, 1700.00, '2023-10-01', 'Active'),
(8, 8, 'Tata Tea Gold 1kg Pack', 'Tata', 499.00, 350.00, '2023-01-05', 'Active'),
(8, 8, 'Aashirvaad Atta 10kg', 'Aashirvaad', 599.00, 420.00, '2023-01-10', 'Active'),
(8, 8, 'Cadbury Dairy Milk Silk 150g', 'Cadbury', 199.00, 130.00, '2023-02-14', 'Active'),
(8, 8, 'Red Bull Energy Drink 250ml x12', 'Red Bull', 1188.00, 850.00, '2023-03-20', 'Active'),
(8, 8, 'Maggi 2-Minute Noodles 12 Pack', 'Nestle', 168.00, 120.00, '2023-01-15', 'Active');

INSERT INTO products (category_id, supplier_id, product_name, brand, unit_price, cost_price, created_date, status) VALUES
(9, 9, 'Nilkamal Executive Office Chair', 'Nilkamal', 8999.00, 6000.00, '2023-04-12', 'Active'),
(9, 9, 'Urban Ladder Bookshelf Solid Wood', 'Urban Ladder', 12999.00, 9000.00, '2023-05-20', 'Active'),
(9, 9, 'Wakefit Orthopaedic Mattress Queen', 'Wakefit', 14999.00, 10500.00, '2023-06-18', 'Active'),
(9, 9, 'IKEA KALLAX Shelf Unit', 'IKEA', 6999.00, 4800.00, '2023-07-25', 'Active'),
(9, 9, 'Godrej Interio Study Table', 'Godrej', 7499.00, 5200.00, '2023-08-30', 'Active'),
(10, 10, 'Bosch Car Battery 65Ah', 'Bosch', 7499.00, 5500.00, '2023-03-10', 'Active'),
(10, 10, 'Michelin Tyre 185/65 R15', 'Michelin', 5999.00, 4200.00, '2023-04-22', 'Active'),
(10, 10, 'Philips LED Headlight Bulb H4', 'Philips', 1999.00, 1300.00, '2023-05-15', 'Active'),
(10, 10, 'Amaron Bike Battery 12V', 'Amaron', 1899.00, 1200.00, '2023-06-10', 'Active'),
(10, 10, '3M Car Dashboard Polish Kit', 'Kenmaster', 899.00, 550.00, '2023-07-05', 'Discontinued');

-- ===========================================
-- EMPLOYEES (20 records)
-- ===========================================
INSERT INTO employees (store_id, first_name, last_name, designation, salary, hire_date) VALUES
(1, 'Rahul', 'Sharma', 'Sales Executive', 35000.00, '2019-04-01'),
(1, 'Pooja', 'Verma', 'Sales Executive', 35000.00, '2019-04-15'),
(1, 'Sunil', 'Patil', 'Senior Sales Executive', 45000.00, '2019-03-20'),
(1, 'Meena', 'Iyer', 'Cashier', 28000.00, '2020-01-10'),
(2, 'Aakash', 'Gupta', 'Sales Executive', 35000.00, '2019-08-01'),
(2, 'Ritu', 'Kapoor', 'Sales Executive', 36000.00, '2019-08-15'),
(2, 'Vijay', 'Kumar', 'Senior Sales Executive', 46000.00, '2019-07-25'),
(2, 'Nisha', 'Agarwal', 'Cashier', 28000.00, '2020-02-20'),
(3, 'Kiran', 'Reddy', 'Sales Executive', 37000.00, '2020-02-01'),
(3, 'Divya', 'Nair', 'Sales Executive', 37000.00, '2020-02-15'),
(3, 'Sanjay', 'Hegde', 'Senior Sales Executive', 48000.00, '2020-01-15'),
(3, 'Anjali', 'Menon', 'Cashier', 29000.00, '2020-03-10'),
(4, 'Prakash', 'Rao', 'Sales Executive', 36000.00, '2020-07-01'),
(4, 'Swati', 'Deshpande', 'Sales Executive', 36000.00, '2020-07-15'),
(4, 'Arjun', 'Pillai', 'Senior Sales Executive', 47000.00, '2020-06-28'),
(4, 'Geeta', 'Sundaram', 'Cashier', 28500.00, '2020-08-20'),
(5, 'Tamil', 'Selvan', 'Sales Executive', 35000.00, '2021-03-01'),
(5, 'Preethi', 'Rajan', 'Sales Executive', 35000.00, '2021-03-15'),
(5, 'Mohan', 'Krishnan', 'Senior Sales Executive', 46000.00, '2021-02-20'),
(5, 'Lavanya', 'Bhat', 'Cashier', 28000.00, '2021-04-10');

-- ===========================================
-- CUSTOMERS (100 records)
-- ===========================================
INSERT INTO customers (first_name, last_name, gender, email, phone, date_of_birth, city, state, country, registration_date, status) VALUES
('Aarav', 'Sharma', 'Male', 'aarav.sharma@gmail.com', '9100000001', '1990-05-14', 'Mumbai', 'Maharashtra', 'India', '2022-01-15', 'Active'),
('Vivaan', 'Patel', 'Male', 'vivaan.patel@yahoo.com', '9100000002', '1988-11-22', 'Ahmedabad', 'Gujarat', 'India', '2022-01-20', 'Active'),
('Aditya', 'Singh', 'Male', 'aditya.singh@outlook.com', '9100000003', '1992-03-08', 'Delhi', 'Delhi', 'India', '2022-02-01', 'Active'),
('Ananya', 'Gupta', 'Female', 'ananya.gupta@gmail.com', '9100000004', '1995-07-19', 'Bangalore', 'Karnataka', 'India', '2022-02-10', 'Active'),
('Diya', 'Reddy', 'Female', 'diya.reddy@gmail.com', '9100000005', '1993-09-25', 'Hyderabad', 'Telangana', 'India', '2022-02-15', 'Active'),
('Arjun', 'Kumar', 'Male', 'arjun.kumar@yahoo.com', '9100000006', '1991-01-30', 'Chennai', 'Tamil Nadu', 'India', '2022-02-20', 'Active'),
('Ishaan', 'Verma', 'Male', 'ishaan.verma@gmail.com', '9100000007', '1989-12-05', 'Pune', 'Maharashtra', 'India', '2022-03-01', 'Active'),
('Saanvi', 'Nair', 'Female', 'saanvi.nair@outlook.com', '9100000008', '1994-06-11', 'Kochi', 'Kerala', 'India', '2022-03-05', 'Active'),
('Reyansh', 'Joshi', 'Male', 'reyansh.joshi@gmail.com', '9100000009', '1990-08-17', 'Jaipur', 'Rajasthan', 'India', '2022-03-10', 'Active'),
('Kiara', 'Iyer', 'Female', 'kiara.iyer@yahoo.com', '9100000010', '1996-02-28', 'Mumbai', 'Maharashtra', 'India', '2022-03-15', 'Active');

INSERT INTO customers (first_name, last_name, gender, email, phone, date_of_birth, city, state, country, registration_date, status) VALUES
('Vihaan', 'Mishra', 'Male', 'vihaan.mishra@gmail.com', '9100000011', '1987-04-03', 'Lucknow', 'Uttar Pradesh', 'India', '2022-03-20', 'Active'),
('Myra', 'Desai', 'Female', 'myra.desai@outlook.com', '9100000012', '1993-10-12', 'Surat', 'Gujarat', 'India', '2022-03-25', 'Active'),
('Kabir', 'Chopra', 'Male', 'kabir.chopra@gmail.com', '9100000013', '1991-07-07', 'Delhi', 'Delhi', 'India', '2022-04-01', 'Active'),
('Aisha', 'Khan', 'Female', 'aisha.khan@yahoo.com', '9100000014', '1994-11-16', 'Mumbai', 'Maharashtra', 'India', '2022-04-05', 'Active'),
('Dhruv', 'Mehta', 'Male', 'dhruv.mehta@gmail.com', '9100000015', '1990-02-21', 'Ahmedabad', 'Gujarat', 'India', '2022-04-10', 'Active'),
('Riya', 'Chatterjee', 'Female', 'riya.chatterjee@outlook.com', '9100000016', '1992-05-30', 'Kolkata', 'West Bengal', 'India', '2022-04-15', 'Active'),
('Ayaan', 'Saxena', 'Male', 'ayaan.saxena@gmail.com', '9100000017', '1988-08-14', 'Indore', 'Madhya Pradesh', 'India', '2022-04-20', 'Active'),
('Pari', 'Kulkarni', 'Female', 'pari.kulkarni@yahoo.com', '9100000018', '1995-01-09', 'Pune', 'Maharashtra', 'India', '2022-04-25', 'Active'),
('Advait', 'Pillai', 'Male', 'advait.pillai@gmail.com', '9100000019', '1993-03-18', 'Trivandrum', 'Kerala', 'India', '2022-05-01', 'Active'),
('Aadhya', 'Srinivasan', 'Female', 'aadhya.srini@outlook.com', '9100000020', '1991-06-24', 'Chennai', 'Tamil Nadu', 'India', '2022-05-05', 'Active');

INSERT INTO customers (first_name, last_name, gender, email, phone, date_of_birth, city, state, country, registration_date, status) VALUES
('Shaurya', 'Bose', 'Male', 'shaurya.bose@gmail.com', '9100000021', '1989-09-01', 'Kolkata', 'West Bengal', 'India', '2022-05-10', 'Active'),
('Tara', 'Hegde', 'Female', 'tara.hegde@yahoo.com', '9100000022', '1994-12-15', 'Bangalore', 'Karnataka', 'India', '2022-05-15', 'Active'),
('Rohan', 'Malhotra', 'Male', 'rohan.malhotra@gmail.com', '9100000023', '1990-04-22', 'Delhi', 'Delhi', 'India', '2022-05-20', 'Active'),
('Nisha', 'Pandey', 'Female', 'nisha.pandey@outlook.com', '9100000024', '1992-07-08', 'Varanasi', 'Uttar Pradesh', 'India', '2022-05-25', 'Active'),
('Yash', 'Rathore', 'Male', 'yash.rathore@gmail.com', '9100000025', '1991-11-27', 'Jaipur', 'Rajasthan', 'India', '2022-06-01', 'Active'),
('Mira', 'Thakur', 'Female', 'mira.thakur@yahoo.com', '9100000026', '1993-02-14', 'Shimla', 'Himachal Pradesh', 'India', '2022-06-05', 'Active'),
('Arnav', 'Choudhury', 'Male', 'arnav.choudhury@gmail.com', '9100000027', '1988-05-19', 'Guwahati', 'Assam', 'India', '2022-06-10', 'Active'),
('Zara', 'Sheikh', 'Female', 'zara.sheikh@outlook.com', '9100000028', '1995-08-03', 'Mumbai', 'Maharashtra', 'India', '2022-06-15', 'Active'),
('Kartik', 'Banerjee', 'Male', 'kartik.banerjee@gmail.com', '9100000029', '1990-10-28', 'Kolkata', 'West Bengal', 'India', '2022-06-20', 'Active'),
('Avni', 'Jain', 'Female', 'avni.jain@yahoo.com', '9100000030', '1992-01-06', 'Ahmedabad', 'Gujarat', 'India', '2022-06-25', 'Active');

INSERT INTO customers (first_name, last_name, gender, email, phone, date_of_birth, city, state, country, registration_date, status) VALUES
('Laksh', 'Aggarwal', 'Male', 'laksh.aggarwal@gmail.com', '9100000031', '1987-03-13', 'Delhi', 'Delhi', 'India', '2022-07-01', 'Active'),
('Ishita', 'Sinha', 'Female', 'ishita.sinha@outlook.com', '9100000032', '1994-06-20', 'Patna', 'Bihar', 'India', '2022-07-05', 'Active'),
('Rudra', 'Tiwari', 'Male', 'rudra.tiwari@gmail.com', '9100000033', '1991-09-09', 'Lucknow', 'Uttar Pradesh', 'India', '2022-07-10', 'Active'),
('Prisha', 'Menon', 'Female', 'prisha.menon@yahoo.com', '9100000034', '1993-12-01', 'Kochi', 'Kerala', 'India', '2022-07-15', 'Active'),
('Dev', 'Chauhan', 'Male', 'dev.chauhan@gmail.com', '9100000035', '1990-04-16', 'Bhopal', 'Madhya Pradesh', 'India', '2022-07-20', 'Active'),
('Anika', 'Das', 'Female', 'anika.das@outlook.com', '9100000036', '1992-07-25', 'Kolkata', 'West Bengal', 'India', '2022-07-25', 'Active'),
('Vivek', 'Yadav', 'Male', 'vivek.yadav@gmail.com', '9100000037', '1989-10-30', 'Delhi', 'Delhi', 'India', '2022-08-01', 'Active'),
('Kavya', 'Rao', 'Female', 'kavya.rao@yahoo.com', '9100000038', '1995-01-18', 'Bangalore', 'Karnataka', 'India', '2022-08-05', 'Active'),
('Neil', 'Bhatt', 'Male', 'neil.bhatt@gmail.com', '9100000039', '1991-05-07', 'Surat', 'Gujarat', 'India', '2022-08-10', 'Active'),
('Sara', 'Kapoor', 'Female', 'sara.kapoor@outlook.com', '9100000040', '1993-08-22', 'Mumbai', 'Maharashtra', 'India', '2022-08-15', 'Active');

INSERT INTO customers (first_name, last_name, gender, email, phone, date_of_birth, city, state, country, registration_date, status) VALUES
('Atharv', 'Goel', 'Male', 'atharv.goel@gmail.com', '9100000041', '1988-11-11', 'Chandigarh', 'Punjab', 'India', '2022-08-20', 'Active'),
('Ira', 'Mukherjee', 'Female', 'ira.mukherjee@yahoo.com', '9100000042', '1994-02-03', 'Kolkata', 'West Bengal', 'India', '2022-08-25', 'Active'),
('Rian', 'Dubey', 'Male', 'rian.dubey@gmail.com', '9100000043', '1990-06-17', 'Nagpur', 'Maharashtra', 'India', '2022-09-01', 'Active'),
('Navya', 'Sethi', 'Female', 'navya.sethi@outlook.com', '9100000044', '1992-09-28', 'Delhi', 'Delhi', 'India', '2022-09-05', 'Active'),
('Siddharth', 'Acharya', 'Male', 'sid.acharya@gmail.com', '9100000045', '1991-12-14', 'Pune', 'Maharashtra', 'India', '2022-09-10', 'Active'),
('Ahana', 'Bhat', 'Female', 'ahana.bhat@yahoo.com', '9100000046', '1993-03-21', 'Bangalore', 'Karnataka', 'India', '2022-09-15', 'Active'),
('Krishna', 'Mohan', 'Male', 'krishna.mohan@gmail.com', '9100000047', '1989-07-06', 'Hyderabad', 'Telangana', 'India', '2022-09-20', 'Inactive'),
('Trisha', 'Goyal', 'Female', 'trisha.goyal@outlook.com', '9100000048', '1995-10-10', 'Jaipur', 'Rajasthan', 'India', '2022-09-25', 'Active'),
('Harsh', 'Srivastava', 'Male', 'harsh.srivastava@gmail.com', '9100000049', '1990-01-25', 'Lucknow', 'Uttar Pradesh', 'India', '2022-10-01', 'Active'),
('Sia', 'Pillai', 'Female', 'sia.pillai@yahoo.com', '9100000050', '1992-04-15', 'Chennai', 'Tamil Nadu', 'India', '2022-10-05', 'Active');

INSERT INTO customers (first_name, last_name, gender, email, phone, date_of_birth, city, state, country, registration_date, status) VALUES
('Parth', 'Nanda', 'Male', 'parth.nanda@gmail.com', '9100000051', '1988-08-08', 'Mumbai', 'Maharashtra', 'India', '2022-10-10', 'Active'),
('Anvi', 'Shukla', 'Female', 'anvi.shukla@outlook.com', '9100000052', '1994-11-20', 'Varanasi', 'Uttar Pradesh', 'India', '2022-10-15', 'Active'),
('Aarush', 'Dixit', 'Male', 'aarush.dixit@gmail.com', '9100000053', '1991-02-12', 'Indore', 'Madhya Pradesh', 'India', '2022-10-20', 'Active'),
('Kyra', 'Mahajan', 'Female', 'kyra.mahajan@yahoo.com', '9100000054', '1993-05-27', 'Pune', 'Maharashtra', 'India', '2022-10-25', 'Active'),
('Aayan', 'Gill', 'Male', 'aayan.gill@gmail.com', '9100000055', '1990-09-04', 'Amritsar', 'Punjab', 'India', '2022-11-01', 'Active'),
('Misha', 'Bajaj', 'Female', 'misha.bajaj@outlook.com', '9100000056', '1992-12-16', 'Delhi', 'Delhi', 'India', '2022-11-05', 'Active'),
('Veer', 'Khatri', 'Male', 'veer.khatri@gmail.com', '9100000057', '1989-03-29', 'Jaipur', 'Rajasthan', 'India', '2022-11-10', 'Active'),
('Amaira', 'Luthra', 'Female', 'amaira.luthra@yahoo.com', '9100000058', '1995-06-13', 'Chandigarh', 'Punjab', 'India', '2022-11-15', 'Active'),
('Kabir', 'Rastogi', 'Male', 'kabir.rastogi@gmail.com', '9100000059', '1991-08-20', 'Dehradun', 'Uttarakhand', 'India', '2022-11-20', 'Active'),
('Shanaya', 'Oberoi', 'Female', 'shanaya.oberoi@outlook.com', '9100000060', '1993-11-05', 'Mumbai', 'Maharashtra', 'India', '2022-11-25', 'Active');

INSERT INTO customers (first_name, last_name, gender, email, phone, date_of_birth, city, state, country, registration_date, status) VALUES
('Rehan', 'Malik', 'Male', 'rehan.malik@gmail.com', '9100000061', '1988-01-17', 'Hyderabad', 'Telangana', 'India', '2022-12-01', 'Active'),
('Aditi', 'Soni', 'Female', 'aditi.soni@yahoo.com', '9100000062', '1994-04-09', 'Ahmedabad', 'Gujarat', 'India', '2022-12-05', 'Active'),
('Viraj', 'Pandey', 'Male', 'viraj.pandey@gmail.com', '9100000063', '1990-07-23', 'Varanasi', 'Uttar Pradesh', 'India', '2022-12-10', 'Active'),
('Sana', 'Ahmed', 'Female', 'sana.ahmed@outlook.com', '9100000064', '1992-10-31', 'Bangalore', 'Karnataka', 'India', '2022-12-15', 'Active'),
('Aryan', 'Bhatnagar', 'Male', 'aryan.bhatnagar@gmail.com', '9100000065', '1991-01-05', 'Delhi', 'Delhi', 'India', '2022-12-20', 'Active'),
('Nitya', 'Kaul', 'Female', 'nitya.kaul@yahoo.com', '9100000066', '1993-04-18', 'Srinagar', 'Jammu & Kashmir', 'India', '2022-12-25', 'Active'),
('Aadit', 'Trivedi', 'Male', 'aadit.trivedi@gmail.com', '9100000067', '1989-06-30', 'Vadodara', 'Gujarat', 'India', '2023-01-01', 'Active'),
('Rhea', 'Khanna', 'Female', 'rhea.khanna@outlook.com', '9100000068', '1995-09-14', 'Delhi', 'Delhi', 'India', '2023-01-05', 'Active'),
('Shivam', 'Rawat', 'Male', 'shivam.rawat@gmail.com', '9100000069', '1990-12-22', 'Dehradun', 'Uttarakhand', 'India', '2023-01-10', 'Active'),
('Isha', 'Bhargava', 'Female', 'isha.bhargava@yahoo.com', '9100000070', '1992-03-07', 'Bhopal', 'Madhya Pradesh', 'India', '2023-01-15', 'Active');

INSERT INTO customers (first_name, last_name, gender, email, phone, date_of_birth, city, state, country, registration_date, status) VALUES
('Pranav', 'Dutta', 'Male', 'pranav.dutta@gmail.com', '9100000071', '1988-05-11', 'Kolkata', 'West Bengal', 'India', '2023-01-20', 'Active'),
('Meera', 'Tandon', 'Female', 'meera.tandon@outlook.com', '9100000072', '1994-08-25', 'Mumbai', 'Maharashtra', 'India', '2023-01-25', 'Active'),
('Daksh', 'Mittal', 'Male', 'daksh.mittal@gmail.com', '9100000073', '1991-11-03', 'Delhi', 'Delhi', 'India', '2023-02-01', 'Active'),
('Aarna', 'Dewan', 'Female', 'aarna.dewan@yahoo.com', '9100000074', '1993-01-29', 'Chandigarh', 'Punjab', 'India', '2023-02-05', 'Inactive'),
('Krish', 'Saxena', 'Male', 'krish.saxena@gmail.com', '9100000075', '1990-04-08', 'Lucknow', 'Uttar Pradesh', 'India', '2023-02-10', 'Active'),
('Siya', 'Sharma', 'Female', 'siya.sharma@outlook.com', '9100000076', '1992-07-14', 'Jaipur', 'Rajasthan', 'India', '2023-02-15', 'Active'),
('Om', 'Prakash', 'Male', 'om.prakash@gmail.com', '9100000077', '1989-10-20', 'Patna', 'Bihar', 'India', '2023-02-20', 'Active'),
('Anushka', 'Roy', 'Female', 'anushka.roy@yahoo.com', '9100000078', '1995-01-02', 'Kolkata', 'West Bengal', 'India', '2023-02-25', 'Active'),
('Taksh', 'Dhawan', 'Male', 'taksh.dhawan@gmail.com', '9100000079', '1991-03-16', 'Mumbai', 'Maharashtra', 'India', '2023-03-01', 'Active'),
('Pihu', 'Grover', 'Female', 'pihu.grover@outlook.com', '9100000080', '1993-06-28', 'Delhi', 'Delhi', 'India', '2023-03-05', 'Active');

INSERT INTO customers (first_name, last_name, gender, email, phone, date_of_birth, city, state, country, registration_date, status) VALUES
('Ranveer', 'Anand', 'Male', 'ranveer.anand@gmail.com', '9100000081', '1988-09-05', 'Pune', 'Maharashtra', 'India', '2023-03-10', 'Active'),
('Aira', 'Chadha', 'Female', 'aira.chadha@yahoo.com', '9100000082', '1994-12-19', 'Amritsar', 'Punjab', 'India', '2023-03-15', 'Active'),
('Ishan', 'Venkatesh', 'Male', 'ishan.venkatesh@gmail.com', '9100000083', '1990-02-28', 'Bangalore', 'Karnataka', 'India', '2023-03-20', 'Active'),
('Tanya', 'Mathur', 'Female', 'tanya.mathur@outlook.com', '9100000084', '1992-05-15', 'Jaipur', 'Rajasthan', 'India', '2023-03-25', 'Active'),
('Jai', 'Singhania', 'Male', 'jai.singhania@gmail.com', '9100000085', '1991-08-01', 'Mumbai', 'Maharashtra', 'India', '2023-04-01', 'Active'),
('Nyra', 'Vohra', 'Female', 'nyra.vohra@yahoo.com', '9100000086', '1993-11-12', 'Delhi', 'Delhi', 'India', '2023-04-05', 'Active'),
('Arham', 'Kapoor', 'Male', 'arham.kapoor@gmail.com', '9100000087', '1989-01-24', 'Chennai', 'Tamil Nadu', 'India', '2023-04-10', 'Active'),
('Kiyana', 'Reddy', 'Female', 'kiyana.reddy@outlook.com', '9100000088', '1995-04-06', 'Hyderabad', 'Telangana', 'India', '2023-04-15', 'Active'),
('Yuvan', 'Naidu', 'Male', 'yuvan.naidu@gmail.com', '9100000089', '1990-07-18', 'Visakhapatnam', 'Andhra Pradesh', 'India', '2023-04-20', 'Active'),
('Samaira', 'Malik', 'Female', 'samaira.malik@yahoo.com', '9100000090', '1992-10-03', 'Delhi', 'Delhi', 'India', '2023-04-25', 'Active');

INSERT INTO customers (first_name, last_name, gender, email, phone, date_of_birth, city, state, country, registration_date, status) VALUES
('Agastya', 'Sehgal', 'Male', 'agastya.sehgal@gmail.com', '9100000091', '1988-12-29', 'Chandigarh', 'Punjab', 'India', '2023-05-01', 'Active'),
('Dhriti', 'Bose', 'Female', 'dhriti.bose@outlook.com', '9100000092', '1994-03-14', 'Kolkata', 'West Bengal', 'India', '2023-05-05', 'Active'),
('Manav', 'Thapa', 'Male', 'manav.thapa@gmail.com', '9100000093', '1991-06-08', 'Gangtok', 'Sikkim', 'India', '2023-05-10', 'Inactive'),
('Aanya', 'Walia', 'Female', 'aanya.walia@yahoo.com', '9100000094', '1993-09-22', 'Mumbai', 'Maharashtra', 'India', '2023-05-15', 'Active'),
('Shivansh', 'Arora', 'Male', 'shivansh.arora@gmail.com', '9100000095', '1990-11-07', 'Delhi', 'Delhi', 'India', '2023-05-20', 'Active'),
('Ivana', 'Rodrigues', 'Female', 'ivana.rodrigues@outlook.com', '9100000096', '1992-02-18', 'Goa', 'Goa', 'India', '2023-05-25', 'Active'),
('Dhairya', 'Hegde', 'Male', 'dhairya.hegde@gmail.com', '9100000097', '1989-04-30', 'Mangalore', 'Karnataka', 'India', '2023-06-01', 'Active'),
('Miraya', 'Puri', 'Female', 'miraya.puri@yahoo.com', '9100000098', '1995-07-12', 'Delhi', 'Delhi', 'India', '2023-06-05', 'Active'),
('Ranbir', 'Sodhi', 'Male', 'ranbir.sodhi@gmail.com', '9100000099', '1991-10-25', 'Ludhiana', 'Punjab', 'India', '2023-06-10', 'Blocked'),
('Falak', 'Mehra', 'Female', 'falak.mehra@outlook.com', '9100000100', '1993-01-15', 'Mumbai', 'Maharashtra', 'India', '2023-06-15', 'Active');

-- ===========================================
-- INVENTORY (60 records - products 1-10 get 2 stores each,
-- products 11-50 get 1 store each)
-- ===========================================
INSERT INTO inventory (product_id, store_id, stock_quantity, last_updated) VALUES
(1, 1, 25, '2024-06-01 10:00:00'), (1, 2, 18, '2024-06-01 10:00:00'),
(2, 1, 30, '2024-06-01 10:00:00'), (2, 3, 22, '2024-06-01 10:00:00'),
(3, 2, 40, '2024-06-01 10:00:00'), (3, 4, 35, '2024-06-01 10:00:00'),
(4, 1, 15, '2024-06-01 10:00:00'), (4, 5, 12, '2024-06-01 10:00:00'),
(5, 3, 50, '2024-06-01 10:00:00'), (5, 1, 45, '2024-06-01 10:00:00'),
(6, 2, 100, '2024-06-01 10:00:00'), (6, 4, 80, '2024-06-01 10:00:00'),
(7, 1, 75, '2024-06-01 10:00:00'), (7, 3, 60, '2024-06-01 10:00:00'),
(8, 5, 40, '2024-06-01 10:00:00'), (8, 2, 35, '2024-06-01 10:00:00'),
(9, 4, 55, '2024-06-01 10:00:00'), (9, 1, 45, '2024-06-01 10:00:00'),
(10, 3, 65, '2024-06-01 10:00:00'), (10, 5, 50, '2024-06-01 10:00:00'),
(11, 1, 30, '2024-06-01 10:00:00'), (12, 2, 25, '2024-06-01 10:00:00'),
(13, 3, 45, '2024-06-01 10:00:00'), (14, 4, 10, '2024-06-01 10:00:00'),
(15, 5, 90, '2024-06-01 10:00:00'), (16, 1, 200, '2024-06-01 10:00:00'),
(17, 2, 180, '2024-06-01 10:00:00'), (18, 3, 150, '2024-06-01 10:00:00'),
(19, 4, 80, '2024-06-01 10:00:00'), (20, 5, 60, '2024-06-01 10:00:00'),
(21, 1, 8, '2024-06-01 10:00:00'), (22, 2, 35, '2024-06-01 10:00:00'),
(23, 3, 120, '2024-06-01 10:00:00'), (24, 4, 55, '2024-06-01 10:00:00'),
(25, 5, 20, '2024-06-01 10:00:00'), (26, 1, 90, '2024-06-01 10:00:00'),
(27, 2, 110, '2024-06-01 10:00:00'), (28, 3, 85, '2024-06-01 10:00:00'),
(29, 4, 70, '2024-06-01 10:00:00'), (30, 5, 95, '2024-06-01 10:00:00'),
(31, 1, 20, '2024-06-01 10:00:00'), (32, 2, 40, '2024-06-01 10:00:00'),
(33, 3, 30, '2024-06-01 10:00:00'), (34, 4, 65, '2024-06-01 10:00:00'),
(35, 5, 50, '2024-06-01 10:00:00'), (36, 1, 300, '2024-06-01 10:00:00'),
(37, 2, 250, '2024-06-01 10:00:00'), (38, 3, 400, '2024-06-01 10:00:00'),
(39, 4, 150, '2024-06-01 10:00:00'), (40, 5, 200, '2024-06-01 10:00:00'),
(41, 1, 15, '2024-06-01 10:00:00'), (42, 2, 12, '2024-06-01 10:00:00'),
(43, 3, 18, '2024-06-01 10:00:00'), (44, 4, 10, '2024-06-01 10:00:00'),
(45, 5, 8, '2024-06-01 10:00:00'), (46, 1, 20, '2024-06-01 10:00:00'),
(47, 2, 25, '2024-06-01 10:00:00'), (48, 3, 30, '2024-06-01 10:00:00'),
(49, 4, 14, '2024-06-01 10:00:00'), (50, 5, 22, '2024-06-01 10:00:00');

-- ===========================================
-- ORDERS (500 records)
-- Generated using stored procedure for realistic data
-- ===========================================
DELIMITER //
CREATE PROCEDURE generate_orders()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE v_customer_id INT;
    DECLARE v_store_id INT;
    DECLARE v_employee_id INT;
    DECLARE v_order_date DATETIME;
    DECLARE v_status VARCHAR(20);
    DECLARE v_day_offset INT;
    DECLARE v_status_rand DECIMAL(3,2);
    
    WHILE i <= 500 DO
        -- Random customer (1-100)
        SET v_customer_id = FLOOR(1 + RAND() * 100);
        -- Random store (1-5)
        SET v_store_id = FLOOR(1 + RAND() * 5);
        -- Employee from that store (4 employees per store)
        SET v_employee_id = (v_store_id - 1) * 4 + FLOOR(1 + RAND() * 4);
        -- Random date in 2024 (Jan to Dec)
        SET v_day_offset = FLOOR(RAND() * 365);
        SET v_order_date = DATE_ADD('2024-01-01 08:00:00', INTERVAL v_day_offset DAY);
        SET v_order_date = DATE_ADD(v_order_date, INTERVAL FLOOR(RAND() * 14) HOUR);
        -- Random status
        SET v_status_rand = RAND();
        IF v_status_rand < 0.45 THEN SET v_status = 'Delivered';
        ELSEIF v_status_rand < 0.60 THEN SET v_status = 'Shipped';
        ELSEIF v_status_rand < 0.72 THEN SET v_status = 'Processing';
        ELSEIF v_status_rand < 0.82 THEN SET v_status = 'Pending';
        ELSEIF v_status_rand < 0.92 THEN SET v_status = 'Cancelled';
        ELSE SET v_status = 'Returned';
        END IF;
        
        INSERT INTO orders (customer_id, store_id, employee_id, order_date, order_status, total_amount)
        VALUES (v_customer_id, v_store_id, v_employee_id, v_order_date, v_status, 0.00);
        
        SET i = i + 1;
    END WHILE;
END //
DELIMITER ;

CALL generate_orders();
DROP PROCEDURE IF EXISTS generate_orders;

-- ===========================================
-- ORDER_ITEMS (~1000 records)
-- Each order gets 1-3 items (ensures all orders have items)
-- discount_pct: percentage discount applied
-- tax_pct: GST percentage (18%)
-- net_amount: qty * unit_price * (1 - discount_pct/100)
-- tax_amount: net_amount * tax_pct / 100
-- line_total: net_amount + tax_amount
-- ===========================================
DELIMITER //
CREATE PROCEDURE generate_order_items()
BEGIN
    DECLARE v_order_id INT DEFAULT 1;
    DECLARE v_product_id INT;
    DECLARE v_quantity INT;
    DECLARE v_unit_price DECIMAL(10,2);
    DECLARE v_discount_pct DECIMAL(5,2);
    DECLARE v_tax_pct DECIMAL(5,2);
    DECLARE v_net_amount DECIMAL(10,2);
    DECLARE v_tax_amount DECIMAL(10,2);
    DECLARE v_line_total DECIMAL(10,2);
    DECLARE v_items_per_order INT;
    DECLARE j INT;
    
    -- Loop through ALL 500 orders to ensure each gets at least 1 item
    WHILE v_order_id <= 500 DO
        -- Each order gets 1 to 3 items (avg ~2, total ~1000)
        SET v_items_per_order = FLOOR(1 + RAND() * 3);
        SET j = 1;
        
        WHILE j <= v_items_per_order DO
            SET v_product_id = FLOOR(1 + RAND() * 50);
            SET v_quantity = FLOOR(1 + RAND() * 5);
            
            -- Get actual product price
            SELECT unit_price INTO v_unit_price 
            FROM products WHERE product_id = v_product_id;
            
            -- Random discount 0-15%
            SET v_discount_pct = ROUND(RAND() * 15, 2);
            -- Tax 18% GST
            SET v_tax_pct = 18.00;
            -- Calculate net amount (pre-tax)
            SET v_net_amount = ROUND(
                v_quantity * v_unit_price * (1 - v_discount_pct/100), 2
            );
            -- Calculate tax amount
            SET v_tax_amount = ROUND(v_net_amount * v_tax_pct / 100, 2);
            -- Line total = net + tax
            SET v_line_total = v_net_amount + v_tax_amount;
            
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct, tax_pct, net_amount, tax_amount, line_total)
            VALUES (v_order_id, v_product_id, v_quantity, v_unit_price, v_discount_pct, v_tax_pct, v_net_amount, v_tax_amount, v_line_total);
            
            SET j = j + 1;
        END WHILE;
        
        SET v_order_id = v_order_id + 1;
    END WHILE;
END //
DELIMITER ;

CALL generate_order_items();
DROP PROCEDURE IF EXISTS generate_order_items;

-- ===========================================
-- UPDATE ORDER TOTALS
-- Sum line_total from order_items into orders
-- ===========================================
UPDATE orders o
SET total_amount = (
    SELECT COALESCE(SUM(oi.line_total), 0)
    FROM order_items oi
    WHERE oi.order_id = o.order_id
);

-- ===========================================
-- PAYMENTS (one per order that has items/amount > 0)
-- ===========================================
DELIMITER //
CREATE PROCEDURE generate_payments()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE v_order_date DATETIME;
    DECLARE v_total DECIMAL(12,2);
    DECLARE v_status VARCHAR(20);
    DECLARE v_order_status VARCHAR(20);
    DECLARE v_method VARCHAR(20);
    DECLARE v_method_rand DECIMAL(3,2);
    
    WHILE i <= 500 DO
        SELECT order_date, total_amount, order_status 
        INTO v_order_date, v_total, v_order_status
        FROM orders WHERE order_id = i;
        
        -- Skip orders with zero amount (no items assigned)
        IF v_total > 0 THEN
            -- Payment method distribution
            SET v_method_rand = RAND();
            IF v_method_rand < 0.25 THEN SET v_method = 'UPI';
            ELSEIF v_method_rand < 0.45 THEN SET v_method = 'Credit Card';
            ELSEIF v_method_rand < 0.65 THEN SET v_method = 'Debit Card';
            ELSEIF v_method_rand < 0.80 THEN SET v_method = 'Net Banking';
            ELSEIF v_method_rand < 0.90 THEN SET v_method = 'Cash';
            ELSE SET v_method = 'Wallet';
            END IF;
            
            -- Payment status based on order status
            IF v_order_status = 'Cancelled' THEN SET v_status = 'Refunded';
            ELSEIF v_order_status = 'Returned' THEN SET v_status = 'Refunded';
            ELSEIF v_order_status = 'Pending' THEN SET v_status = 'Pending';
            ELSE SET v_status = 'Completed';
            END IF;
            
            INSERT INTO payments (order_id, payment_method, payment_status, payment_date, amount_paid)
            VALUES (i, v_method, v_status, v_order_date, v_total);
        END IF;
        
        SET i = i + 1;
    END WHILE;
END //
DELIMITER ;

CALL generate_payments();
DROP PROCEDURE IF EXISTS generate_payments;

-- ===========================================
-- SHIPMENTS (for Shipped and Delivered orders)
-- ===========================================
DELIMITER //
CREATE PROCEDURE generate_shipments()
BEGIN
    DECLARE v_order_id INT;
    DECLARE v_order_date DATETIME;
    DECLARE v_order_status VARCHAR(20);
    DECLARE v_partner VARCHAR(100);
    DECLARE v_tracking VARCHAR(50);
    DECLARE v_ship_date DATE;
    DECLARE v_delivery_date DATE;
    DECLARE v_ship_status VARCHAR(20);
    DECLARE v_partner_rand DECIMAL(3,2);
    DECLARE done INT DEFAULT FALSE;
    
    DECLARE cur CURSOR FOR 
        SELECT order_id, order_date, order_status 
        FROM orders 
        WHERE order_status IN ('Shipped', 'Delivered', 'Returned');
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_order_id, v_order_date, v_order_status;
        IF done THEN LEAVE read_loop; END IF;
        
        -- Random shipping partner
        SET v_partner_rand = RAND();
        IF v_partner_rand < 0.25 THEN SET v_partner = 'BlueDart';
        ELSEIF v_partner_rand < 0.50 THEN SET v_partner = 'Delhivery';
        ELSEIF v_partner_rand < 0.70 THEN SET v_partner = 'DTDC';
        ELSEIF v_partner_rand < 0.85 THEN SET v_partner = 'Ekart Logistics';
        ELSE SET v_partner = 'India Post';
        END IF;
        
        -- Tracking number
        SET v_tracking = CONCAT('TRK', LPAD(v_order_id, 8, '0'), FLOOR(RAND()*1000));
        
        -- Ship date: 1-2 days after order
        SET v_ship_date = DATE_ADD(DATE(v_order_date), INTERVAL FLOOR(1 + RAND()*2) DAY);
        
        -- Delivery date & status
        IF v_order_status = 'Delivered' OR v_order_status = 'Returned' THEN
            SET v_delivery_date = DATE_ADD(v_ship_date, INTERVAL FLOOR(2 + RAND()*5) DAY);
            SET v_ship_status = 'Delivered';
        ELSE
            SET v_delivery_date = NULL;
            SET v_ship_status = 'In Transit';
        END IF;
        
        INSERT INTO shipments (order_id, shipping_partner, tracking_number, shipment_date, delivery_date, shipment_status)
        VALUES (v_order_id, v_partner, v_tracking, v_ship_date, v_delivery_date, v_ship_status);
        
    END LOOP;
    CLOSE cur;
END //
DELIMITER ;

CALL generate_shipments();
DROP PROCEDURE IF EXISTS generate_shipments;

-- ===========================================
-- RETURNS (~40 records for 'Returned' orders)
-- ===========================================
DELIMITER //
CREATE PROCEDURE generate_returns()
BEGIN
    DECLARE v_order_item_id INT;
    DECLARE v_line_total DECIMAL(10,2);
    DECLARE v_order_date DATETIME;
    DECLARE v_reason VARCHAR(255);
    DECLARE v_reason_rand DECIMAL(3,2);
    DECLARE done INT DEFAULT FALSE;
    
    DECLARE cur CURSOR FOR
        SELECT oi.order_item_id, oi.line_total, o.order_date
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status = 'Returned';
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_order_item_id, v_line_total, v_order_date;
        IF done THEN LEAVE read_loop; END IF;
        
        -- Random return reason
        SET v_reason_rand = RAND();
        IF v_reason_rand < 0.25 THEN SET v_reason = 'Defective product received';
        ELSEIF v_reason_rand < 0.45 THEN SET v_reason = 'Wrong item delivered';
        ELSEIF v_reason_rand < 0.60 THEN SET v_reason = 'Product not as described';
        ELSEIF v_reason_rand < 0.75 THEN SET v_reason = 'Size/fit issue';
        ELSEIF v_reason_rand < 0.85 THEN SET v_reason = 'Changed mind';
        ELSE SET v_reason = 'Better price available elsewhere';
        END IF;
        
        INSERT INTO returns (order_item_id, return_reason, return_date, refund_amount)
        VALUES (
            v_order_item_id,
            v_reason,
            DATE_ADD(DATE(v_order_date), INTERVAL FLOOR(7 + RAND()*14) DAY),
            v_line_total
        );
        
    END LOOP;
    CLOSE cur;
END //
DELIMITER ;

CALL generate_returns();
DROP PROCEDURE IF EXISTS generate_returns;

-- ===========================================
-- VERIFICATION QUERIES
-- ===========================================
SELECT 'Sample data inserted successfully.' AS status;
SELECT COUNT(*) AS total_customers FROM customers;
SELECT COUNT(*) AS total_products FROM products;
SELECT COUNT(*) AS total_orders FROM orders;
SELECT COUNT(*) AS total_order_items FROM order_items;
SELECT COUNT(*) AS total_payments FROM payments;
SELECT COUNT(*) AS total_shipments FROM shipments;
SELECT COUNT(*) AS total_returns FROM returns;

-- Referential integrity check (should all return 0)
SELECT COUNT(*) AS orphan_orders_no_items
FROM orders o LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE oi.order_item_id IS NULL;

SELECT COUNT(*) AS orphan_orders_no_payments
FROM orders o LEFT JOIN payments p ON o.order_id = p.order_id
WHERE p.payment_id IS NULL AND o.total_amount > 0;
