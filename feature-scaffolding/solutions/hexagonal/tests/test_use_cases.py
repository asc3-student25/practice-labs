"""Tests for use cases — stubbed adapters, real use case logic."""


def test_create_and_dispatch_persists_and_returns_status():
    raise NotImplementedError


def test_create_and_dispatch_marks_partial_when_one_channel_fails():
    raise NotImplementedError


def test_transient_failure_schedules_retry_per_policy():
    raise NotImplementedError


def test_permanent_failure_does_not_schedule_retry():
    raise NotImplementedError


def test_audit_entry_appended_on_every_status_change():
    raise NotImplementedError
