from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error


app = Flask(__name__)
DATABASE = "app_assessment_daniel.sqlite"


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


@app.route('/contact')
def site_contact():
    return render_template("contact.html")


@app.route('/login')
def site_login():
    return render_template("login.html")


@app.route('/signup', methods=['GET', 'POST'])
def site_signup():
    print(request.form)
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    type = request.form.get('type')

    con = create_connection(DATABASE)

    query = "INSERT INTO people(id, fname, lname, email, password,type) VALUES(NULL,?,?,?,?,?)"

    cur = con.cursor()
    cur.execute(query, (fname, lname, email, password, type))
    con.commit()
    con.close()

    return render_template("signup.html")


if __name__ == '__main__':
    app.run()
