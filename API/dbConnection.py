import mysql.connector as con
import mysql

db = con.connect(
        host="localhost",
        user="root",
        password="root",
        database="db_mail"
)


def db_create(tablename):
    cur=db.cursor()
    query="CREATE TABLE IF NOT EXISTS "+tablename+" ( _id INT AUTO_INCREMENT PRIMARY KEY, _to VARCHAR(255) NOT NULL, _from VARCHAR(255) NOT NULL, _subject VARCHAR(255) NOT NULL, _date VARCHAR(255) NOT NULL, _DataFile VARCHAR(255) NOT NULL, _FolderName VARCHAR(255) NOT NULL )"
    cur.execute(query)


def db_insert(_to, _from,_subject,_date,_dataFile,_folderName,tablename):
    cur = db.cursor()
    query="insert into "+ tablename+" (_to, _from,_subject,_date,_dataFile,_folderName) values(%s,%s,%s,%s,%s,%s)"
    value=[_to, _from,_subject,_date,_dataFile,_folderName]
    cur.execute(query,value)
    

def db_read(tbl_name):
    cur = db.cursor()
    query="SELECT *  FROM " +tbl_name+" WHERE _folderName = " +tbl_name+ " ORDER BY _date DESC ;"
    cur.execute(query)
    return cur.fetchall()
   
 

