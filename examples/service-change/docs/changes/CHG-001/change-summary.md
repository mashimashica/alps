# Change brief (CHG-001)

## Needs

Reduce the search p95 response time at peak.

## Acceptance conditions

- Under peak-equivalent load in the pilot environment, the search p95 response time is at most 800 ms.
- A test purchase through the checkout path completes.

## Assumptions

- The main cause of the latency is the product-list aggregation query (based on the production observations).
