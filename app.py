# Brands
# brand_id | brand_name 

# Product
# product_id, product_name, product_quantity, product_price, date_updated, and brand_id  foreign key.

from sqlite3 import Date
from sqlalchemy import (create_engine, Column, Integer, 
                        String, ForeignKey, DateTime)
from sqlalchemy import func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import csv
import time



engine = create_engine("sqlite:///inventory.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

#********************************* Model *******************************************************************

class Brand(Base):
    __tablename__ = "brands"

    brand_id = Column(Integer, primary_key=True)
    brand_name = Column(String)
    products = relationship("Product", back_populates="brand")

    def __repr__(self):
        return f"""
    \nbrandId {self.brand_id}\r
    Name = {self.brand_name}\r
    """


class Product(Base):
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.brand_id"))
    product_name = Column(String)
    product_quantity = Column(Integer)
    product_price = Column(Integer)
    date_updated= Column(DateTime)

    brand = relationship("Brand", back_populates="products")

    def __repr__(self):
        return f"""
    \nproduct_id {self.product_id}\r
    brand_id = {self.brand_id }\r
    product_quantity = {self.product_quantity}
    product_price = {self.product_price}
    date_updated= {self.date_updated}
    """

#********************************* celaning Functions *******************************************************************

def clean_date(date_str):   
    split_date = date_str.split('/')
    return  datetime.date(int(split_date[2]),int(split_date[0]),int(split_date[1]) )
    
def clean_price(price_str):
    return int(float(price_str[1:]) *100)

def clean_price2(price_str):
    try:
        price_float = float(price_str)
    except ValueError:
        input('''
            \n**************** Price ERROR ********************
            \rThe price sould be a number without any symbols
            \rEx: 90.99
            \rPress enter tor try again.
            \r****************************************************
            ''')
        return
    else:
        return int(price_float * 100)

def clean_id(id_string, options ):
    try:
        product_id = int(id_string)
    except ValueError:
        input('''
            \n**************** ID ERROR ********************
            \rThe ID sould be a number 
            \rPress enter tor try again.
            \r****************************************************
            ''')
        return 
    else:
        if product_id in options:
            return product_id
        else:
            input(f'''
            \n**************** ID ERROR ********************
            \rOptions: {options}  
            \rPress enter tor try again.
            \r****************************************************
            ''')
            return

def clean_quantity(quantity ):
    try:
        quantity = int(quantity)
    except ValueError:
        input('''
            \n**************** Quantity ERROR ********************
            \rThe Quantity sould be a number 
            \rPress enter tor try again.
            \r****************************************************
            ''')
        return 
    else:
        return quantity

def clean_brand(brand_choise , brand_options):
    if brand_choise in brand_options:
        brand = session.query(Brand).filter(Brand.brand_name == brand_choise).first()
        return brand.brand_id
    else:
        input(f'''
        \n**************** Brand ERROR ********************
        \rOptions: {brand_options}  
        \rPress enter tor try again.
        \r****************************************************
        ''')
        return

# ********************************** load form CSV **************************************************

def add_brands():
    with open('store-inventory/brands.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            if row[0] != 'brand_name':
                new_brand = Brand(brand_name =row[0])
                session.add(new_brand)
        session.commit()        


def add_inventory():
    with open('store-inventory/inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            #print(row)
                if row[3] != 'date_updated':
                    date = clean_date(row[3])
                    name = row[0]
                    price = clean_price(row[1])
                    quantity = int(row[2])
                    brand = session.query(Brand).filter(Brand.brand_name == row[4]).first()
                    brand = brand.brand_id
                    #print(brand)
                    new_product = Product(product_name=name,brand_id= brand,product_quantity= quantity, product_price= price, date_updated=date)
                    session.add(new_product)
        session.commit()

# ****************************************** Backup to CSV *************************************

def backup_brands():
        f = open('brands_backup.csv', 'w',newline="")
        out = csv.writer(f)
        out.writerow(['brand_id', 'brand_name'])
        for item in session.query(Brand).all():
                out.writerow([item.brand_id, item.brand_name])
        f.close()


def backup_products():
        f = open('inventory_backup.csv', 'w',newline="")
        out = csv.writer(f)
        out.writerow(['product_id', 'brand_id', 'product_name', 'product_quantity', 'product_price', 'date_updated'])
        for item in session.query(Product).all():
                out.writerow([item.product_id, item.brand_id, item.product_name, item.product_quantity, item.product_price, item.date_updated])
        f.close()

# ****************************************** menu and app *************************************

def menu():
    while True:
        print('''
                \n Products Handler:
                \rV: View product:
                \rN: Add product:
                \rA) Produt Analysis
                \rB) Make a Backup
                \rE: Exit ''')
        choice = input('What would you like to do? ')

        if choice in ['V','N','A','B','E']:
            print(choice)
            return choice
        else:
            input('''
                \rPlease choose one of the options above
                \rA V, N, A, B, E.
                \rPress enter to try again.
                ''')


def app():
    app_running = True

    while app_running:
        choice = menu()
        if choice == 'V':
            # search
            id_options = []
            for product in session.query(Product):
                id_options.append(product.product_id)
            id_error = True
            while id_error:                  
                id_choise = input(f'''
                    \nId Options: {id_options} 
                    \rprodct id:  ''')
                id_choise = clean_id(id_choise, id_options)
                if type(id_choise ) == int:
                    id_error = False
            the_product = session.query(Product).filter(Product.product_id==id_choise).first()
            print(f'''
                    \n{the_product.product_name} by the brand {the_product.brand_id}
                    \rQuantity: {the_product.product_quantity}
                    \rPrice: ${the_product.product_price/100}
                    \rUpdated: {the_product.date_updated}
            ''')
            
        elif choice == 'N':
            # add book
            name = input('Product Name: ')
             # search
            brand_options = []
            for brand in session.query(Brand):
                
                brand_options.append(brand.brand_name)
            brand_error = True
            while brand_error:                  
                brand_choise = input(f'''
                    \nBrand Options: {brand_options} 
                    \rInput Brand Name:  ''')
                brand_choise  = clean_brand(brand_choise , brand_options)
                if type(brand_choise ) == int:
                    brand_error = False
            
            quantaty_error = True
            while quantaty_error :
                quantity = input('Input Quantity: ')
                quantity = clean_quantity(quantity )

                if type(quantity) == int:
                    quantaty_error = False

            price_error = True
            while price_error:
                price = input('Price: (Ex: 29.99) ')
                price = clean_price2(price)
                if type(price) == int:
                    price_error = False
            new_product = Product(product_name=name,brand_id= brand_choise,product_quantity= quantity, product_price= price, date_updated=datetime.date.today())
            session.add(new_product)
            session.commit()
            print('New product was added')
            time.sleep(1.5)

        elif choice == 'A':
            # analysis
            cheap_book = session.query(Product).order_by(Product.product_price).first()
            expense_book = session.query(Product).order_by(Product.product_price.desc()).first()
            brand = session.query(Product.brand_id, func.count(Product.brand_id)).group_by(Product.brand_id).order_by(func.count(Product.brand_id).desc()).first()
            print(brand['brand_id'])
            brand_name = session.query(Brand).filter(Brand.brand_id == brand['brand_id']).first()
            print(f'''
                    \n*********** Product ANALYSIS **************
                    \rMost expensive Product: {expense_book.product_name} {expense_book.product_price/100} 
                    \rLeast expensive Product: {cheap_book.product_name} {cheap_book.product_price/100}
                    \rBrand with the most Nr. of Products is: {brand_name.brand_name}''')
            input('\nPress enter to return to the main menu.')

        elif choice == 'B':
            backup_brands()
            backup_products() 

        else:
            print('GOODBYE')
            app_running = False

#***********************************************************************************************************

if __name__ == "__main__":
    Base.metadata.create_all(engine)

    add_brands()
    add_inventory()
    app()
    

    
   