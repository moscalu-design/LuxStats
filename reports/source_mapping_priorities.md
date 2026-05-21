# Source Mapping Priorities

Generated during the production-readiness pass on 2026-05-21.

## Summary

The unified source catalog currently contains 1,396 official STATEC/LUSTAT records. The highest-value product work is not adding more raw sources; it is mapping the best sources into beginner-friendly metrics, charts, commune profiles, and update watches.

Priority ordering was checked against current Luxembourg public-interest signals on 2026-05-21: population growth and migration, housing-market stabilization and construction, inflation/indexation, labour-market pressure, and short-term economic weakness. These signals guide mapping order only; the app still charts official STATEC/LUSTAT data and curated metadata.

Current mapping coverage by priority theme:

| Theme | Sources | Chart-ready | Commune-ready | High-priority unmapped |
| --- | ---: | ---: | ---: | ---: |
| Housing | 55 | 2 | 1 | 2 |
| Prices / Inflation | 19 | 1 | 0 | 0 |
| Labour Market | 62 | 2 | 1 | 0 |
| Population | 191 | 1 | 0 | 4 |
| Salaries / Income | 71 | 1 | 1 | 0 |
| Economy / National Accounts | 278 | 0 | 0 | 0 |
| Communes / Geography | 32 | 0 | 3 | 24 |

## High-Priority Unmapped Housing Sources

- `DF_D4113` - Building permits: number of dwellings by type of building and canton.
- `DSD_CENSUS_GROUP1_3@DF_B1606` - Housing arrangements by size of locality, sex and age.

Recommended next mapping: add a canton/region construction recovery chart from `DF_D4113`, then decide whether the census housing-arrangement table is useful for beginner housing pages or belongs only in advanced/source views.

## High-Priority Unmapped Inflation Sources

The catalog has CPI/inflation sources and one chart-ready CPI metric. No high-priority unmapped source is currently flagged, but the next product gap is indexation context: add a plain-language source card or metric explaining CPI/indexation timing without pretending to forecast beyond STATEC’s own publications.

## High-Priority Unmapped Labour Sources

The mapped set covers national jobs/unemployment and commune unemployment. The next labour priority is jobseekers/vacancies by occupation or sector if a clean official source can be mapped without exposing raw classification codes first.

## High-Priority Unmapped Population Sources

- `DSD_CENSUS_GROUP7_10@DF_B1625` - Population by canton and municipality, citizenship and sex.
- `DSD_CENSUS_GROUP1_3@DF_B1608` - Population by canton and municipality, household status and sex.
- `DSD_CENSUS_GROUP1_3@DF_B1607` - Population by canton and municipality, sex and age.
- `DF_B2207` - Total period fertility.

Recommended next mapping: add commune age/nationality breakdowns to the Commune Portal only after selecting simple defaults and labels. Add fertility as a national population chart.

## High-Priority Commune-Level Sources

Already mapped to Commune Portal:

- `DF_X021` - Population by commune.
- `DF_X020` - Population density by commune.
- `DF_C1600` - Median monthly salary by commune.
- `DF_X026` - Unemployment rate by commune.
- `DSD_CENSUS_NB_LOG_CLA@DF_B1707` - Dwellings by commune.
- `DSD_CENSUS_MENAGE_PV@DF_B1703` - Private households by commune.

Potential next commune mappings:

- `DSD_CENSUS_GROUP1_3@DF_B1607` - age structure.
- `DSD_CENSUS_GROUP7_10@DF_B1625` - citizenship.
- `DSD_TOUR_NB@DF_D5251` - touristic accommodation capacity.
- `DF_D2181` - agricultural and wine-growing holdings.

## Publication Annexes Worth Mapping

The publication annex catalog should stay advanced by default. Map publication annexes only when they answer a high-priority question and can be parsed into a stable table. Priority families:

- Housing market publications and Observatoire de l'Habitat tables.
- Inflation forecasts and indexation publications.
- Conjoncture Flash / short-term economic indicators.
- Labour-market publications with jobseekers and vacancies.

## Short-Term Indicators Worth Mapping

Recommended chart-ready additions:

- GDP / activity indicator trend for Economy.
- Business confidence or production indicator.
- Building permits by canton/region.
- Job vacancy or jobseeker trend.
- Energy/consumer-price component chart if clean CPI categories can be mapped.

## Deterministic Mapping Workflow

1. Select a high-priority unmapped source from the Source Library or this report.
2. Confirm whether it is API, Excel annex, publication Excel, or PDF-only.
3. Inspect dimensions/sheets and choose one beginner-safe question.
4. Add either a `Concept` in `src/concepts.py` or an Excel parser in `src/data/excel_sources.py`.
5. Add plain labels, filters, time controls, source details, and tests.
6. Keep sources with ambiguous structure as `needs_manual_review` instead of charting them prematurely.
