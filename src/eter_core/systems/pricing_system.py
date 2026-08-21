from eter_core.domain.products import CATALOGO_PRODUCTOS


class PricingSystem:
    """
    Calcula precios dinámicos según ubicación (bioma) y oferta/demanda.

    Reglas de Dominio:
    - Un producto es más barato en su geografía nativa (donde se produce)
      y más caro donde es importado.
    - Un producto sin geografía nativa tiene precio neutral (no depende de ubicación).
    - La oferta y demanda local ajustan el precio: a mayor oferta, menor precio;
      a mayor demanda, mayor precio.
    """

    DESCUENTO_NATIVO: float = 0.7     # factor multiplicador si el bioma es nativo
    RECARGO_IMPORTADO: float = 1.4    # factor si el producto es foráneo
    ELASTICIDAD_OFERTA: float = 0.002
    ELASTICIDAD_DEMANDA: float = 0.004

    @classmethod
    def factor_ubicacion(cls, producto: str, bioma: str) -> float:
        """
        Devuelve el multiplicador de precio por ubicación.
        Nativo → más barato; foráneo → más caro; sin geografía → neutral.
        """
        definicion = CATALOGO_PRODUCTOS.get(producto)
        if definicion is None:
            return 1.0
        nativas = definicion.geografias_nativas
        if not nativas:
            return 1.0
        if bioma in nativas:
            return cls.DESCUENTO_NATIVO
        return cls.RECARGO_IMPORTADO

    @classmethod
    def precio(
        cls,
        producto: str,
        bioma: str,
        oferta: float = 100.0,
        demanda: float = 50.0,
    ) -> float:
        """
        Precio final de un producto en una ubicación con una oferta y demanda dadas.
        """
        definicion = CATALOGO_PRODUCTOS.get(producto)
        if definicion is None:
            return 0.0
        factor_ubicacion = cls.factor_ubicacion(producto, bioma)
        factor_mercado = 1.0 + (demanda * cls.ELASTICIDAD_DEMANDA) - (oferta * cls.ELASTICIDAD_OFERTA)
        factor_mercado = max(0.1, factor_mercado)
        return round(definicion.valor_base * factor_ubicacion * factor_mercado, 1)
