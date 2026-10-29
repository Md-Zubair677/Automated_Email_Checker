# Gmail Unread Message Checker

A small Python script that signs in to Gmail with Playwright, finds unread
messages in the inbox, and prints each message's sender name, sender email
address, and subject in the terminal. It does not open or mark messages as
read.

## What the project does

1. Checks whether a saved Playwright login session exists.
2. If there is no saved session, opens a visible Chromium browser and lets you
   sign in manually, including entering your email, password, and any
   verification prompts.
3. Saves the browser session to `playwright/.auth/storage_state.json`.
4. If a saved session exists, starts a visible Chromium browser and reuses it.
5. Reads unread messages shown in the Gmail inbox and prints the count and
   message details after closing the browser.

Google can expire a saved session or require you to verify again. If that
happens, remove the saved session file and run the script again to sign in
visibly.

## Project files

- `gmail_checker.py` — the Playwright script. It controls the browser,
  collects unread inbox message details, saves the login state, and prints the
  results.
- `credentials.py` — not required; the script does not read or store your
  password or email address.
- `credentials.example.py` — an optional template; it is not used by the
  checker.
- `tests/test_gmail_checker.py` — mocked tests for login flow, unread-message
  extraction, and saved-session behavior.
- `playwright/.auth/storage_state.json` — created automatically after a
  successful sign-in. It contains sensitive browser session data. Do not share
  or commit it.
- `venv/` — an optional local Python virtual environment. It is not required
  in the repository; each user can create their own.
- `README.md` — this guide.

## Requirements

- Python 3.10 or newer
- A Google account with Gmail access
- Internet access

Enter your email, password, and any verification manually in the visible
browser.

## Setup

### 1. Open a terminal in the project folder

For example, in PowerShell:

```powershell
cd C:\Email
```

### 2. Create and activate a virtual environment (recommended)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, you can invoke the environment's Python
directly as `.\venv\Scripts\python.exe`.

### 3. Install Playwright and its Chromium browser

```powershell
python -m pip install playwright
python -m playwright install chromium
```

### 4. Run the script

```powershell
python gmail_checker.py
```

## First sign-in and 2-step verification

When `playwright/.auth/storage_state.json` does not exist:

1. The script opens a visible Chromium window.
2. Enter your email, password, and any verification prompts manually in the
   browser.
3. The script continues after Google redirects to Gmail, checks the inbox, and
   saves the session state.
4. The browser closes, then the unread count and messages are printed in the
   terminal.

The script waits up to five minutes for Gmail to load after you start signing
in. If you do not finish in time, run it again and complete sign-in in the
visible browser.

## Later runs (visible browser)

When the saved session file exists, the script launches a visible Chromium
window and uses the saved session. Run the same command:

```powershell
python gmail_checker.py
```

If the session has expired or Google requests verification, the script reports
that the saved login needs attention. To sign in again, delete only
`playwright/.auth/storage_state.json`, then rerun the script. It will open the
visible sign-in flow and save a replacement session after successful login.
Never upload or send the storage-state file: it may allow access to the
account without entering the password.

## Run tests

The tests mock Playwright and do not open a browser or access a Gmail account.
From the project root, run:

```powershell
python -m pytest -q
```

## Example output

```text
Unread message count: 2

1.
   Sender:  Example Sender
   Email:   sender@example.com
   Subject: Example subject

2.
   Sender:  Another Sender
   Email:   another@example.com
   Subject: Another subject
```

If no unread inbox messages are found, the script prints:

```text
Unread message count: 0
No unread messages found in the inbox.
```

## Scope and limitations

- The script checks unread message rows currently rendered in the Gmail inbox.
  It does not search every Gmail label, archive, spam, or trash folder.
- It prints sender name, sender email address, and subject only. It does not
  download or display message bodies or attachments.
- It does not mark messages as read, delete, send, or modify messages.
- It relies on Gmail's current page structure and sign-in labels. If Google
  changes these, Playwright locators may need to be updated.
- The saved session is sensitive and can stop working at any time.

## Keep private files out of GitHub

The root `.gitignore` excludes the local virtual environment, `credentials.py`,
and `playwright/.auth/storage_state.json`. Keep those private files untracked.
The optional `credentials.example.py` contains placeholders only. Never commit
the real credentials file or saved browser session.

Review the staged files before every push. If a real password or session file
was committed or shared, remove it from the repository and rotate/revoke the
affected credentials or session; deleting it in a later commit may not remove
it from Git history.
