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

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=1000, fields="nextPageToken, files(permissionIds, name, fileExtension, owners, modifiedTime)").execute() #Busca los primeros 1000 archivos en nuestro Drive
    items = results.get('files', [])

    if not items:
        print('No files found.')

    else:
        sql = "DELETE From usuarios where idusuarios > 0;"
        sql2 = "ALTER TABLE usuarios AUTO_INCREMENT = 1;"
        cursor.execute(sql)
        cursor.execute(sql2)
        conexionDB.commit()

        print('Files:')
        print(' ')

        for item in items:

            try:

                visibilidad = len((item['permissionIds']))
                nombre = format(item['name'])
                extension = item['fileExtension']
                owner = format(item['owners'][0]['emailAddress'])
                fecha_modificacion = format(item["modifiedTime"])

                mytime = fecha_modificacion
                myTime = datetime.strptime(mytime, "%Y-%m-%dT%H:%M:%S.%fZ")
                myFormat = "%Y-%m-%d"
                nFecha_Modificacion = (myTime.strftime(myFormat))

                print (visibilidad)
                print (nombre)
                print (extension)
                print (owner)
                print (nFecha_Modificacion)
                print (" ")

                if visibilidad < 2:
                    sql = "INSERT INTO usuarios (owner, nombre_archivo, extension, visibilidad, fecha_modificacion) VALUES (%s, %s, %s, %s, %s)"
                    val = (owner, nombre, extension, "Privado", nFecha_Modificacion)
                    cursor.execute(sql, val)
                    conexionDB.commit()
                else:
                    sql = "INSERT INTO usuarios (owner, nombre_archivo, extension, visibilidad, fecha_modificacion) VALUES (%s, %s, %s, %s, %s)"
                    val = (owner, nombre, extension, "Publico", nFecha_Modificacion)
                    cursor.execute(sql, val)
                    conexionDB.commit()

            except:
                msjError = ("Hay Error")

        else:
            print ("Se cargaron los prouctos a la base de datos correctamente!")
            print (" ")

if __name__ == '__main__':
    main()