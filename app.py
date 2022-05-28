# Importing packages needed for the password hashing, website and database
# including its timestamps also the url encoding to help with the culture / religion categories
from datetime import date
from flask import Flask, render_template, request, session, redirect
from flask_bcrypt import Bcrypt
import sqlite3
from sqlite3 import Error

# Flask Setup
app = Flask(__name__)

# Password hashing setup including the secret key
bcrypt = Bcrypt(app)
app.secret_key = "3P*7iW>d},LHDw<3~(bg"

# Making a variable for the database
DATABASE = "app_assessment_daniel.sqlite"


# Creating a connection to the database
def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    # Except an error occurs where the error is printed and not return anything
    except Error as e:
        print(e)
    return None


# Home page function
@app.route('/')
def site_home():
    # Rendering the page and fetching whether there is a user logged in
    # and getting a list of categories to click on
    return render_template("home.html", logged_in=is_logged_in(), categories=get_categories())


# The function which checks whether a user is logged in
def is_logged_in():
    # Using the session information to find if there is an email attached to the session
    # if there is function returns false if there is one returns true
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


# Function checks if user is a teacher
def is_a_teacher():
    # Checks using session information of stored type returns true of false accordingly
    if session.get("type") == 'teacher':
        print("is teacher")
        return True
    else:
        print("is not teacher")
        return False


# Function that logs out a user
@app.route('/logout')
def logout():
    # Removes the session information
    [session.pop(key) for key in list(session.keys())]
    # Redirects back to home page
    return redirect('/?message=See+you+next+time!')


# Function sends user to the login page unless already logged in
@app.route('/login', methods=["GET", "POST"])
def site_login():
    # Sends logged in users to home page
    if is_logged_in():
        print("is logged in")
        return redirect('/')

    # Runs when user trys to login
    if request.method == "POST":
        # Gets information from form and cleans
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        # Gets information from database where email is email used to log in and puts into list/tuple
        query = """SELECT id, first_name, last_name, password, type FROM people WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        cur.close()

        # Try to set a variable for the details from database
        try:
            user_id = user_data[0][0]
            first_name = user_data[0][1]
            last_name = user_data[0][2]
            db_password = user_data[0][3]
            type = user_data[0][4]

        # If the email cannot be found in the people table it redirects
        except IndexError:
            return redirect("/login?error=Email+Invalid+Or+Password+Incorrect")

        # Checking passwords match
        if not bcrypt.check_password_hash(db_password, password):
            return redirect("/login?error=Email+Invalid+Or+Password+Incorrect")

        # Adds the logged-in user's details to the session storage
        session['email'] = email
        session['user_id'] = user_id
        session['first_name'] = first_name.title()
        session['last_name'] = last_name.title()
        session['type'] = type

        # Redirects home
        return redirect('/')

    # Renders the login page
    return render_template('login.html', logged_in=is_logged_in(), categories=get_categories())


# Signup function
@app.route('/signup', methods=['GET', 'POST'])
def site_signup():
    # Checking somebody is not already signed up / logged in
    if is_logged_in():
        print("is logged in a")
        # Redirects to home page if already logged in
        return redirect('/?already+logged+in')

    # Getting user details from form
    if request.method == 'POST':
        print(request.form)
        first_name = request.form.get('first_name').strip().lower()
        last_name = request.form.get('last_name').strip().lower()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password').strip()
        password2 = request.form.get('password2').strip()
        type = request.form.get('type')

        # Confirming password
        if password != password2:
            return redirect('/signup?error=Passwords+Do+Not+Match')

        # Making sure password is at least 6 characters
        if len(password) < 6:
            return redirect('/signup?error=Password+Must+Be+At+Least+6+Characters')

        # Making sure names are at least 2 letters long
        if len(first_name) < 2 or len(last_name) < 2:
            return redirect('/signup?error=Names+Must+Be+At+Least+2+Characters')

        # Hashing password (making longer with more varied characters)
        hashed_password = bcrypt.generate_password_hash(password)

        # Connecting to database
        con = create_connection(DATABASE)

        # Preparing to insert information into people table in database
        query = "INSERT INTO people(id, first_name, last_name, email, password, type) VALUES(NULL,?,?,?,?,?)"
        cur = con.cursor()

        # Checking that email is not already used
        try:
            cur.execute(query, (first_name, last_name, email, hashed_password, type))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+s+Already+Being+Used')

        # Adding to database
        con.commit()
        con.close()

        # Redirecting to login page once signed up
        return redirect('/login')

    # Renders the signup page
    return render_template("signup.html", logged_in=is_logged_in(), categories=get_categories())


# Making a list of categories to be used to access categories at the top of each page
def get_categories():
    # Selecting distinct non-case-sensitive categories from the maori word table in the database
    query = 'SELECT distinct lower(category) FROM maori_words'
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)

    # Creating the list of categories
    category_list = cur.fetchall()
    con.close()

    # Returning the list
    return category_list


# Function for displaying categories
@app.route('/category/<category_name>')
def site_category(category_name):

    # Replacing the straight lines from with slashes as the extra slashes found in some category names
    # don't work in url and this fixes the problem
    category_name = category_name.replace("|", "/")

    # Getting the words and their information in the selected category from the database
    query = "SELECT maori_name, english_name, definition, level, created_by, created_at, image_filename \
            FROM maori_words WHERE lower(category) = ?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (category_name.lower(),))
    maori_names = cur.fetchall()
    con.close()

    # If there is no words in the category redirecting home, used only after deleting a word
    if maori_names == []:
        return redirect('/')

    # Rendering the page with required information and variables inputted
    return render_template("category.html", logged_in=is_logged_in(), categories=get_categories(),
                           category_name=category_name, maori_names=maori_names, is_a_teacher=is_a_teacher())


# Function for displaying words
@app.route('/category/<category_name>/<maori_word>', methods=['GET', 'POST'])
def site_word(category_name, maori_word):

    # Replacing the straight lines with slashes (putting back after fixing problem of extra slashes in url)
    category_name = category_name.replace("|", "/")

    # Getting the words information and information of word creator using foreign key from database
    query = "SELECT maori_name, english_name, definition, level, created_at, image_filename, maori_words.id, \
            people.first_name, people.last_name \
            FROM maori_words JOIN people ON maori_words.created_by = people.id \
            WHERE lower(maori_name) = ? and lower(category) = ?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (maori_word.lower(), category_name.lower()))
    maori_names = cur.fetchall()
    con.close()

    # If the save edits button is pushed
    if request.method == 'POST' and request.form.get('submit') == "Save":

        # Getting information from form and cleaning it
        category = request.form.get('category').strip().title()
        english_name = request.form.get('english_name').strip().title()
        maori_name = request.form.get('maori_name').strip().title()
        level = request.form.get('level')
        definition = request.form.get('definition').strip().title()

        # Connecting to and updating the details of the word in the database
        con = create_connection(DATABASE)
        query = "UPDATE maori_words SET category = ?, english_name = ?, maori_name = ?, level = ?, definition = ?" \
                "WHERE id = ?"
        cur = con.cursor()
        cur.execute(query, (category, english_name, maori_name, level, definition, maori_names[0][6]))
        con.commit()
        con.close()

        # Redirecting to the updated Word page which may have a new url
        # also replacing the slashes with straight lines to work in the url
        return redirect(f"/category/{category.replace('/', '|')}/{maori_name}")

    # If delete word button is pushed
    if request.method == 'POST' and request.form.get('submit') == "Delete Word":

        # Redirecting to the confirm delete word page with the slashes straight line change for the url
        return redirect(f"/confirm_delete_word/{category_name.replace('/', '|')}/{maori_names[0][6]}")

    # Rendering the maori word page
    return render_template("word.html", logged_in=is_logged_in(), categories=get_categories(), category_name=category_name, maori_names=maori_names, is_a_teacher=is_a_teacher())


# Add word function
@app.route('/add_word', methods=['GET', 'POST'])
def site_add_word():

    # Checks if user is logged in and sends to login page if not
    if not is_logged_in():
        print("must be logged in and be a teacher to add words")
        return redirect('/login')

    # If form submitted
    if request.method == 'POST':
        # Getting information from form
        category = request.form.get('category').strip().title()
        english_name = request.form.get('english_name').strip().title()
        maori_name = request.form.get('maori_name').strip().title()
        level = request.form.get('level')
        definition = request.form.get('definition').strip().title()
        created_at = date.today()
        created_by = session['user_id']

        # Connecting to and inserting the information into the database
        con = create_connection(DATABASE)
        query = "INSERT INTO maori_words(id, category, english_name, maori_name, \
                created_at, definition, level, created_by) \
                VALUES(NULL,?,?,?,?,?,?,?)"
        cur = con.cursor()
        cur.execute(query, (category, english_name, maori_name, created_at, definition, level, created_by))
        con.commit()
        con.close()

    # Rendering the add word page with the required information
    return render_template("add_word.html", categories=get_categories(), is_a_teacher=is_a_teacher(),
                           logged_in=is_logged_in())


# Confirm delete word function
@app.route('/confirm_delete_word/<category_name>/<maori_word_id>', methods=['GET', 'POST'])
def site_confirm_delete_word(category_name, maori_word_id):

    # Replacing straight lines with slashes change after url
    category_name = category_name.replace("|", "/")

    # Finding the maori name of word with selected id to be used on rendered page
    query = "SELECT lower(maori_name) FROM maori_words WHERE id = ?"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (maori_word_id,))
    maori_word = cur.fetchall()
    con.close()

    # If confirmed deleting word form database
    if request.method == 'POST':
        con = create_connection(DATABASE)
        query = "DELETE FROM maori_words WHERE id = ?"
        cur = con.cursor()
        cur.execute(query, (maori_word_id,))
        con.commit()
        con.close()

        # Redirecting to the category page for deleted word and running slash straight line change for url
        return redirect(f"/category/{category_name.replace('/', '|')}")

    # Rendering the page with required variables
    return render_template("confirm_delete_word.html", categories=get_categories(), is_a_teacher=is_a_teacher(),
                           logged_in=is_logged_in(), maori_word=maori_word[0][0], category_name=category_name)


# Running the application
if __name__ == '__main__':
    app.run()
