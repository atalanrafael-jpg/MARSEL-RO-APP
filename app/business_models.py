from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class RepairStatus(str, Enum):
    RECEIVED = "received"
    ASSESSED = "assessed"
    ESTIMATE_APPROVED = "estimate_approved"
    IN_WORK = "in_work"
    WAITING_FOR_PART = "waiting_for_part"
    QUALITY_CONTROL = "quality_control"
    READY_FOR_PICKUP = "ready_for_pickup"
    ISSUED = "issued"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    REWORK_REQUIRED = "rework_required"


@dataclass
class Client:
    id: str
    full_name: str
    phone: str = ""
    email: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "phone": self.phone,
            "email": self.email,
            "notes": self.notes,
        }


@dataclass
class Item:
    id: str
    client_id: str
    category: str
    subtype: str
    material: str
    stones: str = ""
    description: str = ""
    condition_received: str = ""
    serial_number: str = ""
    photos: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "client_id": self.client_id,
            "category": self.category,
            "subtype": self.subtype,
            "material": self.material,
            "stones": self.stones,
            "description": self.description,
            "condition_received": self.condition_received,
            "serial_number": self.serial_number,
            "photos": self.photos,
        }


@dataclass
class Material:
    id: str
    name: str
    category: str
    unit: str
    stock: int
    reorder_level: int
    cost_per_unit: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "unit": self.unit,
            "stock": self.stock,
            "reorder_level": self.reorder_level,
            "cost_per_unit": self.cost_per_unit,
            "low_stock": self.stock <= self.reorder_level,
        }


@dataclass
class Repair:
    id: str
    client: Client
    item: Item
    status: RepairStatus
    description: str = ""
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    due_at: str | None = None
    estimate_cost: float | None = None
    actual_cost: float | None = None
    status_history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "client": self.client.to_dict(),
            "item": self.item.to_dict(),
            "status": self.status.value,
            "description": self.description,
            "received_at": self.received_at.isoformat(),
            "due_at": self.due_at,
            "estimate_cost": self.estimate_cost,
            "actual_cost": self.actual_cost,
            "status_history": self.status_history,
        }


@dataclass
class QualityCheck:
    repair_id: str
    result: str
    notes: str = ""
    checked_by: str = "system"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "repair_id": self.repair_id,
            "result": self.result,
            "notes": self.notes,
            "checked_by": self.checked_by,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class NotificationMessage:
    repair_id: str
    channel: str
    template: str
    message: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "repair_id": self.repair_id,
            "channel": self.channel,
            "template": self.template,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
        }
