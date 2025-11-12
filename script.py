#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
strip_xml_values.py
Elimina todo el contenido sensible de un XML (valores, textos y atributos),
dejando únicamente la estructura jerárquica de etiquetas.

Uso:
    python3 strip_xml_values.py pedimento.xml

Resultado:
    pedimento_skeleton.xml
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def clear_element(element, counter=0):
    """Elimina texto y atributos de cada etiqueta recursivamente."""
    element.text = None
    element.tail = None
    element.attrib.clear()
    counter += 1
    for child in list(element):
        counter = clear_element(child, counter)
    return counter

def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python3 strip_xml_values.py archivo.xml")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"❌ Archivo no encontrado: {input_path}")
        sys.exit(1)

    # Determinar nombre de salida dinámicamente
    output_path = input_path.with_name(f"{input_path.stem}_skeleton.xml")

    parser = ET.XMLParser(encoding="utf-8")
    tree = ET.parse(str(input_path), parser=parser)
    root = tree.getroot()

    total_tags = clear_element(root)

    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"✅ Archivo limpio generado: {output_path.name}")
    print(f"🧱 Total de etiquetas procesadas: {total_tags}")

if __name__ == "__main__":
    main()
#python3 strip_xml_values.py 5004477.xml