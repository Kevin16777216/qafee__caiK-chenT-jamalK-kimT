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

## GET USER XP
def getXP(c, userID):
    return c.execute("SELECT xp FROM users WHERE userID = ?", (userID, ))

def levelUp(xp1, xp2):
    return (int(xp1/100) + 1) != (int(xp2/100) + 1)

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
def getStats(c, userID):
    c.execute('SELECT xp, strength, intelligence, luck, gold FROM users WHERE userID = ?', (userID,))
    stats = c.fetchone()
    statDict = {'xp': stats[0], 'strength': stats[1], 'intelligence': stats[2], 'luck': stats[3], 'gold': stats[4]}
    return statDict

## UPDATE STATS
def updateStats(c, userID, **stats):
    currStats = getStats(c, userID)
    for key, value in stats.items():
        newValue = currStats[key] + value
        c.execute('UPDATE users SET {} = ? WHERE userID = ?'.format(key), (newValue, userID))
        newStats = getStats(c, userID)
        if newStats['intelligence'] > 100:
            c.execute('UPDATE users SET intelligence = 100 WHERE userID = ?', (userID, ))
        if newStats['strength'] > 100:
            c.execute('UPDATE users SET strength = 100 WHERE userID = ?', (userID, ))
        if newStats['luck'] > 100:
            c.execute('UPDATE users SET luck = 100 WHERE userID = ?', (userID, ))

## RETURN ALL CHARACTERS - return list of character names and images
def getCharacters(c, userID):
    c.execute('SELECT charName, charImg FROM characters WHERE userID = ?', (userID,))
    stats = c.fetchall()
    out = []
    for i in stats:
        out.append((i[0], i[1]))
    return out

## GET A HERO IMAGE
def getHeroImage(c, charID):
    req = request.Request('https://www.superheroapi.com/api.php/2503373653110667/'+str(charID), headers={'User-Agent': 'Mozilla/5.0'})
    imagejson = request.urlopen(req).read()
    if json.loads(imagejson)['response'] == 'error':
        return "";
    image = json.loads(imagejson)['image']['url']
    return image

## GET A HERO NAME
def getHeroName(c, charID):
    req = request.Request('https://www.superheroapi.com/api.php/2503373653110667/'+str(charID), headers={'User-Agent': 'Mozilla/5.0'})
    namejson = request.urlopen(req).read()
    if json.loads(namejson)['response'] == 'error':
        return "";
    name = json.loads(namejson)['name']
    return name

# makes dictionary from API
def quest(bank):
    q = request.urlopen("https://opentdb.com/api.php?amount=10&category=18&type=multiple").read()
    for i in range(5):
        count = json.loads(q)['results'][i]
        print(count)
        print(count['correct_answer'])
        ans = [count['correct_answer']]
        bank[count['question']] = [*ans,*count['incorrect_answers']]
    print(bank)
    return bank
