# g es un objeto global donde guardar la info de la app que queramos
# Como es global, es accesible en todo el proyecto.
# Para la ocasión, se usará para 
from flask import Flask, g 

import models

DEBUG = True  # Mayúsuculas indica que es global (por convenio)
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)  # Se instancia la aplicación

# Por convenino se usan (y se nombrar así) los siguientes métodos:
# El nombre de los métodos es opcional.
# Lo que hace que tengan la característica especial deseada es el decorador
# Un decorador es una función que envuelven a otras funciones. Empiezan por @


@app.before_request  # Decorador
def before_request():
    '''Método que se ejecuta antes de hacer una petición (request) a la bbdd.
    
    Establece las conexiones a la bbdd
    '''

    # Esta funcion verifica que el objeto g no tenga ya definido el atributo db
    # Esto evita errores al tratar de volver a definirlo.
    if not hasattr(g, 'db'):
        g.db = models.DB  # La bbdd es la definida en el archivo models
        g.db.connect()


@app.after_request
def after_request(response):  # response es la respuesta a la petición
    '''Método que se ejecuta después de hacer una petición (request) a la bbdd.
    
    Cierra las conexiones con la bbdd
    '''

    g.db.close()
    return response
    

if if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)

