class PedimentoDirector:

    def __init__(self, builder):
        self.builder = builder

    def construct(self):
        return (
            self.builder
                .build_pedimento()
                .build_clientes()
                .build_facturas()
                .build_fracciones()
                .build_contribuciones_globales()
                .build_identificadores()
                .build_incrementables()
                .build_destinatarios()
                .get_result()
        )
