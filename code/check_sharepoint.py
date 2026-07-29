"""Verify that the configured SharePoint destination is reachable and writable.

Answers the question "does this folder have the same read/write access as the
old one?" empirically, before an interview ever runs.

Access for this app is granted at SITE level (Sites.Selected or
Sites.ReadWrite.All application permissions). Microsoft Graph has no
folder-scoped application permission, so any folder in the site the app can
reach is writable. This script confirms that for the destination currently set
in the environment.

Run from the repository root:

    python code/check_sharepoint.py

It uploads one small probe file to the configured destination and reports the
full path. Nothing is deleted; remove the probe file manually if you wish.
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv  # noqa: E402

import sharepoint as sp  # noqa: E402

PROBE_NAME = "_write_check.txt"


def main() -> int:
    load_dotenv(Path(__file__).resolve().parent / ".env")

    if not sp._sp_configured():
        missing = [
            k for k in (
                "TENANT_ID", "CLIENT_ID", "CLIENT_SECRET",
                "SP_HOSTNAME", "SP_SITE_PATH", "SP_LIBRARY_NAME", "SP_TARGET_FOLDER",
            )
            if not os.getenv(k)
        ]
        print(f"FAIL: SharePoint is not configured. Missing: {', '.join(missing)}")
        return 1

    library = os.getenv("SP_LIBRARY_NAME", "")
    folder = os.getenv("SP_TARGET_FOLDER", "").strip("/")
    print(f"Site     : {os.getenv('SP_HOSTNAME')}{os.getenv('SP_SITE_PATH')}")
    print(f"Library  : {library}")
    print(f"Folder   : {folder}")
    print(f"Target   : {library}/{folder}/")
    print()

    try:
        sp.verify_connectivity()
        print("OK  : token acquired and library resolved.")
    except Exception as exc:
        print(f"FAIL: could not reach the library — {exc}")
        print()
        print("If this says the library was not found, either create it in the")
        print("SharePoint UI or point SP_LIBRARY_NAME at an existing library.")
        return 1

    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        sp.upload_text(
            PROBE_NAME,
            f"Write check for {library}/{folder}/ at {stamp} UTC.\n"
            "Safe to delete.\n",
        )
    except Exception as exc:
        print(f"FAIL: could not write to {library}/{folder}/ — {exc}")
        return 1

    print(f"OK  : wrote {library}/{folder}/{PROBE_NAME}")
    print()
    print(f"Destination is writable. Delete {PROBE_NAME} when you are done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
