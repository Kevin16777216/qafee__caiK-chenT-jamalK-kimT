import urllib.request as request
import json
## GENERAL SETUP

## CREATE Database
def createTables(c):
    c.execute('CREATE TABLE IF NOT EXISTS users (userID INTEGER PRIMARY KEY, username TEXT, password TEXT, charID INTEGER, charName TEXT, charImg TEXT, xp INTEGER, strength INTEGER, intelligence INTEGER, luck INTEGER, gold INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS characters (userID, charID INTEGER, charName INTEGER, charImg TEXT)')

## CREATE Account

# function that takes the given parameters to create a story & add it to the database
def createUser(c, username, password, charID):
    image = "https://rickandmortyapi.com/api/character/avatar/"+ charID +".jpeg"
    namejson = request.urlopen("https://rickandmortyapi.com/api/character/"+ charID).read()
    name = json.loads(namejson)['name']
    c.execute('INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, 0, 0, 0, 0, 50)', (username, password, int(charID), name, image))
    id = getUserIDByUsername(c,username)
    c.execute('INSERT INTO characters VALUES (?, ?, ?, ?)', (id, int(charID), name,image))
def getUserIDByUsername(c,username):
    return c.execute("SELECT userID FROM users WHERE username = ?", (username, )).fetchone()[0]
def getUser(c,userID):
    return c.execute("SELECT * FROM users WHERE userID = " + userID).fetchone()

## GET A CHARACTER IMAGE
def getImage(c, charID):
    image = "https://rickandmortyapi.com/api/character/avatar/"+str(charID)+".jpeg"
    return image

## GET A CHARACTER NAME
def getName(c, charID):
    namejson = request.urlopen("https://rickandmortyapi.com/api/character/"+ str(charID)).read()
    name = json.loads(namejson)['name']
    return name

## GET CHARACTER COUNT
def getCharCount(c):
    countjson = request.urlopen("https://rickandmortyapi.com/api/character/").read()
    count = json.loads(countjson)['info']['count']
    return count

## ADD CHARACTER TO USER
def addChar(c, userID, charID, charName, charImg):
    c.execute('INSERT INTO characters VALUES (?, ?, ?, ?)', (userID, charID, charName, charImg))

## SWITCH USERS CURRENT CHARACTER
def switchChar(c, userID, charID, charName, charImg):
    c.execute('UPDATE users SET charID = ?, charName = ?, charImg = ? WHERE userID = ?', (charID, charName, charImg, userID))

## RETURN ALL STATS - return dictionary of stats
def returnStats(c, userID):
    return None

## UPDATE STATS
def updateStats(c, userID, xp, strength, intelligence, luck, gold):
    return None
