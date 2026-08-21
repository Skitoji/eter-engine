# Documento de Diseño y Arquitectura: Proyecto "Éter"

## 1. Visión General y Objetivo del Proyecto
**Éter** es un proyecto de simulación de mundo virtual inmersivo de alta fantasía. El objetivo principal es crear un ecosistema **completamente dinámico y emergente**, donde no existan eventos guionizados, sino una red de causas y consecuencias impulsadas por las acciones de los jugadores y las variables del entorno. 

El proyecto está diseñado para escalar tecnológicamente en fases: comenzando como un motor de simulación puramente lógico (basado en texto/consola), evolucionando hacia interfaces gráficas 2D/3D, y culminando en un **MMORPG en Realidad Virtual (VR)**. Para lograr esto, el núcleo (Core) de la simulación está estrictamente desacoplado del motor gráfico.

---

## 2. Lore y Construcción del Mundo (Worldbuilding)

El universo se desarrolla en el continente de **Éter**, un mundo vivo compuesto por ecosistemas interconectados, política compleja y una amenaza existencial latente.

### 2.1. Geopolítica y Estados Soberanos
El mapa importado desde Azgaar define formalmente 18 estados soberanos. Cada estado es una entidad política de nivel macro con nombre oficial, color identificativo, capital, cultura dominante, modelo económico y una lista explícita de provincias.

Los estados son: **Aberylesky, Bythumnosia, Hielia, Szartonhalia, Arcyrosia, Zolterra, Buecia, Cheria, Briarcele, Crolymia, Papsosia, Lepoki, Crewichin, Burovia, Magarguil, Tanartosia, Kokegyoujsia y Hegeia**.

Estos estados reemplazan la división geopolítica abstracta anterior como estructura territorial principal. Las dinámicas narrativas de los Reinos del Norte, la Zona Central, los Reinos Mercantes del Sur y el Reino Expansionista se conservan como regiones culturales y políticas emergentes que pueden atravesar varias fronteras.

La información macroeconómica y política de cada estado se alimenta de la exportación de Azgaar: capital asignada, cultura, forma de gobierno, datos económicos, color y provincias pertenecientes.

### 2.2. Provincias y Territorio Simulado
El nivel meso está compuesto por **252 provincias válidas**. El registro neutral `0` de Azgaar se descarta. Cada provincia es un nodo territorial autónomo y contiene su propio nombre, tipo administrativo, estado padre, centro geográfico y ciudad principal cuando existe.

El nivel micro está formado por **5.709 celdas terrestres**. Las celdas se agrupan mediante el campo `province` de Azgaar y proporcionan la malla espacial para calcular adyacencias, rutas comerciales, expansión de plagas y distancias entre provincias.

La estructura resultante es:
* **Macro:** 18 estados soberanos.
* **Meso:** 252 provincias y entidades de simulación.
* **Micro:** 5.709 celdas geográficas.

### 2.3. Sociedad, Gremios y Religión
La sociedad se organiza en torno a instituciones con agendas propias que reaccionan al estado del mundo:
* **La Santa Iglesia:** La facción de mayor peso moral e influencia política en todo Éter. Adoran a un único Dios (cuyo nombre no se menciona). La devoción de la población hacia la Iglesia (Fervor Religioso) es el escudo principal contra las artes oscuras.
* **Torre de los Magos:** Institución que rige, educa y controla a los escasos usuarios de magia legal en el mundo.
* **Magos Oscuros y Cultistas:** Entidades ilegales que florecen orgánicamente en regiones donde la población pierde la fe en la Santa Iglesia (ya sea por hambrunas, abandono político o desastres no resueltos).
* **Los Gremios:** 
  * *Gremio de Aventureros:* Organiza escuadrones clásicos (Caballero, Tanque, Rango/Mago) para resolver crisis locales.
  * *Gremio Mercante y Agrícola:* Controlan la economía base. Si una plaga destruye los cultivos, el Gremio Agrícola quiebra y el Gremio Mercante eleva los precios.

### 2.4. Ecosistema y La Amenaza Demoníaca
Los monstruos en Éter (Goblins, Arpías, Lamias, Slimes, Grifos, Wyverns) forman parte de la fauna natural. Incluso existen Dragones, seres ancestrales y nobles que habitan en aislamiento; su simple presencia cerca de reinos es un presagio de desastres a nivel cósmico.

Sin embargo, el equilibrio se ha roto por la **Profecía del Rey Demonio**. Una infección biológica/mágica ha comenzado a propagarse desde el Norte y el extremo Sur. Esta plaga corrompe la tierra, muta a la fauna local y obliga a monstruos territoriales (como los Wyverns) a migrar hacia zonas pobladas buscando refugio, generando crisis emergentes que los jugadores deben resolver.

---

## 3. Arquitectura Técnica (El Motor de Éter)

Para garantizar la escalabilidad desde un script local hasta un servidor masivo para Unreal Engine VR, el código sigue los principios de **Clean Architecture**, **Domain-Driven Design (DDD)** y **Entity Component System (ECS)**.

### 3.1. Inmutabilidad y Desacoplamiento (Data-Driven)
* **Entities:** Cada provincia válida se instancia como una entidad ECS identificada por un `EntityID`. Los estados soberanos funcionan como agrupaciones políticas superiores.
* **Components:** Estructuras de datos puros (`Value Objects`) sin lógica interna. Ejemplos: `FervorReligioso`, `NivelInfeccion`, `RegionComponent` y los futuros componentes económicos y geográficos.
* **Systems:** Clases puramente lógicas que recorren las 252 entidades provinciales y aplican reglas locales y relaciones entre territorios.

### 3.2. Bus de Eventos Determinista (Event Sourcing)
El mundo no cambia modificando variables directamente, sino emitiendo **Eventos de Dominio** inmutables. 
Si el fervor de un reino cae por debajo de un umbral, se emite un evento: `HegemoniaIglesiaRotasEvent`. Otros sistemas (como el de spawneo de NPCs hostiles) escuchan este evento y reaccionan en consecuencia, permitiendo un rendimiento óptimo y un registro histórico perfecto de todo lo que ocurre en el servidor.

### 3.3. Fórmulas Matemáticas del Dominio (Ejemplo Implementado)
La generación de cultistas no es un spawn aleatorio, es una simulación socio-religiosa calculada en el `FaithSystem` mediante la siguiente fórmula:

$$\text{Tasa\_Magos\_Oscuros}=(1.0 - \text{Fervor\_Iglesia})^2 \times \text{Infeccion\_Demoníaca} \times \text{Coeficiente\_Cultismo}$$

Si los jugadores permiten que la infección suba y la fe baje, las matemáticas del sistema generarán enemigos de forma autónoma.

### 3.4. Topología de Grafo Espacial
El mapa de Éter no es un arreglo 2D rígido. Las 252 provincias son nodos territoriales y las 5.709 celdas de Azgaar forman la topología subyacente. Las adyacencias, rutas comerciales y cuencas fluviales actúan como aristas para simular de forma precisa el movimiento de la plaga, los ejércitos, el comercio y las herejías entre provincias y estados.

### 3.5. Interacción y Bucle de Simulación
La interacción actual se mantiene como una consola interactiva por turnos mediante `iniciar_simulacion`. El motor espera comandos del usuario, como `purgar` o `pasar`, y ejecuta `tick(delta_tiempo=1.0)` únicamente cuando el jugador hace avanzar el mundo.

El bucle continental recorre las entidades provinciales y sus sistemas. Los eventos se publican de forma localizada, identificando la provincia y el estado afectados; por ejemplo: `La fe ha colapsado en Treaberfia Shire (Aberylesky)`.

La separación entre `eter_core`, `eter_infrastructure` y el bus de eventos permite conectar posteriormente una GUI o un backend WebSocket para visualizar el mapa en tiempo real sin modificar el núcleo lógico.

---

## 4. Estado Actual del Desarrollo (Fase 1)
Se ha configurado el núcleo del motor (`eter-engine`) en Python con tipado estricto, estructurado en las siguientes capas:
1.  **Dominio (`eter_core/domain`):** Tipos inmutables, eventos del mundo y catálogos de datos (arquetipos, productos, monstruos, objetos, recetas, hechizos, sets, NPCs).
2.  **Componentes (`eter_core/components`):** Datos regionales (población, facción, fe, infección), economía, comercio, enemigos, stock y estado del jugador.
3.  **Sistemas (`eter_core/systems`):** 21 sistemas que cubren toda la simulación.
4.  **Infraestructura (`eter_infrastructure`):** `EventBus` y persistencia (`SaveSystem`).
5.  **Importación de mundo (`eter_infrastructure/persistence`):** `AzgaarTranslator` traduce la exportación real de Azgaar (`pack.states`, `pack.provinces` y `pack.cells`) a estados y regiones normalizadas.
6.  **Escala territorial:** El mapa actual aporta 18 estados soberanos, 252 provincias simulables y 5.709 celdas terrestres.

### 4.1. Catálogos de Datos (Data-Driven)
El mundo es 100% data-driven: nada se hardcodea en los sistemas.

* **`archetypes.py`**: 4 arquetipos de nacimiento con doble nombre y stats.
  * Tanque / Coloso (alta vida y tenacidad), Mago / Erudito (alto maná e inteligencia), Caballero / Vanguardia (balanceado), Asesino / Acechador (alta estamina y +25% crítico).
* **`products.py`**: metales (hierro → hierro rúnico → mithril), subproductos de monstruos y alimentos. Cada producto tiene rareza, valor base, dificultad, geografía nativa y peso.
* **`monsters.py`**: bestiario de 15 criaturas por tiers 1-5, con drops que referencian productos válidos.
* **`items.py`**: objetos consumibles, herramientas y equipables (con slot, peso y conjunto).
* **`recipes.py`**: recetas de herrería (incluye las 36 piezas de set generadas automáticamente).
* **`spells.py`**: 6 hechizos (buff, curación, área, daño).
* **`armor_sets.py`**: 12 sets de ropa (4 clases × 3 niveles), 36 piezas.
* **`npcs.py`**: 6 NPCs amistosos.

### 4.2. Sistemas Implementados (21)
| Sistema | Función |
|---|---|
| `FaithSystem` | El fervor baja con la infección; calcula la tasa de magos oscuros |
| `InfectionSystem` | Propaga la plaga entre provincias adyacentes (grafo) |
| `EconomicSystem` | Genera riqueza y comercio entre provincias |
| `CultistSystem` | Spawn de cultistas según la tasa de fe |
| `MonsterSpawnSystem` | Fauna salvaje emergente por bioma/infección/fe |
| `CombatSystem` | Combate por turnos con crítico, tenacidad y drops |
| `ItemSystem` | Dar/usar/equipar objetos |
| `MerchantSystem` | Compra/venta de materiales con margen |
| `SmithSystem` | Forja de equipo a partir de recetas |
| `PricingSystem` | Precios dinámicos por ubicación + oferta/demanda |
| `WeightSystem` | Peso, capacidad de carga y sobrecarga |
| `HungerSystem` | Hambre por día con penalizaciones según arquetipo |
| `SpawnSystem` | Creación del jugador con arquetipo elegible |
| `SpellSystem` | Lanza hechizos consumiendo maná (buffs temporales) |
| `ProgressionSystem` | XP y subida de nivel |
| `TravelSystem` | Distancias y coste de viaje (fronteras) |
| `RandomEventSystem` | Eventos aleatorios de baja probabilidad |
| `SetSystem` | Detección de sets completos y buffs |
| `NpcSystem` | Interacción con el pueblo (posadero, cura, capitán...) |
| `StockSystem` | Oferta/demanda fluctuante por provincia |
| `SaveSystem` | Persistencia (guardar/cargar partida) |

### 4.3. Bucle de Juego Completo
El jugador ya puede vivir un ciclo completo:

```
elegir arquetipo → explorar → cazar monstruos → drops → vender/forjar
→ equipar sets → lanzar hechizos → subir nivel → interactuar con el pueblo → guardar
```

El mundo vive **sin el jugador**: monstruos, infección, fe, economía, precios y stock evolucionan solos cada tick.

### 4.4. Roadmap (visión de skitoji)
Completado:
* ✅ Precios dinámicos (ubicación + oferta/demanda)
* ✅ Sistema de peso
* ✅ Hambre activa (ligada al día)
* ✅ Arquetipos elegibles con atributos clave
* ✅ Productos (hierro → hierro rúnico → mithril)
* ✅ Bestiario completo + combate + drops
* ✅ Mercader + herrero (economía de NPCs)
* ✅ Distancias (ciudad↔ciudad ≠ país↔país)
* ✅ Hechizos/habilidades (invisibilidad en área, buffs con mana)
* ✅ Eventos aleatorios de baja probabilidad
* ✅ Sets de ropa por clase con buff al completar
* ✅ NPCs amistosos + interacción con el pueblo
* ✅ XP / nivel (progresión)
* ✅ Persistencia (guardar/cargar partida)
* ✅ Stock fluctuante de mercaderes/herreros

Futuro:
* ⏳ Herreros/mercaderes como entidades individuales con stock por NPC (hoy es stock por provincia)
* ⏳ Más hechizos y habilidades
* ⏳ Combate con múltiples enemigos / hordas
* ⏳ Integración gráfica (2D/3D) y, a largo plazo, VR

El lore original se conserva e integra sobre esta geografía. La Infección Demoníaca puede surgir en provincias fronterizas o zonas salvajes; la Santa Iglesia puede medir el fervor por provincia o por estado; y los gremios pueden reaccionar a las crisis económicas y territoriales locales.