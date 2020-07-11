from flask import Flask  # Flask es una clase del módulo flask
from flask import request

# -----------------------------------------------------------------------------

# Esto se encarga de lidiar con los namespace en python
# Le indica a flask que la aplicación apunte siempre a sí misma
# Si ejecutas directamente este scrip, es lo que se va a ejecutar en la consola
# Si se llama desde otro sitio servirá como utilidad
app = Flask(__name__)  # Instancia de una aplicación de flask
# No puede haber dos vistas con el mismo nombre


@app.route('/')  # Vista principal.
@app.route('/<name>')  # Vista principal.
# <name> indica que todo lo que vaya despues de '/' sera la variable name
# De esta manera, si no encuentra nada después de la barra dará error (404)
# Flask resuelve este problema dando la posibilidad de añadir más rutas
def index(name='Mundo'):
    '''Función Principal'''

    # Si no hay parámetro name en el navegador, usará el name por defecto
    name = request.args.get('name', name)  # Busca el parámetro name en la dir.
    return "Hola {}. Mi primera aplicación de Flask.".format(name)


@app.route('/add/<int:num1>/<int:num2>')  # Se ponen tantas como posibilidades
@app.route('/add/<float:num1>/<float:num2>')
@app.route('/add/<int:num1>/<float:num2>')
@app.route('/add/<float:num1>/<int:num2>')
def add(num1, num2):
    '''Suma dos numeros de la barra de direcciones'''

    return """
        <!doctype html>
        <html>
            <head>
                <title>Sumador</title>
            </head>
            <body>
                <h1>
                    add: {} + {} = {}
                </h1>
            </body>
        </html>
        """.format(num1, num2, num1 + num2)

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

# -----------------------------------------------------------------------------
# Lección 25. URLs

# Se debe tratar de hacer legibles y cortas las urls
# Cambiar /name=Guille por -> /Guille directamente

# -----------------------------------------------------------------------------
# Lección 27. Desplegando HTML

# Ahora se intenta mejorar el aspecto del sitio web
# Hay dos maneras de desplegar HTML; Una larga y otra corta
# Manera Larga: poner el html como respuesta
