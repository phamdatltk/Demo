import pyodbc 

server = '10.20.10.10'
database = 'DBdefault'
username = 'admin'
password = '2dhNqbLXtc55'

# Establishing a connection to the SQL Server
cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};\
                      SERVER='+server+';\
                      DATABASE='+database+';\
                      UID='+username+';\
                      PWD='+ password)

cursor = cnxn.cursor()