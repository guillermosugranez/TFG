from flask import Flask  # Flask es una clase del módulo flask

# -----------------------------------------------------------------------------

# Esto se encarga de lidiar con los namespace en python
# Le indica a flask que la aplicación apunte siempre a sí misma
# Si ejecutas directamente este scrip, es lo que se va a ejecutar en la consola
# Si se llama desde otro sitio servirá como utilidad
app = Flask(__name__)  # Instancia de una aplicación de flask

# Un script en flask se llama aplicación

# Ejecuta la aplicación de flask.
# debug=True para mostrar todos los errores que se produzcan
# Normalmente debug=False para pe. un servidor, un página pública...
# El puerto es 8000 porque normalmente es un puerto libre
# host='0.0.0.0' escucha todas las conexiones a nuestra computadora
# host='127.0.0.1' escucha solo las conexiones locales desde el propio PC
app.run(debug=True, port=8000, host='0.0.0.0')

