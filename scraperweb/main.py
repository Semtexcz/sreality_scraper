"""Backward-compatible wrapper for the estate scraper entrypoint."""

from scraperweb.estate_scraper import *  # noqa: F401,F403


if __name__ == "__main__":
    main()

