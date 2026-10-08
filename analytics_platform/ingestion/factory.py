from analytics_platform.ingestion.yahoo import YahooSource
from analytics_platform.ingestion.fred import FredSource
from analytics_platform.ingestion.parquet import ParquetSource

class SourceFactory:

    @staticmethod
    def create(source_type):

        sources = {
            "yahoo": YahooSource,
            "fred": FredSource,
            "parquet": ParquetSource,
        }

        if source_type not in sources:
            raise ValueError(
                f"Unsupported source type: {source_type}"
            )

        return sources[source_type]()
