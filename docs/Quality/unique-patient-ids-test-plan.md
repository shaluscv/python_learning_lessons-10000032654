[CodeWiki](../index.md) / [Quality](index.md)

# Unique Patient IDs and Search — Test Plan

## Purpose and Scope

This document describes the existing automated tests for the [Unique Patient IDs and Search feature](../Specs/FeatureSpecs/unique-patient-ids-and-search.md). It covers patient identity, active-queue search, ID-based removal, console interaction, and regression checks for queue behavior.

Repository discovery found one automated test module:
`python_learning_lessons-10000032654/hospital_management_system/tests/test_patient_search.py`.
Its `PatientSearchTests` class contains 13 tests. No additional Python test modules or pytest, tox, or project test-runner configuration were found in the application repository. Learning scripts are examples, not an automated test suite, and are not executed as tests.

This is an authored test plan and inventory of executable tests, not a linked Spec Builder test-case collection.

## Environment and Preconditions

- Use Python 3 with its standard-library unittest runner. The recorded execution used Python 3.12.3.
- Run from `python_learning_lessons-10000032654/hospital_management_system/` so imports from `src` resolve.
- No additional packages, services, database, credentials, or network access are needed by this suite.
- Every test receives a fresh OperationManager with Cardiology and Neurology queues, each initially holding a patient named Alex Smith.
- Console tests mock `input()` and capture output; no human input is required.
- UUID values are generated dynamically; assertions must not rely on fixed IDs.

## Execution Procedure

1. Discover test modules throughout the application repository, excluding Git metadata and runtime logs. Include filenames matching `test*.py` and `*_test.py`, and check for runner configuration.
2. From the hospital application directory, run `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test*.py' -v`.
3. Record the Python version, UTC execution time, each test outcome, aggregate counts, duration, and exit code.
4. Treat failures, errors, unexpected skips, or a zero-test run as requiring investigation. A passing run requires all 13 currently inventoried tests to pass.
5. Publish the results in the [test report](unique-patient-ids-test-report.md).

Discovery from the repository root alone is not the prescribed command: the test directory is nested under the hospital application. The command above explicitly selects the known suite.

## Automated Test Inventory

All method names below belong to `test_patient_search.PatientSearchTests`. IDs are document-local references, not external artifact IDs.

| ID | Test method | Action and expected assertions | Acceptance criteria |
| --- | --- | --- | --- |
| T01 | test_ids_are_distinct_valid_and_read_only | Compare duplicate-name patients; validate one UUID as version 4; edit name/status and attempt ID assignment. IDs differ, remain stable, and public reassignment raises AttributeError. | AC-1, AC-2 |
| T02 | test_exact_id_search_across_specializations | Search an uppercase ID with surrounding spaces, a prefix, and an invalid ID. Exact search finds the correct specialization/patient pair; other queries return no matches. | AC-3, AC-4 |
| T03 | test_partial_name_search_preserves_duplicate_names | Search a mixed-case partial name with whitespace. Both duplicate-name patients are returned in specialization order; an unmatched name returns no results. | AC-5 |
| T04 | test_empty_query_and_invalid_mode | Submit blank queries in both modes and an unsupported mode programmatically. Blank queries return empty lists; invalid mode raises ValueError. | AC-6 |
| T05 | test_removal_is_by_id_and_last_patient_returns_success | Attempt removal by name, remove the sole patient by ID, then repeat. Name/repeated removal fail, valid removal succeeds, the other queue is unchanged, and the removed ID is not searchable. | AC-7, AC-8 |
| T06 | test_duplicate_names_in_same_queue_can_be_removed_independently | Add a duplicate-name patient in one queue and remove its ID. The original patient remains. | AC-1, AC-7 |
| T07 | test_queue_constraints_and_fifo_are_preserved | Reject an invalid status, fill the queue, reject overflow, and serve the next patient. Rejected additions return None, nine patients remain after service, and the original first patient is no longer searchable. | AC-10 |
| T08 | test_populated_patients_receive_unique_ids | Populate demo queues and collect IDs. Exactly 30 IDs are present and distinct. | AC-1, AC-10 |
| T09 | test_listing_and_next_patient_display_ids | Capture listing and next-patient output. The original patient's ID appears twice. | AC-9 |
| T10 | test_console_search_and_remove | Run name search, exact ID search, removal, and exit with mocked input. Both IDs, Neurology context, and readable emergency status appear; the selected queue becomes empty. | AC-3, AC-5, AC-7, AC-9 |
| T11 | test_console_invalid_and_empty_searches | Submit unsupported mode, blank query, and unmatched ID, then exit. All three expected diagnostic messages appear and the session continues. | AC-6 |
| T12 | test_console_registration_reports_id | Register a patient and exit. The newly created patient's ID appears in console output. | AC-9 |
| T13 | test_console_rejected_registration_does_not_report_success | Attempt registration with status 99 and exit. No specialization is retained and no registration success is printed. | AC-10; FR-3 |

## Acceptance-Criteria Coverage Notes

All ten feature acceptance criteria have related automated tests, but a related test is not proof that every clause is exhaustively asserted.

- AC-1: same-queue duplicate removal indirectly demonstrates distinct identity; explicit UUID format validation is performed on one representative patient.
- AC-4: no-match behavior is asserted, but queue immutability after every failed search is not explicitly snapshot-tested.
- AC-5: cross-specialization result order is checked; ordering of multiple matches within one specialization is not separately asserted.
- AC-9: registration, listing/calling, and search are checked in separate tests, rather than one continuous registration-to-service scenario.
- AC-10: invalid status and capacity rejection are checked, but each accepted status is not independently parameterized.
- Console invalid-mode and empty-query behavior is tested; nonnumeric menu/status recovery, unknown-ID console removal, and every output field on every result are not separately covered.

## Exclusions and Risks

No line or branch coverage percentage was measured. Tests do not establish performance bounds, universal UUID uniqueness, clinical safety, authorization, concurrency behavior, or production readiness.

Persistence, restart-stable IDs, historical patient lookup, appointments, and a web interface are outside feature scope. No manual terminal session, load test, or browser test is represented as executed here.

## Related Documents

- [Feature specification](../Specs/FeatureSpecs/unique-patient-ids-and-search.md)
- [Execution report](unique-patient-ids-test-report.md)
