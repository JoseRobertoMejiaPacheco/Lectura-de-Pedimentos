from builder import PedimentoBuilder

class PedimentoDirector:
    """
    Orquesta todas las fases necesarias para construir un Pedimento.
    """

    def __init__(self, builder: PedimentoBuilder):
        self.builder = builder

    def construct(self):
        (self.builder
            .build_pedimento()
            .build_clientes()
            .build_facturas()
            .build_fracciones()
        )
        return self.builder.get_result()
