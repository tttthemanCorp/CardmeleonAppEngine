from django.dispatch import receiver
from django.db.backends.signals import connection_created
from math import sin, cos, acos, radians
from settings import DATABASES


def mysin(rad):
    return sin(rad)

def mycos(rad):
    return cos(rad)

def myacos(rad):
    return acos(rad)

@receiver(connection_created)
def setup_func(connection,**kwargs):
    """ add trig functions to sqlite only """
    if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        connection.connection.create_function("sin", 1, mysin)
        connection.connection.create_function("cos", 1, mycos)
        connection.connection.create_function("acos", 1, myacos)
