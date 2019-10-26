#Team Fine Pizza avrahamiB huangT linW wangD
#SoftDev1 pd2
#P00: Da Art of Storytellin'
#2019-10-28

from flask import Flask, render_template, request, session, redirect, url_for, flash
import sqlite3
app = Flask(__name__)
app.secret_key = "adsfgt"

session = {}
currentStoryId = -1
currentStoryName = ""

@app.route("/")
def root(): #if user is logged in, redirect to the homepage, otherwise prompt user to login or register
    if 'user' in session:
        return redirect(url_for("home"))
    else:
        return render_template("landingpage.html")

@app.route("/home")
def home(): #display home page of website
    if 'user' in session:
        global currentStoryId, currentStoryName
        currentStoryName = ""
        currentStoryId = -1
        return render_template(
            "homepage.html",
            user = session['user'],
            storyName = getStories(),
            storyAdd = getCanAddToStories()
        )
    else:
        return redirect(url_for("root"))

@app.route("/logout")
def logout(): #logs out user, return to login/register page
    session.pop('user') #removes the user from session
    return redirect(url_for("root"))

@app.route("/login", methods = ["POST"])
def login(): #check credentials against the table and confirms if they are correct
    if (request.form['username'] == "" or request.form['password'] == ""):
        flash("ERROR! Invalid username and password")
        flash("invalid error")
        return redirect(url_for("root"))
    else:
        dbfile = "holding.db"
        db = sqlite3.connect(dbfile)
        c = db.cursor()
        command = "SELECT username FROM users WHERE username = \"{}\";"
        listUsers = c.execute(command.format(request.form['username']))
        bar = list(enumerate(listUsers))
        if len(bar) > 0:
            getPass = "SELECT password FROM users WHERE username = \"{}\";"
            listPass = c.execute(getPass.format(bar[0][1][0]))
            for p in listPass:
                if request.form['password'] == p[0]:
                    session['user'] = request.form['username']
                    return redirect(url_for("home"))
                else:
                    flash("ERROR! Incorrect password")
                    flash("invalid error")
                    return redirect(url_for("root"))
        else:
            flash("ERROR! Incorrect username")
            flash("invalid error")
            return redirect(url_for("root"))

@app.route("/register", methods = ["POST"])
def register(): #adds credentials to the users table and then redirects to the homepage
    #try:
    if (request.form['username'] == "" or request.form['password'] == ""):
        flash("ERROR! Username and password cannot be blank")
        flash("register error")
        return redirect(url_for("root"))
    else:
        dbfile = "holding.db"
        db = sqlite3.connect(dbfile)
        c = db.cursor()
        command = "SELECT username FROM users WHERE username = \"{}\";"
        newUser = c.execute(command.format(request.form['username']))
        if len(list(enumerate(newUser))) > 0:
            flash("Username is already taken. Please choose another one.")
            flash("register error")
            return redirect(url_for("root"))
        else:
            user_id = getTableLen("users")
            c.execute("INSERT into users VALUES(?, ?, ?);", (user_id, request.form['username'], request.form['password']))
            session['user'] = request.form['username']
            db.commit()
            db.close()
            return redirect(url_for("home"))
    #except:
    #    flash("ERROR! Invalid characters")
    #    flash("register error")
    #    return redirect(url_for("root"))

@app.route("/create")
def create(): #lets the user create a new story
    return render_template("newpage.html")

@app.route("/add", methods = ["POST"])
def addStory(): #checks if the story exists and registers the story if it does not yet
    if request.form['title'] == "" or request.form['story'] == "": #if either title or story is empty, return error
        flash("ERROR! Title or story cannot be blank")
        return redirect(url_for("create"))
    else:
        dbfile = "holding.db"
        db = sqlite3.connect(dbfile)
        c = db.cursor()
        command = "SELECT story_name FROM stories WHERE story_name = \"{}\";"
        sameStory = c.execute(command.format(request.form['title']))
        if len(list(enumerate(sameStory))) > 0: #if story exists return an error
            flash("Title has already been taken. Please choose another one.")
            return redirect(url_for("create"))
        else: #else add to table of stories
            story_id = getTableLen("stories")
            command = "INSERT INTO stories VALUES(?, ?, ?, ?);"
            c.execute(command, (story_id, request.form['title'], request.form['story'], request.form['story']))
            id = getUserID()
            command = "INSERT INTO edits VALUES(?, ?);"
            c.execute(command, (id, getTableLen("stories")))
        db.commit()
        db.close()
        return redirect(url_for("home"))

@app.route("/read/<file>")
def read(file):
    dbfile = "holding.db"
    db = sqlite3.connect(dbfile)
    c = db.cursor()
    command = "SELECT story_text FROM stories WHERE story_name = \"{}\""
    q = c.execute(command.format(file))
    text = ""
    for bar in q:
        text = bar[0]
    return render_template(
        "readonly.html",
        name = file,
        story = text
    )

@app.route("/add/<file>")
def add(file):
    global currentStoryId, currentStoryName
    dbfile = "holding.db"
    db = sqlite3.connect(dbfile)
    c = db.cursor()
    currentStoryName = file
    command = "SELECT story_id FROM stories WHERE story_name = \"{}\";"
    q = c.execute(command.format(file))
    for id in q:
        currentStoryId = id[0]
    command = "SELECT last_edit FROM stories WHERE story_name = \"{}\";"
    q = c.execute(command.format(file))
    text = ""
    for bar in q:
        text = bar[0]
    return render_template(
        "add.html",
        name = file,
        story = text
    )

@app.route("/addToStory", methods = ["POST"])
def addToStory():
    if request.form['addition'] == "":
        flash("ERROR! The addition field cannot be left blank.")
        return redirect(url_for("home"))
    else:
        dbfile = "holding.db"
        db = sqlite3.connect(dbfile)
        c = db.cursor()
        command = "UPDATE stories SET last_edit = \"{}\" WHERE story_id = {};"
        c.execute(command.format(request.form['addition'],currentStoryId))
        command = "INSERT INTO edits VALUES (? , ?);"
        c.execute(command, (getUserID(),currentStoryId))
        command = "SELECT story_text FROM stories WHERE story_id = {};"
        story = c.execute(command.format(currentStoryId))
        updatedStory = ""
        for line in story:
            updatedStory = line[0] + request.form['addition']
        command = "UPDATE stories SET story_text = \"{}\" WHERE story_id = {};"
        c.execute(command.format(updatedStory,currentStoryId))
        db.commit()
        db.close()
        return redirect(url_for("home"))

def getTableLen(tbl): #returns the length of a table
    dbfile = "holding.db"
    db = sqlite3.connect(dbfile)
    c = db.cursor()
    command = "SELECT * FROM {};"
    q = c.execute(command.format(tbl))
    count = 0
    for line in q:
        count += 1
    return count

def getStories(): #gets all the story names a user is able to read from the stories table
    dbfile = "holding.db"
    db = sqlite3.connect(dbfile)
    c = db.cursor()
    id = getUserID()
    command = "SELECT story_id FROM edits WHERE user_id = \"{}\";"
    storyIdList = c.execute(command.format(id))
    stories = []
    for storyID in list(enumerate(storyIdList)):
        command = "SELECT story_name FROM stories WHERE story_id = \"{}\";"
        storyList = c.execute(command.format(storyID[1][0]))
        for story in storyList:
            stories.append(story[0])
    db.commit()
    db.close()
    return stories

def getCanAddToStories(): #gets all the stories that the user has not edited before
    dbfile = "holding.db"
    db = sqlite3.connect(dbfile)
    c = db.cursor()
    command = "SELECT story_name FROM stories;"
    storyList = c.execute(command)
    stories = []
    for story in storyList:
        stories.append(story[0])
    id = getUserID()
    command = "SELECT story_id FROM edits WHERE user_id = \"{}\";"
    storyIdList = c.execute(command.format(id))
    shift = 0
    for storyID in list(enumerate(storyIdList)):
        stories.pop(storyID[1][0] - shift)
        shift += 1
    db.commit()
    db.close()
    return stories

def getUserID(): #gets session user id from users table
    dbfile = "holding.db"
    db = sqlite3.connect(dbfile)
    c = db.cursor()
    command = "SELECT user_id FROM users WHERE username = \"{}\";"
    q = c.execute(command.format(session['user']))
    for bar in q:
        return bar[0]


if __name__ == "__main__":
    app.debug = True
    app.run()
