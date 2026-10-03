from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..business_models import Material


@dataclass
class MaterialCatalog:
    """Simple in-memory catalog to represent stock and reorder thresholds."""

    _materials: dict[str, Material] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self._materials:
            self._materials = {
                "gold-01": Material(
                    id="gold-01",
                    name="Gold 585",
                    category="metal",
                    unit="g",
                    stock=1200,
                    reorder_level=500,
                    cost_per_unit=2000,
                ),
                "diamond-01": Material(
                    id="diamond-01",
                    name="Diamond",
                    category="stone",
                    unit="ct",
                    stock=30,
                    reorder_level=10,
                    cost_per_unit=3500,
                ),
            }

    def create_material(
        self,
        *,
        name: str,
        category: str,
        unit: str,
        stock: int,
        reorder_level: int,
        cost_per_unit: float,
    ) -> Material:
        material = Material(
            id=f"material-{len(self._materials) + 1}",
            name=name,
            category=category,
            unit=unit,
            stock=stock,
            reorder_level=reorder_level,
            cost_per_unit=cost_per_unit,
        )
        self._materials[material.id] = material
        return material

    def list_materials(self) -> list[Material]:
        return list(self._materials.values())

    def low_stock_materials(self) -> list[Material]:
        return [m for m in self._materials.values() if m.stock <= m.reorder_level]

    def get_material(self, material_id: str) -> Material:
        if material_id not in self._materials:
            raise KeyError(f"Material {material_id} not found")
        return self._materials[material_id]

    def update_stock(self, material_id: str, delta: int) -> Material:
        material = self.get_material(material_id)
        material.stock = max(0, material.stock + delta)
        return material


__all__ = ["MaterialCatalog"]
