# app/utils/csv_utils.py
import csv
import os
from typing import Dict, Any

def write_to_csv(data: Dict[str, Any], filename: str = "tiempos.csv"):
    """
    Escribe datos en un archivo CSV. Crea el archivo si no existe.

    Args:
        data: Diccionario con los datos a escribir.  Las claves serán las cabeceras.
        filename: Nombre del archivo CSV (por defecto, "tiempos.csv").
    """
    file_exists = os.path.isfile(filename)
    fieldnames = list(data.keys())

    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Escribe la cabecera solo si el archivo es nuevo
        writer.writerow(data)