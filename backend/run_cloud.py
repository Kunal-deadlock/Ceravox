"""Cloud container startup script for Ceravox."""

import os
import subprocess
import sys


def main() -> None:
    print("==> Running Alembic migrations...", flush=True)
    res = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"])
    if res.returncode != 0:
        print(f"ERROR: Alembic failed with exit code {res.returncode}", file=sys.stderr, flush=True)
        sys.exit(res.returncode)

    port = int(os.environ.get("PORT", "8000"))
    print(f"==> Starting Ceravox API on port {port}...", flush=True)
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()

