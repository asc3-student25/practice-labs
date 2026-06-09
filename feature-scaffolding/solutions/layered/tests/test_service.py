"""Tests for the notification service."""


def test_dispatch_marks_sent_when_all_channels_succeed():
    raise NotImplementedError


def test_dispatch_marks_partial_when_some_channels_fail():
    raise NotImplementedError


def test_transient_failure_triggers_retry_policy():
    raise NotImplementedError


def test_permanent_failure_does_not_retry():
    raise NotImplementedError


def test_every_status_change_writes_an_audit_entry():
    raise NotImplementedError
