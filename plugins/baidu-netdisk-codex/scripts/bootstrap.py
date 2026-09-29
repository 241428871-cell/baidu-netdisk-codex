"""Start the plugin with dependencies isolated in Codex's writable plugin data."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import venv


ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = ROOT / "requirements.txt"


def data_directory() -> Path:
    configured = os.environ.get("PLUGIN_DATA")
    return Path(configured) if configured else Path.home() / ".cache" / "baidu-netdisk-codex"


def runtime_python() -> Path:
    data = data_directory()
    environment = data / "venv"
    executable = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    marker = data / "requirements.sha256"
    digest = hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest()

    if not executable.is_file():
        data.mkdir(parents=True, exist_ok=True)
        venv.EnvBuilder(with_pip=True).create(environment)

    if not marker.is_file() or marker.read_text(encoding="ascii") != digest:
        result = subprocess.run(
            [
                str(executable),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--quiet",
                "-r",
                str(REQUIREMENTS),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                "Plugin dependencies could not be installed. "
                "Check Python and PyPI connectivity, then retry."
            )
        marker.write_text(digest, encoding="ascii")
    return executable


def main() -> int:
    operation = sys.argv[1] if len(sys.argv) > 1 else "serve"
    programs = {
        "serve": ROOT / "scripts" / "bridge.py",
        "auth": ROOT / "scripts" / "auth.py",
        "check": ROOT / "scripts" / "check.py",
    }
    if operation not in programs:
        print("Usage: bootstrap.py [serve|auth|check] [options]", file=sys.stderr)
        return 2
    arguments = sys.argv[2:] if len(sys.argv) > 1 else []
    try:
        python = runtime_python()
    except Exception as exc:
        print(f"Plugin startup failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return subprocess.run(
        [str(python), "-u", str(programs[operation]), *arguments],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
