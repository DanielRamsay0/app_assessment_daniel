from datetime import date
import time

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


@app.route('/dictionary')
def site_dictionary():
    return render_template("dictionary.html")


@app.route('/contribute', methods=['GET', 'POST'])
def site_contribute():
    print(request.form)
    category = request.form.get('category')
    english_name = request.form.get('english_name')
    maori_name = request.form.get('maori_name')
    minimum_year_group = request.form.get('minimum_year_group')
    created_at = date.today()

    con = create_connection(DATABASE)

    query = "INSERT INTO maori_words(id, category, english_name, maori_name, created_at, minimum_year_group) VALUES(NULL,?,?,?,?,?)"

    cur = con.cursor()
    cur.execute(query, (category, english_name, maori_name, created_at, minimum_year_group))
    con.commit()
    con.close()

    return render_template("contribute.html")


@app.route('/login', methods=["GET", "POST"])
def site_login():
    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = """SELECT id, fname, password FROM people WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        cur.close()
        try:
            userid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+Invalid+Or+Password+Incorrect")

        if db_password != password:
            return redirect("/login?error=Email+Invalid+Or+Password+Incorrect")

        session['email'] = email
        session['userid'] = userid
        session['firstname'] = firstname
        print(session)
        return redirect('/')
    return render_template('login.html', logged_in=is_logged_in())


@app.route('/signup', methods=['GET', 'POST'])
def site_signup():
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        type = request.form.get('type')

        if password != password2:
            return redirect('/signup?error=Passwords+Do+Not+Match')

        if len(password) < 6:
            return redirect('/signup?error=Password+Must+Be+At+Least+6+Characters')

        if len(fname) < 6 or len(lname) < 6:
            return redirect('/signup?error=Names+Must+Be+At+Least+2+Characters')

        con = create_connection(DATABASE)

        query = "INSERT INTO people(id, fname, lname, email, password, type) VALUES(NULL,?,?,?,?,?)"

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, password, type))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+s+Already+Being+Used')

        con.commit()
        con.close()
        return redirect('/login')

    return render_template("signup.html")


if __name__ == '__main__':
    app.run()

# hihi