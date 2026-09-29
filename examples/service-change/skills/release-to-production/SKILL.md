---
name: release-to-production
description: Make a checked and approved release candidate available to production users with a functioning checkout. Use when a change request has been approved and the candidate is to be applied to production.
---

# Production Release

## Purpose

Make the candidate revision available to this service's production users with a functioning checkout.

## Outcomes

- The candidate revision serves this service's production users.
- A test purchase completes through the user checkout path.

## Activities & Tasks

### Candidate qualification

1. Check the release candidate against the service's acceptance criteria.
2. Obtain the service owner's approval for that exact candidate.

    > NOTE A revision to the candidate can affect both the checked behavior and the scope of an earlier approval.

### Production availability

1. Deploy the approved candidate through the service's authorized release job.
2. Check the production result against the acceptance criteria.

## Controls

Follow the production policy and the [acceptance criteria](../../docs/acceptance-criteria.md).

## Constraints

Candidate checks must precede approval; approval must precede deployment; production checks must follow deployment. Deployment must not occur while approval is missing or unconfirmed.

## Enablers

Checking capability and the authorized release job.

## Resources

This file is the source description for the [Japanese translation](references/locales/ja/SKILL.ja.md).
