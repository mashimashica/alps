# Required source adapter contract

Run the adapter with the current Python interpreter and `--state ABSOLUTE_PATH`. `describe` is unmetered and returns a JSON object with nonempty `snapshot_id`, nonnegative integer `total_records`, `page_size: 3`, `calls_per_tranche: 2`, positive integer `tranche`, and integer `remaining_calls` between zero and two.

`page --snapshot ID` fetches the first page. Subsequent calls add `--cursor CURSOR`, passing the prior non-null `next_cursor` unchanged. Successful stdout is one JSON object with the same snapshot ID and total count, a positive integer tranche, `items` (up to three records) and `next_cursor` (nonempty string or null). Only null means exhaustion. Pages are stable, disjoint, nonchronological and snapshot-bound. An empty ledger still requires its empty terminal first page.

Each record has exactly `entry_id`, `vendor_id`, `posted_on`, `kind`, `status`, `amount_cents`, `currency`. IDs are nonempty strings; entry IDs are unique throughout a snapshot. Dates are canonical valid ISO calendar dates. Kind is `charge` or `credit`, status is `settled`, `pending` or `void`, currency is `USD`, and amount is a nonnegative integer (not a boolean or float).

Every successful page, including retries, costs one call. Exit 75 means `call_budget_exhausted` with no entries; cursor errors exit 2 and snapshot mismatches exit 4. Neither of the latter consumes quota. Any failed/ambiguous response is left unincorporated. A source may charge a successful call even if the response is lost. The runner does not automatically retry such failures in the same invocation. It rereads remaining quota on continuation.

The runner never calls setup or tranche-grant controls. Its only source operations are `describe` and `page`. Its own writes are the checkpoint, `.lock` sidecar and an atomic-save temporary file in the checkpoint directory. The adapter can update the supplied source state and its SQLite journal. No other source backend is bundled; replacing the adapter requires preserving this interface and approval model.
