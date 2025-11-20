from builder import PedimentoBuilder
import pandas as pd
from copy import deepcopy

file_name = '5004580'
xml_file = f"Pedimentos/{file_name}.xml"

builder = (
    PedimentoBuilder(xml_file)
    .build_header()
    .build_cliente()
    .build_facturas()
    .build_fracciones()
    .build_identificadores()
    .build_incrementables()
    .build_contribuciones_generales()
)

pedimento = builder.build()

MAP_CLAVE_IMPUESTO = {
    "6": "IGI/IGE",
    "3": "IVA",
    "2": "CC"
}

MAP_CLAVE_IMPUESTO_GENERAL = {
    "1": "DTA",
    "15": "PRV",
    "23": "IVA/PRV",
}


# ==========================================
# CONTRIBUCIONES GENERALES
# ==========================================
contrib_gen_total = 0
contrib_gen_keys = {}

for c in pedimento.contribuciones_generales:
    tipo = (c.tipo_de_tasa or "").strip()
    if tipo == "0":
        continue

    importe = float(c.importe or 0)
    contrib_gen_total += importe

    clave_raw = (c.clave_impuesto or "").strip()

    if clave_raw in MAP_CLAVE_IMPUESTO_GENERAL:
        clave = MAP_CLAVE_IMPUESTO_GENERAL[clave_raw]
    else:
        clave = f"GEN_{clave_raw}"

    contrib_gen_keys[clave] = contrib_gen_keys.get(clave, 0) + importe


# ==========================================
# CREAR LISTA items_raw
# ==========================================
items_raw = []
cantidad_total_pedimento = 0

for fraccion in pedimento.fracciones:

    dta = float(fraccion.dta or 0)
    contrib_frac_total = 0
    contrib_frac_keys = {}

    for contribucion in fraccion.contribuciones:
        tipo = (contribucion.tipo_de_tasa or "").strip()
        if tipo == "0":
            continue

        importe = float(contribucion.importe or 0)
        contrib_frac_total += importe

        clave_raw = (contribucion.clave_impuesto or "").strip()

        if clave_raw in MAP_CLAVE_IMPUESTO:
            clave = MAP_CLAVE_IMPUESTO[clave_raw]
        else:
            clave = f"CONTRIB_{clave_raw}"

        contrib_frac_keys[clave] = contrib_frac_keys.get(clave, 0) + importe

    for item in fraccion.items:

        cantidad = float(item.cantidad or 0)
        cantidad_total_pedimento += cantidad

        factor = float(pedimento.valor_aduana) / float(pedimento.precio_pagado_valor_comecrial)

        vals = {
            "codigo": item.item_number,
            "valor_aduana": (float(item.total or 0) * float(pedimento.tipo_de_cambio or 0)) * factor,
            "precio_unitario": float(item.precio_unitario or 0),
            "cantidad": cantidad,
            "dta": dta,
            "contribuciones_fraccion": contrib_frac_total,
            "tipo_de_cambio": float(pedimento.tipo_de_cambio or 0),
        }

        vals.update(contrib_frac_keys)
        items_raw.append(vals)


# ==========================================
# PRORRATEO CONTRIBUCIONES GENERALES
# ==========================================
for vals in items_raw:

    cantidad_item = vals["cantidad"]

    factor = (cantidad_item / cantidad_total_pedimento) if cantidad_total_pedimento else 0

    for k, v in contrib_gen_keys.items():
        vals[k] = v * factor

    vals["contrib_gen_prorrateado"] = contrib_gen_total * factor


# ==========================================
# AGRUPAR ITEMS POR CÓDIGO (SIN DUPLICADOS)
# ==========================================
agrupado = {}

for item in items_raw:
    codigo = item["codigo"]

    if codigo not in agrupado:
        agrupado[codigo] = deepcopy(item)
    else:
        agrupado[codigo]["cantidad"] += item["cantidad"]
        agrupado[codigo]["valor_aduana"] += item["valor_aduana"]

        for key, value in item.items():
            if key not in [
                "codigo", "cantidad", "valor_aduana",
                "precio_unitario", "precio_final",
                "tipo_de_cambio", "dta"
            ]:
                if isinstance(value, (int, float)):
                    agrupado[codigo][key] = agrupado[codigo].get(key, 0) + value


# ==========================================
# ARMAR items_final
# ==========================================
items_final = []

print("ITEMS AGRUPADOS ======================")

for codigo, vals in agrupado.items():

    cantidad = vals.get("cantidad", 0)
    va = vals.get("valor_aduana", 0)
    dta = vals.get("dta", 0)
    iva = vals.get("IVA", 0)
    igi = vals.get("IGI/IGE", 0)
    prv = vals.get("PRV", 0)
    cc = vals.get("CC", 0)
    iva_prv = vals.get("IVA/PRV", 0)

    costo_total = va + iva + igi + prv + iva_prv + dta + cc

    vals["costo_final"] = costo_total / cantidad if cantidad else 0

    print(codigo, costo_total)

    items_final.append(vals)


# ==========================================
# EXPORTAR
# ==========================================
df_items = pd.DataFrame(items_final)
df_items.to_excel(f"Files Pedimentos/Costo{file_name}.xlsx", index=False)

print("=================================")
print("Pedimento:", pedimento.numero_completo)
print("Total fracciones:", len(pedimento.fracciones))
print("Total facturas:", len(pedimento.facturas))
print("Items agrupados:", len(items_final))
print("=================================")
print("EXPORTADO:", f"FINAL {file_name}.xlsx")
