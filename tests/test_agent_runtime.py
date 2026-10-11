from agent_runtime.registry import Agent, AgentRegistry
from agent_runtime.permissions import PermissionEngine


def test_registry_round_trip_and_permission_boundary():
    registry = AgentRegistry()
    agent = Agent("tester", "testing", frozenset({"read", "test"}))
    registry.register(agent)
    assert registry.get("tester") == agent

    engine = PermissionEngine()
    assert engine.allowed(agent, "test", "LOW") is True
    assert engine.allowed(agent, "production_write", "LOW") is False
    assert engine.allowed(agent, "delete", "LOW") is False
    assert engine.allowed(agent, "read", "CRITICAL") is False


def test_critical_risk_is_case_insensitive_and_whitespace_tolerant():
    agent = Agent("tester", "testing", frozenset({"read"}))
    engine = PermissionEngine()

    assert engine.allowed(agent, "read", "critical") is False
    assert engine.allowed(agent, "read", " CRITICAL ") is False


def test_unknown_or_missing_risk_level_fails_closed():
    agent = Agent("tester", "testing", frozenset({"read"}))
    engine = PermissionEngine()

    assert engine.allowed(agent, "read", "URGENT") is False
    assert engine.allowed(agent, "read", "") is False
    assert engine.allowed(agent, "read", None) is False


def test_denied_actions_are_case_insensitive():
    agent = Agent("tester", "testing", frozenset({"delete", "production_write"}))
    engine = PermissionEngine()

    assert engine.allowed(agent, "DELETE", "LOW") is False
    assert engine.allowed(agent, "Production_Write", "LOW") is False
