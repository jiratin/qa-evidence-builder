QA Evidence Builder - Large Test Samples

All records in this directory are synthetic test data. They contain no
production credentials, customer data, or real personal information. Values
that resemble passwords, tokens, phone numbers, accounts, and email addresses
exist only to exercise the sensitive-data masking features.

1) qa_logs_72_entries_realistic.json
   - 72 Elasticsearch/Kibana-style entries
   - Multiple transactions
   - 200 / 403 / 404 / 500
   - Slow APIs > 3000 ms
   - Repeated payment errors
   - Sensitive fields for masking

2) qa_network_64_entries_realistic.har
   - HAR 1.2
   - 64 entries
   - Multiple transactions
   - 200 / 403 / 404 / 500
   - Slow APIs and Authorization headers

Suggested tests:
- Resize window small/large
- Search/filter many rows
- Include Selected / Include All Filtered
- Transaction grouping
- 4xx / 5xx / Slow only
- Error Fingerprint duplicates
- Mask sensitive data
- Extra mask key: accountNumber
- Export only selected logs
- Select package contents
