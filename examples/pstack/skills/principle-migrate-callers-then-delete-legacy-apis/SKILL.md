---
name: principle-migrate-callers-then-delete-legacy-apis
description: "Apply when introducing a new internal API while old callers still exist. Migrate callers and delete the old API in the same wave instead of preserving compatibility layers."
disable-model-invocation: true
---

# Migrate Callers Then Delete Legacy APIs

## Purpose

Complete the move to a new internal API in one wave, leaving no old API or compatibility layer behind.

## Outcomes

- Callers are migrated to the new API.
- The old API is deleted in the same wave as the caller migration.
- No compatibility layer is preserved.
- The tests assert the new contract.
- No test remains that only protects pre-refactor implementation details.

## Tasks

The following Tasks are required whenever this principle applies, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Migrate callers and delete the old API in the same wave instead of preserving compatibility layers.
2. Update tests to assert the new contract, and delete tests that only protect pre-refactor implementation details

## Constraints

This principle applies when introducing a new internal API while old callers still exist. When another description cites this principle, that description's own limits on it hold.

**When this applies:**
- No external users depend on backward compatibility
- The project can absorb coordinated breaking changes
- The new API is part of a simplification or refactor initiative
