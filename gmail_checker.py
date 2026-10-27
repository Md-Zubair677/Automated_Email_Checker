from pathlib import Path

from playwright.sync_api import sync_playwright
from credentials import GMAIL_PASSWORD, GMAIL_USERNAME

unread_messages = []
auth_state_path = (
    Path(__file__).resolve().parent
    / "playwright"
    / ".auth"
    / "storage_state.json"
)
# First login needs a visible browser; saved sessions can run headlessly.
has_saved_state = auth_state_path.is_file()

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=has_saved_state,
        args=[
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ],
    )
    if has_saved_state:
        context = browser.new_context(storage_state=str(auth_state_path))
    else:
        context = browser.new_context()
    page = context.new_page()

    if has_saved_state:
        page.goto("https://mail.google.com/mail/u/0/#inbox")
        if "accounts.google.com" in page.url:
            browser.close()
            raise RuntimeError(
                "The saved Gmail login has expired or needs verification. "
                "Delete the saved state and run again to sign in visibly."
            )
    else:
        # Sign in interactively so the user can complete Google's 2-step check.
        page.goto("https://mail.google.com")
        page.get_by_label("Email or phone").fill(GMAIL_USERNAME)
        page.get_by_role("button", name="Next").click()
        page.get_by_label("Enter your password").fill(GMAIL_PASSWORD)
        page.get_by_role("button", name="Next").click()
        print(
            "Complete 2-step verification in the browser. "
            "The script will continue when Gmail loads."
        )
        page.wait_for_url("https://mail.google.com/**", timeout=300_000)

        page.goto("https://mail.google.com/mail/u/0/#inbox")

    page.get_by_role("main").wait_for()

    auth_state_path.parent.mkdir(parents=True, exist_ok=True)
    # Gmail marks unread inbox rows with the zA and zE classes.
    unread_rows = page.locator("tr.zA.zE")
    for index in range(unread_rows.count()):
        row = unread_rows.nth(index)
        sender = row.locator("span[email]").first
        unread_messages.append(
            {
                "sender_name": sender.inner_text().strip(),
                "sender_email": sender.get_attribute("email") or "",
                "subject": row.locator("span.bog").first.inner_text().strip(),
            }
        )

    # Refresh the session state so it can be reused on the next run.
    context.storage_state(path=str(auth_state_path))

    browser.close()

print(f"Unread message count: {len(unread_messages)}")

if not unread_messages:
    print("No unread messages found in the inbox.")
else:
    for index, message in enumerate(unread_messages, start=1):
        print(f"\n{index}.")
        print(f"   Sender:  {message['sender_name']}")
        print(f"   Email:   {message['sender_email']}")
        print(f"   Subject: {message['subject']}")