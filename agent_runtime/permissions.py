class PermissionEngine:
    """Fail-closed permission checks for agent actions."""

    _VALID_RISK_LEVELS = frozenset({"LOW", "MEDIUM", "HIGH", "CRITICAL"})
    _DENIED_ACTIONS = frozenset({"delete", "production_write"})

    def allowed(self, agent, action: str, risk_level: str) -> bool:
        if not isinstance(action, str) or not action.strip():
            return False
        if not isinstance(risk_level, str):
            return False

        normalized_action = action.strip().lower()
        normalized_risk = risk_level.strip().upper()

        if normalized_risk not in self._VALID_RISK_LEVELS:
            return False
        if normalized_action in self._DENIED_ACTIONS:
            return False
        if normalized_risk == "CRITICAL":
            return False

        return normalized_action in agent.permissions
