# Importing packages needed for the password hashing, website and database including its timestamps
from datetime import date
from flask import Flask, render_template, request, session, redirect
from flask_bcrypt import Bcrypt
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "3P*7iW>d},LHDw<3~(bg"

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
    return render_template("home.html", logged_in=is_logged_in())


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


@app.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys())]
    print(session)
    return redirect('/?message=See+you+next+time!')


@app.route('/login', methods=["GET", "POST"])
def site_login():
    if is_logged_in():
        print("is logged in b")
        return redirect('/')

    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = """SELECT id, first_name, last_name, password FROM people WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        cur.close()
        try:
            user_id = user_data[0][0]
            first_name = user_data[0][1]
            last_name = user_data[0][2]
            db_password = user_data[0][3]
        except IndexError:
            return redirect("/login?error=Email+Invalid+Or+Password+Incorrect")

        if not bcrypt.check_password_hash(db_password, password):
            return redirect("/login?error=Email+Invalid+Or+Password+Incorrect")

        session['email'] = email
        session['user_id'] = user_id
        session['first_name'] = first_name
        session['last_name'] = last_name
        print(session)
        return redirect('/')

    return render_template('login.html', logged_in=is_logged_in())


# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def site_signup():
    # Checking somebody is not already signed up / logged in
    if is_logged_in():
        print("is logged in a")
        return redirect('/')

    # Getting their details
    if request.method == 'POST':
        print(request.form)
        first_name = request.form.get('first_name').strip().title()
        last_name = request.form.get('last_name').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        type = request.form.get('type')

        # Restricting entries for authenticity and security
        if password != password2:
            return redirect('/signup?error=Passwords+Do+Not+Match')

        if len(password) < 6:
            return redirect('/signup?error=Password+Must+Be+At+Least+6+Characters')

        if len(first_name) < 2 or len(last_name) < 2:
            return redirect('/signup?error=Names+Must+Be+At+Least+2+Characters')

        # Hashing password (making longer with more varied characters) for security
        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DATABASE)

        query = "INSERT INTO people(id, first_name, last_name, email, password, type) VALUES(NULL,?,?,?,?,?)"

        cur = con.cursor()
        # Checking that email is not already used
        try:
            cur.execute(query, (first_name, last_name, email, hashed_password, type))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+s+Already+Being+Used')

        con.commit()
        con.close()
        return redirect('/login')

    return render_template("signup.html", logged_in=is_logged_in())


# Making a list of categories
def get_categories():
    query = "SELECT category FROM categories"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    print(category_list)
    return category_list


@app.route('/contribute', methods=['GET', 'POST'])
def site_contribute():
    print(request.form)
    category = request.form.get('category')
    english_name = request.form.get('english_name')
    maori_name = request.form.get('maori_name')
    level = request.form.get('level')
    definition = request.form.get('definition')
    created_at = date.today()

    con = create_connection(DATABASE)

    query = "INSERT INTO maori_words(id, category, english_name, maori_name," \
            " created_at, definition, level)" \
            " VALUES(NULL,?,?,?,?,?,?)"

    cur = con.cursor()
    cur.execute(query, (category, english_name, maori_name, created_at, definition, level))
    con.commit()
    con.close()

    return render_template("contribute.html")


if __name__ == '__main__':
    app.run()
