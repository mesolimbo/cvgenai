#!/usr/bin/env python3
import tomllib
import pathlib

def main():
    data = tomllib.loads(pathlib.Path("pyproject.toml").read_text())
    print(data["project"]["version"])

if __name__ == "__main__":
    main()
