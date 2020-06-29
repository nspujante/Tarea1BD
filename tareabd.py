import pyodbc
from random import choice
from datetime import datetime

#Conexion con la base de datos
conn = pyodbc.connect("DRIVER={Oracle en OraDB18Home1};DBQ=XE;Uid=boji;Pwd=Compaq123;DATABASE=bojiBD")
cur = conn.cursor()

#funcion para crear la tabla poyo
def poyo_table():
    cur.execute("DROP TABLE POYO")
    #inicia la tabla POYO
    cur.execute("CREATE TABLE POYO(pokedex INTEGER NOT NULL,nombre VARCHAR2(32) NOT NULL,type1 VARCHAR2(32) NOT NULL,type2 VARCHAR2(32),hp_total INTEGER NOT NULL,legendary CHAR(1) NOT NULL)")
    arch=open("C:/Users/Nicolás/Desktop/tareabd/pokemon.csv","r")
    for row in arch:
        row_list=row.strip().split(",")
        if row_list[0]!="#":#se salta la primera linea del csv
            if row_list[12]=="True":#revisa si es legendario
                legendary='1'
            else:
                legendary='0'
            cur.execute("INSERT INTO POYO VALUES(?,?,?,?,?,?)",(int(row_list[0]),row_list[1],row_list[2],row_list[3],int(row_list[5]),legendary))#inserta el pokemon a la tabla POYO
    arch.close()
    cur.commit()
    print("Se ha creado la tabla POYO de forma exitosa")

#funcion para crear la tabla sansanito
def sansanito_table():
    cur.execute("DROP TABLE SANSANITO")
    cur.execute("CREATE TABLE SANSANITO(id INTEGER GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1) PRIMARY KEY, pokedex INTEGER NOT NULL,nombre VARCHAR2(32) NOT NULL,type1 VARCHAR2(32) NOT NULL,type2 VARCHAR2(32),hp_actual INTEGER NOT NULL ,hp_max INTEGER NOT NULL,legendary CHAR(1) NOT NULL, estado VARCHAR2(16), fechyhora DATE NOT NULL, prioridad INTEGER NOT NULL)")
    cur.commit()
    print("Se ha creado la tabla Sansanito de forma exitosa")

def create():
    inPok=input("Ingrese el nombre del pokemon a ingresar: ")
    cur.execute("SELECT * FROM POYO WHERE nombre=?",(inPok))
    pok=cur.fetchone()#devuelve una tupla con todos los datos del pokemon solicitados
    cur.execute("SELECT id FROM SANSANITO")
    lenghtList=cur.fetchall()#devuelve una lista con todos los id
    lenght=len(lenghtList)#se usa el largo de la lista para ver cuantos pokemones hay
    if lenght<50:
        (dex, nom, typ1, typ2, hp, legen)=pok #descomprime la tupla
        hpAct=choice(range(int(hp)))#va entre 0-(hp-1)
        stateList=["Envenenado", "Paralizado", "Quemado", "Dormido", "Congelado", None]
        state=choice(stateList)
        if state!=None: #revisa si el pokemon tiene algun estado para agregar la prioridad
            prio=(int(hp)-hpAct)+10
        else:
            prio=(int(hp)-hpAct)
        date=datetime.now()##ver si es mejor tener fecha aleatoria
        cur.execute("INSERT INTO SANSANITO (pokedex,nombre,type1,type2,hp_actual,hp_max,legendary,estado,fechyhora,prioridad) VALUES (?,?,?,?,?,?,?,?,?,?)",(int(dex), nom, typ1, typ2, hpAct, int(hp), legen, state, date, prio))
        cur.commit()
        cur.execute("SELECT id FROM SANSANITO WHERE fechyhora=?",(date)) #compara la hora de netrada con la hora registrada para obtener el id
        pokeId=cur.fetchone()
        #print(pokeId)
        print("Se ingreso el pokemon "+nom+" con el ID ",pokeId[0])
    else:
        if legen=='1':
            print("Hacer el caso cuando se ingresa un legndario, tener una view puede servir")

def read():
    print("Escoja una opcion")
    print("1. Mostrar estadisticas de un pokemon")
    print("2. Mostrar estadisticas de todos los pokemones")
    inp=int(input("Opcion: "))
    if inp==1:
        pokeID=int(input("Ingrese el ID del pokemon que desea verificar: "))
        cur.execute("SELECT * FROM SANSANITO WHERE id=?",(pokeID))
        poke=cur.fetchone()
        (idd, dex, nom, typ1, typ2, hpAct, hp, legen, estado, fecha, prio)=poke
        if typ2==None:
            tipo=typ1
        else:
            tipo=str(typ1)+" y "+str(typ2)
        if legen=='1':
            leg="Si"
        else:
            leg="No"
        print("ID:",idd,"Pokedex:",dex,"Nombre:",nom,"Tipo:",tipo,"HP Actual:",hpAct,"HP Max",hp,"Es legendario?:",leg,"Estado:",estado,"fecha y hora de ingreso:",fecha,"Prioridad",prio)


#poyo_table()
#sansanito_table()
#create()
#create()
read()