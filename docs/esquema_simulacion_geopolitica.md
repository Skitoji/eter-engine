# Esquema de Simulación Geopolítica de Éter

## Nivel 1: Macro - Estados

- Total: 18 estados soberanos.
- Ejemplos: Aberylesky, Bythumnosia, Hielia, Arcyrosia, Burovia y Kokegyoujsia.
- Atributos: nombre oficial, color, capital, cultura, gobierno, economía y lista de provincias.
- Fuente: `pack.states` en la exportación de Azgaar.

## Nivel 2: Meso - Provincias

- Total: 252 provincias válidas.
- El índice neutral `0` de Azgaar se descarta.
- Ejemplos: Treaberfia Shire, Linningled Shire y Duria County.
- Atributos: ID único, nombre, nombre completo, tipo administrativo, estado padre, centro geográfico y ciudad principal.
- Rol ECS: cada provincia válida es una entidad con componentes de fe, infección, economía y geografía.
- Fuente: `pack.provinces` en la exportación de Azgaar.

## Nivel 3: Micro - Celdas Geográficas

- Total: 5.709 celdas terrestres asignadas a provincias.
- Rol: topología espacial para calcular adyacencias, rutas comerciales, expansión de plagas y distancias.
- Relación: cada celda se asocia a una provincia mediante su campo `province`.
- Fuente: `pack.cells` en la exportación de Azgaar.

## Simulación e Interacción

- La interacción actual es una consola por turnos mediante `iniciar_simulacion`.
- Los comandos del usuario, como `purgar` y `pasar`, avanzan el mundo mediante `tick(delta_tiempo=1.0)`.
- Los sistemas recorren las entidades provinciales y aplican reglas locales y espaciales.
- El bus de eventos identifica la provincia y el estado afectados por cada crisis.
- La arquitectura permite conectar en el futuro una GUI o un backend WebSocket sin modificar `eter_core`.

## Integración del Lore

La geografía importada sirve como base para el lore existente:

- La Infección Demoníaca puede originarse en fronteras, zonas salvajes o provincias concretas.
- La Santa Iglesia mide y pierde fervor a escala provincial o estatal.
- Los gremios reaccionan a crisis económicas, agrícolas y comerciales locales.
- Los cultistas y magos oscuros aparecen como consecuencia sistémica de la pérdida de fe y el avance de la infección.
