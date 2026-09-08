# Northbank decision

Stop the current all-order second-person check on East for the twenty-shift period; keep the shared packing-list template and do not expand to West. The quality signal is promising, but observed capacity and dispatch effects violate hard commitments.

East baseline was 132/3,000 = 4.40% mature customer mispacks; mature pilot cohorts were 45/3,000 = 1.50%. West moved from 120/3,000 (4.00%) to 59/3,000 (1.97%) too, while the template, order mix, and station-catch recording changed. East volunteered and was not randomized, so the checker’s causal effect is unproven. June 26 has zero mature orders and cannot support a quality rate; station catches are not comparable outcomes.

At the planned 80/20 mix, East band rates imply 3.2% baseline (2% standard, 8% complex) versus 2.0% pilot (1% standard, 6% complex), or about 288 fewer errors over 24,000 orders. At $65, gross avoidable cost is $18,720, a scenario rather than a causal forecast. The reproducible arithmetic is `python deliverables/reproduce_decision.py`.

East used 265 non-training productive hours over three full pilot shifts, 88.3 hours/shift versus 69 baseline, exceeding the 84-hour limit. Late dispatch averaged 21 orders/shift versus 5 baseline; the next promise allows 12 per 1,200-order shift. Extra labor is roughly 19.3 hours × 20 × $28 = $10,827, leaving $7,893 before the unpriced dispatch impact. Therefore expansion is not feasible.

If further evidence is desired, approve a five-full-shift, explicitly defined narrower check only after staffing confirmation. Review after the seven-day maturity window; record outcomes by band, productive hours (training separately), and late dispatch. Stop early on any shift above 84 hours or 1% late dispatch, and keep the ordinary process during review. Treat that variant as unmeasured until observed.
