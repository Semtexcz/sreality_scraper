"""Persistence adapters for raw listing storage."""

from scraperweb.persistence.repositories import (
    FilesystemRawRecordRepository,
    MongoRawRecordRepository,
    RawRecordRepository,
)

__all__ = [
    "FilesystemRawRecordRepository",
    "MongoRawRecordRepository",
    "RawRecordRepository",
]
