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
