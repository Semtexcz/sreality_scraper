"""Backward-compatible wrapper for the top-level CLI entrypoint."""

from scraperweb.cli import *  # noqa: F401,F403


if __name__ == "__main__":
    main()
