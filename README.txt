Nicolás Pujante 
201873533-7

Instrucciones:
	Se necesita Python 3 y tener pyodbc instalado en el PATH

Uso del Trigger:
	El trigger se utiliza para actualizar la prioridad de los pokemones
	al hacer un update a su HP actual o a su estado.

Uso de la View:
	La view creada es una tabla virtual que contiene a los legendarios que están
	en la tabla SANSANITO, se utiliza para el cálculo de espacio en el create, 
	ver si ya está el legendario en la tabla y para la función para printear los legendarios

Consideraciones:
	-Se considera que el usuario realiza inputs válidas
	-Al pedir el pokémon más repetido y haber un empate, se muestra el que aparezca primero
	en la tabla (alfabéticamente)
	-Al haber un empate de prioridad, el pokémon no entra al sansanito, la prioridad debe ser mayor
	-La fecha de ingreso de los pokemones es la fecha actual del equipo
	-Al rellenar la tabla artificialmente se ingresan pokemones aleatorios con hp actual y estado aleatorios,
	la fecha es la actual, así que al ver el más antiguo se ve por diferencia de milisegundos.
	-Si al empezar el programa no se quiere hacer un relleno artificial hay que comentar la línea 735 (función llenarArtificial() en el main)
	-Si se va a correr el programa en un equipo en donde no existen las tablas POYO y SANSANITO hay que comentar las líneas 20 y 46
	correspondiente a los DROP de cada tabla.
	-Si no se quiere reiniciar las tablas hay que comentar las líneas 731 y 732 (funciones poyo_table() y sansanito_table() en el main), esto
	hará que se puedan seguir usando las tablas creadas anteriormente.
	-La CRUD create y la opción ingresar pokemón del menú utilizan la misma función, ya que necesitan realizar el mismo proceso, pero se dan como opciones separadas en el menú
	tal como nombra el enunciado.