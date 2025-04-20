#!/usr/bin/env python3
import subprocess
import sys
import time

def fetch_index(idx):
    """Run `python get_data.py idx`, retrying on timeout or error."""
    while True:
        try:
            subprocess.run(
                [sys.executable, "get_data.py", str(idx)],
                check=True,
                timeout=10,
            )
            print(f"[{idx}] OK")
            return
        except subprocess.TimeoutExpired:
            print(f"[{idx}] timed out, retrying…")
        except subprocess.CalledProcessError as e:
            print(f"[{idx}] exited {e.returncode}, retrying…")
        # small back‐off if you like
        time.sleep(0.1)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} START END")
        sys.exit(1)

    start, end = map(int, sys.argv[1:3])
    for i in range(start, end + 1):
        fetch_index(i)

if __name__ == "__main__":
    main()
