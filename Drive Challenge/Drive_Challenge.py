import mysql.connector

#Creamos la conexion con la base de datos
conexionDB = mysql.connector.connect(
    host = "127.0.0.1",
    user = "root",
    password = "123123",
)

try:
    #Intentamos ingresar a la base de datos DriveDB
    try:
        cursor = conexionDB.cursor(buffered=True) #El cursor permite enviar y recibir datos

        sqlcnx = cursor.execute("use DriveDB") #Intentamos usar la base de datos (si no existe, entra al catch)

        cursor.execute(sqlcnx)

        print ("Conexion realizada correctamente!")
        print (" ")

    #En el caso de que la base de datos no exista, la creamos
    except mysql.connector.DatabaseError:

        print ("La base de datos 'DriveDB' no existe. Se creará automaticamente.")
        print (" ")
        print ("Creando...")
        print (" ")
 
        sqlcnx = cursor.execute("CREATE DATABASE DriveDB")

        cursor.execute(sqlcnx)

        print ("La base de datos 'DriveDB' se creo correctamente!")
        print (" ")

    #Intentamos utilizar la tabla 'Usuarios'
    try:

        sqlTabla = cursor.execute("SELECT * from usuarios") #Intentamos usar la base de datos (si no existe, entra al catch)

        cursor.execute(sqlTabla)

    #En el caso de que la tabla 'Usuarios' no exista, la creamos
    except mysql.connector.DatabaseError:

        print ("La tabla 'Usuarios' no existe. Se creará automaticamente.")
        print (" ")
        print ("Creando...")
        print (" ")
    
        sqltbl = cursor.execute("CREATE TABLE `drivedb`.`usuarios` (`idusuarios` INT NOT NULL AUTO_INCREMENT, `owner` VARCHAR(45) NULL, `nombre_archivo` VARCHAR(45) NULL, `extension` VARCHAR(45) NULL, `visibilidad` VARCHAR(45) NULL, `fecha_modificacion` DATE NULL, PRIMARY KEY (`idusuarios`));")
    
        cursor.execute(sqltbl)

        print ("La tabla 'Usuarios' se creo correctamente!")
        print (" ")

except exception:
    print ("Error desconocido. Consulte con un administrador.")
    print (" ")

#FINALIZA la conexion y creacion de tablas



#Iniciamos

sqlDatos = "select * from usuarios"

cursor.execute(sqlDatos)

resultados = cursor.fetchall()

print (resultados)