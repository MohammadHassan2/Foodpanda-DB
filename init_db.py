import sqlite3

def setup_database():
    conn = sqlite3.connect("foodpanda.db")
    cursor = conn.cursor()

    # Enable Foreign Key support in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Complete 3NF Schema & Data Setup
    sql_script = """
    DROP TABLE IF EXISTS Order_Details;
    DROP TABLE IF EXISTS Live_Tracking;
    DROP TABLE IF EXISTS Order_Record;
    DROP TABLE IF EXISTS Saved_Address;
    DROP TABLE IF EXISTS Menu_Item;
    DROP TABLE IF EXISTS Rider_Contact;
    DROP TABLE IF EXISTS Customer_Contact;
    DROP TABLE IF EXISTS Restaurant;
    DROP TABLE IF EXISTS Rider;
    DROP TABLE IF EXISTS Customer;

    CREATE TABLE Customer (
        Customer_ID     INTEGER PRIMARY KEY AUTOINCREMENT,
        Full_Name       TEXT    NOT NULL,
        Email           TEXT    NOT NULL UNIQUE,
        Wallet_Balance  REAL    NOT NULL DEFAULT 0.00 CHECK (Wallet_Balance >= 0)
    );

    CREATE TABLE Customer_Contact (
        Contact_ID      INTEGER PRIMARY KEY AUTOINCREMENT,
        Customer_ID     INTEGER NOT NULL,
        Phone_Number    TEXT    NOT NULL,
        Contact_Type    TEXT    NOT NULL DEFAULT 'primary' CHECK (Contact_Type IN ('primary', 'secondary')),
        FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID) ON DELETE CASCADE
    );

    CREATE TABLE Rider (
        Rider_ID        INTEGER PRIMARY KEY AUTOINCREMENT,
        Full_Name       TEXT    NOT NULL,
        Vehicle_Reg     TEXT    NOT NULL UNIQUE,
        Shift_Status    TEXT    NOT NULL DEFAULT 'inactive' CHECK (Shift_Status IN ('active', 'inactive', 'on_break'))
    );

    CREATE TABLE Rider_Contact (
        Contact_ID      INTEGER PRIMARY KEY AUTOINCREMENT,
        Rider_ID        INTEGER NOT NULL,
        Phone_Number    TEXT    NOT NULL,
        Contact_Type    TEXT    NOT NULL DEFAULT 'primary' CHECK (Contact_Type IN ('primary', 'secondary')),
        FOREIGN KEY (Rider_ID) REFERENCES Rider(Rider_ID) ON DELETE CASCADE
    );

    CREATE TABLE Saved_Address (
        Customer_ID             INTEGER NOT NULL,
        Address_Label           TEXT    NOT NULL,
        Street                  TEXT    NOT NULL,
        City                    TEXT    NOT NULL,
        Zip                     TEXT    NOT NULL,
        Delivery_Instructions   TEXT,
        PRIMARY KEY (Customer_ID, Address_Label),
        FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID) ON DELETE CASCADE
    );

    CREATE TABLE Restaurant (
        Restaurant_ID       INTEGER PRIMARY KEY AUTOINCREMENT,
        Rest_Name           TEXT    NOT NULL,
        Operating_Status    TEXT    NOT NULL DEFAULT 'open' CHECK (Operating_Status IN ('open', 'closed', 'busy')),
        Rating              REAL    NOT NULL DEFAULT 0.0 CHECK (Rating BETWEEN 0.0 AND 5.0)
    );

    CREATE TABLE Menu_Item (
        Item_ID         INTEGER PRIMARY KEY AUTOINCREMENT,
        Restaurant_ID   INTEGER NOT NULL,
        Item_Name       TEXT    NOT NULL,
        Price           REAL    NOT NULL CHECK (Price > 0),
        Category        TEXT    NOT NULL,
        FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID) ON DELETE CASCADE
    );

    CREATE TABLE Order_Record (
        Order_ID        INTEGER PRIMARY KEY AUTOINCREMENT,
        Customer_ID     INTEGER NOT NULL,
        Rider_ID        INTEGER NOT NULL,
        Total_Amount    REAL    NOT NULL CHECK (Total_Amount >= 0),
        Order_Status    TEXT    NOT NULL DEFAULT 'pending' CHECK (Order_Status IN ('pending','preparing','on_the_way','delivered','cancelled')),
        Order_Time      TEXT    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID),
        FOREIGN KEY (Rider_ID)    REFERENCES Rider(Rider_ID)
    );

    CREATE TABLE Live_Tracking (
        Tracking_ID         INTEGER PRIMARY KEY AUTOINCREMENT,
        Order_ID            INTEGER NOT NULL UNIQUE,
        Estimated_Arrival   TEXT    NOT NULL,
        Ping_Status         TEXT    NOT NULL DEFAULT 'active' CHECK (Ping_Status IN ('active', 'idle', 'completed')),
        FOREIGN KEY (Order_ID) REFERENCES Order_Record(Order_ID) ON DELETE CASCADE
    );

    CREATE TABLE Order_Details (
        Order_ID    INTEGER NOT NULL,
        Item_ID     INTEGER NOT NULL,
        Quantity    INTEGER NOT NULL CHECK (Quantity > 0),
        PRIMARY KEY (Order_ID, Item_ID),
        FOREIGN KEY (Order_ID) REFERENCES Order_Record(Order_ID) ON DELETE CASCADE,
        FOREIGN KEY (Item_ID)  REFERENCES Menu_Item(Item_ID)     ON DELETE CASCADE
    );

    -- Sample Data Insertion
    INSERT INTO Customer (Full_Name, Email, Wallet_Balance) VALUES
        ('Ayesha Khan', 'ayesha.khan@gmail.com', 1500.00),
        ('Bilal Ahmed', 'bilal.ahmed@hotmail.com', 750.50),
        ('Sara Malik', 'sara.malik@yahoo.com', 2200.00),
        ('Usman Tariq', 'usman.tariq@gmail.com', 300.00),
        ('Hina Chaudhry', 'hina.ch@outlook.com', 950.75);

    INSERT INTO Customer_Contact (Customer_ID, Phone_Number, Contact_Type) VALUES
        (1, '0300-1234567', 'primary'), (1, '0321-9876543', 'secondary'),
        (2, '0333-4567890', 'primary'), (3, '0345-6789012', 'primary'),
        (3, '0311-1122334', 'secondary'), (4, '0322-9988776', 'primary'),
        (5, '0301-5544332', 'primary');

    INSERT INTO Saved_Address (Customer_ID, Address_Label, Street, City, Zip, Delivery_Instructions) VALUES
        (1, 'Home', '12-A Gulshan Block 3', 'Karachi', '75300', 'Ring bell twice'),
        (1, 'Office', '4th Floor, Plaza 21, I-8', 'Islamabad', '44000', 'Lobby reception'),
        (2, 'Home', '23 Johar Town Phase 2', 'Lahore', '54782', 'Gate code: 1234'),
        (3, 'Home', '7-B DHA Phase 5', 'Lahore', '54810', NULL),
        (4, 'Hostel', 'Block C, FAST University', 'Islamabad', '44020', 'Call on arrival'),
        (5, 'Home', '88 Satellite Town G-3', 'Rawalpindi', '46000', NULL);

    INSERT INTO Rider (Full_Name, Vehicle_Reg, Shift_Status) VALUES
        ('Kamran Ali', 'LHR-2345', 'active'), ('Zain Hussain', 'ISB-8871', 'active'),
        ('Farhan Siddiqui', 'KHI-6630', 'on_break'), ('Asad Mehmood', 'RWP-1192', 'inactive'),
        ('Omer Butt', 'LHR-5509', 'active');

    INSERT INTO Rider_Contact (Rider_ID, Phone_Number, Contact_Type) VALUES
        (1, '0302-1112233', 'primary'), (2, '0315-4445566', 'primary'),
        (2, '0300-9998877', 'secondary'), (3, '0344-7778899', 'primary'),
        (4, '0321-6665544', 'primary'), (5, '0303-3332211', 'primary');

    INSERT INTO Restaurant (Rest_Name, Operating_Status, Rating) VALUES
        ('Monal Grill', 'open', 4.7), ('Howdy BBQ', 'open', 4.5),
        ('Savour Foods', 'busy', 4.3), ('Meat the Cheese', 'open', 4.6),
        ('The Burning Brownie', 'closed', 4.8);

    INSERT INTO Menu_Item (Restaurant_ID, Item_Name, Price, Category) VALUES
        (1, 'Chicken Karahi', 850.00, 'Main Course'), (1, 'Mutton Namkeen', 1100.00, 'Main Course'),
        (1, 'Garlic Naan', 60.00, 'Bread'), (1, 'Raita', 80.00, 'Side'),
        (2, 'BBQ Platter (Full)', 1400.00, 'Main Course'), (2, 'Seekh Kebab (6 pcs)', 450.00, 'Starter'),
        (2, 'Chapli Kebab', 350.00, 'Starter'), (2, 'Cold Drink', 80.00, 'Beverage'),
        (3, 'Paya', 650.00, 'Main Course'), (3, 'Nihari', 750.00, 'Main Course'),
        (3, 'Kulcha', 50.00, 'Bread'), (4, 'Classic Burger', 550.00, 'Burger'),
        (4, 'Double Smash Burger', 850.00, 'Burger'), (4, 'Loaded Fries', 350.00, 'Side'),
        (4, 'Milkshake', 300.00, 'Beverage'), (5, 'Lava Brownie', 350.00, 'Dessert'),
        (5, 'Nutella Waffle', 420.00, 'Dessert'), (5, 'Cold Coffee', 280.00, 'Beverage');

    INSERT INTO Order_Record (Customer_ID, Rider_ID, Total_Amount, Order_Status, Order_Time) VALUES
        (1, 1, 1910.00, 'delivered', '2025-06-01 12:30:00'), (2, 2, 1480.00, 'on_the_way', '2025-06-02 13:15:00'),
        (3, 5, 1150.00, 'delivered', '2025-06-02 19:00:00'), (4, 1, 700.00, 'pending', '2025-06-03 09:45:00'),
        (5, 3, 1200.00, 'preparing', '2025-06-03 20:10:00'), (1, 2, 2500.00, 'delivered', '2025-06-04 14:00:00'),
        (3, 5, 900.00, 'cancelled', '2025-06-04 18:30:00'), (2, 1, 1730.00, 'delivered', '2025-06-05 12:00:00');

    INSERT INTO Live_Tracking (Order_ID, Estimated_Arrival, Ping_Status) VALUES
        (2, '2025-06-02 13:45:00', 'active'), (4, '2025-06-03 10:15:00', 'active'),
        (5, '2025-06-03 20:40:00', 'idle'), (1, '2025-06-01 13:00:00', 'completed'),
        (3, '2025-06-02 19:30:00', 'completed'), (6, '2025-06-04 14:30:00', 'completed'),
        (8, '2025-06-05 12:25:00', 'completed');

    INSERT INTO Order_Details (Order_ID, Item_ID, Quantity) VALUES
        (1, 1, 1), (1, 3, 3), (1, 4, 2), (2, 5, 1), (2, 8, 2),
        (3, 13, 1), (3, 14, 1), (3, 15, 1), (4, 10, 1), (4, 11, 2),
        (5, 12, 2), (5, 14, 1), (6, 2, 2), (6, 3, 3), (7, 9, 1),
        (7, 11, 2), (8, 6, 2), (8, 7, 1), (8, 8, 3);
    """

    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("Database foodpanda.db successfully created and populated!")

if __name__ == "__main__":
    setup_database()