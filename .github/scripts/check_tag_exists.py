#!/usr/bin/env python3
import subprocess
import sys

def main():
    """Check if a git tag exists and print 'true' or 'false'."""
    if len(sys.argv) != 2:
        print("Usage: check_tag_exists.py <tag>", file=sys.stderr)
        sys.exit(1)
    tag = sys.argv[1]

    try:
        subprocess.run([
            "/usr/bin/git",
            "rev-parse",
            "--quiet",
            "--verify",
            f"refs/tags/{tag}"
        ], check=True)
        print("true")
    except subprocess.CalledProcessError:
        print("false")

if __name__ == "__main__":
    main()
