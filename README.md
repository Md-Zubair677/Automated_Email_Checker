# Gmail Unread Message Checker

A small Python script that signs in to Gmail with Playwright, finds unread
messages in the inbox, and prints each message's sender name, sender email
address, and subject in the terminal. It does not open or mark messages as
read.

## What the project does

1. Checks whether a saved Playwright login session exists.
2. If there is no saved session, opens a visible Chromium browser, enters the
   credentials configured in `credentials.py`, and lets you complete Google's
   2-step verification.
3. Saves the browser session to `playwright/.auth/storage_state.json`.
4. If a saved session exists, starts Chromium in headless mode and reuses it.
5. Reads unread messages shown in the Gmail inbox and prints the count and
   message details after closing the browser.

Google can expire a saved session or require you to verify again. If that
happens, remove the saved session file and run the script again to sign in
visibly.

## Project files

- `gmail_checker.py` — the Playwright script. It controls the browser,
  collects unread inbox message details, saves the login state, and prints the
  results.
- `credentials.py` — a local configuration file containing `GMAIL_USERNAME`
  and `GMAIL_PASSWORD`. Create it yourself as described below. Do not share or
  commit it.
- `credentials.example.py` — a safe template with placeholder values. Copy it
  to `credentials.py` and replace the placeholders on your own machine.
- `playwright/.auth/storage_state.json` — created automatically after a
  successful sign-in. It contains sensitive browser session data. Do not share
  or commit it. The tracked `.gitkeep` in this directory only preserves the
  empty directory in Git; it contains no login data.
- `venv/` — an optional local Python virtual environment. It is not required
  in the repository; each user can create their own.
- `README.md` — this guide.

## Requirements

- Python 3.10 or newer
- A Google account with Gmail access
- Internet access

Google may challenge or block automated sign-in. This script uses the regular
Google sign-in page; successful login is not guaranteed for every account or
environment.

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

### 4. Create your private `credentials.py`

In PowerShell, copy the safe template to the local credentials file:

```powershell
Copy-Item credentials.example.py credentials.py
```

Open `credentials.py` and replace the placeholder values with your own Gmail
username and password. Keep the values inside quotes. This local file is
ignored by Git. Never publish it or paste credentials into chat, screenshots,
or issue trackers. Storing a Google password in a plain-text file is risky;
use this approach only on a trusted, private machine. Anyone who can read this
file can see the password.

### 5. Run the script

```powershell
python gmail_checker.py
```

## First sign-in and 2-step verification

When `playwright/.auth/storage_state.json` does not exist:

1. The script opens a visible Chromium window.
2. It enters the username and password from `credentials.py`.
3. Complete any Google sign-in prompts and 2-step verification in the browser.
4. The script continues after Google redirects to Gmail, checks the inbox, and
   saves the session state.
5. The browser closes, then the unread count and messages are printed in the
   terminal.

The script waits up to five minutes for Gmail to load after the password step.
If Google presents a different page or the wait times out, complete the sign-in
manually in the visible browser if possible. Google may change its sign-in
screens, so the automated field labels can also need updating.

## Later runs (headless mode)

When the saved session file exists, the script launches Chromium headlessly and
uses the saved session; no browser window is displayed. Run the same command:

```powershell
python gmail_checker.py
```

If the session has expired or Google requests verification, the script reports
that the saved login needs attention. To sign in again, delete only
`playwright/.auth/storage_state.json`, then rerun the script. It will open the
visible sign-in flow and save a replacement session after successful login.
Never upload or send the storage-state file: it may allow access to the
account without entering the password.

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

Before pushing the project, add a `.gitignore` file in the project root with:

```gitignore
venv/
__pycache__/
credentials.py
playwright/.auth/storage_state.json
.env
```

You may commit `credentials.example.py` and `playwright/.auth/.gitkeep` as
references. The example contains placeholders only; `.gitkeep` is an empty
marker and does not contain a session. Do not commit `credentials.py` or
`playwright/.auth/storage_state.json`.

Review the staged files before every push. If a real password or session file
was committed or shared, remove it from the repository and rotate/revoke the
affected credentials or session; deleting it in a later commit may not remove
it from Git history.
