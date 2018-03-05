from ..bottoken import getConn
import psycopg2

conn = None
cur = None

def initDB():
  global conn
  global cur
  conn = getConn('antitrollbot')
  cur = conn.cursor()
  conn.rollback()
  cur.execute("CREATE TABLE IF NOT EXISTS Trolls(Id BIGINT PRIMARY KEY NOT NULL, Aka TEXT NOT NULL, Reason TEXT NOT NULL, Channelmsg BIGINT NOT NULL);")
  cur.execute("CREATE TABLE IF NOT EXISTS Admins(Id BIGINT PRIMARY KEY NOT NULL);")
  conn.commit()

def getAdmins():
  cur.execute("SELECT Id FROM Admins;")
  return evaluateList(cur.fetchall())

def getMessageFromId(id):
  cur.execute("SELECT Channelmsg FROM Trolls WHERE Id = %s;", (id,))
  test = evaluateOne(cur.fetchone())
  if test != None:
    return test
  return False

def insertTroll(id, aka, reason, channelmsg):
  cur.execute("INSERT INTO Trolls(Id, Aka, Reason, Channelmsg) VALUES(%s, %s, %s, %s);", (id, aka, reason, channelmsg))
  conn.commit()

def removeTroll(id):
  cur.execute("DELETE FROM Trolls WHERE Id = %s;", (id,))
  conn.commit()

def updateReason(id, newReason):
  cur.execute("UPDATE Trolls SET Reason = %s WHERE Id = %s;", (newReason, id))
  conn.commit()

def getAkas(id):
  cur.execute("SELECT Aka FROM Trolls WHERE Id = %s;", (id,))
  test = evaluateOne(cur.fetchone())
  if test != None:
    return test.split(',')
  return []

def updateAka(id, aka):
  temp = getAkas(id)
  dbEntry = temp + aka
  cur.execute("UPDATE Trolls SET Aka = %s WHERE Id = %s;", (','.join(dbEntry), id))
  conn.commit()

def isTroll(id):
  cur.execute("SELECT Id FROM Trolls WHERE Id = %s;", (id,))
  if evaluateOne(cur.fetchone()) != None:
    return True
  return False

def evaluateList(datas):
  cur.fetchall()
  list = []
  for i in datas:
    list.append(i[0])
  return list

def evaluateOne(data):
  cur.fetchall()
  if data != None:
    if data[0] != None:
      return data[0]
  return None

def close():
  conn.close()
