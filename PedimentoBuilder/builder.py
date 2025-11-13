import xml.etree.ElementTree as ET
from domain import (
    Pedimento, Cliente, Factura, ProveedorComprador,
    Fraccion, Contribucion, Item
)


def get(el, path):
    e = el.find(path)
    return e.text.strip() if e is not None and e.text else ""


class PedimentoBuilder:
    """
    Builder que construye un objeto Pedimento a partir de un XML.
    """

    def __init__(self, xml_path):
        self.tree = ET.parse(xml_path)
        self.root = self.tree.getroot()
        self.pedimento = None

    def build_pedimento(self):
        self.pedimento = Pedimento(
            numero=get(self.root, "NumerodePedimentoCompleto"),
            tipo_cambio=get(self.root, "TipoDeCambio"),
            fecha_pago=get(self.root, "FechaDePagoDelPedimento"),
        )
        return self

    def build_clientes(self):
        for cli in self.root.findall("Cliente"):
            self.pedimento.add_cliente(
                Cliente(
                    razon_social=get(cli, "RazonSocial"),
                    pais=get(cli, "Pais"),
                    rfc=get(cli, "RFC")
                )
            )
        return self

    def build_facturas(self):
        for fac in self.root.findall(".//Facturas/Factura"):
            prov = fac.find("ProveedorComprador")
            proveedor = ProveedorComprador(
                razon_social=get(prov, "RazonSocial"),
                pais=get(prov, "Pais"),
                rfc_tax_id=get(prov, "RfcTaxId")
            )
            self.pedimento.add_factura(
                Factura(
                    folio=get(fac, "Folio"),
                    proveedor=proveedor
                )
            )
        return self

    def build_fracciones(self):
        for fr in self.root.findall(".//Fracciones/Fraccion"):
            fr_obj = Fraccion(
                valor_aduana=get(fr, "ValorAduana"),
                dta=get(fr, "DTA"),
            )

            # Contribuciones válidas
            for con in fr.findall(".//Impuestos/Contribucion"):
                if get(con, "TipoDeTasa") not in ["", "0", "0.0", "0.00"]:
                    fr_obj.add_contribucion(
                        Contribucion(
                            concepto_impuesto=get(con, "ConceptoImpuesto"),
                            importe=get(con, "Importe"),
                            tipo_de_tasa=get(con, "TipoDeTasa"),
                        )
                    )

            # Items
            for it in fr.findall(".//Items/Item"):
                fr_obj.add_item(
                    Item(
                        item_number=get(it, "ItemNumber"),
                        cantidad=get(it, "Cantidad"),
                        total=get(it, "Total")
                    )
                )

            self.pedimento.add_fraccion(fr_obj)

        return self

    def get_result(self):
        return self.pedimento
