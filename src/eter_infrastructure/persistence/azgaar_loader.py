import json
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

@dataclass
class RegionData:
    id: int
    name: str
    cell_ids: List[int] = field(default_factory=list)
    biome: str = ""
    religion_id: Optional[int] = None
    fervor: float = 0.0
    state_id: int = 0
    full_name: str = ""
    center_cell_id: Optional[int] = None
    has_city: bool = False
    coordinates: tuple[float, float] = (0.0, 0.0)

@dataclass
class StateData:
    id: int
    name: str
    color: str
    provinces: List[int] = field(default_factory=list)

class AzgaarTranslator:
    """Traduce y normaliza la data cruda de un mapa de Azgaar a entidades de Éter."""
    
    def __init__(self, json_file_path: str):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)

    def _pack(self) -> Dict[str, Any]:
        pack = self.raw_data.get('pack', {})
        return pack if isinstance(pack, dict) else {}

    @property
    def raw_map(self) -> Dict[str, Any]:
        return self.raw_data

    def _records(self, key: str) -> Iterable[Dict[str, Any]]:
        records = self.raw_data.get(key)
        if records is None:
            records = self._pack().get(key, [])
        return (record for record in records if isinstance(record, dict))
            
    def extract_states(self) -> Dict[int, StateData]:
        states = {}
        for raw_state in self._records('states'):
            state_id = raw_state.get('id', raw_state.get('i'))
            if state_id in (None, 0):
                continue

            states[state_id] = StateData(
                id=state_id,
                name=raw_state.get('name', 'Desconocido'),
                color=raw_state.get('color', '#000000'),
                provinces=raw_state.get('provinces', [])
            )
        return states

    def extract_regions(self) -> Dict[int, RegionData]:
        regions = {}
        cells_by_province: Dict[int, List[Dict[str, Any]]] = {}
        for cell in self._pack().get('cells', []):
            province_id = cell.get('province', 0)
            if province_id:
                cells_by_province.setdefault(province_id, []).append(cell)

        for raw_prov in self._records('provinces'):
            prov_id = raw_prov.get('id', raw_prov.get('i'))
            if prov_id in (None, 0):
                continue

            province_cells = cells_by_province.get(prov_id, [])
            biomes = Counter(
                cell.get('biome') for cell in province_cells
                if cell.get('biome') not in (None, 0)
            )
            religions = Counter(
                cell.get('religion') for cell in province_cells
                if cell.get('religion') not in (None, 0)
            )
            regions[prov_id] = RegionData(
                id=prov_id,
                name=raw_prov.get('name', 'Región sin nombre'),
                cell_ids=[cell.get('i') for cell in province_cells if cell.get('i') is not None],
                biome=raw_prov.get('biome', biomes.most_common(1)[0][0] if biomes else ''),
                religion_id=religions.most_common(1)[0][0] if religions else None
                ,state_id=raw_prov.get('state', 0) or 0,
                full_name=raw_prov.get('fullName', raw_prov.get('name', 'Región sin nombre')),
                center_cell_id=raw_prov.get('center'),
                has_city=bool(raw_prov.get('burg', 0)),
                coordinates=tuple(
                    province_cells[0].get('p', [0.0, 0.0])
                    if province_cells else [0.0, 0.0]
                )
            )
        return regions

    def extract_adjacencies(self, valid_province_ids: Optional[set[int]] = None) -> Dict[int, set[int]]:
        """Construye adyacencias entre provincias usando vecinos de celdas."""
        valid_ids = valid_province_ids or set(self.extract_regions())
        adjacencies = {province_id: set() for province_id in valid_ids}
        cells = self._pack().get('cells', [])
        for cell in cells:
            province_id = cell.get('province', 0)
            if province_id not in valid_ids:
                continue
            for neighbor_id in cell.get('c', []):
                if not isinstance(neighbor_id, int) or not 0 <= neighbor_id < len(cells):
                    continue
                neighbor_province = cells[neighbor_id].get('province', 0)
                if neighbor_province in valid_ids and neighbor_province != province_id:
                    adjacencies[province_id].add(neighbor_province)
        return adjacencies