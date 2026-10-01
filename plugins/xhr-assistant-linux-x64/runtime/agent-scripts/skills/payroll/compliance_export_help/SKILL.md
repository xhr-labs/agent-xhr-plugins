---
name: payroll-compliance-export-help
description: Explain Payroll compliance exports such as UAE WPS/SIF. Use when the user asks about compliance export mappings, SIF export, validation errors, employer facts, employee facts, or correcting export data.
---

# Compliance Export Help

## Intent: payroll-compliance-export-help
### User request patterns
- export payroll compliance file
- generate a SIF file
- fix compliance export validation errors
- map payroll compliance fields
- explain UAE WPS payroll export

### Retrieval tags
- payroll
- compliance-export
- sif
- wps
- validation
- direct-answer

### Answer objective
Explain compliance export purpose, mapping, and validation correction.

### Instructions
- Answer directly without calling executable tools.
- Avoid country-specific legal advice; describe product behavior only.
- Treat export as a sensitive action. Explain the preview and validation result, then ask for confirmation before a separate action skill starts a download or proceeds past warnings.

### Direct answer
Open [Payroll -> Pay Runs]({{pay_runs_url}}) and select the relevant pay run.

Payroll compliance exports help payroll teams produce jurisdiction-specific files or mappings, such as UAE WPS/SIF where configured. CSV export is available for a non-draft pay run. UAE WPS/SIF export is available for UAE pay runs in **Calculated**, **Approved**, or **Published** status. Review the preview, saved mappings, employer information, employee information, and selected rows before exporting.

Structural validation failures block the export. Soft validation warnings may offer an explicit choice to export anyway; that choice should be made by the payroll owner after reviewing the risk. If validation errors appear, correct the mapped payroll, employer, employee, or compliance fields before using the export for submission. Confirm final requirements with the local payroll owner or compliance advisor.
