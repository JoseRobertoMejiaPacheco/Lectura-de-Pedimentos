from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import pandas as pd
import io
import logging
import os
import json
from typing import Dict, List, Any

# Importaciones de tu proyecto existente
from builder import PedimentoBuilder
from domain import Pedimento
from copy import deepcopy

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Mapeos de impuestos (los que ya tenías)
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

class PedimentoProcessor:
    """Clase para procesar pedimentos - Manteniendo tu lógica original"""
    
    def __init__(self):
        self.pedimento = None
        self.contrib_gen_keys = {}
        self.contrib_gen_total = 0
        
    def load_pedimento(self, xml_file_path: str):
        """Carga el pedimento desde archivo XML"""
        try:
            builder = (
                PedimentoBuilder(xml_file_path)
                .build_header()
                .build_cliente()
                .build_facturas()
                .build_fracciones()
                .build_identificadores()
                .build_incrementables()
                .build_contribuciones_generales()
            )
            self.pedimento = builder.build()
            return True
        except Exception as e:
            logging.error(f"Error cargando pedimento: {e}")
            return False
    
    def _procesar_contribuciones_generales(self):
        """Procesa las contribuciones generales del pedimento"""
        self.contrib_gen_total = 0
        self.contrib_gen_keys = {}
        
        for c in self.pedimento.contribuciones_generales:
            tipo = (c.tipo_de_tasa or "").strip()
            if tipo == "0":
                continue

            importe = float(c.importe or 0)
            self.contrib_gen_total += importe

            clave_raw = (c.clave_impuesto or "").strip()

            if clave_raw in MAP_CLAVE_IMPUESTO_GENERAL:
                clave = MAP_CLAVE_IMPUESTO_GENERAL[clave_raw]
            else:
                clave = f"GEN_{clave_raw}"

            self.contrib_gen_keys[clave] = self.contrib_gen_keys.get(clave, 0) + importe
    
    def _procesar_items_raw(self):
        """Procesa los items del pedimento y retorna lista de items raw"""
        items_raw = []
        cantidad_total_pedimento = 0

        for fraccion in self.pedimento.fracciones:
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

                factor = float(self.pedimento.valor_aduana) / float(self.pedimento.precio_pagado_valor_comecrial)

                vals = {
                    "codigo": item.item_number,
                    "valor_aduana": (float(item.total or 0) * float(self.pedimento.tipo_de_cambio or 0)) * factor,
                    "precio_unitario": float(item.precio_unitario or 0),
                    "cantidad": cantidad,
                    "dta": dta,
                    "contribuciones_fraccion": contrib_frac_total,
                    "tipo_de_cambio": float(self.pedimento.tipo_de_cambio or 0),
                }

                vals.update(contrib_frac_keys)
                items_raw.append(vals)
                
        return items_raw, cantidad_total_pedimento
    
    def _aplicar_prorrateo(self, items_raw, cantidad_total):
        """Aplica prorrateo de contribuciones generales a los items"""
        for vals in items_raw:
            cantidad_item = vals["cantidad"]
            factor = (cantidad_item / cantidad_total) if cantidad_total else 0

            for k, v in self.contrib_gen_keys.items():
                vals[k] = v * factor

            vals["contrib_gen_prorrateado"] = self.contrib_gen_total * factor
            
        return items_raw
    
    def _agrupar_items(self, items_raw):
        """Agrupa items por código"""
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
                        "tipo_de_cambio", "dta", "contribuciones_fraccion",
                        'IVA', 'IGI/IGE', 'CC'
                    ]:
                        if isinstance(value, (int, float)):
                            agrupado[codigo][key] = agrupado[codigo].get(key, 0) + value
                            
        return agrupado
    
    def _calcular_costos_finales(self, items_agrupados):
        """Calcula costos finales para items agrupados"""
        items_final = []
        
        for codigo, vals in items_agrupados.items():
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
            vals["costo_total"] = costo_total
            
            items_final.append(vals)
            
        return items_final
    
    def procesar_pedimento(self, xml_file_path: str):
        """Procesa completo el pedimento y retorna resultados"""
        if not self.load_pedimento(xml_file_path):
            raise Exception("Error al cargar el pedimento")
        
        self._procesar_contribuciones_generales()
        items_raw, cantidad_total = self._procesar_items_raw()
        items_con_prorrateo = self._aplicar_prorrateo(items_raw, cantidad_total)
        items_agrupados = self._agrupar_items(items_con_prorrateo)
        items_final = self._calcular_costos_finales(items_agrupados)
        
        info_pedimento = {
            "numero_completo": self.pedimento.numero_completo,
            "total_fracciones": len(self.pedimento.fracciones),
            "total_facturas": len(self.pedimento.facturas),
            "items_agrupados": len(items_final),
            "contribuciones_generales": self.contrib_gen_keys,
            "total_contribuciones_generales": self.contrib_gen_total
        }
        
        return {
            "pedimento": info_pedimento,
            "items": items_final
        }

# Instancia global del procesador
processor = PedimentoProcessor()

# ==========================================
# RUTAS DE LA API
# ==========================================

@app.route('/')
def index():
    """Página principal con la interfaz web"""
    return render_template('index.html')

@app.route('/api/pedimento/procesar', methods=['POST'])
def procesar_pedimento():
    """Endpoint para procesar un pedimento"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No se proporcionó archivo"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Nombre de archivo vacío"}), 400
        
        if not file.filename.endswith('.xml'):
            return jsonify({"error": "El archivo debe ser XML"}), 400
        
        # Guardar archivo temporalmente
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
            file.save(tmp_file.name)
            file_path = tmp_file.name
        
        # Procesar pedimento
        resultado = processor.procesar_pedimento(file_path)
        
        # Limpiar archivo temporal
        os.unlink(file_path)
        
        return jsonify({
            "success": True,
            "data": resultado
        })
        
    except Exception as e:
        logging.error(f"Error procesando pedimento: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/pedimento/exportar-excel', methods=['POST'])
def exportar_excel():
    """Endpoint para exportar resultados a Excel"""
    try:
        data = request.get_json()
        if not data or 'items' not in data:
            return jsonify({"error": "Datos no proporcionados"}), 400
        
        # Crear DataFrame y Excel en memoria
        df_items = pd.DataFrame(data['items'])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_items.to_excel(writer, sheet_name='Items', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='costo_pedimento.xlsx'
        )
        
    except Exception as e:
        logging.error(f"Error exportando a Excel: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar estado del servicio"""
    return jsonify({"status": "healthy", "service": "pedimento-processor"})

if __name__ == '__main__':
    # Crear directorio de templates si no existe
    os.makedirs('templates', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)