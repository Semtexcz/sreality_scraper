"""Application service for the synchronous raw-to-modeling listing pipeline."""

from __future__ import annotations

from collections.abc import Iterator

from scraperweb.enrichment import NormalizedListingEnricher
from scraperweb.modeling import EnrichedListingModelingInputBuilder, ModelingInputRecord
from scraperweb.normalization import RawListingNormalizer
from scraperweb.scraper.runtime import RawListingCollector


class LinearListingPipelineService:
    """Compose scraper, normalization, enrichment, and modeling in sequence."""

    def __init__(
        self,
        raw_listing_collector: RawListingCollector,
        raw_listing_normalizer: RawListingNormalizer | None = None,
        normalized_listing_enricher: NormalizedListingEnricher | None = None,
        modeling_input_builder: EnrichedListingModelingInputBuilder | None = None,
    ) -> None:
        """Store stage components used by the linear in-process pipeline."""

        self._raw_listing_collector = raw_listing_collector
        self._raw_listing_normalizer = raw_listing_normalizer or RawListingNormalizer()
        self._normalized_listing_enricher = (
            normalized_listing_enricher or NormalizedListingEnricher()
        )
        self._modeling_input_builder = (
            modeling_input_builder or EnrichedListingModelingInputBuilder()
        )

    def collect_modeling_inputs(
        self,
        district_link: str,
        max_pages: int | None,
        max_estates: int | None = None,
    ) -> Iterator[ModelingInputRecord]:
        """Yield model-ready records through the full synchronous stage sequence."""

        emitted_records = 0

        for raw_record in self._raw_listing_collector.collect_region_records(
            district_link=district_link,
            max_pages=max_pages,
        ):
            normalized_record = self._raw_listing_normalizer.normalize(raw_record)
            enriched_record = self._normalized_listing_enricher.enrich(normalized_record)
            yield self._modeling_input_builder.build(enriched_record)

            emitted_records += 1
            if max_estates is not None and emitted_records >= max_estates:
                return
