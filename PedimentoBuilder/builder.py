# builder.py

import xml.etree.ElementTree as ET

from domain import (
    Pedimento, Cliente, ProveedorComprador, Factura,
    Contribucion, Permiso, DescripcionEspecifica,
    Item, Fraccion, Identificador, Incrementable
)

# -------------------------------------------------------------------
# MÉTODOS UTILITARIOS
# -------------------------------------------------------------------
def get(el, field):
    """Devuelve texto limpio del nodo.
       Soporta nodos vacíos, nodos con hijos, nodos con espacios."""
    node = el.find(field)
    if node is None:
        return ""

    # texto directo
    if node.text and node.text.strip():
        if node.text == '59.34':
            pass
        return node.text.strip()

    # texto de hijos
    txt = "".join((c.text or "") for c in node.iter()).strip()
    return txt


def is_empty_node(node):
    """Regresa True si el nodo NO contiene texto útil
       ni hijos con texto útil."""
    # Si no tiene hijos y tampoco texto → vacío total
    if (not node.text or not node.text.strip()) and len(node) == 0:
        return True

    # Si tiene hijos, verificar si al menos uno contiene datos
    for child in node:
        if child.text and child.text.strip():
            return False
        if len(child) > 0:
            # algún nieto contiene datos
            for g in child:
                if g.text and g.text.strip():
                    return False

    # Si llegamos aquí, está vacío
    return True


# ===================================================================
#                  P E D I M E N T O   B U I L D E R
# ===================================================================
class PedimentoBuilder:

    def __init__(self, xml_path):
        self.tree = ET.parse(xml_path)
        self.root = self.tree.getroot()
        self.pedimento = Pedimento()

    # ============================================================
    #  PEDIMENTO HEADER
    # ============================================================
    def build_header(self):
        r = self.root
        self.pedimento.id_pedimento = get(r, "IdPedimento")
        self.pedimento.numero_pedimento = get(r, "NumerodePedimento")
        self.pedimento.numero_completo = get(r, "NumerodePedimentoCompleto")
        self.pedimento.tipo_de_cambio = get(r, "TipoDeCambio")
        self.pedimento.valor_aduana = get(r, "ValorAduana")
        self.pedimento.precio_pagado_valor_comecrial = get(r, "ValorComercialPrecioPagado")
        return self

    # ============================================================
    #  CLIENTE
    # ============================================================
    def build_cliente(self):
        cli = self.root.find("Cliente")
        if cli is None or is_empty_node(cli):
            return self

        c = self.pedimento.cliente
        c.razon_social = get(cli, "RazonSocial")
        c.curp = get(cli, "CURP")
        c.rfc = get(cli, "RFC")
        c.direccion = get(cli, "Direccion")
        c.numero_externo = get(cli, "NumeroExterno")
        c.numero_interno = get(cli, "NumeroInterno")
        c.colonia = get(cli, "Colonia")
        c.ciudad = get(cli, "Ciudad")
        c.cp = get(cli, "CP")
        c.entidad = get(cli, "Entidad")
        c.nombre_entidad = get(cli, "NombreEntidad")
        c.pais = get(cli, "Pais")
        c.nombre_pais = get(cli, "NombrePais")
        c.telefono1 = get(cli, "Telefono1")
        c.telefono2 = get(cli, "Telefono2")

        return self

    # ============================================================
    #  FACTURAS
    # ============================================================
    def build_facturas(self):
        for fac in self.root.findall("Facturas/Factura"):

            if is_empty_node(fac):
                continue

            f = Factura()
            f.orden = get(fac, "Orden")
            f.folio = get(fac, "Folio")
            f.factor_monetario = get(fac, "FactorMonetario")
            f.fecha = get(fac, "Fecha")
            f.incoterm = get(fac, "Incoterm")
            f.moneda_factura = get(fac, "MonedaFactura")
            f.observaciones = get(fac, "Obervaciones")
            f.pais_factura = get(fac, "PaisFactura")
            f.pais_factor_monetario = get(fac, "PaisFactorMonetario")
            f.pedido = get(fac, "Pedido")

            # --------- proveedor/comprador ---------
            pc_node = fac.find("ProveedorComprador")
            if pc_node and not is_empty_node(pc_node):
                pc = f.proveedor_comprador
                pc.cp = get(pc_node, "CP")
                pc.pais = get(pc_node, "Pais")
                pc.razon_social = get(pc_node, "RazonSocial")
                pc.rfc_tax_id = get(pc_node, "RfcTaxId")
                pc.direccion = get(pc_node, "Direccion")
                pc.numero_interno = get(pc_node, "NumeroInterno")
                pc.numero_externo = get(pc_node, "NumeroExterno")
                pc.municipio_ciudad = get(pc_node, "MunicipioCiudad")
                pc.colonia = get(pc_node, "Colonia")
                pc.telefono1 = get(pc_node, "Telefono1")
                pc.telefono2 = get(pc_node, "Telefono2")
                pc.entidad = get(pc_node, "Entidad")
                pc.nombre_entidad = get(pc_node, "NombreEntidad")

            f.valor_dolares = get(fac, "ValorDolares")
            f.valor_moneda_extranjera = get(fac, "ValorMonExtranjera")
            f.vinculacion = get(fac, "Vinculacion")
            f.valor_total = get(fac, "ValorTotal")
            f.subdivision = get(fac, "Subdivision")
            f.es_certificado_origen = get(fac, "EsCertificadoOrigen")
            f.numero_exportador_confiable = get(fac, "NumeroExportadorConfiable")
            f.edocument = get(fac, "Edocument")

            self.pedimento.facturas.append(f)

        return self

    # ============================================================
    #  FRACCIONES COMPLETAS
    # ============================================================
    def build_fracciones(self):
        for fr in self.root.findall("Fracciones/Fraccion"):

            if is_empty_node(fr):
                continue

            f = Fraccion()
            f.orden = get(fr, "Orden")
            f.numero_fraccion = get(fr, "NumeroFraccion")
            f.nico = get(fr, "Nico")
            f.subdivision = get(fr, "Subdivision")
            f.cantidad_factura = get(fr, "CantidadFactura")
            f.cantidad_tarifa = get(fr, "CantidadTarifa")
            f.descripcion = get(fr, "Descripcion")
            f.dta = get(fr, "DTA")
            if f.dta == "59.34":
                pass
            f.metodo_valoracion = get(fr, "MetodoValoracion")
            f.pais_vendedor_comprador = get(fr, "PaisVendedorComprador")
            f.pais_origen_destino = get(fr, "PaisOrigenDestino")
            f.precio_unitario = get(fr, "PrecioUnitario")
            f.unidad_factura = get(fr, "UnidadFactura")
            f.unidad_tarifa = get(fr, "UnidadTarifa")
            f.valor_agregado = get(fr, "ValorAgregado")
            f.valor_aduana = get(fr, "ValorAduana")
            f.valor_dolares = get(fr, "ValorDolares")
            f.valor_moneda_facturacion = get(fr, "ValorMonedaFacturacion")
            f.importe_precio_pagado = get(fr, "ImportePrecioPagado")
            f.vinculacion = get(fr, "Vinculacion")
            f.observaciones = get(fr, "Observaciones")

            # ----------- CONTRIBUCIONES -----------
            for cnode in fr.findall("Impuestos/Contribucion"):
                if is_empty_node(cnode):
                    continue
                c = Contribucion()
                c.forma_pago = get(cnode, "FormaDePago")
                c.clave_impuesto = get(cnode, "ClaveImpuesto")
                c.concepto_impuesto = get(cnode, "ConceptoImpuesto")
                c.importe = get(cnode, "Importe")
                c.tasa = get(cnode, "Tasa")
                c.tipo_de_tasa = get(cnode, "TipoDeTasa")
                f.contribuciones.append(c)

            # ----------- PERMISOS -----------
            for pnode in fr.findall("Permisos/PermisoFraccion"):
                if is_empty_node(pnode):
                    continue
                p = Permiso()
                p.permiso = get(pnode, "Permiso")
                p.numero_permiso = get(pnode, "NumeroPermiso")
                p.firma = get(pnode, "Firma")
                p.complemento_uno = get(pnode, "ComplementoUno")
                p.complemento_dos = get(pnode, "ComplementoDos")
                p.complemento_tres = get(pnode, "ComplementoTres")
                p.valor_dolares = get(pnode, "ValorDolares")
                p.cantidad_umt = get(pnode, "CantidadUMT")
                p.tipo_de_permiso = get(pnode, "TipoDePermiso")
                f.permisos.append(p)

            # ----------- ITEMS -----------
            for inode in fr.findall("Items/Item"):

                if is_empty_node(inode):
                    continue

                it = Item()
                it.orden = get(inode, "Orden")
                it.origen = get(inode, "Origen")
                it.factura = get(inode, "Factura")
                it.item_number = get(inode, "ItemNumber")
                it.unidad_factura = get(inode, "UnidadFactura")
                it.unidad_tarifa = get(inode, "UnidadTarifa")
                it.unidad_vu = get(inode, "UnidadVU")
                it.cantidad = get(inode, "Cantidad")
                it.cantidad_tarifa = get(inode, "CantidadTarifa")
                it.cantidad_vu = get(inode, "CantidadVU")
                it.precio_unitario = get(inode, "PrecioUnitario")
                it.total = get(inode, "Total")
                it.fraccion = get(inode, "Fraccion")
                it.nico = get(inode, "Nico")

                # -------- descripciones --------
                for dnode in inode.findall("DescripcionesEspecificas/DescripcionEspecifica"):
                    if is_empty_node(dnode):
                        continue
                    de = DescripcionEspecifica()
                    de.id = get(dnode, "Id")
                    de.id_item = get(dnode, "IdItem")
                    de.marca = get(dnode, "Marca")
                    de.modelo = get(dnode, "Modelo")
                    de.serie = get(dnode, "Serie")
                    de.dato_identificacion = get(dnode, "DatoIdentificacion")
                    it.descripciones.append(de)

                f.items.append(it)

            self.pedimento.fracciones.append(f)

        return self

    # ============================================================
    #  IDENTIFICADORES
    # ============================================================
    def build_identificadores(self):
        for ide in self.root.findall("Identificadores/IdentificadorPedimento"):
            if is_empty_node(ide):
                continue

            i = Identificador()
            i.identificador = get(ide, "Identificador")
            i.complemento_uno = get(ide, "ComplementoUno")
            i.complemento_dos = get(ide, "ComplementoDos")
            i.complemento_tres = get(ide, "ComplementoTres")

            self.pedimento.identificadores.append(i)

        return self

    # ============================================================
    #  INCREMENTABLES (Otros Pagos)
    # ============================================================
    def build_incrementables(self):
        for op in self.root.findall("Incrementables/OtrosPagos"):
            if is_empty_node(op):
                continue

            inc = Incrementable()
            inc.id = get(op, "Id")
            inc.concepto = get(op, "Concepto")
            inc.importe_me = get(op, "ImporteME")
            inc.importe_mn = get(op, "ImporteMN")
            inc.pais = get(op, "Pais")

            self.pedimento.incrementables.append(inc)

        return self

    # ============================================================
    #  CONTRIBUCIONES GENERALES
    # ============================================================
    def build_contribuciones_generales(self):
        for cnode in self.root.findall("Impuestos/Contribucion"):
            if is_empty_node(cnode):
                continue

            c = Contribucion()
            c.forma_pago = get(cnode, "FormaDePago")
            c.clave_impuesto = get(cnode, "ClaveImpuesto")
            c.concepto_impuesto = get(cnode, "ConceptoImpuesto")
            c.importe = get(cnode, "Importe")
            c.tasa = get(cnode, "Tasa")
            c.tipo_de_tasa = get(cnode, "TipoDeTasa")

            self.pedimento.contribuciones_generales.append(c)

        return self

    # ============================================================
    #  FIN
    # ============================================================
    def build(self):
        return self.pedimento
