from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RepairEstimate:
    item_category: str
    material: str
    labour_hours: float
    material_cost: float
    recommended_price: float
    confidence: str
    requires_manual_review: bool

    def to_dict(self) -> dict[str, str | float | bool]:
        return {
            "item_category": self.item_category,
            "material": self.material,
            "labour_hours": self.labour_hours,
            "material_cost": self.material_cost,
            "recommended_price": self.recommended_price,
            "confidence": self.confidence,
            "requires_manual_review": self.requires_manual_review,
        }


class RepairEstimator:
    """Deterministic, rule-based estimator for a jewelry/watch repair workflow."""

    def estimate(self, *, category: str, material: str, description: str = "") -> RepairEstimate:
        category_key = (category or "jewelry").lower()
        material_key = (material or "gold").lower()

        base_hours = {
            "jewelry": 2.5,
            "watch": 4.0,
            "glasses": 1.5,
        }.get(category_key, 2.0)

        material_multiplier = {
            "gold": 1.0,
            "silver": 0.8,
            "platinum": 1.4,
            "steel": 0.7,
            "leather": 0.6,
        }.get(material_key, 1.0)

        labor_hours = base_hours * (1.1 if "repair" in description.lower() else 1.0)
        material_cost = round(120 * material_multiplier, 2)
        recommended_price = round((labor_hours * 2500) + material_cost, 2)

        requires_manual_review = "stone" in description.lower() or "watch" in category_key
        confidence = "medium" if requires_manual_review else "high"

        return RepairEstimate(
            item_category=category_key,
            material=material_key,
            labour_hours=round(labor_hours, 2),
            material_cost=material_cost,
            recommended_price=recommended_price,
            confidence=confidence,
            requires_manual_review=requires_manual_review,
        )


__all__ = ["RepairEstimator", "RepairEstimate"]
