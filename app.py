from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error


app = Flask(__name__)
DATABASE = "main_database.db"


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


@app.route('/')
def site_home():
    return render_template("home.html")


# @app.route('/menu')
# def site_menu():
#     con = create_connection(DATABASE)
#     query = "SELECT name, description, volume, image, price FROM product"
#     cur = con.cursor()
#     cur.execute(query)
#
#     product_list = cur.fetchall()
#     con.close()
#     return render_template("menu.html", products=product_list)
#
#
@app.route('/contact')
def site_contact():
    return render_template("contact.html")


# @app.route('/login')
# def site_login():
#     return render_template("login.html")
#
#
# @app.route('/signup', methods=['GET', 'POST'])
# def site_signup():
#     print(request.form)
#     fname = request.form.get('fname')
#     lname = request.form.get('lname')
#     email = request.form.get('email')
#     password = request.form.get('password')
#     password2 = request.form.get('password2')
#
#     con = create_connection(DATABASE)
#
#     query = "INSERT INTO customer(id, fname, lname, email, password) VALUES(NULL,?,?,?,?)"
#
#     cur = con.cursor()
#     cur.execute(query, (fname, lname, email, password))
#     con.commit()
#     con.close()
#
#     return render_template("signup.html")


if __name__ == '__main__':
    app.run()
