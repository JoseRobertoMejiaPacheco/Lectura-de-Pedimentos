# utils.py

import json

def object_to_dict(obj, _visited=None):
    """
    Convierte recursivamente un objeto del dominio a un dict profundo.
    Soporta:
    - Objetos con __dict__
    - Listas/tuplas
    - Diccionarios
    - Valores primitivos
    """

    if _visited is None:
        _visited = set()

    # ---------------------------------------
    # Evitar recursión circular
    # ---------------------------------------
    obj_id = id(obj)
    if obj_id in _visited:
        return None  # evitar loops
    _visited.add(obj_id)

    # ---------------------------------------
    # Tipos primitivos -> devolver tal cual
    # ---------------------------------------
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # ---------------------------------------
    # Listas o tuplas -> convertir cada elemento
    # ---------------------------------------
    if isinstance(obj, (list, tuple)):
        return [object_to_dict(item, _visited) for item in obj]

    # ---------------------------------------
    # Diccionarios -> convertir valores
    # ---------------------------------------
    if isinstance(obj, dict):
        return {k: object_to_dict(v, _visited) for k, v in obj.items()}

    # ---------------------------------------
    # Objetos de dominio -> usar __dict__
    # ---------------------------------------
    if hasattr(obj, "__dict__"):
        data = {}
        for key, value in vars(obj).items():
            data[key] = object_to_dict(value, _visited)
        return data

    # ---------------------------------------
    # Tipo desconocido -> representarlo como string
    # ---------------------------------------
    return str(obj)


def object_to_json(obj, indent=2):
    """
    Convierte cualquier objeto a JSON (usando object_to_dict internamente).
    """
    return json.dumps(object_to_dict(obj), indent=indent, ensure_ascii=False)


def pretty_print(obj):
    """
    Imprime el objeto convertido a JSON bonito.
    """
    print(object_to_json(obj, indent=2))


def save_json(obj, path):
    """
    Guarda el objeto como JSON en un archivo.
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(object_to_json(obj, indent=2))
