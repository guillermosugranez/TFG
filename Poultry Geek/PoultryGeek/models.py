from datetime import datetime
import numpy as np

from flask_login import UserMixin
from peewee import *
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('poultrygeek.db')

# Lo más esencial en una red social son los usuarios.
# Hay que definir un modelo que los represente


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True, null=False)
    password = CharField(max_length=120)
    # Asegurarse de que now es el atributo y no la función
    joined_at = DateTimeField(default=datetime.now)
    is_admin = BooleanField(default=False)
    is_active = BooleanField(default=False)

    # La clase Meta sirve para tener en cuenta los metadatos del modelo
    # Cualquier modelo necesita la class Meta
    # Añade información extra, al margen de los atributos, métodos... etc.
    class Meta:
        database = DATABASE  # Indica cuál es la bbdd del modelo
        # Indica cómo serán ordenados los registros cuando sean creados
        order_by = ("-joined_at",)


    @classmethod
    def create_user(cls, username, email, password, is_admin, is_active):
        try:
            with DATABASE.transaction():
                # Utiliza una transacción para realizar la operación de abajo
                # Esto previene que la bbdd pueda quedar bloqueada por un error
                cls.create(  # Crea un registro en la bbdd
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=is_admin,
                    is_active=is_active
                )
        except IntegrityError:
            raise ValueError("User Already exists")


    def get_camadas(self):
        """Devuelve un diccionario con todas las camadas asociadas"""

        # camadas = Camada.select().join(Integrado).where(Camada.integrado.user == self)
        camadas = Camada.select()

        return camadas


    @classmethod
    def user_is_active(cls, email):
        """Permite determinar si un usuario está dado de alta en el sistema
        a partir de su correo electrónico"""

        user = cls.select().where(cls.email == email).get()

        print("resultado en clase es:", user.is_active)

        return user.is_active


    # Métodos de instancia
    # def is_admin(self):
    #     return self.is_admin

    # Nuevo método lección 51. (Método de instancia (del objeto User concreto))
    # def get_posts(self):  # Primero coge todos, luego filtra al objeto que llama
    #     print("He llamado a get_post")
    #     return Post.select().where(Post.user == self)
    #
    # def get_stream(self):
    #     """Mostrar los post míos y de la gente que sigo"""
    #
    #     # Devuelve todos los post
    #     return Post.select().where(  # de...
    #         # Un usuario que se encuentra en la lista de los que sigue
    #         (Post.user << self.following()) |
    #         (Post.user == self)  # ó del mismo usuario
    #     )
    #
    #
    # def get_integrado(self):
    #     """Mostrar los post míos y de la gente que sigo"""
    #
    #     # Devuelve todos los post
    #     return Integrado.select().where(  # de...
    #         # Un usuario que se encuentra en la lista de los que sigue
    #         (Integrado.user == self)  # ó del mismo usuario
    #     )
    #
    #
    # def following(self):
    #     """Los usuarios que sigue el usuario actual"""
    #
    #     return (
    #         User.select().join(  # Se usa el join porque se usan varias tablas
    #             Relationship, on=Relationship.to_user  # Todos los usuarios
    #         ).where(
    #             Relationship.from_user == self  # A los que sigue el actual user
    #         )
    #     )
    #
    # def followers(self):
    #     """Los usuarios que nos siguen"""
    #
    #     return (
    #         User.select().join(  # Se usa el join porque se usan varias tablas
    #             Relationship, on=Relationship.from_user  # Todos los usuarios
    #         ).where(
    #             Relationship.to_user == self  # A los que sigue el actual user
    #         )
    #     )

    # Constructor
    # cls hace que el método sea de la misma clase, y no de la instancia
    # Esto es aconsejable por legibilidad entre otras cuestiones (PEP8)
    # permite hacer usuario = User.create_user(Guille,guille,guille)...
    # en lugar de:
    #   usuario = User() -> primero se crea la instancia
    #   usuario.create_user(aldo,aldo,aldo) -> luego se vuelve a crear?


# class Post(Model):
#     """Pequeños mensajes que aparecen en el timeline de Poultry Geek"""
#
#     # Qué es lo que tiene un post?
#     user = ForeignKeyField(  # Hace referencia a un usuario
#         User,  # A dónde apunta esta clave foránea? Hacia un usuario
#         related_name='posts',  # Nombre relacionado en la otra tabla
#
#     )
#     timestamp = DateTimeField(default=datetime.now)
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


class Provincia(Model):
    """"""

    id_provincia = AutoField()
    nombre_provincia = CharField(unique=True, null=False)

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


    @classmethod
    def get_list_provincias(cls):

        provincias_registradas = cls.select(
            cls.nombre_provincia).dicts()

        lista_provincias_registradas = []

        for provincia in provincias_registradas:
            lista_provincias_registradas.append(provincia['nombre_provincia'])

        print(lista_provincias_registradas)

        return lista_provincias_registradas


class Fabrica(Model):
    """"""

    id_fabrica = AutoField()
    nombre_fabrica = CharField(unique=True, null=False)

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


    @classmethod
    def get_list_fabricas(cls):

        fabricas_registradas = cls.select(
            cls.nombre_fabrica).dicts()

        lista_fabricas_registradas = []

        for fabrica in fabricas_registradas:
            lista_fabricas_registradas.append(fabrica['nombre_fabrica'])

        print(lista_fabricas_registradas)

        return lista_fabricas_registradas


class Poblacion(Model):
    """"""

    id_poblacion = AutoField()
    nombre_poblacion = CharField(unique=True, null=False)

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


    @classmethod
    def get_list_poblaciones(cls):

        poblaciones_registradas = cls.select(
            cls.nombre_poblacion).dicts()

        lista_poblaciones_registradas = []

        for poblacion in poblaciones_registradas:
            lista_poblaciones_registradas.append(poblacion['nombre_poblacion'])

        print(lista_poblaciones_registradas)

        return lista_poblaciones_registradas


class Tecnico(Model):
    """"""

    id_tecnico = AutoField()
    nombre_tecnico = CharField(unique=True, null=False)

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


    @classmethod
    def get_list_tecnicos(cls):

        tecnicos_registradas = cls.select(
            cls.nombre_tecnico).dicts()

        lista_tecnicos_registradas = []

        for tecnico in tecnicos_registradas:
            lista_tecnicos_registradas.append(tecnico['nombre_tecnico'])

        print(lista_tecnicos_registradas)

        return lista_tecnicos_registradas



class Integrado(Model):
    """Representa un granjero asociado a la integración"""

    id_integrado = AutoField()

    user = ForeignKeyField(  # Los integrados los gestiona un usuario
        User,
        related_name='integrados',  # Nombre relacionado en la otra tabla

    )

    codigo = CharField(unique=True, null=False)
    nombre_integrado = CharField(unique=False, null=False)

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

    joined_at = DateTimeField(default=datetime.now)
    # email = CharField(unique=True)
    # password = CharField(max_length=120)

    # La clase Meta sirve para tener en cuenta los metadatos del modelo
    # Cualquier modelo necesita la class Meta
    # Añade información extra, al margen de los atributos, métodos... etc.
    class Meta:
        database = DATABASE  # Indica cuál es la bbdd del modelo
        # Indica cómo serán ordenados los registros cuando sean creados
        order_by = ("-joined_at",)
        constraints = [
            Check('ditancia > 0'),
            Check('ditancia < 100000'),
            Check('metros_cuadrados > 0'),
            Check('metros_cuadrados < 100000'),
        ]

    # # Nuevo método lección 51. (Método de instancia (del objeto User concreto))
    # def get_posts(
    #         self):  # Primero coge todos, luego filtra al objeto que llama
    #     print("He llamado a get_post")
    #     return Integrado.select().where(Post.user == self)

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
                return "ok"
        except DatabaseError as err:
            if str(err) == "CHECK constraint failed: integrado":
                print(err)
                return "error"
            elif str(err) == "UNIQUE constraint failed: integrado.nombre_integrado":
                return "existe"
            else:
                return "desconocido"



class Camada(Model):
    """Representa una camada de un granjero asociado"""

    id_camada = AutoField()

    integrado = ForeignKeyField(  # Hace referencia a un usuario
        Integrado,  # La clave foranea apunta hacia un integrado
        related_name='camadas',  # Nombre relacionado en la otra tabla
    )
    codigo_camada = CharField(unique=True, null=False)
    fecha = DateField(null=False, formats="%Y-%m-%d")

    # Críticas
    pollos_entrados = FloatField(null=False)
    pollos_salidos = FloatField(null=False)
    porcentaje_bajas = FloatField(null=False)
    kilos_carne = FloatField(null=False)
    kilos_pienso = FloatField(null=False)
    peso_medio = FloatField(null=False)
    indice_transformacion = FloatField(null=False)
    retribucion = FloatField(null=False)
    medicamentos_por_pollo = FloatField(null=False)
    dias_media_retirada = FloatField(null=False)
    ganancia_media_diaria = FloatField(null=False)

    # Menos importantes
    bajas_primera_semana = FloatField(default=0, null=True)
    medicamentos = FloatField(default=0.0, null=True)
    liquidacion = FloatField(default=0.0, null=True)
    porcentaje_bajas_primera_semana = FloatField(default=0.0, null=True)
    rendimiento_metro_cuadrado = FloatField(default=0.0, null=True)
    pollo_metro_cuadrado = FloatField(default=0.0, null=True)
    kilos_consumidos_por_pollo_salido = FloatField(default=0.0, null=True)
    dias_primer_camion = FloatField(default=0, null=True)
    peso_primer_dia = FloatField(default=0.0, null=True)
    peso_semana_1 = FloatField(default=0.0, null=True)
    peso_semana_2 = FloatField(default=0.0, null=True)
    peso_semana_3 = FloatField(default=0.0, null=True)
    peso_semana_4 = FloatField(default=0.0, null=True)
    peso_semana_5 = FloatField(default=0.0, null=True)
    peso_semana_6 = FloatField(default=0.0, null=True)
    peso_semana_7 = FloatField(default=0.0, null=True)
    rendimiento = FloatField(default=0.0, null=True)
    FP = FloatField(default=0.0, null=True)
    bajas_matadero = FloatField(default=0, null=True)
    decomisos_matadero = FloatField(default=0, null=True)
    porcentaje_bajas_matadero = FloatField(default=0.0, null=True)
    porcentaje_decomisos = FloatField(default=0.0, null=True)

    # La clase Meta sirve para tener en cuenta los metadatos del modelo
    # Cualquier modelo necesita la class Meta
    # Añade información extra, al margen de los atributos, métodos... etc.
    class Meta:
        database = DATABASE  # Indica cuál es la bbdd del modelo
        order_by = ('-fecha',)
        constraints = [
            Check('pollos_entrados > 0'),
            Check('pollos_salidos > 0'),
            Check('porcentaje_bajas >= 0'),
            Check('porcentaje_bajas <= 1'),
            Check('kilos_carne > 0'),
            Check('kilos_pienso > 0'),
            Check('peso_medio > 0'),
            Check('peso_medio < 5'),
            Check('indice_transformacion > 0'),
            Check('indice_transformacion < 5'),
            Check('retribucion > 0'),
            Check('retribucion < 1'),
            Check('medicamentos_por_pollo > 0'),
            Check('medicamentos_por_pollo < 1'),
            Check('dias_media_retirada > 20'),
            Check('dias_media_retirada < 70'),
            Check('ganancia_media_diaria > 0'),
            Check('ganancia_media_diaria < 1'),
        ]
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
                return "ok"
        except DatabaseError as err:
            # print(err)
            if str(err) == "CHECK constraint failed: camada":
                return "error"
            elif str(err) == "UNIQUE constraint failed: camada.codigo_camada":
                return "existe"
            else:
                return "desconocido"


    @classmethod
    def get_fecha_ultima_camada(cls):

        fecha = cls.select(
            fn.Max(cls.fecha)).scalar()

        fecha = datetime.strptime(fecha, "%Y-%m-%d")

        return fecha


    @classmethod
    def get_fecha_primera_camada(cls):

        fecha = cls.select(
            fn.Min(cls.fecha)).scalar()

        fecha = datetime.strptime(fecha, "%Y-%m-%d")

        return fecha


    @classmethod
    def get_media(cls, fecha, variable):

        # print("la fecha es: ", fecha)
        # print("la variables es: ", variable)
        # print("tipo es: ", type(fecha))

        valores = cls.select(
            Camada
        ).where(
            cls.fecha <= fecha
        ).dicts()

        lista_valores = []

        for valor in valores:
            # print(valor[variable])
            lista_valores.append(valor[variable])

        return np.array(lista_valores).mean()



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
