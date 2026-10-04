from __future__ import annotations

from typing import Any

from ..business_models import Client, Repair, RepairStatus


class CustomerService:
    """Customer-centric service for repair status summaries and contact data."""

    def __init__(self, repair_service: Any) -> None:
        self._repair_service = repair_service

    def register_customer(self, *, client_id: str, full_name: str, phone: str = "", email: str = "") -> Client:
        client = Client(id=client_id, full_name=full_name, phone=phone, email=email)
        return client

    def customer_status(self, client_id: str) -> dict[str, Any]:
        repairs = self._repair_service.customer_repairs(client_id)
        return {
            "client_id": client_id,
            "repair_count": len(repairs),
            "active_repairs": [repair.to_dict() for repair in repairs if repair.status not in {RepairStatus.ISSUED, RepairStatus.CANCELLED}],
            "latest_status": repairs[-1].status.value if repairs else None,
        }


__all__ = ["CustomerService"]
