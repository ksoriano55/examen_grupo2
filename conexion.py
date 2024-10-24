## insertar
import mysql.connector


connection = mysql.connector.connect(
    host="34.42.000000",   ##Reemplazar por ip
    user="xxxxxxxxxx", ##Reemplazar por usuario
    password="xxxxxxxxxx",  ##Reemplazar por credenciales
    database="socket"
)

cursor = connection.cursor()

sql = "INSERT INTO Users (user, userName) VALUES (%s, %s)"
val = ("ricardo.lagos", "Ricardo Lagos")
cursor.execute(sql, val)


connection.commit()

print(cursor.rowcount, "registro insertado.")

cursor.close()
connection.close()