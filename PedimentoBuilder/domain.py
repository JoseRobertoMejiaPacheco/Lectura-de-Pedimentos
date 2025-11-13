from datetime import datetime


class Numeric:
    @staticmethod
    def f(value):
        if value in (None, ""):
            return 0.0
        try:
            return float(str(value).strip())
        except:
            return 0.0


class DateUtil:
    @staticmethod
    def parse(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except:
            return value


class Cliente:
    def __init__(self, razon_social="", pais="", rfc=""):
        self.razon_social = razon_social
        self.pais = pais
        self.rfc = rfc

    def to_dict(self):
        return {
            "razon_social": self.razon_social,
            "pais": self.pais,
            "rfc": self.rfc,
        }


class ProveedorComprador:
    def __init__(self, razon_social="", pais="", rfc_tax_id=""):
        self.razon_social = razon_social
        self.pais = pais
        self.rfc_tax_id = rfc_tax_id

    def to_dict(self):
        return {
            "razon_social": self.razon_social,
            "pais": self.pais,
            "rfc_tax_id": self.rfc_tax_id,
        }


class Factura:
    def __init__(self, folio="", proveedor=None):
        self.folio = folio
        self.proveedor = proveedor or ProveedorComprador()

    def to_dict(self):
        return {
            "folio": self.folio,
            "proveedor": self.proveedor.to_dict()
        }


class Contribucion:
    def __init__(self, concepto_impuesto="", importe="0", tipo_de_tasa="0"):
        self.concepto_impuesto = concepto_impuesto
        self.importe = Numeric.f(importe)
        self.tipo_de_tasa = Numeric.f(tipo_de_tasa)

    def to_dict(self):
        return {
            "concepto_impuesto": self.concepto_impuesto,
            "importe": self.importe,
            "tipo_de_tasa": self.tipo_de_tasa,
        }


class Item:
    def __init__(self, item_number="", cantidad="0", total="0"):
        self.item_number = item_number
        self.cantidad = Numeric.f(cantidad)
        self.total = Numeric.f(total)

    def to_dict(self):
        return {
            "item_number": self.item_number,
            "cantidad": self.cantidad,
            "total": self.total,
        }


class Fraccion:
    def __init__(self, valor_aduana="0", dta="0"):
        self.valor_aduana = Numeric.f(valor_aduana)
        self.dta = Numeric.f(dta)
        self.contribuciones = []
        self.items = []

    def add_contribucion(self, contribucion):
        self.contribuciones.append(contribucion)

    def add_item(self, item):
        self.items.append(item)

    def to_dict(self):
        return {
            "valor_aduana": self.valor_aduana,
            "dta": self.dta,
            "contribuciones": [c.to_dict() for c in self.contribuciones],
            "items": [i.to_dict() for i in self.items],
        }


class Pedimento:
    def __init__(self, numero="", tipo_cambio="0", fecha_pago=""):
        self.numero = numero
        self.tipo_cambio = Numeric.f(tipo_cambio)
        self.fecha_pago = DateUtil.parse(fecha_pago)

        self.clientes = []
        self.facturas = []
        self.fracciones = []

    def add_cliente(self, cliente):
        self.clientes.append(cliente)

    def add_factura(self, factura):
        self.facturas.append(factura)

    def add_fraccion(self, fraccion):
        self.fracciones.append(fraccion)

    def to_dict(self):
        return {
            "numerode_pedimento_completo": self.numero,
            "tipo_de_cambio": self.tipo_cambio,
            "fecha_de_pago": str(self.fecha_pago) if self.fecha_pago else "",
            "clientes": [c.to_dict() for c in self.clientes],
            "facturas": [f.to_dict() for f in self.facturas],
            "fracciones": [fr.to_dict() for fr in self.fracciones],
        }
