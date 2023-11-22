import sqlite3


class RestaurantDB:
    def __init__(self):
        self.connection = sqlite3.connect("restaurant.db")

    def init_user_table(self):
        cursor = self.connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS User')
        cursor.execute(("CREATE TABLE User ("
                        "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "    firstname TEXT NOT NULL,"
                        "    lastname TEXT NOT NULL,"
                        "    phone_number TEXT,"
                        "    mail TEXT NOT NULL UNIQUE,"
                        "    password TEXT NOT NULL);"))
        cursor.close()
        self.connection.commit()

    def init_menu_table(self):
        cursor = self.connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS Menu')
        cursor.execute(("CREATE TABLE Menu ("
                        "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "    food TEXT NOT NULL,"
                        "    price INTEGER NOT NULL,"
                        "    available BOOLEAN NOT NULL);"))
        cursor.close()
        self.connection.commit()

    def init_order_table(self):
        cursor = self.connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS Orders')
        cursor.execute(("CREATE TABLE Orders ("
                        "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "    userId INTEGER NOT NULL,"
                        "    orderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                        "    FOREIGN KEY (userId) REFERENCES User(id));"))
        cursor.close()
        self.connection.commit()

    def init_order_details_table(self):
        cursor = self.connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS OrderDetails ')
        cursor.execute(("CREATE TABLE OrderDetails ("
                        "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "    orderId INTEGER NOT NULL,"
                        "    foodId INTEGER NOT NULL,"
                        "    quantity INTEGER NOT NULL,"
                        "    FOREIGN KEY (orderId) REFERENCES Orders(orderId),"
                        "    FOREIGN KEY (foodId) REFERENCES Foods(foodId));"))
        cursor.close()
        self.connection.commit()

    def add_user(self, firstname, lastname, phone_number, mail, password):
        cursor = self.connection.cursor()
        cursor.execute(("INSERT INTO User (firstname, lastname, phone_number, mail, password)"
                        f"VALUES ('{firstname}', {lastname}, '{phone_number}', '{mail}', '{password}');"))
        cursor.close()
        self.connection.commit()

    def remove_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM User WHERE id = {user_id}")
        cursor.close()
        self.connection.commit()

    def add_menu(self, food, price, available):
        cursor = self.connection.cursor()
        cursor.execute(("INSERT INTO Menu (food, price, available)"
                        f"VALUES ('{food}', {price}, '{available}');"))
        cursor.close()
        self.connection.commit()

    def remove_menu(self, menu_id):
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM Menu WHERE id = {menu_id}")
        cursor.close()
        self.connection.commit()

    def add_order(self, user_id, order_date, quantity):
        cursor = self.connection.cursor()
        cursor.execute(("INSERT INTO Order (userId, order_date, quantity)"
                        f"VALUES ('{user_id}', '{order_date}', {quantity}');"))
        cursor.close()
        self.connection.commit()

    def remove_order(self, order_id):
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM Orders WHERE id = {order_id}")
        cursor.close()
        self.connection.commit()

    def add_order_details(self, order_id, food_id, quantity):
        cursor = self.connection.cursor()
        cursor.execute(("INSERT INTO OrderDetails (order_id, food_id, quantity)"
                        f"VALUES ('{order_id}', {food_id}, '{quantity}');"))
        cursor.close()
        self.connection.commit()

    def remove_order_details(self, order_id):
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM OrderDetails WHERE id = {order_id}")
        cursor.close()
        self.connection.commit()

    def add_random_users(self):
        cursor = self.connection.cursor()
        cursor.execute(("INSERT INTO User (firstname, lastname, phone_number, mail, password)"
                        "VALUES ('John', 'Doe', '123456789', 'john.doe@example.com', '1234');"))
        cursor.execute(("INSERT INTO User (firstname, lastname, phone_number, mail, password)"
                        "VALUES ('Jane', 'Smith', '987654321', 'jane.smith@example.com', '1234');"))
        cursor.close()
        self.connection.commit()

    def read(self):
        cursor = self.connection.cursor()
        rows = cursor.execute("SELECT * from User").fetchall()
        print(rows)


if __name__ == '__main__':
    db = RestaurantDB()
    db.init_user_table()
    db.init_menu_table()
    db.init_order_table()
    db.init_order_details_table()
    db.add_random_users()
    # db.remove_user(1)
    db.read()
