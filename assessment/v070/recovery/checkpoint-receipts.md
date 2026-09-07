# Emergency checkpoint receipts

The last full filesystem export remains bb0b730b49dae994a4869e8002f246e338e9da1f (tree ebdeb7355d14bf5383b531f3b3a89137b01ebd92, 5,268 files). The entries below preserve additional text through the direct API while the execution environment is disconnected; they do not attest an additional filesystem export.

| Verified commit | Tree | Parent | Preserved changes | Verification |
| --- | --- | --- | --- | --- |
| 6a0a6dc737ba93df750c449c3ca752d492300053 | 6b1d4db53f66af3ec70c9c84efe159736a4bd63f | bb0b730b49dae994a4869e8002f246e338e9da1f | Emergency RESUME prefix, recovery plan, relayed S06-P02 primary report, C069 authored-text recovery | Commit parent/tree/author/DCO; non-forced ref update and re-fetch; all four file contents fetched back and exactly matched. |

Read-back blob identities for that commit:

| File | Blob SHA |
| --- | --- |
| assessment/v070/RESUME.md | 8e6c8eb24e76f6fb44a8ea87f4cad98818bd0ec8 |
| assessment/v070/RECOVERY-ENVIRONMENT-OFFLINE.md | 515343625be14ebd9a810c931435a41ca36314d6 |
| assessment/v070/grades/business-S06-P02-primary.md | 6b8a60f80bbcf08b60ae7f7fcd71a286071d916d |
| assessment/v070/recovery/control-069-authored-text.md | 1d3078303a6864aba83cee6924178cf5a66cf0fc |

The descendant that introduces this receipt also preserves C070–072 authored-text recovery and updates the recovery plan. Its identity must be obtained from the verified current branch ref; a self-referential commit hash cannot be embedded in its own tree. No local evidence file, API database, workflow checkpoint or complete execution transcript is inferred recovered by these text-only receipts.

## Subsequent verified emergency checkpoints

| Verified commit | Tree | Parent | Preserved changes | Verification |
| --- | --- | --- | --- | --- |
| 4472e61bff470bab758c98eaa0480330e7566afa | e96fbf3723deb4dd0abc226c784104a63c7bf7ec | 6a0a6dc737ba93df750c449c3ca752d492300053 | C070–072 authored-text recovery, recovery plan and first receipt | Parent/tree/author/DCO, non-forced ref and all five changed files read back with full content matches. |
| c9c04b94d6b2ae12dd0b9bf8767d89049fe8368f | 8a15c1117f8f767db24b762681f97c8c1ffed2f5 | 4472e61bff470bab758c98eaa0480330e7566afa | S06-P02 original probe observations, C-U084 relay and recovery plan | Parent/tree/author/DCO, non-forced ref and all three changed files read back with full content matches. |

The descendant introducing this section attaches C-U085–093 relays and the recovery index, without changing original trials or the product. Its exact identity is the verified evidence ref recorded by the parent after update. Individual consumer relay blobs were first created as isolated immutable UTF-8 trees by their original agents; none of those agents moved a branch or created a commit.

| Recovery relay | Original immutable tree | Verified blob SHA | UTF-8 bytes |
| --- | --- | --- | ---: |
| C-U085 | a61312c477f550cf15c01eeaf1bdaf1e6d0966bb | a8bed5c4a45c37e5a74372c2e4edb66d98122813 | 5506 |
| C-U086 | 41c52e77e80ce9b3c3ac99bf842b42d4658d1f3f | c3b78ded766b696ed23c36b36ec50a0e989e1196 | 9580 |
| C-U087 | 0a6d26e3b01be249f2a0b1f5ab5701294e64dd76 | 29ee368a834bd83d0e8f5502a603d79187ff0b84 | 9089 |
| C-U088 | 5661ac8121fef0872dbc56c6da6555a209552b25 | 958f83367b1519dbbe40f97f42537151deea6f55 | 10281 |
| C-U089 | e77fce3db134dabd5ad2db5dac743f3ff7ebe943 | 37b014df161aa28d74507bc158c41cd6b1138a02 | 8454 |
| C-U090 | 0af2b426b4ffec7eaeb9a06fc44b64ea1ea2ce6b | 00929b7ce4a7d50090455ff7ae0a635540889461 | 10555 |
| C-U091 | 94402378fcd5762c8c1d0f432e0c7d1c914e847a | 7c16b25d4209c79b1eab839f561ec3e5303e4085 | 10792 |
| C-U092 | 84cc5b46f65bb5ca5e354c71b8b1259375b38813 | 857acb10fef302057d524209c81cd3d4e68c545f | 11656 |
| C-U093 | 3d30d067525c5cde29b0845b5b923d72f66a7f86 | c4774905b3809ad5c5352802742ba34b0065ce9a | 6995 |
