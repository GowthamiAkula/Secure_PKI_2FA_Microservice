#!/usr/bin/env python3
"""Cron script to log 2FA codes every minute."""

import os
import sys
import datetime
from pathlib import Path

# Ensure /app is on sys.path so we can import totp_utils
sys.path.append("/app")

from totp_utils import generate_totp_code

SEED_FILE = Path("/data/seed.txt")
LOG_FILE = Path("/cron/last_code.txt")


def main():
    if not SEED_FILE.exists():
        # No seed yet; nothing to log
        return

    hex_seed = SEED_FILE.read_text(encoding="utf-8").strip()
    code = generate_totp_code(hex_seed)

    now_utc = datetime.datetime.utcnow().replace(microsecond=0)
    timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S")

    line = f"{timestamp} - 2FA Code: {code}\n"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)


if __name__ == "__main__":
    main()

