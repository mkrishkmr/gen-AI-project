#!/usr/bin/env python3
"""
Manual Testing Launcher:
1. Installs missing dependencies
2. Runs all tests
3. If tests pass, launches the UI locally
"""

import subprocess
import sys


def run(cmd: list[str], desc: str) -> bool:
    """Run a command and return True if it succeeded."""
    print(f"\n>>> {desc}")
    print(f"    $ {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    # Step 1: Install dependencies
    deps = ["groq", "pandas", "datasets", "python-dotenv", "pytest", "streamlit", "fastapi", "uvicorn"]
    run([sys.executable, "-m", "pip", "install", "-q"] + deps, "Installing dependencies")

    # Step 2: Run tests
    if not run([sys.executable, "-m", "pytest", "tests/", "-v"], "Running tests"):
        print("\n[FAIL] Tests failed. Fix issues before launching UI.")
        sys.exit(1)

    # Step 3: Launch UI
    print("\n[OK] All tests passed. Launching UI...\n")
    run(
        [sys.executable, "-m", "streamlit", "run", "src/ui/app.py", "--server.headless", "true"],
        "Starting Streamlit UI",
    )


if __name__ == "__main__":
    main()
