# Execution note — C-U115

## Scope and files used

Work was confined to `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U115`. No external browsing, messages, operational changes, spending, commits, uploads, installs, or direct simulation-state edits were performed.

Read-only supplied files used:

- `prompt.md`
- `skill/operational-intervention-decision/SKILL.md`
- `input/request.md`
- `input/sources/decision_context.md`
- `input/sources/measurement_notes.md`
- `input/sources/shift_operations.csv`
- `input/sources/shipment_cohorts.csv`

Created files:

- `answer.md`
- `deliverables/analyze.py`
- `deliverables/numerical_basis.md`
- `work/numerical_basis.recheck.md` (temporary deterministic-reproduction check)

## Public command and tool record

1. `cat prompt.md` — exit 0. Exact captured observation: directed use of the supplied Skill, the four authoritative source files, `answer.md` via `apply_patch`, temporary work under `work/`, and an execution note; prohibited modification of Skill/input and external state.

2. Three independent commands were run together; all exited 0:
   - `cat skill/operational-intervention-decision/SKILL.md` — exact relevant observations: inventory/validate packet; distinguish mature outcomes and process proxies; aggregate native grains; compare and standardize; assess economics, staffing and dispatch; make a bounded recommendation with reproducible calculations.
   - `find input -maxdepth 2 -type f -print | sort` — exact stdout:
     ```text
     input/request.md
     input/sources/decision_context.md
     input/sources/measurement_notes.md
     input/sources/shift_operations.csv
     input/sources/shipment_cohorts.csv
     ```
   - `cat input/request.md` — exact relevant observations: make a 20-full-shift recommendation for Iona; the four source files are authoritative; local calculations and new `deliverables/` are allowed; no external or live-operational actions.

3. Four independent `cat` commands read the authoritative sources; all exited 0:
   - `cat input/sources/decision_context.md` — exact captured facts used: nonrandom Harbor start July 20; unchanged crews/definitions and no concurrent interventions; 20 shifts, 800 orders/line-shift, 75%/25% mix; 68 productive-hour line cap; up to 3 separately funded Ridge training hours; $48/error and $32/additional hour; no dispatch price; <=1% late commitment.
   - `cat input/sources/measurement_notes.md` — exact captured facts used: seven-day maturity; July 31 immature and short; catches are separate process observations; operations are whole-line rows; overtime/training are productive-hour subsets; only Harbor July 20 training is one-off; six named ordinary full shifts.
   - `cat input/sources/shift_operations.csv` — exact captured dataset: 14 whole-line rows covering two lines on seven dates.
   - `cat input/sources/shipment_cohorts.csv` — exact captured dataset: 28 date/line/band rows; July 31 rows have zero mature orders.

4. `apply_patch` added `deliverables/analyze.py` — tool returned `{}` (success). The script uses only Python's standard library, validates row keys and count bounds, aggregates at the source grain, excludes immature outcomes and the short shift where appropriate, and prints the numerical basis.

5. `python3 deliverables/analyze.py > deliverables/numerical_basis.md` — exit 1. Exact stderr:
   ```text
   Traceback (most recent call last):
     File "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/consumers/C-U115/deliverables/analyze.py", line 196, in <module>
       for name, passed, detail in checks:
           ^^^^^^^^^^^^^^^^^^^^
   ValueError: too many values to unpack (expected 3)
   ```
   No result from this failed run was accepted.

6. `apply_patch` corrected two validation tuples in `deliverables/analyze.py` — tool returned `{}` (success).

7. `python3 deliverables/analyze.py > deliverables/numerical_basis.md` — exit 0; stdout/stderr empty because stdout was redirected.

8. `cat deliverables/numerical_basis.md` — exit 0. Exact relevant results captured: all seven input checks PASS; mature rates Harbor 2.625% to 1.250% and Ridge 2.625% to 2.500%; checked workload 65 h/shift; linear checked capacity 836 orders; pilot full-shift dispatch 0.542% on each line; conservative two-line conditional net $15,360 before Ridge startup and $15,264 after; favorable equivalents $17,280 and $17,184; break-even 0.250 percentage points.

9. `apply_patch` added next-mix and band comparator calculations to `deliverables/analyze.py` — tool returned `{}` (success).

10. `apply_patch` added overtime totals to `deliverables/analyze.py` — tool returned `{}` (success).

11. `apply_patch` created `answer.md` — tool returned `{}` (success).

12. Three independent verification commands were run together:
    - `python3 -m py_compile deliverables/analyze.py` — exit 0; stdout/stderr empty.
    - `mkdir -p work && python3 deliverables/analyze.py > work/numerical_basis.recheck.md && cmp -s deliverables/numerical_basis.md work/numerical_basis.recheck.md` — exit 1; stdout/stderr empty. Exact interpretation: the saved report had not yet been regenerated after the immediately preceding script enhancements.
    - `cat answer.md` — exit 0; stdout was the complete 44-line decision memo.

13. `python3 deliverables/analyze.py > deliverables/numerical_basis.md && python3 deliverables/analyze.py > work/numerical_basis.recheck.md && cmp -s deliverables/numerical_basis.md work/numerical_basis.recheck.md` — exit 0; stdout/stderr empty. Exact interpretation: the current saved basis was regenerated and is byte-for-byte reproducible from the current script and supplied CSV inputs.

14. `rg -n "Next-mix standardization|Standard comparator-adjusted|Complex comparator-adjusted|pilot \\| Harbor \\| 3|Conservative comparator|Favorable raw|Break-even" deliverables/numerical_basis.md && wc -l answer.md deliverables/analyze.py deliverables/numerical_basis.md` — exit 0. Exact relevant stdout:
    ```text
    40:- Next-mix standardization: Harbor baseline = 0.75 × 1.500% + 0.25 × 6.000% = 2.625%; Harbor pilot = 0.75 × 0.667% + 0.25 × 3.000% = 1.250%.
    41:- Standard comparator-adjusted change = (-0.833 pp) - (0.000 pp) = -0.833 pp.
    42:- Complex comparator-adjusted change = (-3.000 pp) - (-0.500 pp) = -2.500 pp.
    61:| pilot | Harbor | 3 | 198 | 15 | 3 | 195 | 65.00 | 0.08125 |
    87:| Conservative comparator | 2.500% | 1.250% | 200 | $9,600 | $1,920 | $7,680 | $15,360 | $15,264 |
    88:| Favorable raw pre/post | 2.625% | 1.250% | 220 | $10,560 | $1,920 | $8,640 | $17,280 | $17,184 |
    90:Break-even benefit per checked line = (3.00 h × $32) / $48 = 2.00 avoided errors/shift, or 0.250 pp at 800 orders. Dispatch failures are not priced.
       44 answer.md
      294 deliverables/analyze.py
       96 deliverables/numerical_basis.md
      434 total
    ```

15. `sha256sum input/request.md input/sources/decision_context.md input/sources/measurement_notes.md input/sources/shift_operations.csv input/sources/shipment_cohorts.csv skill/operational-intervention-decision/SKILL.md deliverables/analyze.py deliverables/numerical_basis.md answer.md` — exit 0. Exact stdout:
    ```text
    6ac1cdd60955412b8e5f1208862c9574b60e1f70514ae6f63a85359647c3c392  input/request.md
    db617bd327c581d41163649f373944101be1394c760359d77760b395ba42d267  input/sources/decision_context.md
    4f89f6c363b70e69e5acdabde1ba46f3ca96c4a65530ac524a47786830f4a91e  input/sources/measurement_notes.md
    821cefcd24d45b7acebc6a30d1b9f3ab6f2f2cbb300a66aee359ef7cd2779c85  input/sources/shift_operations.csv
    280644532300832a9b74e2b3bc8daf7318f42124bf74f50f630dd22c15ea25b0  input/sources/shipment_cohorts.csv
    e3f0d227775b44f2b81abb0ace98b3fecfb9507ab3d4f9ede42901979c201b7f  skill/operational-intervention-decision/SKILL.md
    3a8f7ae812b56a65816c70f3c8367b9857ecf22d035ba626dacf84cee07d50c9  deliverables/analyze.py
    b01a67dfcfa05358fbe8e1cdd0b7be679454325940c5136678a06ee387e92e26  deliverables/numerical_basis.md
    962a47a32979e1688dbd96a4388b8a410024b93b67821a9903f91010ba87a3f4  answer.md
    ```

16. `apply_patch` clarified the marginal Ridge expansion values in `answer.md` and `deliverables/analyze.py` — tool returned `{}` (success).

17. `python3 deliverables/analyze.py > deliverables/numerical_basis.md && python3 -m py_compile deliverables/analyze.py && python3 deliverables/analyze.py > work/numerical_basis.recheck.md && cmp -s deliverables/numerical_basis.md work/numerical_basis.recheck.md && rg -n "marginal Ridge" answer.md deliverables/numerical_basis.md && sha256sum deliverables/analyze.py deliverables/numerical_basis.md answer.md` — exit 0. The regeneration, syntax check, and byte-for-byte reproduction all passed. Exact stdout:
    ```text
    deliverables/numerical_basis.md:91:- Conservative comparator marginal Ridge expansion net after maximum startup = $7,584.
    deliverables/numerical_basis.md:92:- Favorable raw pre/post marginal Ridge expansion net after maximum startup = $8,544.
    answer.md:31:The favorable raw Harbor pre/post case uses 2.625% as the counterfactual. It gives 220 avoided errors per line, $10,560 gross, and $8,640 net per line; the marginal Ridge figure is **$8,544 after startup**, and across both lines the net is $17,280, or **$17,184 after Ridge startup**. These are scenarios, not proven savings: they assume Harbor's checked rate, incremental hours, and effect transfer to Ridge and persist for 20 shifts.
    0d0d24b3787c67093880e3d1ec9f024b894b338fa17d9bb98312b514fa9217a2  deliverables/analyze.py
    dde1f1e8025f2555c08da038fd5d24e5feffc04098853dca27c457a7aeb04364  deliverables/numerical_basis.md
    265393261393f0fb2d0d88720160e3ee67939edc6a2858f1bda2550402284e0d  answer.md
    ```

    These three hashes supersede their earlier values in command 15 because the corresponding files were deliberately updated in command 16. The supplied input and Skill hashes in command 15 remain the final observed values.

## Exact validated observations and calculated summaries

- Exact structural observations: 28 unique cohort keys, 14 unique operation keys, both bands present for every date/line, exact operation/cohort key match, and all configured count/subset bounds passed.
- Calculated summary: Harbor raw improvement was 1.375 percentage points; Ridge raw improvement was 0.125 points; comparator-adjusted improvement was 1.250 points. The same calculation by band was 0.833 points standard and 2.500 points complex.
- Calculated summary: after removing only the documented 3-hour Harbor introduction, checked work averaged 65 recurring hours versus 62 contemporary no-check hours. Harbor pilot overtime was 15 hours across three full shifts.
- Calculated summary: at 16,000 orders/line, conservative conditional net value is $7,680/line before startup. The 3-hour Ridge startup is separately shown as $96.

## Checks not performed and limitations

- No external benchmarks or substitute assumptions were consulted, as prohibited by the task.
- No live operation, staffing, spending, messaging, or external-state change was performed.
- No statistical significance test or confidence interval was used as a decision gate. The memo instead exposes the small sample, nonrandom allocation, and observational nature of the comparison.
- No band-specific capacity forecast was performed because the source has whole-line labor only.
- No July 31 downstream outcome was inferred; its zero mature and outcome counts were treated as unavailable. July 31 was not used as a full-shift capacity observation.
- No late-dispatch cost was estimated because the packet provides no authorized price.
- The cost and Ridge expansion results are conditional projections, not observed savings or a proven treatment effect.
