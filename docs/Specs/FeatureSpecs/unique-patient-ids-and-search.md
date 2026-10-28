---
id: unique-patient-ids-and-search
type: feature-spec
title: Unique Patient IDs and Search
status: implemented
owner: project-maintainers
tags:
  - hospital-management
  - patient-identity
  - search
---

[CodeWiki](../../index.md) / [Specs](../index.md) / [Feature Specs](index.md)

# Unique Patient IDs and Search

## Overview

Give every queued patient a unique identifier and let console users locate patients across all specialization queues. Names remain display data rather than identity keys, so patients with identical names can be found and removed independently.

This feature extends the in-memory hospital console application. It does not introduce persistent medical records or turn the learning project into a production clinical system.

## User Stories

- As an operator, I want registration to show a patient's ID so I can identify the correct queue entry.
- As an operator, I want exact ID lookup across specializations so I do not need to know the patient's queue.
- As an operator, I want partial-name search to return every match with its specialization so I can distinguish similarly named patients.
- As an operator, I want removal by ID so another patient with the same name is not removed accidentally.

## Functional Requirements

| ID | Requirement |
| --- | --- |
| FR-1 | Construct each Patient with a standard-library UUID v4 string exposed through a read-only patient_id property. Existing Patient(name, status) calls remain valid. |
| FR-2 | Keep the ID unchanged when name or status changes during the object's lifetime. |
| FR-3 | Display the ID after successful registration, in queue listings, when calling the next patient, and in search results. Do not display registration success for rejected additions. |
| FR-4 | Add menu option 6 for search, preserving option 5 for exit. Prompt for id or name mode and a query. |
| FR-5 | Match IDs exactly after trimming surrounding whitespace and normalizing case; do not match ID prefixes or fall back to name search. |
| FR-6 | Match names using case-insensitive substring matching after trimming the query. Return all matching queue entries across all specializations. |
| FR-7 | Show each search result's ID, name, readable status, and specialization. Preserve specialization order and queue order within each specialization. Searching must not mutate queues. |
| FR-8 | Report empty queries, unsupported console search modes, and no matches without terminating the session. Programmatic searches return an empty list for empty queries and raise ValueError for unsupported modes. |
| FR-9 | Change menu option 3 to request a patient ID, locate it globally, and remove only that queue entry. Report unknown IDs without mutation. |
| FR-10 | Keep existing capacity, accepted statuses, and FIFO service behavior unchanged. Demo-populated patients receive IDs through the same creation path. |

## Non-Functional Requirements

- Use only the Python standard library; no service, database, or new package dependency.
- Search is O(N) over the total number of queued patients and uses O(M) space for M matches.
- IDs are probabilistically unique UUIDs, not a centrally enforced database uniqueness constraint.
- The public ID property is read-only; the private backing attribute is not a security boundary.
- Patient IDs are identifiers, not credentials or authorization tokens.
- Automated tests must be non-interactive and must not depend on specific generated UUID values.

## Acceptance Criteria

| ID | Scenario | Expected result |
| --- | --- | --- |
| AC-1 | Create two patients with the same name, in the same or different specializations. | Each receives a different UUID v4 ID. |
| AC-2 | Change a patient's name or status; attempt assignment to patient_id. | ID remains unchanged; public property assignment raises AttributeError. |
| AC-3 | Search using an exact ID with surrounding spaces or uppercase letters. | Only the identified queue entry is returned. |
| AC-4 | Search using an ID prefix or unknown ID. | No matches are returned; queues remain unchanged. |
| AC-5 | Search using a mixed-case partial name shared by multiple patients. | All matching entries are returned with IDs and specialization context. |
| AC-6 | Submit an empty query, invalid mode, or unmatched query in the console. | A clear message appears and the menu remains usable. |
| AC-7 | Remove one of two identically named patients by ID. | Only the selected patient disappears; removed IDs no longer appear in search. |
| AC-8 | Remove the only patient in a queue. | Removal reports success even though the queue becomes empty. |
| AC-9 | Register, list, search, and call a patient. | The same ID appears throughout the patient's queue lifetime. |
| AC-10 | Load demo data, reject an invalid status, fill a queue, or serve its next patient. | Demo IDs are distinct; status validation, capacity 10, and FIFO behavior remain intact. |

## Scope

Included: generated IDs, active-queue search, ID display, ID-based removal, console integration, and automated regression tests.

Excluded: persistence, restart-stable identities, importing external IDs, editing patient details, consultation history, deduplication, authentication, appointments, priority service, and a web API.

Search covers currently waiting patients only. Removed or served patients are not retained as searchable records.

## Dependencies

Implementation paths are relative to the application directory
`python_learning_lessons-10000032654/hospital_management_system/`.

| Component | Responsibility |
| --- | --- |
| src/user_data/patient.py — Patient.__init__, patient_id | Generate and expose the ID. |
| src/models/specialization.py — add_new_patient, print_patients, get_next_patient, remove_patient | Return registrations, display IDs, and remove by exact ID. |
| src/models/operation_manager.py — search_patients, options, run | Search all queues and integrate console actions. |
| src/models/data_populator.py — populate_user_data | Existing creation path automatically assigns demo IDs. |
| tests/test_patient_search.py | Unit and mocked-console acceptance coverage. |

The existing serialized-file learning examples are not used; this feature has no storage dependency.

## Rollout Plan

Deploy the updated console application and run the regression suite with
`PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`
from the hospital application directory.

No stored-data migration is necessary because the application recreates in-memory demo queues on startup. IDs are newly generated on each startup. Removal callers must now pass an ID instead of a name; the method reports True for every successful removal, including the last entry.

No roadmap item was supplied, so this specification is standalone and has no roadmap linkage.

## Risks and Limitations

Full UUIDs are longer to type; users should copy them from registration output, listings, or name search results. Name search can return multiple results and does not infer which person the operator intended. UUID collision risk is negligible but not mathematically zero. Persistence and durable patient identity require a separate storage feature.
