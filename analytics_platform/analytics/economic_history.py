import pandas as pd

from analytics_platform.policy.source_policy import SourcePolicy


policy = SourcePolicy()


def _lookup(df, year, column):
    rows = df[df["year"] == year]

    if rows.empty or column not in rows.columns:
        return None

    value = rows.iloc[0][column]

    return value if pd.notna(value) else None


def _select_by_policy(
    domain,
    metric,
    year,
    values_by_source
):
    priorities = policy.get_priority(
        domain=domain,
        metric=metric,
        year=year
    )

    for source in priorities:
        value = values_by_source.get(source)

        if pd.notna(value):
            return value, source

    return None, None


def build_country_timeline(
    country_history: pd.DataFrame,
    long_population: pd.DataFrame,
    world_bank: pd.DataFrame,
    country: str
) -> pd.DataFrame:

    historical = (
        country_history[
            country_history["country"] == country
        ]
        .copy()
        .sort_values("year")
    )

    long_pop = (
        long_population[
            long_population["country"] == country
        ]
        .copy()
        .sort_values("year")
    )

    modern = (
        world_bank[
            world_bank["country"] == country
        ]
        .copy()
    )

    modern = (
        modern
        .pivot_table(
            index=[
                "country_id",
                "country",
                "year"
            ],
            columns="metric",
            values="value",
            aggfunc="first"
        )
        .reset_index()
    )

    years = sorted(
        set(historical["year"])
        | set(long_pop["year"])
        | set(modern["year"])
    )

    records = []

    country_id = None

    for df in [historical, long_pop, modern]:
        if not df.empty:
            country_id = df.iloc[0]["country_id"]
            break

    for year in years:

        historical_population = _lookup(
            historical,
            year,
            "population"
        )

        long_population_value = _lookup(
            long_pop,
            year,
            "population"
        )

        modern_population = _lookup(
            modern,
            year,
            "population"
        )

        historical_gdp = _lookup(
            historical,
            year,
            "gdp"
        )

        historical_gdppc = _lookup(
            historical,
            year,
            "gdp_per_capita"
        )

        modern_gdp = _lookup(
            modern,
            year,
            "gdp"
        )

        modern_gdppc = _lookup(
            modern,
            year,
            "gdp_per_capita"
        )

        population, population_source = _select_by_policy(
            domain="economic_history",
            metric="population",
            year=year,
            values_by_source={
                "MPD2023": historical_population,
                "OWID_LONG_POPULATION": long_population_value,
                "WORLD_BANK_WDI": modern_population,
            }
        )

        gdp, gdp_source = _select_by_policy(
            domain="economic_history",
            metric="gdp",
            year=year,
            values_by_source={
                "MPD2023": historical_gdp,
                "WORLD_BANK_WDI": modern_gdp,
            }
        )

        gdp_per_capita, gdppc_source = _select_by_policy(
            domain="economic_history",
            metric="gdp_per_capita",
            year=year,
            values_by_source={
                "MPD2023": historical_gdppc,
                "WORLD_BANK_WDI": modern_gdppc,
            }
        )

        records.append({
            "country_id": country_id,
            "country": country,
            "year": year,
            "population": population,
            "population_source": population_source,
            "gdp": gdp,
            "gdp_source": gdp_source,
            "gdp_per_capita": gdp_per_capita,
            "gdp_per_capita_source": gdppc_source,
        })

    return pd.DataFrame(records)
