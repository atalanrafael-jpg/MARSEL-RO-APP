from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .business_models import Client, Item, Material, Repair, RepairStatus


class RepairService:
    """In-memory repair service for Phase 1 and Phase 2 operations."""

    def __init__(self) -> None:
        self._repairs: dict[str, Repair] = {}

    def create_repair(
        self,
        *,
        client: Client,
        item: Item,
        status: RepairStatus | str = RepairStatus.RECEIVED,
        description: str = "",
        due_at: str | None = None,
        estimate_cost: float | None = None,
    ) -> Repair:
        repair_status = status if isinstance(status, RepairStatus) else RepairStatus(status)
        repair = Repair(
            id=f"repair-{len(self._repairs) + 1}",
            client=client,
            item=item,
            status=repair_status,
            description=description,
            due_at=due_at,
            estimate_cost=estimate_cost,
            actual_cost=None,
            status_history=[
                {
                    "status": repair_status.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "note": "Repair created",
                }
            ],
        )
        self._repairs[repair.id] = repair
        return repair

    def list_repairs(self) -> list[Repair]:
        return list(self._repairs.values())

    def get_repair(self, repair_id: str) -> Repair:
        if repair_id not in self._repairs:
            raise KeyError(f"Repair {repair_id} not found")
        return self._repairs[repair_id]

    def update_status(self, repair_id: str, *, status: RepairStatus | str, note: str = "") -> Repair:
        repair = self.get_repair(repair_id)
        new_status = status if isinstance(status, RepairStatus) else RepairStatus(status)
        repair.status = new_status
        repair.status_history.append(
            {
                "status": new_status.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": note or "Status updated",
            }
        )
        return repair

    def customer_repairs(self, client_id: str) -> list[Repair]:
        return [repair for repair in self._repairs.values() if repair.client.id == client_id]


__all__ = ["RepairService"]
