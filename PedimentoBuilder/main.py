from builder import PedimentoBuilder
from director import PedimentoDirector
from exporter import (
    df_costos_por_item,
    df_contribuciones_detalle,
    exportar_excel_pedimento_premium
)
file_name = '5004477'
xml_file = f"Pedimentos/{file_name}.xml"

builder = PedimentoBuilder(xml_file)
director = PedimentoDirector(builder)
pedimento = director.construct()

df_costos = df_costos_por_item(pedimento)
df_contrib = df_contribuciones_detalle(pedimento)

exportar_excel_pedimento_premium(
    pedimento,
    df_costos,
    df_contrib,
    f"{file_name}.xlsx"
)
