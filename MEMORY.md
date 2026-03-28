# Memory

## 2026-03-26

- Mistake: The first scraper version tried to read `currentBatch` from raw YC HTML without accounting for HTML-escaped JSON inside the `data-page` attribute.
- Prevention rule: Before regex-parsing structured values from YC server-rendered HTML, HTML-unescape the page source first and validate the parser against a live response sample.
- Applies to: scraping logic, parsing logic, final output validation.

## 2026-03-27

- Mistake: LLM extraction for Scheduling Wizard failed deterministic validation: LLM output for market_size_estimate exceeded the allowed length of 180 characters.
- Prevention rule: After LLM extraction, validate founder names and output field lengths against the deterministic input before returning enriched results.
- Applies to: LLM prompts, final output validation.

## 2026-03-28

- Mistake: A full-batch refresh failed because one founder background summary exceeded the validator length limit, which caused the whole endpoint to return 422.
- Prevention rule: When validating overlong LLM text fields, trim them to the allowed character limit instead of returning null or failing the entire batch response.
- Applies to: LLM prompts, final output validation, batch refresh flow.
