from flask import Flask, render_template, request, redirect, url_for, session, flash
import urllib.request as urlrequest
import json
import sqlite3, os, random
import utl.dbfunctions as dbfunctions
app = Flask(__name__)

#creates secret key for sessions
app.secret_key = os.urandom(32)

#sets up database
DB_FILE = "rammm.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False) #open if file exists, otherwise create
c = db.cursor() #facilitate db operations
dbfunctions.createTables(c)

@app.route("/")
def root():
    if "userID" in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route("/login") #login page
def login():
    if "userID" in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')

@app.route("/signup") #signup page
def signup():
    if "userID" in session:
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

#creates a new user in the database if provided valid signup information
@app.route("/register", methods=["POST"])
def register():
    if "userID" in session:
        return redirect(url_for('dashboard'))
    #gets user information from POST request
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']
    character = request.form['starterSelect']
    c.execute("SELECT username FROM users WHERE username = ?", (username, ))
    a = c.fetchone()
    if a != None:
        flash("Account with that username already exists")
        return redirect(url_for('signup'))
    elif password != password2:
        flash("Passwords do not matcwhich you can then use the function from this package: 'random.random()'. Youh")
        return redirect(url_for('signup'))
    elif len(password) < 8:
        flash("Password must be at least 8 characters in length")
        return redirect(url_for('signup'))

    else:
        dbfunctions.createUser(c,username,password,character)
        db.commit()
        flash("Successfuly created user")
        return redirect(url_for('login'))

#authenticates user upon a login attempt
@app.route("/auth", methods=["POST"])
def auth():
    if "userID" in session:
        flash("You were already logged in, "+session['username']+".")
        return redirect(url_for('dashboard'))
    # information inputted into the form by the user
    username = request.form['username']
    password = request.form['password']
    # looking for username & password from database
    c.execute("SELECT userID, password FROM users WHERE username = ?", (username, ))
    a = c.fetchone()
    if a == None: # if username not found
        flash("No user found with given username")
        return redirect(url_for('login'))
    elif password != a[1]: # if password is incorrect
        flash("Incorrect password")
        return redirect(url_for('login'))
    else: # hooray! the username and password are both valid
        session['userID'] = a[0]
        session['username'] = username
        flash("Welcome " + username + ". You have been logged in successfully.")
        return redirect(url_for('dashboard'))

#logs out user by deleting info from the session
@app.route("/logout")
def logout():
    if not "userID" in session:
        flash("Already logged out, no need to log out again")
    else:
        session.pop('userID')
        session.pop('username')
    return redirect(url_for('root')) # should redirect back to login page

# DASHBOARD

@app.route("/dashboard")
def dashboard():
    if not "userID" in session:
        return redirect(url_for('login'))
    user = dbfunctions.getUser(c,str(session['userID']))
    return render_template('dashboard.html', name = user[4], image = user[5], xp = user[6], strength = user[7], intelligence = user[8], luck = user[9], gold = user[10])

# TRIVIA MINIGAME

@app.route("/trivia")
def trivia():
    if not "userID" in session:
        return redirect(url_for('login'))
    return render_template('trivia.html')

# STRENGTH MINIGAME

@app.route("/strength")
def strength():
    if not "userID" in session:
        return redirect(url_for('login'))
    user = dbfunctions.getUser(c,str(session['userID']))
    return render_template('strength.html', image = user[5], name = user[4])

# LOTTO MINIGAME

@app.route("/lotto")
def lotto():
    if not "userID" in session:
        return redirect(url_for('login'))
    return render_template('lotto.html')

@app.route("/lottoresults")
def lottoResults():
    if not "userID" in session:
        return redirect(url_for('login'))
    rand1 = random.randint(0, 1)
    rand2 = random.randint(0, 1)
    rand3 = random.randint(0, 1)
    charCount = dbfunctions.getCharCount(c)
    randCharID1 = random.randint(1, charCount)
    randCharID2 = random.randint(1, charCount)
    randCharID3 = random.randint(1, charCount)
    if rand1 == rand2 == rand3:
        return render_template('lottoresults.html', charID = randCharID1, img1 = dbfunctions.getImage(c, randCharID1), img2 = dbfunctions.getImage(c, randCharID1), img3 = dbfunctions.getImage(c, randCharID1), isWinner = True)
    else:
        return render_template('lottoresults.html', img1 = dbfunctions.getImage(c, randCharID1), img2 = dbfunctions.getImage(c, randCharID2), img3 = dbfunctions.getImage(c, randCharID3), isWinner = False)

# COLLECTION

@app.route("/collection")
def collection():
    if not "userID" in session:
        return redirect(url_for('login'))
    usernameCurrent = session['username']
    return render_template('collection.html', username = usernameCurrent)

if __name__ == "__main__":
    app.debug = True
    app.run()

db.commit()
db.close()
