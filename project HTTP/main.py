from flask import Flask, render_template, request, url_for
import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

class base_users:
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
    
    def add_user(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users
                        (login, password) 
                        VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()     
    
    def check_log(self):
        user_name = form.username.data
        password = form.password.data
        user_model = UserModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
        return redirect("/index")        

base = base_users()
base.init_table()

@app.route('/')
@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    
    elif request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        base.add_user(login, password)
        return redirect("/login")
    

    
app.run(port = 8080, host = '127.0.0.1')