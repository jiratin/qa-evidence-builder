# Product Roadmap

Status values are `Done`, `Partial`, `Planned`, `Deferred`, and `Rejected`.
`Done` means the acceptance criteria are represented by released code and tests.

## Product goals

- Reduce time spent locating related API logs.
- Connect calls into an understandable transaction journey.
- Produce evidence ready for defect tickets.
- Prevent sensitive information from leaving the machine unintentionally.
- Support multiple log structures and larger datasets without regressions.

## P0 — Release reliability and product identity

### Done

- Application icon and Guide Jir metadata on Windows and macOS.
- Transaction ID source and Request ID fallback indication.
- Import validation that retains usable records.
- Raw-export warning and confirmation.
- Version/tag, icon, artifact, bundle, and packaged startup validation.
- Tabbed Included Evidence and Export Tree previews showing the exact next root
  name, grouping tree, per-group counts, package contents, safety state, and ZIP
  state without writing files or exposing log contents.

## P1 — Investigation and defect analysis

### Done

- HTTP-success business-error detection using `success`, known error fields, and
  configurable successful result codes.
- Transaction journey with first API, first error, slowest API, counts, duration,
  and fallback warning.
- Per-log Unicode evidence notes included only for included logs.
- Configurable slow threshold.
- Filter chips, filter count, category clear actions, and investigation presets.
- Evidence Preview search with forward/backward navigation, case matching, and wrap-around.

### Partial

- Configurable analysis rules: slow threshold and successful result codes persist,
  but arbitrary rule profiles and configurable field names do not exist.
- Transaction journey does not yet identify missing or repeated expected calls.

### Planned

- Compare Two Logs: select exactly two logs and compare headers, body, query,
  response, status, response time, and result code with sensitive values masked.

### Compare acceptance criteria

- Comparison works for success/error and cross-source records.
- Added, removed, and changed fields are visually distinct in both themes.
- Masking is enabled by default and raw values require an explicit safe design.
- Large nested structures remain readable and comparison errors are actionable.
- Core, UI, requirements, User Guide, and changelog coverage are updated.

## P2 — Data compatibility

### Done

- Multiple JSON/HAR file import, collision-free indexes, source tracking, merge,
  and timestamp sorting.
- Import summary for skipped records, unreadable timestamps, and missing endpoints.
- Automatic support for current Elasticsearch-style, flat JSON, array, and HAR inputs.

### Planned

- Field Mapping Profiles for URI, transaction, topic, page URL, duration, and
  other normalized fields.
- Explicit schema-detection result and unsupported-structure diagnostics.
- Duplicate-record reporting with a documented identity rule.

### Acceptance criteria

- Profiles can be created, named, selected, edited, and removed without storing log contents.
- Invalid mappings cannot silently replace required normalized values.
- Import reports identify selected schema/profile and mapping failures.
- Existing automatic parsing remains the default and retains regression coverage.

## P3 — Security and governance

### Done

- Default sensitive-key masking, extra mask keys, raw export disabled by default,
  and explicit raw-export confirmation.

### Planned

- Sensitive Data Scanner for credentials, tokens, cookies, common personal data,
  and organization-specific patterns.
- Masking Report with occurrence counts before export.
- Named organization mask profiles.

### Acceptance criteria

- Scanning remains local and reports categories/counts without copying secrets
  into telemetry, logs, exceptions, or documentation.
- False positives can be reviewed without disabling default masking globally.
- Raw export confirmation incorporates scan results and included-file count.
- Profiles store rules only, never imported values.

## P4 — Productivity and scale

### Planned

- Save/Load Workspace without embedding raw log contents by default.
- Recent Files storing paths only.
- Remaining keyboard shortcuts and discoverable shortcut help.
- JSON tree inspector with search, copy, JSON path, and masked-value indication.
- Evidence export templates.
- Background import, filtering, analysis, sanitization, and export with progress/cancel.
- Large-file mode with incremental parsing and virtualized or paged rendering.

### Performance targets

- 1,000 logs import within 2 seconds on a documented reference machine.
- 10,000 logs import within 8 seconds on that machine.
- Filter response within 500 ms.
- UI must remain responsive; operations over 1 second show progress.

Benchmarks must document machine, operating system, Python version, input shape,
and whether the measurement is a source or packaged build.

## Deferred intentionally

- General-purpose rule builder. Current categorized filters cover the primary
  workflow; revisit only after evidence from real users shows a concrete need.
- Cloud upload or direct ticket-system integration. These require an explicit
  security model, authentication design, and organization-specific configuration.

## Prioritization guidance

Finish the partial P0 export preview before adding broad new export behaviour.
For investigation work, Compare Two Logs is the next bounded user-facing item.
Field Mapping Profiles should precede broad schema customization. Sensitive Data
Scanner and Masking Report should be designed together. Performance work requires
repeatable benchmarks before architectural changes.
