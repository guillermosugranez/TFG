import datetime

from flask_login import UserMixin
from peewee import *
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase("social.db")

# Lo más esencial en una red social son los usuarios.
# Hay que definir un modelo que los represente


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=120)
    # Asegurarse de que now es el atributo y no la función
    joined_at = DateTimeField(default=datetime.datetime.now)

    # La clase Meta sirve para tener en cuenta los metadatos del modelo
    # Cualquier modelo necesita la class Meta
    # Añade información extra, al margen de los atributos, métodos... etc.
    class Meta:
        database = DATABASE  # Indica cuál es la bbdd del modelo
        # Indica cómo serán ordenados los registros cuando sean creados
        order_by = ("-joined_at",)

    # Nuevo método lección 51. (Método de instancia (del objeto User concreto))
    def get_posts(self):  # Primero coge todos, luego filtra al objeto que llama
        print("He llamado a get_post")
        return Post.select().where(Post.user == self)

    def get_stream(self):
        """Mostrar los post míos y de la gente que sigo"""

        # Devuelve todos los post
        return Post.select().where(  # de...
            # Un usuario que se encuentra en la lista de los que sigue
            (Post.user << self.following()) |
            (Post.user == self)  # ó del mismo usuario
        )


    def get_integrado(self):
        """Mostrar los post míos y de la gente que sigo"""

        # Devuelve todos los post
        return Integrado.select().where(  # de...
            # Un usuario que se encuentra en la lista de los que sigue
            (Integrado.user == self)  # ó del mismo usuario
        )


    def following(self):
        """Los usuarios que sigue el usuario actual"""

        return (
            User.select().join(  # Se usa el join porque se usan varias tablas
                Relationship, on=Relationship.to_user  # Todos los usuarios
            ).where(
                Relationship.from_user == self  # A los que sigue el actual user
            )
        )

    def followers(self):
        """Los usuarios que nos siguen"""

        return (
            User.select().join(  # Se usa el join porque se usan varias tablas
                Relationship, on=Relationship.from_user  # Todos los usuarios
            ).where(
                Relationship.to_user == self  # A los que sigue el actual user
            )
        )

    # Constructor
    # cls hace que el método sea de la misma clase, y no de la instancia
    # Esto es aconsejable por legibilidad entre otras cuestiones (PEP8)
    # permite hacer usuario = User.create_user(Guille,guille,guille)...
    # en lugar de:
    #   usuario = User() -> primero se crea la instancia
    #   usuario.create_user(aldo,aldo,aldo) -> luego se vuelve a crear?
    @classmethod
    def create_user(cls, username, email, password):
        try:
            with DATABASE.transaction():
                # Utiliza una transacción para realizar la operación de abajo
                # Esto previene que la bbdd pueda quedar bloqueada por un error
                cls.create(  # Crea un registro en la bbdd
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                )
        except IntegrityError:
            raise ValueError("User Already exists")


# class Post(Model):
#     """Pequeños mensajes que aparecen en el timeline de FaceSmash"""
#
#     # Qué es lo que tiene un post?
#     user = ForeignKeyField(  # Hace referencia a un usuario
#         User,  # A dónde apunta esta clave foránea? Hacia un usuario
#         related_name='posts',  # Nombre relacionado en la otra tabla
#
#     )
#     timestamp = DateTimeField(default=datetime.datetime.now)
#     content = TextField()
#
#     class Meta:
#         database = DATABASE
#
#         # La coma indica que es una tupla. Evita posibles errores
#         order_by = ('-joined_at',)


# class Relationship(Model):
#     """ Representa que un usuario (from) sigue a otro (to)"""
#
#     from_user = ForeignKeyField(User, related_name='relationships')
#     to_user = ForeignKeyField(User, related_name='related_to')
#
#     class Meta:
#         database = DATABASE
#         # Atributo indexes. Sirve para:
#         # - Buscar más rápidamente en la bbdd
#         # - Definir relaciones únicas. No seguir a un mismo usuario más de 1 vez
#         indexes = (
#             (('from_user', 'to_user'), True),
#         )


class Tecnico(Model):
    """"""

    nombre_tecnico = CharField(unique=True, null=False, primary_key=True)

    class Meta:
        database = DATABASE

    @classmethod
    def create_tecnico(cls, nombre_tecnico):
        try:
            with DATABASE.transaction():
                # Utiliza una transacción para realizar la operación de abajo
                # Esto previene que la bbdd pueda quedar bloqueada por un error
                cls.create(  # Crea un registro en la bbdd
                    nombre_tecnico=nombre_tecnico,
                )
        except IntegrityError:
            raise ValueError("Tecnico Already exists")


class Provincia(Model):
    """"""

    nombre_provincia = CharField(unique=True, null=False, primary_key=True)

    class Meta:
        database = DATABASE

    @classmethod
    def create_provincia(cls, nombre_provincia):
        try:
            with DATABASE.transaction():
                # Utiliza una transacción para realizar la operación de abajo
                # Esto previene que la bbdd pueda quedar bloqueada por un error
                cls.create(  # Crea un registro en la bbdd
                    nombre_provincia=nombre_provincia,
                )
        except IntegrityError:
            raise ValueError("Provincia Already exists")


class Fabrica(Model):
    """"""

    nombre_fabrica = CharField(unique=True, null=False, primary_key=True)

    class Meta:
        database = DATABASE

    @classmethod
    def create_fabrica(cls, nombre_fabrica):
        try:
            with DATABASE.transaction():
                # Utiliza una transacción para realizar la operación de abajo
                # Esto previene que la bbdd pueda quedar bloqueada por un error
                cls.create(  # Crea un registro en la bbdd
                    nombre_fabrica=nombre_fabrica,
                )
        except IntegrityError:
            raise ValueError("Fabrica Already exists")


class Poblacion(Model):
    """"""

    nombre_poblacion = CharField(unique=True, null=False, primary_key=True)

    class Meta:
        database = DATABASE

    @classmethod
    def create_poblacion(cls, nombre_poblacion):
        try:
            with DATABASE.transaction():
                # Utiliza una transacción para realizar la operación de abajo
                # Esto previene que la bbdd pueda quedar bloqueada por un error
                cls.create(  # Crea un registro en la bbdd
                    nombre_poblacion=nombre_poblacion,
                )
        except IntegrityError:
            raise ValueError("Poblacion Already exists")



class Integrado(Model):
    """Representa un granjero asociado a la integración"""

    user = ForeignKeyField(  # Los integrados los gestiona un usuario
        User,
        related_name='integrados',  # Nombre relacionado en la otra tabla

    )

    codigo = CharField(null=False)
    nombre_integrado = CharField(unique=True, null=False, primary_key=True)

    fabrica = ForeignKeyField(  # Los integrados los gestiona un usuario
        Fabrica,
        related_name='fabrica',  # Nombre relacionado en la otra tabla

    )

    poblacion = ForeignKeyField(  # Los integrados los gestiona un usuario
        Poblacion,
        related_name='poblacion',  # Nombre relacionado en la otra tabla
    )

    tecnico = ForeignKeyField(  # Los integrados los gestiona un usuario
        Tecnico,
        related_name='tecnico',  # Nombre relacionado en la otra tabla

    )

    provincia = ForeignKeyField(  # Los integrados los gestiona un usuario
        Provincia,
        related_name='provincia',  # Nombre relacionado en la otra tabla

    )

    ditancia = IntegerField(null=False)
    metros_cuadrados = IntegerField(null=False)

    joined_at = DateTimeField(default=datetime.datetime.now)
    # email = CharField(unique=True)
    # password = CharField(max_length=120)

    # La clase Meta sirve para tener en cuenta los metadatos del modelo
    # Cualquier modelo necesita la class Meta
    # Añade información extra, al margen de los atributos, métodos... etc.
    class Meta:
        database = DATABASE  # Indica cuál es la bbdd del modelo
        # Indica cómo serán ordenados los registros cuando sean creados
        order_by = ("-joined_at",)

    @classmethod
    def create_integrado(cls, user, codigo, tecnico, fabrica, nombre_integrado,
                         poblacion, provincia, ditancia, metros_cuadrados):
        try:
            with DATABASE.transaction():
                # Utiliza una transacción para realizar la operación de abajo
                # Esto previene que la bbdd pueda quedar bloqueada por un error
                cls.create(  # Crea un registro en la bbdd
                    user=user,
                    codigo=codigo,
                    tecnico=tecnico,
                    fabrica=fabrica,
                    nombre_integrado=nombre_integrado,
                    poblacion=poblacion,
                    provincia=provincia,
                    ditancia=ditancia,
                    metros_cuadrados=metros_cuadrados,
                )
        except IntegrityError:
            # raise ValueError("Integrado Already exists")
            pass


class Camada(Model):
    """Representa una camada de un granjero asociado"""

    integrado = ForeignKeyField(  # Hace referencia a un usuario
        Integrado,  # La clave foranea apunta hacia un integrado
        related_name='camadas',  # Nombre relacionado en la otra tabla
    )

    codigo_camada = CharField(unique=True, null=False, primary_key=True)

    medicamentos = FloatField(default=0.0, null=True)
    liquidacion = FloatField(default=0.0, null=True)
    pollos_entrados = IntegerField(default=0, null=True)
    pollos_salidos = IntegerField(default=0, null=True)
    porcentaje_bajas = FloatField(default=0.0, null=True)
    bajas_primera_semana = IntegerField(default=0, null=True)
    porcentaje_bajas_primera_semana = FloatField(default=0.0, null=True)
    kilos_carne = IntegerField(default=0, null=True)
    kilos_pienso = IntegerField(default=0, null=True)
    peso_medio = FloatField(default=0.0, null=True)
    indice_transformacion = FloatField(default=0.0, null=True)
    retribucion = FloatField(default=0.0, null=True)
    medicamentos_por_pollo = FloatField(default=0.0, null=True)
    rendimiento_metro_cuadrado = FloatField(default=0.0, null=True)
    pollo_metro_cuadrado = FloatField(default=0.0, null=True)
    kilos_consumidos_por_pollo_salido = FloatField(default=0.0, null=True)
    dias_media_retirada = FloatField(default=0.0, null=True)
    ganancia_media_diaria = FloatField(default=0.0, null=True)
    dias_primer_camion = IntegerField(default=0, null=True)
    peso_primer_dia = FloatField(default=0.0, null=True)
    peso_semana_1 = FloatField(default=0.0, null=True)
    peso_semana_2 = FloatField(default=0.0, null=True)
    peso_semana_3 = FloatField(default=0.0, null=True)
    peso_semana_4 = FloatField(default=0.0, null=True)
    peso_semana_5 = FloatField(default=0.0, null=True)
    peso_semana_6 = FloatField(default=0.0, null=True)
    peso_semana_7 = FloatField(default=0.0, null=True)
    fecha = DateField(formats='%d/%m/%Y', null=True)
    rendimiento = FloatField(default=0.0, null=True)
    FP = FloatField(default=0.0, null=True)
    bajas_matadero = IntegerField(default=0, null=True)
    decomisos_matadero = IntegerField(default=0, null=True)
    porcentaje_bajas_matadero = FloatField(default=0.0, null=True)
    porcentaje_decomisos = FloatField(default=0.0, null=True)

    # La clase Meta sirve para tener en cuenta los metadatos del modelo
    # Cualquier modelo necesita la class Meta
    # Añade información extra, al margen de los atributos, métodos... etc.
    class Meta:
        database = DATABASE  # Indica cuál es la bbdd del modelo
        # Indica cómo serán ordenados los registros cuando sean creados
        # order_by = ("-joined_at",)

    @classmethod
    def create_camada(cls, integrado, codigo_camada, medicamentos, liquidacion,
                      pollos_entrados,
                      pollos_salidos, porcentaje_bajas, bajas_primera_semana,
                      porcentaje_bajas_primera_semana, kilos_carne,
                      kilos_pienso, peso_medio, indice_transformacion,
                      retribucion, medicamentos_por_pollo,
                      rendimiento_metro_cuadrado, pollo_metro_cuadrado,
                      kilos_consumidos_por_pollo_salido, dias_media_retirada,
                      ganancia_media_diaria, dias_primer_camion,
                      peso_primer_dia, peso_semana_1, peso_semana_2,
                      peso_semana_3, peso_semana_4, peso_semana_5,
                      peso_semana_6, peso_semana_7, fecha, rendimiento,
                      FP, bajas_matadero, decomisos_matadero,
                      porcentaje_bajas_matadero, porcentaje_decomisos):
        try:
            with DATABASE.transaction():
                # Utiliza una transacción para realizar la operación de abajo
                # Esto previene que la bbdd pueda quedar bloqueada por un error
                cls.create(  # Crea un registro en la bbdd
                    integrado=integrado,
                    codigo_camada=codigo_camada,
                    medicamentos=medicamentos,
                    liquidacion=liquidacion,
                    pollos_entrados=pollos_entrados,
                    pollos_salidos=pollos_salidos,
                    porcentaje_bajas=porcentaje_bajas,
                    bajas_primera_semana=bajas_primera_semana,
                    porcentaje_bajas_primera_semana=porcentaje_bajas_primera_semana,
                    kilos_carne=kilos_carne,
                    kilos_pienso=kilos_pienso,
                    peso_medio=peso_medio,
                    indice_transformacion=indice_transformacion,
                    retribucion=retribucion,
                    medicamentos_por_pollo=medicamentos_por_pollo,
                    rendimiento_metro_cuadrado=rendimiento_metro_cuadrado,
                    pollo_metro_cuadrado=pollo_metro_cuadrado,
                    kilos_consumidos_por_pollo_salido=kilos_consumidos_por_pollo_salido,
                    dias_media_retirada=dias_media_retirada,
                    ganancia_media_diaria=ganancia_media_diaria,
                    dias_primer_camion=dias_primer_camion,
                    peso_primer_dia=peso_primer_dia,
                    peso_semana_1=peso_semana_1,
                    peso_semana_2=peso_semana_2,
                    peso_semana_3=peso_semana_3,
                    peso_semana_4=peso_semana_4,
                    peso_semana_5=peso_semana_5,
                    peso_semana_6=peso_semana_6,
                    peso_semana_7=peso_semana_7,
                    fecha=fecha,
                    rendimiento=rendimiento,
                    FP=FP,
                    bajas_matadero=bajas_matadero,
                    decomisos_matadero=decomisos_matadero,
                    porcentaje_bajas_matadero=porcentaje_bajas_matadero,
                    porcentaje_decomisos=porcentaje_decomisos,
                )
        except IntegrityError:
            # raise ValueError("Camada Already exists")
            pass


def initialize():
    """Crea las tablas del proyecto a partir de los modelos propuestos"""

    DATABASE.connect()  # Establece la conexión
    DATABASE.create_tables([User, Provincia, Poblacion, Fabrica, Tecnico, Integrado, Camada], safe=True)
    DATABASE.close()  # Se cierra

# -----------------------------------------------------------------------------
# Lección 34. UserMixin

# NO HAY QUE REIVENTAR LA RUEDA
# Para saber si un usuario está ya creado o no, si está logueado o no...
# Se debe usar otro módulo de la librería de Flask (flask-login)
# Esto ahorra mucho tiempo y evita posibles errores
# Para poder usar este módulo hay que ponerle al modelo un mix-in
# Un mixin es una clase diseñada para agregar funcionalidad a otras clases
# No tiene sentido usar un mixin por sí misma
# Se agrega el Mixin deseado desde los parámetros de la definición de clase
# Partes de este mixin:
#   - is_authenticated: Es true si el usuario ya inició sesión
#   - is_active:        True si el usuario ha verificado su eMail
#   - is_anonymous:     Para usuario anonimos
#   - get_id():         Regresa un unicode que hace único a cada usuario

# -----------------------------------------------------------------------------
# Lección 35. Encriptación y Hasing

# No guardar las password como texto plano.
# Se usarán algoritmos de hasing. La encriptación es obsoleta en este caso.
# Cuando se le pasa la función Hash a un texto, no hay manera de volver atrás
# Para poder usar esta funcionalidad en la aplicación se usa flask_bcrypt

# Al generar un password desde una cadena, el resultado es diferente cada vez:
#   >>> from flask_bcrypt import generate_password_hash
#   >>> generate_password_hash('aldo')
#   b'$2b$12$ke06Vq2J315W6fZX69mDxObFsOyfYrx5IX77DNhdjJVWsVj2HLTEC'
#   >>> generate_password_hash('aldo')
#   b'$2b$12$umfZGyJacQtTZDES0jh.c.dZcj5Y9FcsdhM8lgI5BmpqJBlgiTkRq'
#   >>>
# Para poder volver atrás:
#   >>> password_aldo = generate_password_hash('aldo')
#   >>> from flask_bcrypt import check_password_hash
#   >>> check_password_hash(password_aldo, 'aldo')
#   True
#   >>>

# -----------------------------------------------------------------------------
# Lección 39 - Creando nuestras tablas
#
# Hay que crear las tablas a partir de los modelos propuestos
# Por legibilidad, esta tarea se define en un método

# -----------------------------------------------------------------------------
# Lección 39 - Formularios
# La información en la web se recibe con formularios
# En este asunto, es muy importante la seguiradad y la integridad
# Para manejar formularios en flask, se usa flask_forms
