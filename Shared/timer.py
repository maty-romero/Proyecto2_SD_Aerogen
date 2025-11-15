# utils.py
import time
import functools
import logging

# logger para poder llevarlo a consola
timer_logger = logging.getLogger("timer_logger")

def measure_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        timer_logger.info(f"funcion [{func.__name__}] ejecutada {end - start:.6f} segundos")
        return result

    return wrapper


"""Ej. de configuracion de salida:

import logging
from utils import measure_time, timer_logger

# Ejemplo 1: enviar la salida a la consola
logging.basicConfig(level=logging.INFO)

# Ejemplo 2: enviar la salida a otro archivo
handler = logging.FileHandler("times.log")
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)

timer_logger.addHandler(handler)
timer_logger.setLevel(logging.INFO)

"""