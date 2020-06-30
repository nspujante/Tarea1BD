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

def trigger_prioridad(): ##Terminar
    cur.execute("CREATE OR REPLACE TRIGGER NEW_PRIORIDAD")
    cur.execute("AFTER UPDATE ON SANSANITO")

def createState():
    print("Ingrese el estado del pokemon:")
    print("1. Envenenado")
    print("2. Paralizado")
    print("3. Quemado")
    print("4. Dormido")
    print("5. Congelado")
    print("6. Sin estado")
    newEstado=int(input("Opcion: "))
    if newEstado==1:
        return "Envenenado"
    elif newEstado==2:
        return "Paralizado"
    elif newEstado==3:
        return "Quemado"
    elif newEstado==4:
        return "Dormido"
    elif newEstado==5:
        return "Congelado"
    elif newEstado==6:
        return None

def create():
    inPok=input("Ingrese el nombre del pokemon a ingresar: ")
    cur.execute("SELECT * FROM POYO WHERE nombre=?",(inPok))
    pok=cur.fetchone()#devuelve una tupla con todos los datos del pokemon solicitados
    cur.execute("SELECT id FROM SANSANITO")
    lenghtList=cur.fetchall()#devuelve una lista con todos los id
    lenght=len(lenghtList)#se usa el largo de la lista para ver cuantos pokemones hay
    if lenght<50:
        (dex, nom, typ1, typ2, hp, legen)=pok #descomprime la tupla
        hpAct=int(input("Ingrese el hp actual (debe ser menor o igual a "+str(hp)+"): "))
        state=createState() #llama a la funcion auxiliar para determinar el estado
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
    input("Pulse ENTER para continuar")

def read():
    print("Escoja una opcion")
    print("1. Mostrar estadisticas de un pokemon")
    print("2. Mostrar estadisticas de todos los pokemones")
    inp=int(input("Opcion: "))
    if inp==1:
        pokeID=int(input("Ingrese el ID del pokemon que desea verificar: "))
        cur.execute("SELECT * FROM SANSANITO WHERE id=?",(pokeID)) #recibe todos los datos de la fila con la id dada
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
        if estado==None:
            estado="Sin estado"
        print("|ID:",idd,"|Pokedex:",dex,"|Nombre:",nom,"|Tipo:",tipo,"|HP Actual:",hpAct,"|HP Max:",hp,"|Es legendario:",leg,"|Estado:",estado,"|fecha y hora de ingreso:",fecha,"|Prioridad",prio,"|")
    elif inp==2:
        cur.execute("SELECT * FROM SANSANITO") #recibe todos los datos de todas las filas
        pokeList=cur.fetchall()
        for poke in pokeList: #recorre la lista con las tuplas de cada fila
            (idd, dex, nom, typ1, typ2, hpAct, hp, legen, estado, fecha, prio)=poke #descomprime la tupla correspondiente a una fila de la tabla
            if typ2==None:
                tipo=typ1
            else:
                tipo=str(typ1)+" y "+str(typ2)
            if legen=='1':
                leg="Si"
            else:
                leg="No"
            if estado==None:
                estado="Sin estado"
            print("|ID:",idd,"|Pokedex:",dex,"|Nombre:",nom,"|Tipo:",tipo,"|HP Actual:",hpAct,"|HP Max:",hp,"|Es legendario:",leg,"|Estado:",estado,"|fecha y hora de ingreso:",fecha,"|Prioridad",prio,"|")
    input("Pulse ENTER para continuar")

def update():
    pokeID=input("Seleccione el ID del pokemon a modificar: ")
    cur.execute("SELECT * FROM SANSANITO WHERE id=?",(pokeID)) #recibe todos los datos de la fila con la id dada
    poke=cur.fetchone()
    (idd, dex, nom, typ1, typ2, hpAct, hp, legen, estado, fecha, prio)=poke
    while True:
        print("Ingrese el parametro que desea editar:")
        print("1. HP Actual")
        print("2. Estado")
        print("0. Terminar de editar")
        inn=int(input("Opcion: "))
        if inn==0:
            break
        #incluir trigger para el calculo de la prioridad
        elif inn==1: #cambiar el hp actual
            newHp=int(input("Ingrese el hp actual (debe ser menor o igual a "+str(hp)+"): "))
            cur.execute("UPDATE SANSANITO SET hp_actual=? WHERE id=?",(newHp,pokeID))
            cur.commit()
        elif inn==2: #cambiar el estado
            print("Ingrese el nuevo estado del pokemon:")
            print("1. Envenenado")
            print("2. Paralizado")
            print("3. Quemado")
            print("4. Dormido")
            print("5. Congelado")
            print("6. Sin estado")
            newEstado=int(input("Opcion: "))
            if newEstado==1:
                cur.execute("UPDATE SANSANITO SET estado='Envenenado' WHERE id=?",(pokeID))
                cur.commit()
            elif newEstado==2:
                cur.execute("UPDATE SANSANITO SET estado='Paralizado' WHERE id=?",(pokeID))
                cur.commit()
            elif newEstado==3:
                cur.execute("UPDATE SANSANITO SET estado='Quemado' WHERE id=?",(pokeID))
                cur.commit()
            elif newEstado==4:
                cur.execute("UPDATE SANSANITO SET estado='Dormido' WHERE id=?",(pokeID))
                cur.commit()
            elif newEstado==5:
                cur.execute("UPDATE SANSANITO SET estado='Congelado' WHERE id=?",(pokeID))
                cur.commit()
            elif newEstado==6:
                cur.execute("UPDATE SANSANITO SET estado=? WHERE id=?",(None,pokeID))
                cur.commit()
            else:
                print("Ingrese un estado valido")

def delete():
    pokeID=int(input("Ingrese la ID del pokemon a eliminar: "))
    cur.execute("SELECT nombre FROM SANSANITO WHERE id=?",(pokeID)) #compara la hora de netrada con la hora registrada para obtener el id
    nom=cur.fetchone()[0]
    cur.execute("DELETE FROM SANSANITO WHERE id=?",(pokeID))
    cur.commit()
    print("Se ha eliminado a",nom,"con el ID",pokeID)
    input("Pulse ENTER para continuar")

def top10max():
    cur.execute("SELECT prioridad,id,nombre FROM SANSANITO ORDER BY prioridad DESC")
    pokeList=cur.fetchall()
    cont=0
    for poke in pokeList:
        (prio, idd, nom)=poke
        if cont<10:
            print("|ID:",idd,"|Nombre:",nom,"|Prioridad:",prio,"|")
    input("Pulse ENTER para continuar")

def top10min():
    cur.execute("SELECT prioridad,id,nombre FROM SANSANITO ORDER BY prioridad ASC")
    pokeList=cur.fetchall()
    cont=0
    for poke in pokeList:
        (prio, idd, nom)=poke
        if cont<10:
            print("|ID:",idd,"|Nombre:",nom,"|Prioridad:",prio,"|")
    input("Pulse ENTER para continuar")

def pokeTime():
    cur.execute("SELECT fechyhora,id,nombre FROM SANSANITO ORDER BY fechyhora ASC")
    poke=cur.fetchone()
    (fecha, idd, nom)=poke
    print("|ID:",idd,"|Nombre:",nom,"|Fecha y hora de ingreso:",fecha,"|")
    input("Pulse ENTER para continuar")

def pokeState():
    print("Ingrese el estado que desea ver:")
    print("1. Envenenado")
    print("2. Paralizado")
    print("3. Quemado")
    print("4. Dormido")
    print("5. Congelado")
    print("6. Sin estado")
    userState=int(input("Opcion: "))
    if userState==1:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado='Envenenado'")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            for poke in pokeList:
                (idd, nom, state)=poke
                print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
    elif userState==2:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado='Paralizado'")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            for poke in pokeList:
                (idd, nom, state)=poke
                print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
    elif userState==3:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado='Quemado'")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            for poke in pokeList:
                (idd, nom, state)=poke
                print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
    elif userState==4:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado='Dormido'")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            for poke in pokeList:
                (idd, nom, state)=poke
                print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
    elif userState==5:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado='Congelado'")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            for poke in pokeList:
                (idd, nom, state)=poke
                print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
    elif userState==6:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado IS NULL")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            for poke in pokeList:
                (idd, nom, state)=poke
                print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
    input("Pulse ENTER para continuar")

def printPrioridad():
    cur.execute("SELECT nombre,hp_actual,hp_max,prioridad FROM SANSANITO ORDER BY prioridad DESC")
    pokeList=cur.fetchall()
    for poke in pokeList:
        (nom,hpAct,hp,prio)=poke
        print("|Nombre:",nom,"|HP Actual:",hpAct,"|HP Max",hp,"|Prioridad:",prio,"|")
    input("Pulse ENTER para continuar")

def repetido():
    cur.execute("SELECT nombre, COUNT( nombre ) AS total FROM SANSANITO GROUP BY nombre ORDER BY total DESC ")
    repe=cur.fetchall()
    if repe[0][1]==1:
        print("No hay pokemones repetidos")
    else:
        print("El pokemon mas repetido es",repe[0][0],"con",int(repe[0][1]),"repeticiones")
    input("Pulse ENTER para continuar")

#Main
print("Bienvenido(a) al Sansanito Pokemon!")
#poyo_table()
#sansanito_table()
while True:
    print("Ingrese la accion que desea hacer: ")
    print("1. Operaciones CRUD")
    print("2. Ingresar un pokemon")
    print("3. Ver los 10 pokemones con mayor prioridad")
    print("4. Ver los 10 pokemones con menor prioridad")
    print("5. Ver todos los pokemones con un estado especifico")
    print("6. Ver todos los pokemones legendarios")
    print("7. Ver el pokemon que lleva mas tiempo ingresado")
    print("8. Ver el pokemon mas repetido")
    print("9. Ver nombre, HP actual, HP Max y prioridad de todos los Pokemon, ordenados por prioridad")
    print("0. Salir")
    user=int(input("Opcion: "))
    if user==0:
        break
    elif user==1:
        while True:
            print("Ingrese la accion que desea hacer: ")
            print("1. Create")
            print("2. Read")
            print("3. Update")
            print("4. Delete")
            print("0. Volver")
            userCRUD=int(input("Opcion: "))
            if userCRUD==0:
                break
            elif userCRUD==1:
                create()
            elif userCRUD==2:
                read()
            elif userCRUD==3:
                update()
            elif userCRUD==4:
                delete()
            else:
                print("Ingrese una opcion valida")
    elif user==2:
        create()##cambiar
    elif user==3:
        top10max()
    elif user==4:
        top10min()
    elif user==5:
        pokeState()
    elif user==7:
        pokeTime()
    elif user==8:
        repetido()
    elif user==9:
        printPrioridad()
    else:
        print("Ingrese una opcion valida")

"""
util para hacer el relleno artificial
hpAct=choice(range(int(hp)))#va entre 0-(hp-1)
stateList=["Envenenado", "Paralizado", "Quemado", "Dormido", "Congelado", None]
state=choice(stateList)
"""
