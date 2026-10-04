from __future__ import annotations

from collections import Counter
from typing import Any

from ..business_models import Material, Repair, RepairStatus


class DashboardService:
    """Generate aggregated KPIs for the owner dashboard."""

    def build_summary(self, repairs: list[Repair], materials: list[Material]) -> dict[str, Any]:
        status_counts = Counter(item.status.value for item in repairs)
        low_stock = [m for m in materials if m.stock <= m.reorder_level]

        return {
            "total_repairs": len(repairs),
            "status_counts": dict(status_counts),
            "overdue_repairs": sum(
                1
                for repair in repairs
                if repair.status != RepairStatus.ISSUED and repair.due_at is not None
            ),
            "ready_for_pickup": sum(
                1 for repair in repairs if repair.status == RepairStatus.READY_FOR_PICKUP
            ),
            "low_stock_items": len(low_stock),
            "total_estimate_cost": round(sum((r.estimate_cost or 0) for r in repairs), 2),
            "materials_low_stock": [m.to_dict() for m in low_stock],
        }


__all__ = ["DashboardService"]
