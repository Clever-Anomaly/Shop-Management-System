import mysql.connector
from prettytable import PrettyTable
import random

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Saurav@2022464',
    database='store'
)


try:
    if mydb.is_connected():
        

        cursor = mydb.cursor()


        while True:
            print('-------------------------------------------------------')
            print('Welcome to the Store')

            print('1. Login')
            print('2. Sign Up')
            print('3. Admin Login')
            print('4. Exit')
            print('-------------------------------------------------------')
            ch = int(input('Enter your choice: '))
            print('-------------------------------------------------------')
            if ch == 4:
                print('Thank you for visiting the store')
                print('-------------------------------------------------------')
                break
            elif ch == 1:
                first_name = input('Enter your first name: ').strip()
                last_name = input('Enter your last name: ').strip()
                password = input('Enter your mobile no as password: ').strip()
                cursor.execute('SELECT * FROM customer WHERE first_name = %s AND last_name = %s AND mobile_no = %s', (first_name, last_name, password))
                if cursor.fetchone() is not None:
                    print('Login Successful')
                    print('-------------------------------------------------------')
                    cursor.execute('SELECT Id FROM customer WHERE first_name = %s AND last_name = %s AND mobile_no = %s', (first_name, last_name, password))
                    cust_id = cursor.fetchone()[0]
                    cursor.execute('SELECT ID FROM cart WHERE customer_id = %s', (cust_id,))
                    cart_id = cursor.fetchone()[0]
                    cursor.execute('SELECT Store_Id FROM Customer WHERE Id = %s', (cust_id,))
                    store_id = cursor.fetchone()[0]

                    print('Welcome', first_name, last_name)
                    while True:
                        print('-------------------------------------------------------')
                        print('1. View Cart')
                        print('2. Browse all Products')
                        print('3. Browse Products by Category')
                        print('4. View Orders')
                        print('5. Logout')
                        print('-------------------------------------------------------')
                        choice = int(input('Enter your choice: '))
                        print('-------------------------------------------------------')
                        if choice == 5:
                            print('Logged out successfully')
                            print('-------------------------------------------------------')
                            break
                        elif choice == 1:
                            cursor.execute('SELECT p.Id, p.Name, p.Brand, p.Cost, ci.No_of_Items FROM Product p JOIN Cart_Items ci ON p.Id = ci.Product_Id WHERE ci.Cart_Id = %s',(cart_id,))
                            cart_items = cursor.fetchall()
                            product_ids = []
                            quantities = []
                            cursor.execute('SELECT Total_Cost, Total_Items FROM Cart WHERE Id = %s', (cart_id,))
                            total_cost, total_items = cursor.fetchone()
                            table = PrettyTable()
                            table.field_names = ["ID", "Name", "Brand", "Cost", "Quantity"]
                            for item in cart_items:
                                table.add_row(item)
                                product_ids.append(item[0])
                                quantities.append(item[4])
                            table.add_row(["", "", "", "", ""])
                            table.add_row(["Total:", "", "", total_cost, total_items])
                            print(table)
                            print('-------------------------------------------------------')
                            while True:
                                print('1. Remove from Cart')
                                print('2. Place Order')
                                print('3. Go Back')
                                print('-------------------------------------------------------')
                                c = int(input('Enter your choice: '))
                                print('-------------------------------------------------------')
                                if c == 3:
                                    break
                                elif c == 1:
                                    if total_items == 0:
                                        print('Cart is Empty, Please add products to cart to remove products')
                                        print('-------------------------------------------------------')
                                        continue
                                    product_id = int(input('Enter the product id: '))
                                    if product_id not in product_ids:
                                        print('Invalid Product ID, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    cursor.execute('SELECT No_of_Items FROM Cart_Items WHERE Cart_Id = %s AND Product_Id = %s', (cart_id, product_id))
                                    quantity = cursor.fetchone()[0]
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        cursor.execute('DELETE FROM Cart_Items WHERE Cart_Id = %s AND Product_Id = %s', (cart_id, product_id))
                                        cursor.execute('SELECT Cost FROM Product WHERE Id = %s', (product_id,))
                                        product_cost = cursor.fetchone()[0]
                                        new_total_cost = total_cost - (quantity * product_cost)
                                        new_total_items = total_items - quantity
                                        cursor.execute('UPDATE Cart SET Total_Cost = %s, Total_Items = %s WHERE Id = %s', (new_total_cost, new_total_items, cart_id))
                                        mydb.commit()
                                        print('Product removed from cart successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:',e)
                                        mydb.rollback()
                                        print('Rollback occured, coudn\'t remove items from cart')
                                        print('-------------------------------------------------------')
                                elif c == 2:
                                    if total_items == 0:
                                        print('Cart is Empty, Please add products to cart to place order')
                                        print('-------------------------------------------------------')
                                        continue

                                    payment_method = input('Enter the payment method: ').strip()
                                    cursor.execute('SELECT Delivery_Partner_Id FROM Works_for WHERE Store_Id = %s', (store_id,))
                                    delivery_partner_id = cursor.fetchall()
                                    no_of_available_delivery_partners = len(delivery_partner_id)
                                    assigned_delivery_partner_id = delivery_partner_id[random.randint(0, no_of_available_delivery_partners - 1)][0]
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        for i in range(len(product_ids)):
                                            cursor.execute('SELECT Stock FROM Product WHERE Id = %s', (product_ids[i],))
                                            stock = cursor.fetchone()[0]
                                            if quantities[i] > stock:
                                                raise Exception('Insufficient Stock')
                                            cursor.execute('UPDATE Product SET Stock = Stock - %s WHERE Id = %s', (quantities[i], product_ids[i]))
                                        cursor.execute('INSERT INTO Orders(Cart_Id,Delivery_Partner_Id,Payment_method) VALUES(%s,%s,%s)', (cart_id, assigned_delivery_partner_id, payment_method))
                                        mydb.commit()
                                        print('Order Placed Successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:', e)
                                        mydb.rollback()
                                        print('Rollback occurred, couldn\'t place order')
                                        print('-------------------------------------------------------')
                            
                                    
                        elif choice == 2:
                            cursor.execute('SELECT p.Id,p.Name,c.Name,p.Brand,p.Cost,p.Stock FROM Product p join Category c on p.Category_Id = c.Id')
                            products = cursor.fetchall()
                            product_ids = []
                            table = PrettyTable()
                            table.field_names = ["ID", "Name", "Category", "Brand", "Cost", "Stock"]
                            for product in products:
                                table.add_row(product)
                                product_ids.append(product[0])
                            print(table)
                            print('-------------------------------------------------------')
                            while True:
                                print('1. Add to Cart')
                                print('2. Go Back')
                                print('-------------------------------------------------------')
                                c = int(input('Enter your choice: '))
                                print('-------------------------------------------------------')
                                if c == 2:
                                    break
                                elif c == 1:
                                    product_id = int(input('Enter the product id: '))
                                    if product_id not in product_ids:
                                        print('Invalid Product ID, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    cursor.execute('SELECT Stock FROM Product WHERE Id = %s', (product_id,))
                                    stock = cursor.fetchone()[0]
                                    quantity = int(input('Enter the quantity: '))
                                    print('-------------------------------------------------------')
                                    if quantity > stock:
                                        print('Insufficient Stock, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        cursor.execute('SELECT * FROM Cart_Items WHERE Cart_Id = %s AND Product_Id = %s', (cart_id, product_id))
                                        if cursor.fetchone() is not None:
                                            cursor.execute('UPDATE Cart_Items SET No_of_Items = No_of_Items + %s WHERE Cart_Id = %s AND Product_Id = %s', (quantity, cart_id, product_id))
                                        else:
                                            cursor.execute('INSERT INTO Cart_Items(Cart_Id, Product_Id, No_of_Items) VALUES(%s, %s, %s)', (cart_id, product_id, quantity))
                                        mydb.commit()
                                        print('Product added to cart successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:', e)
                                        mydb.rollback()
                                        print('Rollback occurred, couldn\'t add product to cart')
                                        print('-------------------------------------------------------')
                                else:
                                    print('Invalid Choice, Please try again')
                                    print('-------------------------------------------------------')

                        elif choice == 3:  
                            cursor.execute('SELECT Id,Name FROM Category')
                            categories = cursor.fetchall()
                            category_dict = {}
                            table = PrettyTable()
                            table.field_names = ["ID", "Category"]
                            for category in categories:
                                table.add_row(category)
                                category_dict[category[0]] = category[1]
                            while True:
                                print(table)
                                print('-------------------------------------------------------')
                                print(table)
                                print('-------------------------------------------------------')
                                print('1. Select Category')
                                print('2. Go Back')
                                print('-------------------------------------------------------')
                                c = int(input('Enter your choice: '))
                                print('-------------------------------------------------------')
                                if c == 2:
                                    break
                                elif c == 1:
                                    category_id = int(input('Enter the category id: '))
                                    print('-------------------------------------------------------')
                                    if category_id not in category_dict:
                                        print('Invalid Category ID, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    cursor.execute('SELECT p.Id,p.Name,p.Brand,p.Cost,p.Stock FROM Product p join Category c on p.Category_Id = c.Id WHERE p.Category_Id = %s', (category_id,))
                                    products = cursor.fetchall()
                                    product_ids = []
                                    table = PrettyTable()
                                    table.field_names = ["ID", "Name", "Brand", "Cost", "Stock"]
                                    for product in products:
                                        table.add_row(product)
                                        product_ids.append(product[0])
                                    print(table)
                                    print('-------------------------------------------------------')
                                    while True:
                                        print('1. Add to Cart')
                                        print('2. Go Back')
                                        print('-------------------------------------------------------')
                                        op = int(input('Enter your choice: '))
                                        print('-------------------------------------------------------')
                                        if op == 2:
                                            break
                                        elif op == 1:
                                            product_id = int(input('Enter the product id: '))
                                            if product_id not in product_ids:
                                                print('Invalid Product ID, Please try again')
                                                print('-------------------------------------------------------')
                                                continue
                                            cursor.execute('SELECT Stock FROM Product WHERE Id = %s', (product_id,))
                                            stock = cursor.fetchone()[0]
                                            quantity = int(input('Enter the quantity: '))
                                            print('-------------------------------------------------------')
                                            if quantity > stock:
                                                print('Insufficient Stock, Please try again')
                                                print('-------------------------------------------------------')
                                                continue
                                            try:
                                                cursor.execute('START TRANSACTION')
                                                cursor.execute('SELECT * FROM Cart_Items WHERE Cart_Id = %s AND Product_Id = %s', (cart_id, product_id))
                                                if cursor.fetchone() is not None:
                                                    cursor.execute('UPDATE Cart_Items SET No_of_Items = No_of_Items + %s WHERE Cart_Id = %s AND Product_Id = %s', (quantity, cart_id, product_id))
                                                else:
                                                    cursor.execute('INSERT INTO Cart_Items(Cart_Id, Product_Id, No_of_Items) VALUES(%s, %s, %s)', (cart_id, product_id, quantity))
                                                mydb.commit()
                                                cursor.execute('UPDATE Product SET Stock = Stock - %s WHERE Id = %s', (quantity, product_id))
                                                mydb.commit()
                                                print('Product added to cart successfully')
                                                print('-------------------------------------------------------')
                                            except Exception as e:
                                                print('Error:', e)
                                                mydb.rollback()
                                                print('Rollback occurred, couldn\'t add product to cart')
                                                print('-------------------------------------------------------')
                                        else:
                                            print('Invalid Choice, Please try again')
                                            print('-------------------------------------------------------')
                                else:
                                    print('Invalid Choice, Please try again')
                                    print('-------------------------------------------------------')
                                                    

                        elif choice == 4:
                            cursor.execute('SELECT o.Id,CONCAT(d.First_name,\' \',d.Last_name) as name,d.Mobile_no,o.Order_Date,o.Total_Cost,o.Payment_method,o.orderstatus FROM Orders o JOIN Delivery_partner d WHERE o.Delivery_Partner_Id = d.Id and o.Customer_Id = %s', (cust_id,))
                            orders = cursor.fetchall()
                            if len(orders) == 0:
                                print('No Orders Found')
                                print('-------------------------------------------------------')
                                continue
                            table = PrettyTable()
                            table.field_names = ["ID", "Delivery Partner", "Mobile No", "Order Date", "Total Cost", "Payment Method", "Order Status"]
                            order_ids = []
                            for order in orders:
                                table.add_row(order)
                                order_ids.append(order[0])
                            print(table)
                            while True:
                                print('-------------------------------------------------------')
                                print('1. View Order Details')
                                print('2. Go Back')
                                print('-------------------------------------------------------')
                                c = int(input('Enter your choice: '))
                                print('-------------------------------------------------------')
                                if c == 2:
                                    break
                                elif c == 1:
                                    order_id = int(input('Enter the order id: '))
                                    print('-------------------------------------------------------')
                                    if order_id not in order_ids:
                                        print('Invalid Order ID, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    cursor.execute('SELECT p.Id, p.Name, p.Brand, p.Cost, oi.No_of_Items FROM Product p JOIN Order_Items oi ON p.Id = oi.Product_Id WHERE oi.Order_Id = %s',(order_id,))
                                    order_items = cursor.fetchall()
                                    cursor.execute('SELECT Total_Cost FROM Orders WHERE Id = %s', (order_id,))
                                    total_cost = cursor.fetchone()[0]
                                    total_items = 0
                                    table = PrettyTable()
                                    table.field_names = ["ID", "Name", "Brand", "Cost", "Quantity"]
                                    for item in order_items:
                                        table.add_row(item)
                                        total_items += item[4]
                                    table.add_row(["", "", "", "", ""])
                                    table.add_row(["Total:", "", "", total_cost, total_items])
                                    print(table)
                                    print('-------------------------------------------------------')
                                else:
                                    print('Invalid Choice, Please try again')
                                    print('-------------------------------------------------------')

                        else:
                            print('Invalid Choice, Please try again')
                            print('-------------------------------------------------------')
                else:
                    print('Invalid Username or Password')
                    print('-------------------------------------------------------')
            elif ch == 2:
                first_name = input('Enter your first name: ').strip()
                last_name = input('Enter your last name: ').strip()
                mobile_no = input('Enter your mobile no: ').strip()
                age = int(input('Enter your age: '))
                dob = input('Enter your date of birth(\'yyyy-mm-dd\'): ').strip()
                state = input('Enter your state: ').strip()
                city = input('Enter your city: ').strip()
                pincode = int(input('Enter your pincode: '))    
                house_no = input('Enter your house no: ').strip()
                print('-------------------------------------------------------')
                try:
                    cursor.execute('START TRANSACTION')
                    cursor.execute('INSERT INTO customer(first_name, last_name, mobile_no, age, dob, state, city, pincode, house_no) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)', (first_name, last_name, mobile_no, age, dob, state, city, pincode, house_no))
                    mydb.commit()
                    print('Sign Up Successful')
                    print('-------------------------------------------------------')
                except:
                    mydb.rollback()
                    print('Sign Up Failed')
                    print('-------------------------------------------------------')
            elif ch == 3:
                username = input('Enter your username: ').strip()
                password = input('Enter your password: ').strip()
                cursor.execute('SELECT * FROM Administrator WHERE username = %s AND pass = %s', (username, password))
                if cursor.fetchone() is not None:
                    print('Login Successful')
                    print('-------------------------------------------------------')
                    while True:
                        print('1. View all Products')
                        print('2. View all Customers')
                        print('3. View all Delivery Partners')
                        print('4. Logout')
                        print('-------------------------------------------------------')
                        choice = int(input('Enter your choice: '))
                        print('-------------------------------------------------------')
                        if choice == 4:
                            print('Logged out successfully')
                            print('-------------------------------------------------------')
                            break
                        elif choice == 1:
                            cursor.execute('SELECT * FROM Product')
                            products = cursor.fetchall()
                            table = PrettyTable()
                            table.field_names = ["ID","Category Id","Name", "Brand", "Cost", "Stock"]
                            for product in products:
                                table.add_row(product)
                            print(table)
                            print('-------------------------------------------------------')
                            while True:
                                print('1. Add Product')
                                print('2. Update Product')
                                print('3. Delete Product')
                                print('4. Go Back')
                                print('-------------------------------------------------------')
                                c = int(input('Enter your choice: '))
                                print('-------------------------------------------------------')
                                if c == 4:
                                    break
                                elif c == 1:
                                    category_id = int(input('Enter the category id: '))
                                    name = input('Enter the name: ').strip()
                                    brand = input('Enter the brand: ').strip()
                                    cost = float(input('Enter the cost: '))
                                    stock = int(input('Enter the stock: '))
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        cursor.execute('INSERT INTO Product(Category_Id, Name, Brand, Cost, Stock) VALUES(%s, %s, %s, %s, %s)', (category_id, name, brand, cost, stock))
                                        mydb.commit()
                                        print('Product added successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:', e)
                                        mydb.rollback()
                                        print('Rollback occurred, couldn\'t add product')
                                        print('-------------------------------------------------------')
                                elif c == 2:
                                    product_id = int(input('Enter the product id: '))
                                    cursor.execute('SELECT * FROM Product WHERE Id = %s', (product_id,))
                                    if cursor.fetchone() is None:
                                        print('Invalid Product ID, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    category_id = int(input('Enter the category id: '))
                                    name = input('Enter the name: ').strip()
                                    brand = input('Enter the brand: ').strip()
                                    cost = float(input('Enter the cost: '))
                                    stock = int(input('Enter the stock: '))
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        cursor.execute('UPDATE Product SET Category_Id = %s, Name = %s, Brand = %s, Cost = %s, Stock = %s WHERE Id = %s', (category_id, name, brand, cost, stock, product_id))
                                        mydb.commit()
                                        print('Product updated successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:', e)
                                        mydb.rollback()
                                        print('Rollback occurred, couldn\'t update product')
                                        print('-------------------------------------------------------')
                                elif c == 3:
                                    product_id = int(input('Enter the product id: '))
                                    cursor.execute('SELECT * FROM Product WHERE Id = %s', (product_id,))
                                    if cursor.fetchone() is None:
                                        print('Invalid Product ID, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        cursor.execute('DELETE FROM Product WHERE Id = %s', (product_id,))
                                        mydb.commit()
                                        print('Product deleted successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:', e)
                                        mydb.rollback()
                                        print('Rollback occurred, couldn\'t delete product')
                                        print('-------------------------------------------------------')
                                else:
                                    print('Invalid Choice, Please try again')
                                    print('-------------------------------------------------------')

                        elif choice == 2:
                            cursor.execute('SELECT * FROM Customer')
                            customers = cursor.fetchall()
                            table = PrettyTable()
                            table.field_names = ["ID", "First Name", "Last Name", "Mobile No", "Age", "DOB", "State", "City", "Pincode", "House No"]
                            for customer in customers:
                                table.add_row(customer)
                            print(table)
                            print('-------------------------------------------------------')
                            while True:
                                print('1. Update Customer')
                                print('2. Delete Customer')
                                print('3. Go Back')
                                print('-------------------------------------------------------')
                                c = int(input('Enter your choice: '))
                                print('-------------------------------------------------------')
                                if c == 3:
                                    break
                                elif c == 1:
                                    customer_id = int(input('Enter the customer id: '))
                                    cursor.execute('SELECT * FROM Customer WHERE Id = %s', (customer_id,))
                                    if cursor.fetchone() is None:
                                        print('Invalid Customer ID, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    first_name = input('Enter the first name: ').strip()
                                    last_name = input('Enter the last name: ').strip()
                                    mobile_no = input('Enter the mobile no: ').strip()
                                    age = int(input('Enter the age: '))
                                    dob = input('Enter the date of birth(\'yyyy-mm-dd\'): ').strip()
                                    state = input('Enter the state: ').strip()
                                    city = input('Enter the city: ').strip()
                                    pincode = int(input('Enter the pincode: '))
                                    house_no = input('Enter the house no: ').strip()
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        cursor.execute('UPDATE Customer SET first_name = %s, last_name = %s, mobile_no = %s, age = %s, dob = %s, state = %s, city = %s, pincode = %s, house_no = %s WHERE Id = %s', (first_name, last_name, mobile_no, age, dob, state, city, pincode, house_no, customer_id))
                                        mydb.commit()
                                        print('Customer updated successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:', e)
                                        mydb.rollback()
                                        print('Rollback occurred, couldn\'t update customer')
                                        print('-------------------------------------------------------')
                                elif c == 2:
                                    customer_id = int(input('Enter the customer id: '))
                                    cursor.execute('SELECT * FROM Customer WHERE Id = %s', (customer_id,))
                                    if cursor.fetchone() is None:
                                        print('Invalid Customer ID, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        cursor.execute('DELETE FROM Customer WHERE Id = %s', (customer_id,))
                                        mydb.commit()
                                        print('Customer deleted successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:', e)
                                        mydb.rollback()
                                        print('Rollback occurred, couldn\'t delete customer')
                                        print('-------------------------------------------------------')
                                else:
                                    print('Invalid Choice, Please try again')
                                    print('-------------------------------------------------------')


                        elif choice == 3:
                            cursor.execute('SELECT * FROM Delivery_partner')
                            delivery_partners = cursor.fetchall()
                            table = PrettyTable()
                            table.field_names = ["ID", "First Name", "Last Name", "Mobile No"]
                            for delivery_partner in delivery_partners:
                                table.add_row(delivery_partner)
                            print(table)
                            print('-------------------------------------------------------')
                            while True:
                                print('1. Add Delivery Partner')
                                print('2. Update Delivery Partner')
                                print('3. Delete Delivery Partner')
                                print('4. Go Back')
                                print('-------------------------------------------------------')
                                c = int(input('Enter your choice: '))
                                print('-------------------------------------------------------')
                                if c == 4:
                                    break
                                elif c == 1:
                                    first_name = input('Enter the first name: ').strip()
                                    last_name = input('Enter the last name: ').strip()
                                    mobile_no = input('Enter the mobile no: ').strip()
                                    store_ids = []
                                    cursor.execute('SELECT Id FROM Store')
                                    stores = cursor.fetchall()
                                    for store in stores:
                                        store_ids.append(store[0])
                                    assigned_store_id = store_ids[random.randint(0, len(store_ids) - 1)]
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        cursor.execute('INSERT INTO Delivery_partner(Store_Id,First_name, Last_name, Mobile_no) VALUES(%s,%s, %s, %s)', (assigned_store_id,first_name, last_name, mobile_no))
                                        mydb.commit()
                                        print('Delivery Partner added successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:', e)
                                        mydb.rollback()
                                        print('Rollback occurred, couldn\'t add delivery partner')
                                        print('-------------------------------------------------------')
                                elif c == 2:
                                    delivery_partner_id = int(input('Enter the delivery partner id: '))
                                    cursor.execute('SELECT * FROM Delivery_partner WHERE Id = %s', (delivery_partner_id,))
                                    if cursor.fetchone() is None:
                                        print('Invalid Delivery Partner ID, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    first_name = input('Enter the first name: ').strip()
                                    last_name = input('Enter the last name: ').strip()
                                    mobile_no = input('Enter the mobile no: ').strip()
                                    store_id = int(input('Enter the store id: '))
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        cursor.execute('UPDATE Delivery_partner SET Store_Id = %s, First_name = %s, Last_name = %s, Mobile_no = %s WHERE Id = %s', (assigned_store_id, first_name, last_name, mobile_no, delivery_partner_id))
                                        mydb.commit()
                                        print('Delivery Partner updated successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:', e)
                                        mydb.rollback()
                                        print('Rollback occurred, couldn\'t update delivery partner')
                                        print('-------------------------------------------------------')
                                elif c == 3:
                                    delivery_partner_id = int(input('Enter the delivery partner id: '))
                                    cursor.execute('SELECT * FROM Delivery_partner WHERE Id = %s', (delivery_partner_id,))
                                    if cursor.fetchone() is None:
                                        print('Invalid Delivery Partner ID, Please try again')
                                        print('-------------------------------------------------------')
                                        continue
                                    try:
                                        cursor.execute('START TRANSACTION')
                                        cursor.execute('DELETE FROM Delivery_partner WHERE Id = %s', (delivery_partner_id,))
                                        mydb.commit()
                                        print('Delivery Partner deleted successfully')
                                        print('-------------------------------------------------------')
                                    except Exception as e:
                                        print('Error:', e)
                                        mydb.rollback()
                                        print('Rollback occurred, couldn\'t delete delivery partner')
                                        print('-------------------------------------------------------')

            else:
                print('Invalid Choice, Please try again')
                print('-------------------------------------------------------')

        cursor.close()
    else:
        print('Error in Connection')
        print('-------------------------------------------------------')
except Exception as e:
    print('Error in Connection: ',e.with_traceback())
    print('-------------------------------------------------------')

finally:
    mydb.close()