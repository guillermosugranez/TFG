from flask import Flask  # Flask es una clase del módulo flask

# -----------------------------------------------------------------------------

# Esto se encarga de lidiar con los namespace en python
# Le indica a flask que la aplicación apunte siempre a sí misma
# Si ejecutas directamente este scrip, es lo que se va a ejecutar en la consola
# Si se llama desde otro sitio servirá como utilidad
app = Flask(__name__)  # Instancia de una aplicación de flask


@app.route('/')  # Vista principal. Cuando los usuarios no ponen nada más
def index():  # No puede haber dos vistas con el mismo nombre
    '''Primera función '''

    return "Hola mundo! Mi primera aplicación de Flask."


@app.route('/Guille')  # Vista principal. Cuando los usuarios no ponen nada más
def guille():  # No puede haber dos vistas con el mismo nombre
    '''Segunda función '''

    return "Hola soy Aldo!!, que diga... Guille"

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

# Al arrancar la app tal cual, en el navegador aparece not found
# No maneja la URL proporcionada, no sabe qué tiene que hacer
# ¿Cómo maneja la app las direcciones URL que obtenga del navegador?
#   - A través de vistas y routes

# Vista: Método que despliega contenido en el navegador según URL (Route)
