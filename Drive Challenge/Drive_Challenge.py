from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
import smtplib, getpass, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64
import mysql.connector

# Creamos la conexion con la base de datos
conexionDB = mysql.connector.connect(
    host = "127.0.0.1",
    user = "root",
    password = "123123",
    
)

try:
    # Intentamos ingresar a la base de datos DriveDB
    try:
        cursor = conexionDB.cursor(buffered=True) # El cursor permite enviar y recibir datos

        sqlcnx = cursor.execute("use DriveDB") # Intentamos usar la base de datos (si no existe, entra al catch)

        cursor.execute(sqlcnx)

        print ("Conexion realizada a la base de datos correctamente!")
        print (" ")

    # En el caso de que la base de datos no exista, la creamos
    except mysql.connector.DatabaseError:

        print ("La base de datos 'DriveDB' no existe. Se creará automaticamente.")
        print (" ")
        print ("Creando...")
        print (" ")
 
        sqlcnx = cursor.execute("CREATE DATABASE DriveDB")

        cursor.execute(sqlcnx)

        print ("La base de datos 'DriveDB' se creo correctamente!")
        print (" ")

    # Intentamos utilizar la tabla 'Usuarios'
    try:

        sqlTabla = cursor.execute("SELECT * from usuarios") # Intentamos usar la base de datos (si no existe, entra al catch)
        sqlTabla1 = cursor.execute("SELECT * from historial_publicos") # Intentamos usar la base de datos (si no existe, entra al catch)

        cursor.execute(sqlTabla)
        cursor.execute(sqlTabla1)

    # En el caso de que la tabla 'Usuarios' no exista, la creamos
    except mysql.connector.DatabaseError:

        print ("La tabla 'Usuarios' o 'Historial_publicos' no existe. Se creará automaticamente.")
        print (" ")
        print ("Creando...")
        print (" ")
    
        sqltbl1 = cursor.execute("CREATE TABLE `drivedb`.`usuarios` (`idusuarios` INT NOT NULL AUTO_INCREMENT, `owner` VARCHAR(45) NULL, `nombre_archivo` VARCHAR(45) NULL, `extension` VARCHAR(45) NULL, `visibilidad` VARCHAR(45) NULL, `fecha_modificacion` DATE NULL, PRIMARY KEY (`idusuarios`));")
        sqltbl2 = cursor.execute("CREATE TABLE `drivedb`.`historial_publicos` (`idhistorial_publicos` INT NOT NULL AUTO_INCREMENT, `owner` VARCHAR(45) NULL, `nombre_archivo` VARCHAR(45) NULL, `extension` VARCHAR(45) NULL, `visibilidad` VARCHAR(45) NULL, `fecha_modificacion` DATE NULL, PRIMARY KEY (`idhistorial_publicos`));")

        cursor.execute(sqltbl1)
        cursor.execute(sqltbl2)


        print ("La tabla 'Usuarios' y 'Historail_publicos' se creo correctamente!")
        print (" ")

except exception:
    print ("Error desconocido. Consulte con un administrador.")
    print (" ")

# FINALIZA la conexion y creacion de tablas

# Iniciamos con API GDrive V3

# Apuntamos a la posibilidad de leer y escribir archivos
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    creds = None
    # Se utiliza un token.pickle que almacena el acceso del usuario. refrescar el token significa tener que validar el usuario nuevamente.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Si las credenciales no son validas, hacemos que se valide el usuario
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Guardamos las credenciales para el proximo uso
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Utilizando la API GDrive V3
    results = service.files().list(
        pageSize=1000, fields="nextPageToken, files(permissionIds, name, fileExtension, owners, modifiedTime)").execute() # Busca los primeros 1000 archivos en nuestro Drive
    items = results.get('files', [])

    if not items:
        print('No files found.') # Si nuestro Drive esta vacio, mostramos un mensaje

    else:

        # Almacenamos todos los archivos que se encuentren con su metadata
        for item in items:

            try:
                visibilidad = len((item['permissionIds']))
                nombre = format(item['name'])
                extension = item['fileExtension']
                owner = format(item['owners'][0]['emailAddress'])
                fecha_modificacion = format(item["modifiedTime"])

                # Cambiamos el formato de la fecha de modificacion para que MySQL la acepte (YYYY-mm-dd)
                mytime = fecha_modificacion
                myTime = datetime.strptime(mytime, "%Y-%m-%dT%H:%M:%S.%fZ")
                myFormat = "%Y-%m-%d"
                nFecha_Modificacion = (myTime.strftime(myFormat))

                sqlComp = "SELECT nombre_archivo FROM usuarios WHERE nombre_archivo = '%s'" % (nombre)
                cursor.execute(sqlComp)
                nombreBdd = cursor.fetchone()

                nombreBddComp = str(nombreBdd)
                nombreCmp = ("('" + nombre + "',)")

                #Si el archivo no existe, lo guardamos
                if nombreBddComp != nombreCmp: 
                    # Si el archivo es privado, lo guardamos como tal
                    if visibilidad < 2:
                        sqlUsuarios = "INSERT INTO usuarios (owner, nombre_archivo, extension, visibilidad, fecha_modificacion) VALUES (%s, %s, %s, %s, %s)"

                        valores = (owner, nombre, extension, "Privado", nFecha_Modificacion)

                        cursor.execute(sqlUsuarios, valores)

                        conexionDB.commit()

                    else:
                        valoresPublico = (owner, nombre, extension, "Publico", nFecha_Modificacion)
                        valoresPriv = (owner, nombre, extension, "Privado", nFecha_Modificacion)

                        sqlUsuarios = "INSERT INTO usuarios (owner, nombre_archivo, extension, visibilidad, fecha_modificacion) VALUES (%s, %s, %s, %s, %s)"
                        cursor.execute(sqlUsuarios, valoresPriv)

                        # Guardamos el historial historico de los archivos que fueron publicos
                        sqlHistorial = "INSERT INTO historial_publicos (owner, nombre_archivo, extension, visibilidad, fecha_modificacion) VALUES (%s, %s, %s, %s, %s)"
                        cursor.execute(sqlHistorial, valoresPublico)

                        conexionDB.commit()

                        # Enviamos correo al owner del archivo que cambiamos de publico a privado.
                        mensaje = 'Se notifica de la actualizacion de un archivo de su Google Drive. Este mensaje se envia desde el challenge Gmail desarrollado en Python, es meramente de prueba. Agustin Fourcade - 2020'
                   
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login('drivechallengemeli@gmail.com', 'drivechallenge') 

                        server.sendmail('drivechallengemeli@gmail.com', owner, mensaje)

                        server.quit()

                        print (f"Se envio el correo electronico a: {owner}")
                        print (" ")

                else:
                    print ("El archivo: " + nombre + " Ya esta en la base de datos")

            except:
                msjError = ("Hay Error") # Si se encuentra un error con los archivos o sus metadatos obtenemos un error

        else:
            print ("Se cargaron los prouctos a la base de datos correctamente!") # Si todo sale bien, mostramos un mensaje
            print (" ")


if __name__ == '__main__':
    main()