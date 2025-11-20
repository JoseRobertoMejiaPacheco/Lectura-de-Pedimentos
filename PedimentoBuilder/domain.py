# domain.py

class Cliente:
    def __init__(self):
        self.razon_social = ""
        self.curp = ""
        self.rfc = ""
        self.direccion = ""
        self.numero_externo = ""
        self.numero_interno = ""
        self.colonia = ""
        self.ciudad = ""
        self.cp = ""
        self.entidad = ""
        self.nombre_entidad = ""
        self.pais = ""
        self.nombre_pais = ""
        self.telefono1 = ""
        self.telefono2 = ""


class ProveedorComprador:
    def __init__(self):
        self.cp = ""
        self.pais = ""
        self.razon_social = ""
        self.rfc_tax_id = ""
        self.direccion = ""
        self.numero_interno = ""
        self.numero_externo = ""
        self.municipio_ciudad = ""
        self.colonia = ""
        self.telefono1 = ""
        self.telefono2 = ""
        self.entidad = ""
        self.nombre_entidad = ""


class Factura:
    def __init__(self):
        self.orden = ""
        self.folio = ""
        self.factor_monetario = ""
        self.fecha = ""
        self.incoterm = ""
        self.moneda_factura = ""
        self.observaciones = ""
        self.pais_factura = ""
        self.pais_factor_monetario = ""
        self.pedido = ""
        self.proveedor_comprador = ProveedorComprador()
        self.valor_dolares = ""
        self.valor_moneda_extranjera = ""
        self.vinculacion = ""
        self.valor_total = ""
        self.subdivision = ""
        self.es_certificado_origen = ""
        self.numero_exportador_confiable = ""
        self.edocument = ""


class Contribucion:
    def __init__(self):
        self.forma_pago = ""
        self.clave_impuesto = ""
        self.concepto_impuesto = ""
        self.importe = ""
        self.tasa = ""
        self.tipo_de_tasa = ""


class Permiso:
    def __init__(self):
        self.permiso = ""
        self.numero_permiso = ""
        self.firma = ""
        self.complemento_uno = ""
        self.complemento_dos = ""
        self.complemento_tres = ""
        self.valor_dolares = ""
        self.cantidad_umt = ""
        self.tipo_de_permiso = ""


class DescripcionEspecifica:
    def __init__(self):
        self.id = ""
        self.id_item = ""
        self.marca = ""
        self.modelo = ""
        self.serie = ""
        self.dato_identificacion = ""


class Item:
    def __init__(self):
        self.orden = ""
        self.origen = ""
        self.factura = ""
        self.item_number = ""
        self.unidad_factura = ""
        self.unidad_tarifa = ""
        self.unidad_vu = ""
        self.cantidad = ""
        self.cantidad_tarifa = ""
        self.cantidad_vu = ""
        self.precio_unitario = ""
        self.total = ""
        self.fraccion = ""
        self.nico = ""
        self.descripciones = []  # lista de DescripcionEspecifica()


class Fraccion:
    def __init__(self):
        self.orden = ""
        self.numero_fraccion = ""
        self.nico = ""
        self.subdivision = ""
        self.cantidad_factura = ""
        self.cantidad_tarifa = ""
        self.descripcion = ""
        self.dta = ""
        self.metodo_valoracion = ""
        self.pais_vendedor_comprador = ""
        self.pais_origen_destino = ""
        self.precio_unitario = ""
        self.unidad_factura = ""
        self.unidad_tarifa = ""
        self.valor_agregado = ""
        self.valor_aduana = ""
        self.valor_dolares = ""
        self.valor_moneda_facturacion = ""
        self.importe_precio_pagado = ""
        self.vinculacion = ""
        self.observaciones = ""

        self.contribuciones = []   # lista Contribucion()
        self.permisos = []         # lista Permiso()
        self.items = []            # lista Item()


class Identificador:
    def __init__(self):
        self.identificador = ""
        self.complemento_uno = ""
        self.complemento_dos = ""
        self.complemento_tres = ""


class Incrementable:
    def __init__(self):
        self.id = ""
        self.concepto = ""
        self.importe_me = ""
        self.importe_mn = ""
        self.pais = ""


class Pedimento:
    def __init__(self):
        self.id_pedimento = ""
        self.numero_pedimento = ""
        self.numero_completo = ""
        self.tipo_de_cambio = ""
        self.valor_aduana = ""
        self.precio_pagado_valor_comecrial = ""

        self.cliente = Cliente()

        self.facturas = []
        self.fracciones = []
        self.identificadores = []
        self.incrementables = []
        self.contribuciones_generales = []
