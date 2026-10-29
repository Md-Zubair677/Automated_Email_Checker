import importlib.util
import sys
import types
from pathlib import Path
from unittest import mock

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "gmail_checker.py"


class FakeLocator:
    def __init__(self, text="", email="", items=None):
        self.text = text
        self.email = email
        self.items = items or []
        self.first = self

    def count(self):
        return len(self.items)

    def nth(self, index):
        return self.items[index]

    def inner_text(self):
        return self.text

    def get_attribute(self, name):
        if name == "email":
            return self.email
        return None


class FakeMessageRow:
    def __init__(self, sender_name, sender_email, subject):
        self.sender = FakeLocator(sender_name, sender_email)
        self.subject = FakeLocator(subject)

    def locator(self, selector):
        if selector == "span[email]":
            return self.sender
        if selector == "span.bog":
            return self.subject
        raise AssertionError(f"Unexpected row selector: {selector}")


class FakePage:
    def __init__(self, rows, expired_saved_state=False):
        self.rows = FakeLocator(items=rows)
        self.url = ""
        self.expired_saved_state = expired_saved_state
        self.labels = {}
        self.buttons = {}
        self.main = mock.Mock()
        self.main.wait_for = mock.Mock()

    def goto(self, url):
        if self.expired_saved_state:
            self.url = "https://accounts.google.com/signin"
        else:
            self.url = url

    def get_by_label(self, label):
        return self.labels.setdefault(label, mock.Mock())

    def get_by_role(self, role, name=None):
        if role == "main":
            return self.main
        return self.buttons.setdefault((role, name), mock.Mock())

    def wait_for_url(self, url, timeout):
        self.url = "https://mail.google.com/mail/u/0/#inbox"

    def locator(self, selector):
        if selector != "tr.zA.zE":
            raise AssertionError(f"Unexpected page selector: {selector}")
        return self.rows


@pytest.fixture
def checker(monkeypatch, capsys):
    harness = types.SimpleNamespace(last_browser=None)

    def run(has_saved_state, rows=(), expired_saved_state=False):
        page = FakePage(rows, expired_saved_state)
        browser_context = mock.Mock()
        browser_context.new_page.return_value = page
        browser = mock.Mock()
        browser.new_context.return_value = browser_context
        playwright = mock.Mock()
        playwright.chromium.launch.return_value = browser
        harness.last_browser = browser

        manager = mock.MagicMock()
        manager.__enter__.return_value = playwright
        sync_api = types.ModuleType("playwright.sync_api")
        sync_api.sync_playwright = mock.Mock(return_value=manager)
        playwright_package = types.ModuleType("playwright")
        playwright_package.__path__ = []

        module_name = f"gmail_checker_test_run_{id(page)}"
        spec = importlib.util.spec_from_file_location(module_name, SCRIPT_PATH)
        module = importlib.util.module_from_spec(spec)

        with monkeypatch.context() as patcher:
            patcher.setitem(
                sys.modules,
                "playwright",
                playwright_package,
            )
            patcher.setitem(sys.modules, "playwright.sync_api", sync_api)
            patcher.setitem(sys.modules, module_name, module)
            patcher.syspath_prepend(str(SCRIPT_PATH.parent))
            patcher.setattr(Path, "is_file", mock.Mock(return_value=has_saved_state))
            patcher.setattr(Path, "mkdir", mock.Mock())
            spec.loader.exec_module(module)

        output = capsys.readouterr().out
        return types.SimpleNamespace(
            output=output,
            page=page,
            browser=browser,
            browser_context=browser_context,
            playwright=playwright,
        )

    harness.run = run
    return harness


def test_manual_login_prints_message_details(checker):
    message = FakeMessageRow("Example Sender", "sender@example.com", "Example subject")
    result = checker.run(False, [message])

    assert "Sign in to Gmail manually in the browser" in result.output
    assert "Unread message count: 1" in result.output
    assert "Sender:  Example Sender" in result.output
    assert "Email:   sender@example.com" in result.output
    assert "Subject: Example subject" in result.output
    assert result.page.labels == {}
    assert result.page.buttons == {}
    result.browser.new_context.assert_called_once_with()
    result.browser_context.storage_state.assert_called_once()
    result.browser.close.assert_called_once()
    assert not result.playwright.chromium.launch.call_args.kwargs["headless"]


def test_extracts_multiple_unread_messages(checker):
    messages = [
        FakeMessageRow("First Sender", "first@example.com", "First subject"),
        FakeMessageRow("Second Sender", "second@example.com", "Second subject"),
    ]

    result = checker.run(False, messages)

    assert "Unread message count: 2" in result.output
    assert "Sender:  First Sender" in result.output
    assert "Email:   first@example.com" in result.output
    assert "Subject: First subject" in result.output
    assert "Sender:  Second Sender" in result.output
    assert "Email:   second@example.com" in result.output
    assert "Subject: Second subject" in result.output


def test_missing_sender_and_subject_are_printed_as_empty(checker):
    message = FakeMessageRow("", "", "")

    result = checker.run(False, [message])

    assert "Unread message count: 1" in result.output
    assert "Sender:  \n" in result.output
    assert "Email:   \n" in result.output
    assert "Subject: \n" in result.output


def test_saved_session_uses_headed_mode_and_reports_empty_inbox(checker):
    result = checker.run(True)

    assert "Unread message count: 0" in result.output
    assert "No unread messages found in the inbox." in result.output
    assert not result.playwright.chromium.launch.call_args.kwargs["headless"]
    result.browser_context.storage_state.assert_called_once()
    assert result.browser.new_context.call_args.kwargs["storage_state"]


def test_expired_saved_session_raises_and_closes_browser(checker):
    with pytest.raises(RuntimeError, match="saved Gmail login has expired"):
        checker.run(True, expired_saved_state=True)

    checker.last_browser.close.assert_called_once()
