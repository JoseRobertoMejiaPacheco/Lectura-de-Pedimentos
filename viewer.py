#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xml_viewer_local.py
Convierte cualquier XML (ej. pedimento aduanal) en un archivo HTML navegable,
tipo árbol expandible (como jsonformatter.org/xml-viewer), pero 100 % local.

Uso:
    python3 xml_viewer_local.py archivo.xml
Resultado:
    archivo_viewer.html
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import html

def generar_html(element):
    """Crea HTML recursivo con estructura expandible."""
    tag = html.escape(element.tag)
    text = (element.text or "").strip()
    valor = f": <span class='valor'>{html.escape(text)}</span>" if text else ": <span class='valor'>null</span>"

    contenido = ""
    for attr, val in element.attrib.items():
        contenido += f"<div class='atributo'>@{html.escape(attr)} = '{html.escape(val)}'</div>"

    hijos = list(element)
    if hijos:
        contenido_hijos = "".join(generar_html(hijo) for hijo in hijos)
        return f"""
        <li>
            <span class="caret">{tag}{valor}</span>
            <ul class="nested">
                {contenido}{contenido_hijos}
            </ul>
        </li>
        """
    else:
        return f"<li><span class='leaf'>{tag}{valor}</span>{contenido}</li>"

def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python3 xml_viewer_local.py archivo.xml")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"❌ Archivo no encontrado: {path}")
        sys.exit(1)

    tree = ET.parse(str(path))
    root = tree.getroot()
    html_body = generar_html(root)

    html_output = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Visor XML Local</title>
        <style>
            body {{
                font-family: Consolas, monospace;
                background-color: #f8f9fa;
                margin: 1em;
            }}
            ul, #myUL {{
                list-style-type: none;
            }}
            .caret {{
                cursor: pointer;
                user-select: none;
            }}
            .caret::before {{
                content: "\\25B6";
                color: #6c757d;
                display: inline-block;
                margin-right: 6px;
            }}
            .caret-down::before {{
                transform: rotate(90deg);
            }}
            .nested {{
                display: none;
                margin-left: 1em;
                border-left: 1px dotted #bbb;
                padding-left: 8px;
            }}
            .active {{
                display: block;
            }}
            .leaf {{
                color: #0d6efd;
            }}
            .valor {{
                color: #198754;
                font-weight: bold;
            }}
            .atributo {{
                color: #6f42c1;
                margin-left: 1.5em;
            }}
            h1 {{
                color: #343a40;
                font-size: 1.3em;
                margin-bottom: 0.5em;
            }}
            .botones {{
                margin-bottom: 10px;
            }}
            button {{
                background-color: #0d6efd;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                margin-right: 10px;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #0b5ed7;
            }}
        </style>
    </head>
    <body>
        <h1>Visor XML Local - {html.escape(path.name)}</h1>
        <div class="botones">
            <button onclick="expandAll()">Expandir todo</button>
            <button onclick="collapseAll()">Colapsar todo</button>
        </div>
        <ul id="myUL">{html_body}</ul>
        <script>
            const togglers = document.getElementsByClassName("caret");
            for (let i = 0; i < togglers.length; i++) {{
                togglers[i].addEventListener("click", function() {{
                    const nested = this.parentElement.querySelector(".nested");
                    if (nested) {{
                        nested.classList.toggle("active");
                        this.classList.toggle("caret-down");
                    }}
                }});
            }}
            function expandAll() {{
                const all = document.getElementsByClassName('nested');
                for (let i = 0; i < all.length; i++) {{
                    all[i].classList.add('active');
                }}
                const carets = document.getElementsByClassName('caret');
                for (let i = 0; i < carets.length; i++) {{
                    carets[i].classList.add('caret-down');
                }}
            }}
            function collapseAll() {{
                const all = document.getElementsByClassName('nested');
                for (let i = 0; i < all.length; i++) {{
                    all[i].classList.remove('active');
                }}
                const carets = document.getElementsByClassName('caret');
                for (let i = 0; i < carets.length; i++) {{
                    carets[i].classList.remove('caret-down');
                }}
            }}
        </script>
    </body>
    </html>
    """

    # ✅ Guardar concatenando nombre del XML
    output_file = path.stem + "_viewer.html"
    Path(output_file).write_text(html_output, encoding="utf-8")

    print(f"✅ Archivo generado: {output_file}")
    print("🌐 Ábrelo en tu navegador (sin conexión).")

if __name__ == "__main__":
    main()
#python3 xml_viewer_local.py 5004477.xml
