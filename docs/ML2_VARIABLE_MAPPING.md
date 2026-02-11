# ML2 variable mapping for Streamlit MVP

This mapping is derived from `pc.parms` in this repository and can be used to replace placeholders in the Python MVP.

## STEP 2 live chart variables

- **GDP growth**: `grt(GDP_)`
- **Inflation**: `grt(PC_)`
- **Public deficit (% GDP)**: `DR_` (displayed as `%` with `DR_*100`)
- **Unemployment rate**: `UR_` (displayed as `%` with `UR_*100`)

## Policy instruments found in ML2

The editable policy/exogenous variables configured for STEP 1 are:

1. `VIG_X` — change in public investments (mln)
2. `ITPC0R_X` — VAT rate on consumption (%)
3. `DTH_X` — change in personal income tax receipts (mln)
4. `CSSFR_X` — employers' social contribution rate (% wages)
5. `CSSHR_X` — employees' social contribution rate (% wages)
6. `TGH_X` — transfers to households (growth rate, constant prices)
7. `WR_X` — correction of private wage growth (%)
8. `WGRR_X` — public real wage growth (%)
9. `NG_X` — change of public employment (thousands)
10. `ZX_X` — change in automatic indexation (%)

## Suggested MVP placeholder mapping

If your MVP currently uses placeholders like `TVA_`, `IGR_`, `UR_`, etc., map them as:

- `TVA_` -> `ITPC0R_X`
- `IGR_` (PIT instrument) -> `DTH_X`
- Employer SSC instrument -> `CSSFR_X`
- Employee SSC instrument -> `CSSHR_X`
- Transfers instrument -> `TGH_X`
- Public employment instrument -> `NG_X`
- Public investment instrument -> `VIG_X`
- Wage/public wage instrument -> `WGRR_X` (or `WR_X` if you intended private wage correction)

And for monitored outcomes:

- GDP / GDP growth -> `GDP_` / `grt(GDP_)`
- Inflation -> `PC_` / `grt(PC_)`
- Unemployment rate -> `UR_`
- Deficit ratio -> `DR_`
