# ALPS Repository Checker Test Migration Ledger

Status: Historical migration ledger for PR #32.  The A=3/B=47/C=85 inventory
below is an exact snapshot of the pre-replacement test file at baseline commit
`1167de6192872707123407be87305f11639c6875`.  It is the implementation-before
migration decision ledger: the keep, rewrite, or delete decisions were made
against that 135-method file before the replacement checker was implemented.
The current ratified replacement suite is tracked separately below.  **A + B =
残す**; **C = 削除**.  A method in B keeps its semantic assertion but its
baseline fixture and usually its name are replaced by a profile-focused test.

## Counts

| Bucket | Meaning | Count |
| --- | --- | ---: |
| A. KEEP AS-IS | Already tests a selected canonical-profile behavior | 3 |
| B. KEEP, REWRITE TO PROFILE | Valuable semantic intent; fixture relies on a rejected or mixed form | 47 |
| C. DELETE | General Markdown/YAML compatibility, flexible inference, or redundant form coverage | 85 |
| **Total** | Every baseline method, exactly once | **135** |

The retained set is **50** methods and the deleted set is **85** methods.  The
bucket totals are a result of the exact-name inventory below, not an assumption
that the baseline snapshot is complete.

## A. KEEP AS-IS — 3

These baseline methods already exercise behavior in the narrowed profile without
depending on arrow relationship lists, Process Model process lists, multiple
tables, View non-table inclusions, H4 Tasks, or mixed representations.

### Canonical Reference Model locale outcomes

- `test_reference_model_pair_accepts_translated_named_endpoints` — Retains a passing locale pair using the fixed four-column relationship table and exact Reference Model entry form.
- `test_reference_model_pair_rejects_reversed_named_endpoints` — Retains the locale endpoint-order mismatch for the fixed relationship table.
- `test_shipped_reference_model_pair_passes_named_endpoint_comparison` — Retains the shipped Reference Model/package/locale smoke check.

## B. KEEP, REWRITE TO PROFILE — 47

Each method below retains a useful semantic assertion, but its fixture must be
replaced by the single canonical IR-producing path.  Replacements MUST use the
exact frontmatter, section order, headings, lists, tables, and single-backtick
references defined in `checker-profile.md`; removed forms must not be described
as canonical or preserved for compatibility.

### Relationship and endpoint semantics

- `test_process_model_pair_sees_short_relationship_row_omission` — Keep locale row-count intent; replace the short/unpiped row with a canonical four-column row-count mismatch.
- `test_process_model_checks_canonical_endpoint_display_name` — Keep endpoint display/reference agreement; move the reference to the designated `Process | Skill` cell and use the exact relationship table only for declared names.
- `test_process_model_rejects_multiple_canonical_endpoint_references` — Keep the one-reference boundary; express it in one designated Skill cell and reject the second span as unsupported/profile syntax.
- `test_process_reference_model_checks_canonical_endpoint_display_name` — Keep Reference Model endpoint agreement; use the exact H3/H4 entry blocks with the designated Skill line and exact four-column relationship table.
- `test_process_model_rejects_undeclared_named_table_endpoint` — Keep undeclared endpoint rejection in one fixed relationship table.
- `test_process_model_accepts_declared_named_table_endpoints` — Keep declared endpoint acceptance after replacing the flexible headers with the exact four-column schema.
- `test_process_model_validates_two_column_provider_recipient_tables` — Keep provider/recipient validation; rewrite the two-column compatibility fixture as one fixed four-column table.
- `test_process_models_validate_mixed_table_and_list_relationships` — Keep undeclared-endpoint semantics; collapse the mixed input to one fixed relationship table and remove list extraction.
- `test_process_model_pair_compares_mixed_relationship_entries` — Keep locale relationship count/identity comparison; replace mixed table/list entries with rows in one canonical table.
- `test_process_model_pair_detects_mixed_relationship_endpoint_order` — Keep endpoint-order mismatch detection; express both locale documents with one exact four-column table.
- `test_process_reference_model_pair_compares_mixed_relationship_entries` — Keep Reference Model locale relationship comparison; remove mixed-form discovery and use one exact table.

### Outcomes, Process tasks, and profile references

- `test_outcome_items_merge_mixed_forms_in_order_and_mask_code` — Keep visible Outcome order/reference semantics; rewrite to the one unindented hyphen list and remove mixed-form merging.
- `test_process_view_pair_compares_mixed_outcome_entries` — Keep locale Outcome count/order comparison; replace table/list mixing with one canonical Outcome list per locale.
- `test_process_view_pair_counts_keyword_free_tasks_under_activity_headings` — Keep task-kind/count comparison; rewrite the fixture to compare rows in the fixed `Source Process | Source element` Included table with exact `Activity:`/`Task:` prefixes.
- `test_frontmatter_folds_plain_description_continuations_and_checks_suffix` — Keep description and Process suffix validation; rewrite multiline YAML cases to direct one-line scalars.
- `test_process_tasks_under_recognized_child_sections_preserve_order_and_boundaries` — Keep task order/continuation semantics; allow opaque introductory prose, then use one direct list under an Activity H3 and remove H4 Tasks/H5 boundaries.
- `test_process_tasks_under_child_heading_require_normative_force` — Keep normative-class validation; replace the H4 Tasks fixture with an Activity H3 direct ordered list.
- `test_process_pair_counts_child_tasks_and_compares_normative_force` — Keep locale task-count and normative-class comparison; rewrite both assets without child Task headings.
- `test_process_resolves_operative_references_and_ignores_masked_forms` — Keep reference resolution; replace the broad masking matrix with exact designated single-backtick fields and defer lookalike coverage to the one table-driven boundary per family.
- `test_inline_code_keeps_valid_canonical_reference_operative` — Keep only the exact single-backtick reference assertion; remove the current bare-token-operative assertion and rewrite the replacement so bare `skill:` text is non-operative.
- `test_process_resolves_localized_references_and_rejects_unsafe_targets` — Keep localized target resolution, package-root containment, and symlink/escape rejection; rewrite bare references to designated single-backtick fields and replace the bullet Task with one normative ordered Task list.

### Process View source and inclusion semantics

- `test_process_view_checks_source_list_display_name` — Keep source display/reference identity; rewrite the source list as the fixed two-column Source Processes table.
- `test_process_view_pair_compares_structured_non_table_included_elements` — Keep included Activity/Task kind and order comparison; use one fixed two-column inclusion table.
- `test_process_view_accepts_valid_non_table_canonical_inclusions` — Keep valid inclusion semantics; migrate the non-table fixture to the exact `Source Process | Source element` table and required `Activity:`/`Task:` prefix.
- `test_process_view_rejects_non_table_inclusion_missing_canonical_reference` — Keep missing/unresolved inclusion-reference rejection; express it as a malformed designated cell in the canonical inclusion table.
- `test_process_view_rejects_non_table_inclusion_undeclared_source` — Keep undeclared-source rejection; use one canonical inclusion-table row with an undeclared source reference.
- `test_process_view_validates_all_source_process_tables` — Keep validation of every source row; consolidate the current multiple-table fixture into one fixed source table.
- `test_process_view_rejects_wrong_source_in_later_source_table` — Keep source identity rejection; express the later row in the one canonical source table.
- `test_process_view_pair_compares_all_source_process_tables` — Keep locale source count/order comparison; use one table with multiple canonical rows in each locale.
- `test_process_view_validates_non_table_items_after_provenance_table` — Keep inclusion-reference validation; replace the table-plus-non-table fixture with one canonical inclusion table and a designated invalid row.
- `test_process_view_pair_compares_mixed_provenance_and_non_table_items` — Keep locale inclusion count/order/identity comparison; rewrite both documents to one fixed inclusion table.
- `test_process_view_rejects_undeclared_source_in_later_provenance_table` — Keep undeclared-source rejection; use one canonical inclusion table rather than a later table block.
- `test_process_view_pair_compares_every_provenance_table` — Keep locale provenance count/order comparison; represent all rows in one fixed inclusion table.
- `test_process_view_pair_compares_stable_included_source_identity` — Keep stable source identity/order comparison; place exact references and prefixes in the fixed inclusion table.
- `test_process_view_checks_source_table_display_name_and_canonical_only` — Keep source display/reference checks; repair bare references and non-prefixed elements to the exact source/inclusion table schemas.
- `test_process_view_rejects_multiple_source_references` — Keep the single-reference-per-source-row boundary in the exact Source Processes table.
- `test_process_view_rejects_unstructured_included_content_and_keeps_supported_forms` — Keep rejection of an inclusion without the exact Activity/Task prefix; replace the old mixed fixture with canonical table rows.

### Kind dispatch and Process Model locale semantics

- `test_non_process_representations_resolve_operative_references` — Keep resolution across the three non-Process kinds; rewrite every fixture to the exact kind-specific sections and designated reference fields.
- `test_process_model_pair_accepts_translated_named_endpoints` — Keep the locale success path; replace flexible Process/relationship representations with the two exact tables.
- `test_process_model_pair_preserves_canonical_endpoint_comparison` — Keep stable endpoint identity/order comparison; put any display/reference agreement in Process declaration rows and keep relationship endpoint cells display names only.
- `test_process_model_pair_correlates_table_process_names_with_skill_references` — Keep Process-name/Skill-reference correlation in the fixed `Process | Skill` table; keep the fixed relationship table's endpoint cells display names only.
- `test_process_model_pair_reports_reversed_translated_endpoints_as_unverified` — Keep the warning path for unstable translated names; express it with empty Skill cells and otherwise exact tables.
- `test_process_model_merges_mixed_process_entries_and_masks_code` — Keep Process identity/reference order; replace mixed entries with one `Process | Skill` table and remove parser masking compatibility.
- `test_process_model_process_table_derives_name_and_skill_columns` — Keep Process identity and Skill-column semantics; rewrite reversed/flexible columns to the exact header order.
- `test_process_model_pair_compares_mixed_process_entries` — Keep locale Process count/order comparison; replace mixed Process representations with one exact Process table.
- `test_process_model_validates_all_relationship_tables` — Keep all-row validation; consolidate multiple relationship tables into one exact four-column table with multiple rows.
- `test_process_model_rejects_undeclared_named_list_endpoint` — Keep undeclared endpoint semantics; rewrite the arrow-list fixture as one fixed relationship-table row.

## C. DELETE — 85

These methods preserve generic Markdown/YAML compatibility, flexible inference, or
redundant rejected-form matrices.  The new profile suite should cover each
explicit boundary once in table-driven form; these current methods should not be
carried forward as compatibility obligations.

### Generic table and tokenizer compatibility

- `test_table_tokenizer_honors_escape_parity_and_exact_code_run` — Delete escape-parity and arbitrary code-run tokenization outside exact profile tables.
- `test_process_model_accepts_escaped_and_inline_code_pipes` — Delete escaped/inline pipe support; v1 rejects pipe-bearing cells.
- `test_table_accepts_outer_and_unpiped_gfm_rows` — Delete unpiped and partial-pipe GFM acceptance.
- `test_table_ignores_unrelated_pipe_prose_around_contiguous_block` — Delete broad pipe-prose table discovery.
- `test_table_stops_before_blank_and_second_table` — Delete heuristic table stopping and second-table discovery.
- `test_markdown_tables_pad_short_rows_without_absorbing_prose_or_extra_cells` — Delete short-row padding and extra-cell tolerance.

### Flexible headings, containers, and mixed representations

- `test_process_reference_model_accepts_entry_heading_levels_three_to_five` — Delete alternate entry heading levels; v1 requires exact H3 entries.
- `test_process_reference_model_keeps_deeper_custom_headings_in_entry_body` — Delete deeper custom-heading boundary inference.
- `test_process_reference_model_rejects_malformed_child_level_and_ignores_fake_headings` — Delete the broad fake-heading/container matrix; the exact H4 Purpose-then-Outcomes boundary is covered by a new table-driven negative case.
- `test_process_view_combines_source_tables_and_outside_entries` — Delete mixed source-table/list discovery.
- `test_process_view_pair_combines_mixed_source_table_and_outside_order` — Delete locale comparison of mixed source forms.
- `test_process_view_validates_every_provenance_table_and_ignores_fenced_tables` — Delete multiple-table and fenced-table compatibility; one boundary case is table-driven.
- `test_process_view_non_table_extractor_ignores_code_and_comments` — Delete the broad non-table extractor and container masking matrix; indented code is unsupported.
- `test_process_view_heading_extractor_uses_shallowest_activity_level` — Delete shallowest-heading inference.
- `test_process_view_heading_extractor_ignores_shallower_task_heading` — Delete nested heading/container inference.
- `test_process_view_heading_extractor_preserves_task_kind_at_activity_level` — Delete kind inference from arbitrary heading text.
- `test_process_model_accepts_heading_form_process_entries` — Delete Process Model heading-entry compatibility.
- `test_process_model_process_table_rejects_missing_or_ambiguous_headers` — Delete broad Process-table header inference; v1 has one exact header.
- `test_process_model_accepts_list_process_descriptions` — Delete Process Model list-entry compatibility.
- `test_process_model_preserves_meaningful_parenthetical_names` — Delete general display-name punctuation/description parsing.
- `test_process_model_accepts_declared_named_list_endpoints` — Delete arrow-list endpoint acceptance.
- `test_process_model_rejects_endpointless_relationship_list_item` — Delete the arrow-list endpointless case; the fixed-table missing endpoint case is covered once by new tests.
- `test_process_reference_model_rejects_endpointless_relationship_list_item` — Delete the duplicate arrow-list endpointless case for Reference Model.
- `test_process_models_reject_single_canonical_relationship_list_items` — Delete the one-ended arrow-list item case; use the fixed four-column boundary test instead.
- `test_process_models_accept_canonical_provider_and_recipient_relationships` — Delete positive arrow-list relationship parsing; fixed table rows cover provider/recipient semantics.
- `test_process_model_trims_named_recipient_description` — Delete free-form trailing relationship-description trimming.
- `test_process_model_accepts_canonical_provider_in_arrow_list` — Delete arrow-list provider-form acceptance.
- `test_process_model_accepts_canonical_recipient_in_arrow_list` — Delete arrow-list recipient-form acceptance.
- `test_process_models_separate_reference_only_endpoint_descriptions` — Delete free-form endpoint-description separation.
- `test_process_model_pair_compares_reference_only_endpoint_descriptions` — Delete locale comparison tied only to free-form endpoint-description extraction.
- `test_process_model_pair_accepts_outer_and_unpiped_relationship_tables` — Delete unpiped relationship-table compatibility.
- `test_process_model_pair_reports_reversed_unpiped_relationship_as_unverified` — Delete unpiped reversed-endpoint compatibility.
- `test_process_model_rejects_unidentified_two_column_relationship_table` — Delete two-column relationship inference; v1 has a fixed four-column schema.
- `test_process_models_reject_endpointless_mixed_relationship_list_item` — Delete endpointless mixed-form duplication.
- `test_process_models_accept_mixed_relationships_and_ignore_fenced_code` — Delete mixed relationship/fence compatibility.
- `test_relationship_semantic_entries_preserve_mixed_document_order` — Delete mixed table/list/fence event ordering internals.
- `test_relationship_tables_derive_endpoint_columns_from_localized_headers` — Delete localized header alias/order inference.
- `test_relationship_tables_reject_missing_or_ambiguous_endpoint_headers` — Delete missing/ambiguous header inference.
- `test_process_reference_model_pair_detects_mixed_relationship_endpoint_order` — Delete locale comparison tied to mixed relationship extraction.
- `test_process_model_pair_reports_reversed_two_column_relationship_as_unverified` — Delete two-column/unpiped locale compatibility.

### Reference masking and naturalness matrices

- `test_inline_code_cannot_hide_following_canonical_reference` — Delete arbitrary inline-code/run scanner behavior; the selected exact-reference boundary is covered once elsewhere.
- `test_reference_scan_ignores_top_level_and_list_indented_code` — Delete indented-code and list-container scanning; indented code is unsupported profile syntax.
- `test_reference_scan_ignores_blockquoted_fences_and_indented_code` — Delete blockquote/nested-container masking.
- `test_reference_scan_masks_fences_nested_in_list_containers` — Delete nested list/fence masking.
- `test_reference_scan_rejects_backtick_fence_openers_with_backticks_in_info` — Delete fence-info parser compatibility.
- `test_reference_scan_masks_only_markdown_link_destination_spans` — Delete general Markdown link masking.
- `test_inline_code_exact_runs_keep_following_reference_operative` — Delete arbitrary code-run handling beyond exact single-backtick references.
- `test_japanese_naturalness_masks_exact_arbitrary_inline_code_runs` — Delete naturalness checks coupled to arbitrary code-span masking.
- `test_japanese_naturalness_checks_decoded_description_forms` — Delete naturalness checks coupled to broad YAML decoding.

### Broad YAML, frontmatter, and separator compatibility

- `test_anchored_metadata_kind_is_preserved_for_valid_view` — Delete anchor acceptance; anchors are unsupported profile syntax.
- `test_anchored_process_view_requires_view_sections` — Delete anchor-based kind dispatch.
- `test_frontmatter_aliases_select_view_kind_and_validate_view_sections` — Delete alias and flow-map resolution.
- `test_frontmatter_merges_nested_metadata_aliases_before_kind_dispatch` — Delete nested alias/merge dispatch.
- `test_frontmatter_resolves_mapping_merge_before_kind_dispatch` — Delete YAML merge resolution.
- `test_frontmatter_rejects_invalid_and_cyclic_mapping_merges` — Delete merge-specific error matrix.
- `test_frontmatter_resolves_sequence_mapping_merges_with_precedence` — Delete sequence merge precedence and unrelated sequence parsing.
- `test_frontmatter_accumulates_multiline_flow_metadata_before_kind_dispatch` — Delete multiline flow-collection parsing.
- `test_frontmatter_flow_quote_scanner_preserves_multiline_hash_and_brace` — Delete flow/quoted scanner behavior.
- `test_frontmatter_flow_double_quoted_line_breaks_fold_and_preserve_blanks` — Delete folded quoted-flow behavior.
- `test_frontmatter_reports_invalid_and_unclosed_flow_mappings` — Delete general flow-map diagnostics.
- `test_frontmatter_aliases_report_unresolved_cyclic_and_wrong_nodes` — Delete unresolved/cyclic alias matrices.
- `test_frontmatter_scalar_aliases_resolve_and_mapping_aliases_remain_non_scalar` — Delete scalar/mapping alias semantics.
- `test_frontmatter_parses_scalar_anchors_tags_and_preserves_yaml_forms` — Delete anchors, tags, and broad scalar-form acceptance.
- `test_frontmatter_parses_quoted_block_keys_and_dispatches_nested_view_kind` — Delete quoted/complex keys and flow metadata.
- `test_frontmatter_scalar_anchor_fixture_passes_asset_checks` — Delete anchored fixture acceptance.
- `test_frontmatter_multiline_quoted_scalars_accept_anchor_and_tag_properties` — Delete multiline quoted-scalar compatibility.
- `test_frontmatter_single_line_quoted_scalars_accept_anchor_and_tag_properties` — Delete quoted-scalar/tag compatibility.
- `test_frontmatter_decodes_full_yaml_double_quoted_escape_set` — Delete general YAML escape decoding.
- `test_frontmatter_double_quoted_escapes_decode_name_description_and_kind` — Delete quoted escape-based field decoding.
- `test_frontmatter_double_quoted_escaped_line_break_is_folded` — Delete quoted line-break folding.
- `test_frontmatter_rejects_invalid_yaml_double_quoted_escapes` — Delete general YAML escape diagnostics.
- `test_frontmatter_parses_anchored_tagged_flow_metadata_with_comments` — Delete anchored/tagged flow metadata.
- `test_frontmatter_accepts_separation_before_plain_yaml_colons` — Delete separator-whitespace variants.
- `test_frontmatter_rejects_malformed_plain_yaml_keys_with_separator` — Delete general YAML key-shape diagnostics.
- `test_frontmatter_does_not_fold_name_or_kind_and_keeps_tab_diagnostic` — Delete broad continuation/tab behavior; the exact profile indentation boundary is covered once in the new suite.
- `test_frontmatter_preserves_quoted_scalar_error_checks_with_properties` — Delete quoted-scalar property/error handling.

### Heading and Setext compatibility

- `test_process_activities_accept_alternate_heading_levels_and_exclude_later_sections` — Delete alternate Process Activity heading levels and later-section inference.
- `test_process_activities_keep_deeper_explanatory_headings_in_activity_body` — Delete deeper explanatory-heading compatibility.
- `test_process_tasks_under_alternate_heading_require_normative_force` — Delete alternate task-heading compatibility; v1 uses the direct list under Activity H3.
- `test_semantic_heading_extractors_normalize_atx_closing_markers` — Delete ATX closing-marker normalization.
- `test_heading1_recognizes_setext_h1_and_masks_nonoperative_forms` — Delete Setext H1 and associated masking.
- `test_section_recognizes_setext_h2_and_respects_heading_boundaries` — Delete Setext H2 parsing.
- `test_setext_h2_required_sections_work_for_process_models_and_views` — Delete Setext required-section compatibility.
- `test_indented_atx_headings_are_semantic_but_four_spaces_are_code` — Delete indented-heading interpretation; indented code is unsupported.
- `test_closing_markers_apply_to_model_reference_and_view_extractors` — Delete closing-marker compatibility across extractors.

## Replacement-suite coverage

The retained inventory records the migration requirements.  The replacement
suite implements these profile-focused cases:

- Golden canonical assets for every kind (`process`, `process-model`,
  `process-reference-model`, `process-view`) in English and Japanese, with
  paired IR expectations, exact section order, and the shipped Reference Model.
- Table-driven unsupported-profile diagnostics with one negative case per
  explicit boundary: unknown/duplicate frontmatter field; alias, anchor, merge,
  tag, flow, block scalar, or sequence; wrong indentation; unpiped/wrong-header
  or short/extra-row table; Outcome table/prose; arrow relationship list;
  Process Model list/heading entry; H4 Tasks; multiple or mixed relationship or
  View tables; Setext/closing/indented ATX; nested list/container; malformed
  reference; and fence, blockquote, comment, link, or bare-reference lookalike.
  Do not recreate a compatibility matrix for each spelling or nesting variant.
- A serialized IR snapshot/contract covering source spans, locale, kind, exact
  section records, identities, table/list roles, references, and normative
  classes.
- A guard proving validators receive IR and do not read raw source or run
  extraction regexes themselves.
- Severity and exit-code tests for warning-only locale uncertainty, profile or
  semantic errors (`1`), and invocation/input failures (`2`); assert that
  success is not ALPS Conformance.
- Opaque-prose tests proving arbitrary paragraphs, fences, blockquotes, and
  comments do not become semantic records, while only designated exact
  single-backtick references become operative.
- Profile-version tests proving the result reports
  `alps-repository-checker/v1` and that a version change is visible in the
  contract.
- Canonical reference tests for local and package-qualified IDs, including
  `mashimashica/alps`, and rejection of empty, dot, dot-dot, backslash, and
  non-lowercase-hyphen segments; also cover package-root and symlink
  containment.
- Resource-limit tests for bytes, lines, line length, frontmatter size, heading
  depth, and records, plus locale-pair missing/mismatch diagnostics.

## Implementation result

The ratified replacement suite in the current
`tests/test_check_alps_asset.py` contains exactly **27** `test_*` methods.  The
list below is mechanically obtained from that current file.  The historical
A/B/C names do not mean that those old method names remain literally in the
current file: the old tests were integrated or replaced, and the required
semantic intent is retained in the focused profile tests and implementation
coverage described above.  Changes to the current suite require updating this
list and its current-suite check; they do not change the historical A/B/C
inventory.

### Current ratified replacement suite — 27 methods

- `test_profile_version_and_diagnostic_rendered_contract`
- `test_canonical_english_japanese_and_kind_fixtures_produce_ir`
- `test_typed_ir_snapshot_keeps_spans_identities_and_roles`
- `test_document_reference_aggregation_is_unique_without_collapsing_record_order`
- `test_shipped_assets_parse_and_cli_default_requires_japanese`
- `test_frontmatter_exact_order_fields_defaults_suffix_and_rejections`
- `test_h1_h2_exact_grammar_order_duplicates_required_and_html_boundary`
- `test_opaque_containers_are_hidden_and_boundaries_are_diagnostic`
- `test_process_outcome_activity_task_structure_and_normative_classes`
- `test_required_prose_rejects_headings_for_all_kinds_and_view_application`
- `test_decimal_task_marker_is_bounded_without_internal_failure`
- `test_exact_machine_tables_reject_profile_boundary_forms`
- `test_process_model_semantics_references_endpoints_and_locale_identity`
- `test_reference_model_structure_skill_position_target_equality_and_pairs`
- `test_process_view_sources_inclusions_and_locale_matrices`
- `test_resolved_identity_duplicates_and_locale_context`
- `test_cli_passes_configured_package_identity_to_locale_comparison`
- `test_canonical_reference_resolution_and_package_containment`
- `test_ir_only_validator_locale_guard_parse_once_and_serialized_contract`
- `test_cli_shares_parse_cache_across_top_level_and_referenced_assets`
- `test_locale_pair_frontmatter_process_model_reference_and_view_contracts`
- `test_cli_exit_statuses_version_warning_success_and_no_conformance_claim`
- `test_cli_resolves_relative_asset_paths_against_configured_root_from_other_cwd`
- `test_cli_rejects_removed_legacy_ja_allow_term_option`
- `test_input_diagnostics_compose_and_invalid_utf8_keeps_host_status`
- `test_exact_and_plus_one_resource_limits_records_and_container_state_bound`
- `test_diagnostic_class_whitelist_and_profile_version_serialization_contract`

## Mechanical verification

Run the baseline comparison from the repository root.  It deliberately reads
the pre-replacement test file from PR #32 baseline commit
`1167de6192872707123407be87305f11639c6875`; the inventory scan counts only
backtick-delimited method names.  The sorted `diff` proves there is no omission,
duplicate, or invented baseline name:

```bash
baseline=1167de6192872707123407be87305f11639c6875
inventory=docs/checker-test-inventory.md

git show "$baseline:tests/test_check_alps_asset.py" | awk '/^[[:space:]]*def test_[a-z0-9_]+\(/ {
  match($0, /test_[a-z0-9_]+/)
  print substr($0, RSTART, RLENGTH)
}' | sort > /tmp/baseline-checker-tests

sed -n '/^## A\. KEEP AS-IS/,/^## Replacement-suite coverage/p' "$inventory" \
  | rg -o '`test_[a-z0-9_]+`' | tr -d '`' | sort > /tmp/inventory-checker-tests

test "$(wc -l < /tmp/baseline-checker-tests)" -eq 135
test "$(wc -l < /tmp/inventory-checker-tests)" -eq 135
test "$(sort -u /tmp/inventory-checker-tests | wc -l)" -eq 135
test "$(uniq -c /tmp/inventory-checker-tests | awk '$1 != 1 { bad=1 } END { print bad + 0 }')" -eq 0
diff -u /tmp/baseline-checker-tests /tmp/inventory-checker-tests

awk '
  /^## A\. KEEP AS-IS/ { bucket="A"; next }
  /^## B\. KEEP, REWRITE TO PROFILE/ { bucket="B"; next }
  /^## C\. DELETE/ { bucket="C"; next }
  /^## Replacement-suite coverage/ { bucket="" }
  bucket && /^- `test_[a-z0-9_]+`/ { count[bucket]++ }
  END {
    if (count["A"] != 3 || count["B"] != 47 || count["C"] != 85) exit 1
    printf "A=%d B=%d C=%d total=%d\n", count["A"], count["B"], count["C"], count["A"] + count["B"] + count["C"]
  }
' "$inventory"
```

The section headers and summary table must independently report A=3, B=47, and
C=85; their sum must remain 135 for the named baseline.  Any future baseline
inventory change requires rerunning this ledger against the relevant commit.

Run the current replacement suite separately:

```bash
python -m unittest discover -s tests -p 'test_check_alps_asset.py' -v

python - <<'PY'
import ast
from pathlib import Path

path = Path("tests/test_check_alps_asset.py")
tree = ast.parse(path.read_text(encoding="utf-8"))
names = [
    node.name
    for node in ast.walk(tree)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    and node.name.startswith("test_")
]
assert len(names) == 27, len(names)
assert len(names) == len(set(names)), "duplicate test_* method"
print(f"current test_* methods: {len(names)} (unique)")
PY
```
