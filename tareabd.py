import pyodbc
from random import choice
from datetime import datetime

#Conexion con la base de datos
conn = pyodbc.connect("DRIVER={Oracle en OraDB18Home1};DBQ=XE;Uid=boji;Pwd=Compaq123;DATABASE=bojiBD")
cur = conn.cursor()

"""
Funcion: poyo_table

Input: Ninguno

Output: Ninguno

Funcionalidad: Crea la tabla POYO en la base de datos, lee el csv de los pokemones
                e ingresa todos los datos extraidos a la tabla.
"""
def poyo_table():
    cur.execute("DROP TABLE POYO") #comentar si no se han creado las tablas
    #inicia la tabla POYO
    cur.execute("CREATE TABLE POYO(pokedex INTEGER NOT NULL,nombre VARCHAR2(32) NOT NULL,type1 VARCHAR2(32) NOT NULL,type2 VARCHAR2(32),hp_total INTEGER NOT NULL,legendary CHAR(1) NOT NULL)")
    arch=open("pokemon.csv","r")
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

"""
Funcion: sansanito_table

Input: Ninguno

Output: Ninguno

Funcionalidad: Crea la tabla SANSANITO en la base de datos dejandola vacia
"""
def sansanito_table():
    cur.execute("DROP TABLE SANSANITO") #comentar si no se han creado las tablas
    cur.execute("CREATE TABLE SANSANITO(id INTEGER GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1) PRIMARY KEY, pokedex INTEGER NOT NULL,nombre VARCHAR2(32) NOT NULL,type1 VARCHAR2(32) NOT NULL,type2 VARCHAR2(32),hp_actual INTEGER NOT NULL ,hp_max INTEGER NOT NULL,legendary CHAR(1) NOT NULL, estado VARCHAR2(16), fechyhora DATE NOT NULL, prioridad INTEGER NOT NULL)")
    cur.commit()
    print("Se ha creado la tabla Sansanito de forma exitosa")

"""
Funcion: trigger_prioridad

Input: Ninguno

Output: Ninguno

Funcionalidad: Crea un disparador que actualiza la prioridad de los pokemon
                al hacer un update en la tabla SANSANITO
"""
def trigger_prioridad():
    cur.execute("""
    CREATE OR REPLACE TRIGGER prioridad BEFORE UPDATE ON SANSANITO FOR EACH ROW
    BEGIN
        IF :NEW.estado IS NOT NULL THEN 
            :NEW.prioridad := :NEW.hp_max - :NEW.hp_actual + 10; 
        END IF;
        IF :NEW.estado IS NULL THEN 
            :NEW.prioridad := :NEW.hp_max - :NEW.hp_actual; 
        END IF;
    END;
    """)
    cur.commit()

"""
Funcion: view_legendary

Input: Ninguno

Output: Ninguno

Funcionalidad: Crea una vista para guardar los pokemones legendarios ingresados
                en la tabla SANSANITO
"""
def view_legendary():
    cur.execute("CREATE OR REPLACE VIEW VW_LEGENDARIOS AS (SELECT ID, POKEDEX, NOMBRE, TYPE1, TYPE2, HP_ACTUAL, HP_MAX, LEGENDARY, ESTADO, FECHYHORA, PRIORIDAD FROM SANSANITO WHERE LEGENDARY='1')")
    cur.commit()

"""
Funcion: createState

Input: Ninguno

Output: String en caso de haber un estado, None en caso de no haber estado

Funcionalidad: Funcion auxiliar para insertar pokemones que determina el estado del pokemon, el cual retorna
                en forma de String o None
"""
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

"""
Funcion: create

Input: Ninguno

Output: Ninguno

Funcionalidad: Le pide al usuario el nombre de un pokemon para insertar en la tabla
                SANSANITO, obtiene los datos de este en la tabla POYO
                y dependiendo de la capacidad y ciertas condiciones el pokemon es
                admitido en la tabla SANSANITO o queda fuera
"""
def create():
    inPok=input("Ingrese el nombre del pokemon a ingresar: ")
    cur.execute("SELECT * FROM POYO WHERE nombre=?",(inPok))
    pok=cur.fetchone()#devuelve una tupla con todos los datos del pokemon solicitados
    cur.execute("SELECT COUNT( * ) FROM SANSANITO")
    lenPoke=int(cur.fetchone()[0])#devuelve el largo de la tabla
    cur.execute("SELECT COUNT( * ) FROM VW_LEGENDARIOS")
    lenLegen=int(cur.fetchone()[0])#devuelve el largo de la vista
    lenTotal=(lenPoke-lenLegen)+(lenLegen*5)
    (dex, nom, typ1, typ2, hp, legen)=pok #descomprime la tupla

    if lenTotal<50: #hay espacio para al menos un pokemon normal

        if legen=='0':
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
            print("Se ingreso el pokemon "+nom+" con el ID ",pokeId[0])

        elif legen=='1' and lenTotal<=45: #revisa si el pokemon a ingresar es legendario y hay espacio
            cur.execute("SELECT nombre FROM VW_LEGENDARIOS")
            legenLists=cur.fetchall()
            nombres=[] #lista con los nombres d elos legendarios en la tabla
            for tupla in legenLists:
                nombres.append(tupla[0])

            if len(legenLists)==0: #revisa si no hay legendarios en la tabla
                hpAct=int(input("Ingrese el hp actual (debe ser menor o igual a "+str(hp)+"): "))
                state=createState() #llama a la funcion auxiliar para determinar el estado
                if state!=None: #revisa si el pokemon tiene algun estado para agregar la prioridad
                    prio=(int(hp)-hpAct)+10
                else:
                    prio=(int(hp)-hpAct)
                date=datetime.now()
                cur.execute("INSERT INTO SANSANITO (pokedex,nombre,type1,type2,hp_actual,hp_max,legendary,estado,fechyhora,prioridad) VALUES (?,?,?,?,?,?,?,?,?,?)",(int(dex), nom, typ1, typ2, hpAct, int(hp), legen, state, date, prio))
                cur.commit()
                cur.execute("SELECT id FROM SANSANITO WHERE fechyhora=?",(date)) #compara la hora de netrada con la hora registrada para obtener el id
                pokeId=cur.fetchone()
                print("Se ingreso el pokemon "+nom+" con el ID ",pokeId[0])

            elif nom not in nombres: #revisa si no se ha ingresado el legendario que se quiere ingresar
                hpAct=int(input("Ingrese el hp actual (debe ser menor o igual a "+str(hp)+"): "))
                state=createState() #llama a la funcion auxiliar para determinar el estado
                if state!=None: #revisa si el pokemon tiene algun estado para agregar la prioridad
                    prio=(int(hp)-hpAct)+10
                else:
                    prio=(int(hp)-hpAct)
                date=datetime.now()
                cur.execute("INSERT INTO SANSANITO (pokedex,nombre,type1,type2,hp_actual,hp_max,legendary,estado,fechyhora,prioridad) VALUES (?,?,?,?,?,?,?,?,?,?)",(int(dex), nom, typ1, typ2, hpAct, int(hp), legen, state, date, prio))
                cur.commit()
                cur.execute("SELECT id FROM SANSANITO WHERE fechyhora=?",(date)) #compara la hora de netrada con la hora registrada para obtener el id
                pokeId=cur.fetchone()
                print("Se ingreso el pokemon "+nom+" con el ID ",pokeId[0])

            elif nom in nombres: #revisa si hay coincidencia de nombres
                print("El legendario que se quiere ingresar ya esta en el sistema")

        elif legen=='1' and lenTotal>45: #hay espacio para pokemones normales pero no para un legendario
            cur.execute("SELECT nombre FROM VW_LEGENDARIOS")
            legenLists=cur.fetchall()
            nombres=[] #lista con los nombres d elos legendarios en la tabla
            for tupla in legenLists:
                nombres.append(tupla[0])    

            if len(legenLists)==0: #revisa si no hay legendarios en la tabla
                print("No hay espacio en el sansanito para su pokemon") #solo se puede hacer espacio para un legendario sacando un legendario   

            elif nom in nombres: #revisa si hay coincidencia de nombres
                print("El legendario que se quiere ingresar ya esta en el sistema")

            else: #empieza a ver que legendario se puede sacar
                hpAct=int(input("Ingrese el hp actual (debe ser menor o igual a "+str(hp)+"): "))
                state=createState() #llama a la funcion auxiliar para determinar el estado
                if state!=None: #revisa si el pokemon tiene algun estado para agregar la prioridad
                    prio=(int(hp)-hpAct)+10
                else:
                    prio=(int(hp)-hpAct)
                date=datetime.now()
                cur.execute("SELECT nombre,prioridad,id FROM VW_LEGENDARIOS ORDER BY prioridad ASC")
                legenPrio=cur.fetchone()
                
                if legenPrio[1]<prio: #el pokemon ingresado tiene mas prioridad que el de menor prioridad de la tabla
                    cur.execute("INSERT INTO SANSANITO (pokedex,nombre,type1,type2,hp_actual,hp_max,legendary,estado,fechyhora,prioridad) VALUES (?,?,?,?,?,?,?,?,?,?)",(int(dex), nom, typ1, typ2, hpAct, int(hp), legen, state, date, prio))
                    cur.commit()
                    cur.execute("SELECT id FROM SANSANITO WHERE fechyhora=?",(date)) #compara la hora de entrada con la hora registrada para obtener el id
                    pokeId=cur.fetchone()
                    print("Se ingreso el pokemon "+nom+" con el ID ",pokeId[0])
                    cur.execute("DELETE FROM SANSANITO WHERE id=?",(legenPrio[2]))
                    cur.commit()
                    print("Se ha eliminado a",legenPrio[0],"con el ID",legenPrio[2],"ya que se necesitaba espacio en el Sansanito")

                else:
                    print("Tu pokemon no tiene la suficiente prioridad para entrar al Sansanito lleno")      

    else: #el sansanito esta lleno
        cur.execute("SELECT nombre FROM VW_LEGENDARIOS")
        legenLists=cur.fetchall()
        nombres=[] #lista con los nombres d elos legendarios en la tabla
        for tupla in legenLists:
            nombres.append(tupla[0])
        if legen=='0':
            hpAct=int(input("Ingrese el hp actual (debe ser menor o igual a "+str(hp)+"): "))
            state=createState() #llama a la funcion auxiliar para determinar el estado
            if state!=None: #revisa si el pokemon tiene algun estado para agregar la prioridad
                prio=(int(hp)-hpAct)+10
            else:
                prio=(int(hp)-hpAct)
            date=datetime.now()
            cur.execute("SELECT nombre,prioridad,id FROM SANSANITO ORDER BY prioridad ASC")
            pokePrio=cur.fetchone()
            
            if pokePrio[1]<prio: #el pokemon ingresado tiene mas prioridad que el de menor prioridad de la tabla
                cur.execute("INSERT INTO SANSANITO (pokedex,nombre,type1,type2,hp_actual,hp_max,legendary,estado,fechyhora,prioridad) VALUES (?,?,?,?,?,?,?,?,?,?)",(int(dex), nom, typ1, typ2, hpAct, int(hp), legen, state, date, prio))
                cur.commit()
                cur.execute("SELECT id FROM SANSANITO WHERE fechyhora=?",(date)) #compara la hora de entrada con la hora registrada para obtener el id
                pokeId=cur.fetchone()
                print("Se ingreso el pokemon "+nom+" con el ID ",pokeId[0])
                cur.execute("DELETE FROM SANSANITO WHERE id=?",(pokePrio[2]))
                cur.commit()
                print("Se ha eliminado a",pokePrio[0],"con el ID",pokePrio[2],"ya que se necesitaba espacio en el Sansanito")

            else:
                print("Tu pokemon no tiene la suficiente prioridad para entrar al Sansanito lleno")  
        
        elif nom in nombres: #revisa si hay coincidencia de nombres
                print("El legendario que se quiere ingresar ya esta en el sistema")

        else: #empieza a ver que legendario se puede sacar
                hpAct=int(input("Ingrese el hp actual (debe ser menor o igual a "+str(hp)+"): "))
                state=createState() #llama a la funcion auxiliar para determinar el estado
                if state!=None: #revisa si el pokemon tiene algun estado para agregar la prioridad
                    prio=(int(hp)-hpAct)+10
                else:
                    prio=(int(hp)-hpAct)
                date=datetime.now()
                cur.execute("SELECT nombre,prioridad,id FROM VW_LEGENDARIOS ORDER BY prioridad ASC")
                legenPrio=cur.fetchone()
                
                if legenPrio[1]<prio: #el pokemon ingresado tiene mas prioridad que el de menor prioridad de la tabla
                    cur.execute("INSERT INTO SANSANITO (pokedex,nombre,type1,type2,hp_actual,hp_max,legendary,estado,fechyhora,prioridad) VALUES (?,?,?,?,?,?,?,?,?,?)",(int(dex), nom, typ1, typ2, hpAct, int(hp), legen, state, date, prio))
                    cur.commit()
                    cur.execute("SELECT id FROM SANSANITO WHERE fechyhora=?",(date)) #compara la hora de entrada con la hora registrada para obtener el id
                    pokeId=cur.fetchone()
                    print("Se ingreso el pokemon "+nom+" con el ID ",pokeId[0])
                    cur.execute("DELETE FROM SANSANITO WHERE id=?",(legenPrio[2]))
                    cur.commit()
                    print("Se ha eliminado a",legenPrio[0],"con el ID",legenPrio[2],"ya que se necesitaba espacio en el Sansanito")

                else:
                    print("Tu pokemon no tiene la suficiente prioridad para entrar al Sansanito lleno")   

    input("Pulse ENTER para continuar")

"""
Funcion: read

Input: Ninguno

Output: Ninguno

Funcionalidad: Printea todos los datos de un pokemon de la tabla SANSANITO a eleccion del usuario
                a traves de su ID o printea todos los datos de todos los pokemones de la misma tabla
"""
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
        #print("|ID:",idd,"|Pokedex:",dex,"|Nombre:",nom,"|Tipo:",tipo,"|HP Actual:",hpAct,"|HP Max:",hp,"|Es legendario:",leg,"|Estado:",estado,"|fecha y hora de ingreso:",fecha,"|Prioridad",prio,"|")
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("|{:^8}|{:^10}|{:^20}|{:^30}|{:^12}|{:^10}|{:^13}|{:^15}|{:^30}|{:^12}|".format("ID","Pokedex","Nombre","Tipo","HP Actual","HP Max","Legendario","Estado","Fecha y hora de ingreso","Prioridad"))
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("|{:^8}|{:^10}|{:^20}|{:^30}|{:^12}|{:^10}|{:^13}|{:^15}|{:^30}|{:^12}|".format(idd, dex, nom, tipo, hpAct, hp, leg, estado, str(fecha), prio))
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    elif inp==2:
        cur.execute("SELECT * FROM SANSANITO") #recibe todos los datos de todas las filas
        pokeList=cur.fetchall()
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("|{:^8}|{:^10}|{:^20}|{:^30}|{:^12}|{:^10}|{:^13}|{:^15}|{:^30}|{:^12}|".format("ID","Pokedex","Nombre","Tipo","HP Actual","HP Max","Legendario","Estado","Fecha y hora de ingreso","Prioridad"))
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
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
            #print("|ID:",idd,"|Pokedex:",dex,"|Nombre:",nom,"|Tipo:",tipo,"|HP Actual:",hpAct,"|HP Max:",hp,"|Es legendario:",leg,"|Estado:",estado,"|fecha y hora de ingreso:",fecha,"|Prioridad",prio,"|")
            print("|{:^8}|{:^10}|{:^20}|{:^30}|{:^12}|{:^10}|{:^13}|{:^15}|{:^30}|{:^12}|".format(idd, dex, nom, tipo, hpAct, hp, leg, estado, str(fecha), prio))
            print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    input("Pulse ENTER para continuar")

"""
Funcion: update

Input: Ninguno

Output: Ninguno

Funcionalidad: Le da la eleccion al usuario de cambiar el HP actual del pokemon
                o cambiar su estado a traves de su ID, el trigger hace que se actualice su prioridad
"""
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

"""
Funcion: delete

Input: Ninguno

Output: Ninguno

Funcionalidad: Borra un pokemon de la tabla SANSANITO a eleccion del usuario
                a traves del ID del pokemon
"""
def delete():
    pokeID=int(input("Ingrese la ID del pokemon a eliminar: "))
    cur.execute("SELECT nombre FROM SANSANITO WHERE id=?",(pokeID)) #compara la hora de netrada con la hora registrada para obtener el id
    nom=cur.fetchone()[0]
    cur.execute("DELETE FROM SANSANITO WHERE id=?",(pokeID))
    cur.commit()
    print("Se ha eliminado a",nom,"con el ID",pokeID)
    input("Pulse ENTER para continuar")

"""
Funcion: top10max

Input: Ninguno

Output: Ninguno

Funcionalidad: Printea el ID, el nombre y la prioridad de los 10 pokemones
                 con mayor prioridad de la tabla SANSANITO
"""
def top10max():
    cur.execute("SELECT prioridad,id,nombre FROM SANSANITO ORDER BY prioridad DESC")
    pokeList=cur.fetchall()
    cont=0
    print("--------------------------------------------")
    print("|{:^8}|{:^20}|{:^12}|".format("ID","Nombre","Prioridad"))
    print("--------------------------------------------")
    for poke in pokeList:
        (prio, idd, nom)=poke
        if cont<10:
            #print("|ID:",idd,"|Nombre:",nom,"|Prioridad:",prio,"|")
            print("|{:^8}|{:^20}|{:^12}|".format(idd, nom, prio))
            print("--------------------------------------------")
            cont+=1
        else:
            break
    input("Pulse ENTER para continuar")

"""
Funcion: top10min

Input: Ninguno

Output: Ninguno

Funcionalidad: Printea el ID, el nombre y la prioridad de los 10 pokemones
                 con menor prioridad de la tabla SANSANITO
"""
def top10min():
    cur.execute("SELECT prioridad,id,nombre FROM SANSANITO ORDER BY prioridad ASC")
    pokeList=cur.fetchall()
    cont=0
    print("--------------------------------------------")
    print("|{:^8}|{:^20}|{:^12}|".format("ID","Nombre","Prioridad"))
    print("--------------------------------------------")
    for poke in pokeList:
        (prio, idd, nom)=poke
        if cont<10:
            #print("|ID:",idd,"|Nombre:",nom,"|Prioridad:",prio,"|")
            print("|{:^8}|{:^20}|{:^12}|".format(idd, nom, prio))
            print("--------------------------------------------")
            cont+=1
        else:
            break
    input("Pulse ENTER para continuar")

"""
Funcion: pokeTime

Input: Ninguno

Output: Ninguno

Funcionalidad: Printea el ID, el nombre y la fecha y hora de ingreso
                del pokemon que lleva mas tiempo en la tabla SANSANITO
"""
def pokeTime():
    cur.execute("SELECT fechyhora,id,nombre FROM SANSANITO ORDER BY fechyhora ASC")
    poke=cur.fetchone()
    (fecha, idd, nom)=poke
    #print("|ID:",idd,"|Nombre:",nom,"|Fecha y hora de ingreso:",fecha,"|")
    print("--------------------------------------------------------------")
    print("|{:^8}|{:^20}|{:^30}|".format("ID","Nombre","Fecha y hora de ingreso"))
    print("--------------------------------------------------------------")
    print("|{:^8}|{:^20}|{:^30}|".format(idd, nom, str(fecha)))
    print("--------------------------------------------------------------")
    input("Pulse ENTER para continuar")

"""
Funcion: pokeState

Input: Ninguno

Output: Ninguno

Funcionalidad: Printea el ID, el nombre y el estado de todos los pokemones
                que tengan el estado ingresado por el usuario
"""
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
            print("-----------------------------------------------")
            print("|{:^8}|{:^20}|{:^15}|".format("ID","Nombre","Estado"))
            print("-----------------------------------------------")
            for poke in pokeList:
                (idd, nom, state)=poke
                #print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
                print("|{:^8}|{:^20}|{:^15}|".format(idd, nom, state))
                print("-----------------------------------------------")
    elif userState==2:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado='Paralizado'")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            print("-----------------------------------------------")
            print("|{:^8}|{:^20}|{:^15}|".format("ID","Nombre","Estado"))
            print("-----------------------------------------------")
            for poke in pokeList:
                (idd, nom, state)=poke
                #print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
                print("|{:^8}|{:^20}|{:^15}|".format(idd, nom, state))
                print("-----------------------------------------------")
    elif userState==3:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado='Quemado'")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            print("-----------------------------------------------")
            print("|{:^8}|{:^20}|{:^15}|".format("ID","Nombre","Estado"))
            print("-----------------------------------------------")
            for poke in pokeList:
                (idd, nom, state)=poke
                #print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
                print("|{:^8}|{:^20}|{:^15}|".format(idd, nom, state))
                print("-----------------------------------------------")
    elif userState==4:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado='Dormido'")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            print("-----------------------------------------------")
            print("|{:^8}|{:^20}|{:^15}|".format("ID","Nombre","Estado"))
            print("-----------------------------------------------")
            for poke in pokeList:
                (idd, nom, state)=poke
                #print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
                print("|{:^8}|{:^20}|{:^15}|".format(idd, nom, state))
                print("-----------------------------------------------")
    elif userState==5:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado='Congelado'")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            print("-----------------------------------------------")
            print("|{:^8}|{:^20}|{:^15}|".format("ID","Nombre","Estado"))
            print("-----------------------------------------------")
            for poke in pokeList:
                (idd, nom, state)=poke
                #print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
                print("|{:^8}|{:^20}|{:^15}|".format(idd, nom, state))
                print("-----------------------------------------------")
    elif userState==6:
        cur.execute("SELECT id,nombre,estado FROM SANSANITO WHERE estado IS NULL")
        pokeList=cur.fetchall()
        if len(pokeList)==0:
            print("No hay pokemones con ese estado")
        else:
            print("-----------------------------------------------")
            print("|{:^8}|{:^20}|{:^15}|".format("ID","Nombre","Estado"))
            print("-----------------------------------------------")
            for poke in pokeList:
                (idd, nom, state)=poke
                state="Sin estado"
                #print("|ID:",idd,"|Nombre:",nom,"|Estado:",state,"|")
                print("|{:^8}|{:^20}|{:^15}|".format(idd, nom, state))
                print("-----------------------------------------------")
    input("Pulse ENTER para continuar")
"""
Funcion: printPrioridad

Input: Ninguno

Output: Ninguno

Funcionalidad: Printea el nombre, el HP actual, el HP maximo y la prioridad 
                de todos los pokemon que hay en la tabla SANSANITO ordenados por prioridad
"""
def printPrioridad():
    cur.execute("SELECT nombre,hp_actual,hp_max,prioridad FROM SANSANITO ORDER BY prioridad DESC")
    pokeList=cur.fetchall()
    print("-----------------------------------------------------------")
    print("|{:^20}|{:^12}|{:^10}|{:^12}|".format("Nombre","HP Actual","HP Max","Prioridad"))
    print("-----------------------------------------------------------")
    for poke in pokeList:
        (nom,hpAct,hp,prio)=poke
        #print("|Nombre:",nom,"|HP Actual:",hpAct,"|HP Max",hp,"|Prioridad:",prio,"|")
        print("|{:^20}|{:^12}|{:^10}|{:^12}|".format(nom, hpAct, hp, prio))
        print("-----------------------------------------------------------")
    input("Pulse ENTER para continuar")
"""
Funcion: repetido

Input: Ninguno

Output: Ninguno

Funcionalidad: Printea el nombre del pokemon mas repetido en la
                tabla SANSANITO y muestra la cantidad de repeticiones,
                en caso de empate, escoge por orden alfabetico
"""
def repetido():
    cur.execute("SELECT nombre, COUNT( nombre ) AS total FROM SANSANITO GROUP BY nombre ORDER BY total DESC")
    repe=cur.fetchall()
    if repe[0][1]==1:
        print("No hay pokemones repetidos")
    else:
        print("El pokemon mas repetido es",repe[0][0],"con",int(repe[0][1]),"repeticiones")
    input("Pulse ENTER para continuar")
"""
Funcion: printLegendarios

Input: Ninguno

Output: Ninguno

Funcionalidad: Printea todos los datos de los legendarios que estan
                en la tabla SANSANITO utilizando la vista creada
"""
def printLegendarios():
    cur.execute("SELECT * FROM VW_LEGENDARIOS")
    legenList=cur.fetchall()
    if len(legenList)==0:
        print("No hay pokemones legendarios ingresados")
    else:
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("|{:^8}|{:^10}|{:^20}|{:^30}|{:^12}|{:^10}|{:^13}|{:^15}|{:^30}|{:^12}|".format("ID","Pokedex","Nombre","Tipo","HP Actual","HP Max","Legendario","Estado","Fecha y hora de ingreso","Prioridad"))
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        for legen in legenList:
            (idd, dex, nom, typ1, typ2, hpAct, hp, legen, estado, fecha, prio)=legen #descomprime la tupla correspondiente a una fila de la tabla
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
            #print("|ID:",idd,"|Pokedex:",dex,"|Nombre:",nom,"|Tipo:",tipo,"|HP Actual:",hpAct,"|HP Max:",hp,"|Es legendario:",leg,"|Estado:",estado,"|fecha y hora de ingreso:",fecha,"|Prioridad",prio,"|")
            print("|{:^8}|{:^10}|{:^20}|{:^30}|{:^12}|{:^10}|{:^13}|{:^15}|{:^30}|{:^12}|".format(idd, dex, nom, tipo, hpAct, hp, leg, estado, str(fecha), prio))
            print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    input("Pulse ENTER para continuar")
"""
Funcion: llenarArtificial

Input: Ninguno

Output: Ninguno

Funcionalidad: Rellena los 50 espacios disponibles de la tabla SANSANITO
                con pokemones aleatorios, hp actual aleatoria y estado aleatorio
"""
def llenarArtificial():
    cont=0
    espacio=0
    while cont!=50:
        pokedexx=choice(range(721))+1
        cur.execute("SELECT * FROM POYO WHERE pokedex=?",(pokedexx))
        pok=cur.fetchone()#devuelve una tupla con todos los datos del pokemon solicitados
        (dex, nom, typ1, typ2, hp, legen)=pok #descomprime la tupla
        if legen=='1':
            if cont<=45:
                cont+=5
            else:
                continue
        else:
            cont+=1
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
        #print("Se ingreso el pokemon "+nom+" con el ID ",pokeId[0])


#Main
print("Bienvenido(a) al Sansanito Pokemon!")
poyo_table()
sansanito_table()
trigger_prioridad()
view_legendary()
llenarArtificial()
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
        create()
    elif user==3:
        top10max()
    elif user==4:
        top10min()
    elif user==5:
        pokeState()
    elif user==6:
        printLegendarios()
    elif user==7:
        pokeTime()
    elif user==8:
        repetido()
    elif user==9:
        printPrioridad()
    else:
        print("Ingrese una opcion valida")