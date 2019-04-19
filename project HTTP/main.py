from flask import Flask, render_template, request, url_for
import os
import json
import sqlite3
from flask import session, redirect

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

global products
products = ['смартфон', 'системный блок', 'клавиатура', 'мышь', 'монитор']

class data_base:
    def __init__(self):
        connection = sqlite3.connect('users.db', check_same_thread=False)
        self.connection = connection 
        
    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (login VARCHAR(100),
                             password VARCHAR(100)
                            )
                       ''')
        cursor.close()
        self.connection.commit()
    
    def get_connection(self):
        return self.connection
    
    def add_user(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users
                        (login, password) 
                        VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()     
    
    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)    
  
    
class trash:
    def __init__(self):
        connection = sqlite3.connect('trash.db', check_same_thread=False)
        self.connection = connection 
        
    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS trash
                            (login VARCHAR(100),
                             content VARCHAR(100)
                            )
                       ''')
        cursor.close()
        self.connection.commit()
    
    def get_connection(self):
        return self.connection
    
    def add_thing(self, user_name, content):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO trash
                        (login, content) 
                        VALUES (?,?)''', (user_name, content))
        cursor.close()
        self.connection.commit()     
        
    def get_trash(self, login):
        cursor = self.connection.cursor()
        cursor.execute('''SELECT * FROM trash WHERE login = ?''', (login,))
        row = cursor.fetchall()
        return row    
    
    def delete(self, cont):   #передается название товара
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM trash WHERE login = ? and content = ?''', (session['username'], cont))
        cursor.close()
        self.connection.commit()    
        
class products_db:
    def __init__(self):
        connection = sqlite3.connect('products.db', check_same_thread=False)
        self.connection = connection 
        
    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS products
                          (name VARCHAR(100))
                       ''')
        cursor.close()
        self.connection.commit()  
        
    def get_connection(self):
        return self.connection    
    
    def add_thing(self, content):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO products
                        (name)
                        VALUES (?)''', (content,))
        cursor.close()
        self.connection.commit() 
        
    def get_products(self):
        cursor = self.connection.cursor()
        cursor.execute('''SELECT name FROM products''')
        row = cursor.fetchall()
        print(row)
        return row     
    
    def delete(self, name):   #передается название товара
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM products WHERE name = ?''', (name,))
        cursor.close()
        self.connection.commit()    

base = data_base()
base.init_table()

trash = trash()
trash.init_table()

products_db = products_db()
products_db.init_table()
    

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    
    elif request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        base.add_user(login, password)
        print(login)
        print(password)
        return redirect("/login")
    
@app.route('/logout')
def logout():
    session.pop('username',0)
    session.pop('user_id',0)
    return redirect('/login')       

@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        user_name = request.form['login']
        password = request.form['password']
        user_model = base.get_connection()
        print(user_name)
        print(password)
        exists = base.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            return redirect("/main_page")
        
        
@app.route('/main_page', methods=['POST', 'GET'])
def main_page():
    if 'username' not in session:
            return redirect('/login')    
    if request.method == 'GET':
        return render_template('main_page.html')
    
@app.route('/assort')
def assort():
    if 'username' not in session:
            return redirect('/login')    
    row = products_db.get_products()
    pr = []
    string = ''
    
    for i in row:
        for j in range(len(i)):
            if i[j] != ',' or i[j] != "'":
                string+= i[j]
            pr.append(string)
            string = ''
    print(pr)
    return render_template('assort.html', pr = pr)
    
@app.route('/trash_add/<product>', methods=['GET'])
def trash_add(product):  
    if request.method == 'GET':
        login = session['username']
        row = products_db.get_products()
        string = ''
        pr = []
        for i in row:
            for j in range(len(i)):
                if i[j] != ',' or i[j] != "'":
                    string+= i[j]
            pr.append(string)
            string = ''
        for i in pr:
            if i in product:
                content = i
                break
        trash.add_thing(login, content)
        return redirect("/assort")
    
@app.route('/my_trash', methods=['GET', 'POST'])
def my_trash():
    if request.method == 'GET':
        row = trash.get_trash(session['username'])
        c_row = []
        for i in row:
            c_row.append(i[1])
        row = []
        for i in c_row:
            incomes = c_row.count(i)
            string = 'x' + str(incomes) + ' ' + str(i)
            row.append(string)
            string = ''
            
        final = []
        global sd_c_row
        sd_c_row = []
        
        for i in c_row:
            if i in sd_c_row:
                continue
            sd_c_row.append(i)
    
        for i in row:
            if i in final:
                continue
            final.append(i)
        return render_template('my_trash.html', rows = final)
        
    
@app.route('/del_trash/<name>')
def del_trash(name):
    thing = ''
    for i in sd_c_row:
        if i in name:
            thing = i
            break
    print(thing)
    cd_c_row = []
    trash.delete(thing)
    return redirect("/my_trash")

@app.route('/admin_addition', methods=['GET', 'POST'])
def admin_addition():
    if session['username'] == '1':
        if request.method == 'GET':
            row = products_db.get_products()
            pr = []
            string = ''
            for i in row:
                for j in range(len(i)):
                    if i[j] != ',' or i[j] != "'":
                        string+= i[j]
                    pr.append(string)
                    string = ''    
            print('pr:', pr)
            return render_template('admin_addition.html', pr = pr)
        elif request.method == 'POST':
            product = request.form['name']
            products_db.add_thing(product)
            return(redirect("/admin_addition"))
    else:
        return redirect("/main_page")
    
@app.route('/del_prod/<product>')    
def del_prod(product):
    print(product)
    row = products_db.get_products()
    print(row)
        
    pr = []
    name = ''
    string = ''
    for i in row:
        for j in range(len(i)):
            if i[j] != ',' or i[j] != "'":
                string+= i[j]
        pr.append(string)
        string = ''        
    for i in pr:
        if i in product:
            name = i
            break
    print('name:', name)
    products_db.delete(name)
    return redirect("/admin_addition")
    
app.run(port = 8080, host = '127.0.0.1')