from flask import Flask  # Flask es una clase del módulo flask
from flask import request

# -----------------------------------------------------------------------------

# Esto se encarga de lidiar con los namespace en python
# Le indica a flask que la aplicación apunte siempre a sí misma
# Si ejecutas directamente este scrip, es lo que se va a ejecutar en la consola
# Si se llama desde otro sitio servirá como utilidad
app = Flask(__name__)  # Instancia de una aplicación de flask
# No puede haber dos vistas con el mismo nombre


@app.route('/')  # Vista principal. Cuando los usuarios no ponen nada más
# Añadida variable name. Por defecto name=Mundo
# Añadida variable lastname. Por defecto lastname=!!!!
def index(name='Mundo', lastname='!!!'):
    '''Primera función '''

    # Si no hay parámetro name en el navegador, usará el name por defecto
    name = request.args.get('name', name)  # Busca el parámetro name en la dir.
    lastname = request.args.get('lastname', lastname)
    return "Hola {} {}. Mi primera aplicación de Flask.".format(name, lastname)

# Un script en flask se llama aplicación
# Ejecuta la aplicación de flask.
# debug=True para mostrar todos los errores que se produzcan.
# Normalmente debug=False para un servidor, un página pública...
# El puerto es 8000 porque normalmente es un puerto libre.
# host='0.0.0.0' escucha todas las conexiones a nuestra computadora.
# host='127.0.0.1' escucha solo las conexiones locales desde el propio PC.
# Usar esta última en el navegador, si no no sale.
app.run(debug=True, port=8000, host='0.0.0.0')

# -----------------------------------------------------------------------------
# Lección 23. Route

# Al arrancar la app tal cual, en el navegador aparece not found
# No maneja la URL proporcionada, no sabe qué tiene que hacer
# ¿Cómo maneja la app las direcciones URL que obtenga del navegador?
#   - A través de vistas y routes

# Vista: Método que despliega contenido en el navegador según URL (Route)

# -----------------------------------------------------------------------------
# Lección 24. parámetros

# ¿Cómo tomar parámetros de las peticiones http?
# Una forma común es a través de los query parameters
# Son los que vienen después del signo de interrogación
# Formato: ?nombre=Guille&apellido=Sugráñez
# No se puede hacer una ruta para cada posible conjunto de parámetros
# Habría que usar una variable global que contenga toda la info de la request
# request es un objeto global que guarda toda la info de la petición http
# Como es una variable global, se puede acceder a ella desde donde sea
# Lo normal es manejarlo dentro de las vistas
