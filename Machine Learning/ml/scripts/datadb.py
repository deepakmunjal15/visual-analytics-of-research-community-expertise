
#Install these libraries
import MySQLdb as MS
import csv
import pandas as pd

#Read all keywords from sheet to save in db
def read_keywords():
    with open('Path to Topics.csv', 'r') as fp:
        reader = csv.reader(fp, delimiter=',', quotechar='"')
        keywords = [row for row in reader]
    return keywords

keywords=read_keywords()

#Connect to database and save all data
db1 = MS.connect(host="localhost",user="root",passwd="root")
cursor = db1.cursor()
sql = 'create database IF NOT EXISTS mydata;'
cursor.execute(sql)
cursor.execute("USE mydata;")

#Read training data
def read_training_data():
    df = pd.read_csv("Path to train_data.csv")
    df=df.as_matrix()
    return df

df=read_training_data()

#Save training data in database
cursor.execute("drop table IF EXISTS training_data;")
cursor.execute("create table IF NOT EXISTS training_data (title Nvarchar(max), abstract Nvarchar(max), topic Nvarchar(max));")

#Insert into table in the db
for i in range(0, len(df)):
    cursor.execute("""insert into training_data (title, abstract, topic) values(%s, %s, %s);""" % (df[i][0], df[i][1], df[i][2]))
    db1.commit()

k=cursor.execute("select * from training_data")
df=cursor.fetchall()

# disconnect from server
db1.close()
