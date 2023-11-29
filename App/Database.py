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
                        "    status TEXT NOT NULL,"
                        "    orderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                        "    FOREIGN KEY (userId) REFERENCES User(id));"))
        cursor.close()
        self.connection.commit()

    def init_order_details_table(self):
        cursor = self.connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS OrderDetails ')
        cursor.execute(("CREATE TABLE OrderDetails ("
                        "    orderId INTEGER NOT NULL,"
                        "    foodId INTEGER NOT NULL,"
                        "    quantity INTEGER NOT NULL,"
                        "    PRIMARY KEY (orderId, foodId)"
                        "    FOREIGN KEY (orderId) REFERENCES Orders(orderId),"
                        "    FOREIGN KEY (foodId) REFERENCES Foods(foodId));"))
        cursor.close()
        self.connection.commit()

    def add_user(self, firstname, lastname, phone_number, mail, password):
        cursor = self.connection.cursor()
        query = ("INSERT INTO User (firstname, lastname, phone_number, mail, password)"
                 "VALUES (?, ?, ?, ?, ?);")
        user_data = (firstname, lastname, phone_number, mail, password)
        cursor.execute(query, user_data)
        last_id = cursor.lastrowid
        cursor.close()
        self.connection.commit()
        return last_id

    def remove_user(self, user_id):
        cursor = self.connection.cursor()
        query = "DELETE FROM User WHERE id = ?"
        cursor.execute(query, (user_id,))
        cursor.close()
        self.connection.commit()

    def add_menu(self, food, price, available):
        cursor = self.connection.cursor()
        query = ("INSERT INTO Menu (food, price, available)"
                 "VALUES (?, ?, ?);")
        menu_data = (food, price, available)
        cursor.execute(query, menu_data)
        last_id = cursor.lastrowid
        cursor.close()
        self.connection.commit()
        return last_id

    def update_menu(self, id, food, price, available):
        cursor = self.connection.cursor()
        query = "UPDATE Menu SET food = ?, price = ?, available = ? WHERE id = ?"
        menu_data = (food, price, available, id)
        cursor.execute(query, menu_data)
        cursor.close()
        self.connection.commit()

    def remove_menu(self, menu_id):
        cursor = self.connection.cursor()
        query = "DELETE FROM Menu WHERE id = ?"
        cursor.execute(query, (menu_id,))
        cursor.close()
        self.connection.commit()

    def get_all_foods(self):
        cursor = self.connection.cursor()
        rows = cursor.execute("SELECT * from Menu").fetchall()
        cursor.close()
        return rows

    def add_order(self, user_id, status):
        cursor = self.connection.cursor()
        query = ("INSERT INTO Orders (userId, status)"
                 "VALUES (?, ?);")
        order_data = (user_id, status)
        cursor.execute(query, order_data)
        last_id = cursor.lastrowid
        cursor.close()
        self.connection.commit()
        return last_id

    def update_order_stats(self, order_id: int, new_status: str):
        # Update the status of the order with the specified orderId
        cursor = self.connection.cursor()
        query = ("UPDATE Orders "
                 "SET status = ? "
                 "WHERE id = ?")

        cursor.execute(query, (new_status, order_id))
        cursor.close()
        self.connection.commit()

    def get_all_orders(self):
        cursor = self.connection.cursor()
        rows = cursor.execute("SELECT * from Orders").fetchall()
        cursor.close()
        return rows

    def remove_order(self, order_id):
        cursor = self.connection.cursor()
        query = "DELETE FROM Orders WHERE id = ?"
        cursor.execute(query, (order_id,))
        cursor.close()
        self.connection.commit()

    def add_order_details(self, order_id, food_id, quantity):
        cursor = self.connection.cursor()
        query = ("INSERT INTO OrderDetails (orderId, foodId, quantity)"
                 "VALUES (?, ?, ?);")
        order_details_data = (order_id, food_id, quantity)
        cursor.execute(query, order_details_data)
        last_id = cursor.lastrowid
        cursor.close()
        self.connection.commit()
        return last_id

    def remove_order_details(self, order_id):
        cursor = self.connection.cursor()
        query = "DELETE FROM OrderDetails WHERE id = ?"
        cursor.execute(query, (order_id,))
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
        rows = cursor.execute("SELECT * from Orders").fetchall()
        print(rows)
        rows = cursor.execute("SELECT * from OrderDetails").fetchall()
        print(rows)
        rows = cursor.execute("SELECT * from Menu").fetchall()
        print(rows)


if __name__ == '__main__':
    db = RestaurantDB()
    # db.init_user_table()
    # db.init_menu_table()
    # db.init_order_table()
    # db.init_order_details_table()
    # db.add_user("eu", "tu", "0127931", "mai@as.c", "fawonflaiks")

    db.read()
