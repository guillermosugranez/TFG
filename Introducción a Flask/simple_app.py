from flask import Flask  # Flask es una clase del módulo flask
from flask import request  # Para los parámetros de la URL
from flask import render_template  # Despliega una template con información

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

    context = {'name': name}
    return render_template('index.html', **context)


@app.route('/add/<int:num1>/<int:num2>')  # Se ponen tantas como posibilidades
@app.route('/add/<float:num1>/<float:num2>')
@app.route('/add/<int:num1>/<float:num2>')
@app.route('/add/<float:num1>/<int:num2>')
def add(num1, num2):
    '''Suma dos numeros de la barra de direcciones'''

    # Se entregan las variables como parámetros
    # Así, el HTML puede usarlas
    # Hay que especificar el nombre de la variable que se usará en el HTML
    # Para no enviar muchas variables, se usa un diccionario (context)
    # El diccionario se envía desempaquetado(**)
    # No tienes que extraer las variables en el otro extremo
    context = {"num1": num1, "num2": num2}
    return render_template("add.html", **context)

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
# Esto no es una buena solución por muchos motivos (largo, no reutilizable...)

# -----------------------------------------------------------------------------
# Lección 28. Desplegando HTML Templates

# Los templates representan el HTML de la aplicación
# Se guardan en una carpeta aparte. Por defecto es templates
# Flask por defecto irá hasta allí a buscarlas si las necesita

# -----------------------------------------------------------------------------
# Lección 29. Herencia de templates

# Si las templates son muy parecidas, se pueden generalizar y ahorrar código
# Se usan bloques html ({% block %}), con solo un par de llaves
# Para imprimir las variables se tienen que usar dos pares de llaves
# Se hacen diferentes tipos de bloques (content, title, head...)

# -----------------------------------------------------------------------------
# Lección 30. Archivos estáticos (css)

# Los arhivos estáticos se guardan en static por defecto (como los templates)
# Se suele enlazar en html con el tag link
# El atributo rel, define un enlace hacía un recurso externo
# Si el recurso externo es una hoja de estilo se usa rel="stylesheet"
# href indica la ubicación del recurso externo
