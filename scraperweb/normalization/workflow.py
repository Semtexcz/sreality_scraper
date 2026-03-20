"""Operator-facing filesystem workflow for persisted raw-to-normalized runs."""

from __future__ import annotations

from collections.abc import Iterable
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from scraperweb.normalization.models import NormalizedListingRecord
from scraperweb.normalization.runtime import RawListingNormalizer
from scraperweb.persistence.repositories import _sanitize_path_component, _timestamp_for_filename
from scraperweb.progress import BatchWorkflowProgressReporter
from scraperweb.scraper.models import RawListingRecord, RawSourceMetadata


@dataclass(frozen=True)
class NormalizationWorkflowSelection:
    """Describe one supported normalization scope selector."""

    region: str | None = None
    listing_id: str | None = None
    scrape_run_id: str | None = None

    def __post_init__(self) -> None:
        """Validate that exactly one normalization scope is selected."""

        selected_values = (
            self.region is not None,
            self.listing_id is not None,
            self.scrape_run_id is not None,
        )
        if sum(selected_values) != 1:
            raise NormalizationWorkflowError(
                "Exactly one normalization selector must be provided: "
                "--region, --listing-id, or --scrape-run-id.",
            )

    def describe(self) -> str:
        """Return a human-readable description of the selected scope."""

        if self.region is not None:
            return f"region={self.region}"
        if self.listing_id is not None:
            return f"listing_id={self.listing_id}"
        return f"scrape_run_id={self.scrape_run_id}"


class NormalizationWorkflowError(ValueError):
    """Raised when the operator-facing normalization workflow cannot proceed."""


class FilesystemRawSnapshotSource:
    """Load persisted raw listing records from the filesystem."""

    def __init__(self, input_dir: Path) -> None:
        """Store the root directory that contains raw listing snapshots."""

        self._input_dir = input_dir

    def iter_records(
        self,
        selection: NormalizationWorkflowSelection,
    ) -> list[RawListingRecord]:
        """Return persisted raw records matching one supported workflow scope."""

        if not self._input_dir.exists():
            raise NormalizationWorkflowError(
                f"Raw input directory does not exist: {self._input_dir}",
            )

        if selection.region is not None:
            records = self._load_region_records(selection.region)
        elif selection.listing_id is not None:
            records = self._load_listing_records(selection.listing_id)
        else:
            records = self._load_scrape_run_records(selection.scrape_run_id or "")

        if not records:
            raise NormalizationWorkflowError(
                "No persisted raw snapshots matched the selected normalization scope: "
                f"{selection.describe()}.",
            )
        return records

    def _load_region_records(self, region: str) -> list[RawListingRecord]:
        """Load every raw snapshot that belongs to one region dataset."""

        region_dir = self._input_dir / region
        if not region_dir.exists():
            raise NormalizationWorkflowError(
                f"Raw region directory does not exist: {region_dir}",
            )
        return [
            self._load_record(path)
            for path in self._iter_record_paths(region_dir.rglob("*.json"))
        ]

    def _load_listing_records(self, listing_id: str) -> list[RawListingRecord]:
        """Load every raw snapshot stored for one listing id."""

        listing_paths = sorted(
            self._input_dir.glob(f"*/{_sanitize_path_component(listing_id)}/*.json"),
        )
        return [self._load_record(path) for path in self._iter_record_paths(listing_paths)]

    def _load_scrape_run_records(self, scrape_run_id: str) -> list[RawListingRecord]:
        """Load raw snapshots captured during one scrape run id."""

        matching_records: list[RawListingRecord] = []
        for path in self._iter_record_paths(self._input_dir.rglob("*.json")):
            record = self._load_record(path)
            if record.source_metadata.scrape_run_id == scrape_run_id:
                matching_records.append(record)
        return matching_records

    @staticmethod
    def _iter_record_paths(paths: Iterable[Path]) -> list[Path]:
        """Return sorted record paths while skipping non-record JSON artifacts."""

        filtered_paths = [path for path in paths if not path.name.endswith(".markup-failure.json")]
        return sorted(filtered_paths)

    @staticmethod
    def _load_record(path: Path) -> RawListingRecord:
        """Deserialize one persisted raw record snapshot from JSON."""

        serialized_record = json.loads(path.read_text(encoding="utf-8"))
        source_metadata = RawSourceMetadata(**serialized_record["source_metadata"])
        return RawListingRecord(
            listing_id=serialized_record["listing_id"],
            source_url=serialized_record["source_url"],
            captured_at_utc=datetime.fromisoformat(serialized_record["captured_at_utc"]),
            source_payload=serialized_record["source_payload"],
            source_metadata=source_metadata,
            raw_page_snapshot=serialized_record["raw_page_snapshot"],
        )


class FilesystemNormalizedRecordRepository:
    """Persist normalized listing records into a stable filesystem layout."""

    def __init__(self, output_dir: Path) -> None:
        """Store the configured normalization output root and ensure it exists."""

        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def save_record(self, record: NormalizedListingRecord) -> Path:
        """Persist one normalized listing snapshot and return the written path."""

        listing_directory = (
            self._output_dir
            / _sanitize_path_component(record.normalization_metadata.source_region)
            / _sanitize_path_component(record.listing_id)
        )
        listing_directory.mkdir(parents=True, exist_ok=True)
        base_name = _timestamp_for_filename(record.captured_at_utc.isoformat())
        output_path = listing_directory / f"{base_name}.json"
        with output_path.open("w", encoding="utf-8") as output_file:
            json.dump(
                record.to_serializable_dict(),
                output_file,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            output_file.write("\n")
        return output_path


class FilesystemNormalizationWorkflowService:
    """Normalize persisted raw filesystem snapshots into stable JSON artifacts."""

    def __init__(
        self,
        raw_snapshot_source: FilesystemRawSnapshotSource,
        normalized_record_repository: FilesystemNormalizedRecordRepository,
        raw_listing_normalizer: RawListingNormalizer | None = None,
        progress_reporter: BatchWorkflowProgressReporter | None = None,
    ) -> None:
        """Store collaborators used by the filesystem normalization workflow."""

        self._raw_snapshot_source = raw_snapshot_source
        self._normalized_record_repository = normalized_record_repository
        self._raw_listing_normalizer = raw_listing_normalizer or RawListingNormalizer()
        self._progress_reporter = progress_reporter or BatchWorkflowProgressReporter()

    def normalize(self, selection: NormalizationWorkflowSelection) -> int:
        """Normalize every raw snapshot in the selected workflow scope."""

        raw_records = self._raw_snapshot_source.iter_records(selection)
        self._progress_reporter.workflow_started(
            workflow_name="normalization",
            selection=selection.describe(),
            total_records=len(raw_records),
        )
        normalized_records = 0
        for raw_record in raw_records:
            normalized_record = self._raw_listing_normalizer.normalize(raw_record)
            self._normalized_record_repository.save_record(normalized_record)
            normalized_records += 1
            self._progress_reporter.record_processed(
                workflow_name="normalization",
                total_processed=normalized_records,
                total_records=len(raw_records),
                listing_id=raw_record.listing_id,
            )
        return normalized_records


def run_filesystem_normalization_workflow(
    *,
    input_dir: Path,
    output_dir: Path,
    region: str | None = None,
    listing_id: str | None = None,
    scrape_run_id: str | None = None,
    progress_reporter: BatchWorkflowProgressReporter | None = None,
) -> int:
    """Run the public filesystem normalization workflow for one selected scope."""

    selection = NormalizationWorkflowSelection(
        region=region,
        listing_id=listing_id,
        scrape_run_id=scrape_run_id,
    )
    service = FilesystemNormalizationWorkflowService(
        raw_snapshot_source=FilesystemRawSnapshotSource(input_dir=input_dir),
        normalized_record_repository=FilesystemNormalizedRecordRepository(output_dir=output_dir),
        progress_reporter=progress_reporter,
    )
    return service.normalize(selection)
