# Creator 061 input cache observation

The creator explicitly completed and passed the pinned physical-format validator. Consumer preparation then refused the additional file in its input folder before writing a freeze or consumer destination. Both supplied inputs still match their original assignment hashes:

- `input/brief.md`: `284eab48172c8b996d5eb3218590fb453c1e24f5b532f9d4457bda99fb38485e`
- `input/release_tool.py`: `939931810a40d9f813280ea46c95fec2c4a1ed72368937353bf5c899b8217577`

The only added regular file is `input/__pycache__/release_tool.cpython-312.pyc`, SHA-256 `817e07c25329c62c67ad09f7db52c4dde4222c6d3f42733d40a7d0228682b44b`. The creator's public note reports `python3 -m py_compile input/release_tool.py`, exit 0. This explains a runtime cache without establishing a change to the supplied source. The raw added file is retained locally; its bytes are not claimed saved by the existing UTF-8 checkpoint cache exclusion.

A proposed assessment-helper correction verifies all original input identities, rejects every added non-cache file and all symlinks, and records hashes for added regular `.pyc` files immediately under `__pycache__` in the external freeze manifest. It does not remove, alter or expose these caches to consumers, change a business criterion, repair a target Skill or rerun a creator. Independent review is requested before using the correction. C-U121/122 remain unprepared pending that review; C-U123/124 from completed creator 062 were prepared independently before this refusal.

The independent review is now complete and read in full: `audits/control-input-cache-review.md`. Its 25 disposable mechanical checks passed with no blocking finding; limitations of name-based cache classification, metadata coverage and concurrent mutation remain explicit. Root adopts the narrow correction at SHA-256 `3eb8b617b9bd7264a25d871d675ff02c5c9e55b8df3d659c22c815cdf18af581`. This permits normal preparation of the original completed creator, with the cache observation retained. No original is repaired or creator rerun; no semantic success is inferred. Subsequent preparation and save receipts are recorded separately.
