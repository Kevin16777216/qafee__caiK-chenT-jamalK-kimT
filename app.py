from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import urllib.request as urlrequest
import json
import sqlite3, os, random, copy
import utl.dbfunctions as dbfunctions
app = Flask(__name__)

#creates secret key for sessions
app.secret_key = os.urandom(32)

#sets up database
DB_FILE = "rammm.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False) #open if file exists, otherwise create
c = db.cursor() #facilitate db operations
dbfunctions.createTables(c)

#decorator that redirects user to login page if not logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "userID" not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
        flash("Account with that username already exists", "error")
        return redirect(url_for('signup'))
    elif password != password2:
        flash("Passwords do not match", "error")
        return redirect(url_for('signup'))
    elif len(password) < 8:
        flash("Password must be at least 8 characters in length", "error")
        return redirect(url_for('signup'))

    else:
        dbfunctions.createUser(c,username,password,character)
        db.commit()
        flash("Successfuly created user", "success")
        return redirect(url_for('login'))

#authenticates user upon a login attempt
@app.route("/auth", methods=["POST"])
def auth():
    if "userID" in session:
        flash("You were already logged in, "+session['username']+".", "error")
        return redirect(url_for('dashboard'))
    # information inputted into the form by the user
    username = request.form['username']
    password = request.form['password']
    # looking for username & password from database
    c.execute("SELECT userID, password FROM users WHERE username = ?", (username, ))
    a = c.fetchone()
    if a == None: # if username not found
        flash("No user found with given username", "error")
        return redirect(url_for('login'))
    elif password != a[1]: # if password is incorrect
        flash("Incorrect password", "error")
        return redirect(url_for('login'))
    else: # hooray! the username and password are both valid
        session['userID'] = a[0]
        session['username'] = username
        flash("Welcome " + username + ". You have been logged in successfully.", "success")
        return redirect(url_for('dashboard'))

#logs out user by deleting info from the session
@app.route("/logout")
def logout():
    if not "userID" in session:
        flash("Already logged out, no need to log out again", "error")
    else:
        session.pop('userID')
        session.pop('username')
        flash("Successfuly logged out", "success")
    return redirect(url_for('root')) # should redirect back to login page

# DASHBOARD

@app.route("/dashboard")
@login_required
def dashboard():
    user = dbfunctions.getUser(c,str(session['userID']))
    return render_template('dashboard.html', name = user[4], image = user[5], xp = user[6], strength = user[7], intelligence = user[8], luck = user[9], gold = user[10])

# TRIVIA MINIGAME
original_questions = {
 #Format is 'question':[options]
 'The programming language Swift was created to replace what other programming language?':['Objective-C','Ruby','Java','C++'],
 'On which computer hardware device is the BIOS chip located?':['Motherboard','Hard Disk Drive','Central Processing Unit','Graphics Processing Unit'],
 'In the programming language Java, which of these keywords would you put on a variable to make sure it doesn&#039;t get modified?':['Final','Static','Private','Public'],

}

questions = copy.deepcopy(original_questions)

def shuffle(q):
 """
 This function is for shuffling
 the dictionary elements.
 """
 selected_keys = []
 i = 0
 while i < len(q):
  current_selection = random.choice(list(q.keys()))
  if current_selection not in selected_keys:
   selected_keys.append(current_selection)
   i += 1
 return selected_keys

@app.route("/trivia")
def trivia():
 questions_shuffled = shuffle(questions)
 for i in questions.keys():
  random.shuffle(questions[i])
 return render_template('trivia.html', q = questions_shuffled, o = questions)

@app.route('/quiz', methods=['POST'])
def quiz_answers():
 correct = 0
 for i in questions.keys():
  answered = request.form[i]
  if original_questions[i][0] == answered:
   correct += 1
 return '<h1>Correct Answers: <u>'+str(correct)+'</u></h1>'

# STRENGTH MINIGAME
randHeroID = 0
@app.route("/strength")
@login_required
def strength():
    user = dbfunctions.getUser(c,str(session['userID']))
    global randHeroID
    randHeroID = random.randint(1, 731)
    hImage = dbfunctions.getHeroImage(c, randHeroID)
    hName = dbfunctions.getHeroName(c, randHeroID)
    return render_template('strength.html', image = user[5], name = user[4], heroImage = hImage, heroName = hName)

@app.route("/strengthresults")
@login_required
def strengthresult():
    userID = session['userID']
    user = dbfunctions.getUser(c,str(userID))
    global randHeroID
    randRPC = random.randint(1, 3)
    userRPC = int(request.form['rpc'])
    hImage = dbfunctions.getHeroImage(c, randHeroID)
    hName = dbfunctions.getHeroName(c, randHeroID)
    if (userRPC == 1 and randRPC == 3) or (userRPC == 3 and randRPC == 2) or (userRPC == 2 and randRPC == 1):
        dbfunctions.updateStats(c, userID, strength = 3, xp = 25, gold = 2)
        return render_template('strengthresults.html', image = user[5], name = user[4], heroImage = hImage, heroName = hName, userResult = userRPC, heroResult = randRPC, isWinner = True)
    else:
        dbfunctions.updateStats(c, userID, strength = 1, xp = 10)
        return render_template('strengthresults.html', image = user[5], name = user[4], heroImage = hImage, heroName = hName, userResult = userRPC, heroResult = randRPC, isWinner = False)

# LOTTO MINIGAME

@app.route("/lotto")
@login_required
def lotto():
    return render_template('lotto.html')

@app.route("/lottoresults")
@login_required
def lottoResults():
    userID = session['userID']
    if dbfunctions.getStats(c, userID)['gold'] < 10:
        flash("You do not have enough gold!")
        return redirect(url_for('dashboard'))
    dbfunctions.updateStats(c, userID, gold = -10)
    db.commit()
    rand1 = random.randint(0, 1)
    rand2 = random.randint(0, 1)
    rand3 = random.randint(0, 1)
    charCount = dbfunctions.getCharCount(c)
    randCharID1 = random.randint(1, charCount)
    randCharID2 = random.randint(1, charCount)
    randCharID3 = random.randint(1, charCount)
    charName = dbfunctions.getName(c, randCharID1)
    if rand1 == rand2 == rand3:
        return render_template('lottoresults.html', charID = randCharID1, charName = charName, img1 = dbfunctions.getImage(c, randCharID1), img2 = dbfunctions.getImage(c, randCharID1), img3 = dbfunctions.getImage(c, randCharID1), isWinner = True)
    else:
        return render_template('lottoresults.html', img1 = dbfunctions.getImage(c, randCharID1), img2 = dbfunctions.getImage(c, randCharID2), img3 = dbfunctions.getImage(c, randCharID3), isWinner = False)

@app.route("/lottoswitch", methods=["POST"])
@login_required
def lottoSwitch():
    userID = session['userID']
    charID = request.form['charID']
    charName = request.form['charName']
    charImg = request.form['charImg']
    dbfunctions.addChar(c, userID, charID, charName, charImg)
    dbfunctions.switchChar(c, userID, charID, charName, charImg)
    dbfunctions.updateStats(c, userID, luck = 5, xp = 25)
    db.commit()
    stats = dbfunctions.getStats(c, userID)
    return render_template("lottoswitch.html", charName = charName, charImg = charImg, luck = stats['luck'], xp = stats['xp'])

@app.route("/lottogold", methods=["POST"])
@login_required
def lottoGold():
    userID = session['userID']
    dbfunctions.updateStats(c, userID, gold = 50, luck = 5, xp = 25)
    db.commit()
    stats = dbfunctions.getStats(c, userID)
    return render_template("lottogold.html", gold = stats['gold'], luck = stats['luck'], xp = stats['xp'])

# COLLECTION
@app.route("/collection")
@login_required
def collection():
    return render_template('collection.html')

if __name__ == "__main__":
    app.debug = True
    app.run()

db.commit()
db.close()
