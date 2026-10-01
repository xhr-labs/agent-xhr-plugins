---
name: employee-bulk-import-employees-help
description: "Explain how to bulk import employees in X-HR. Use when the user asks about CSV templates, field mapping, row review, compliance or custom fields, address validation, activation links, employee limits, or import status."
---

# Bulk Import Employees Help

Answer directly without calling executable tools. Emphasize the updated XLS/XLSX support and the existing CSV-based flow.

# Intent Map

## Intent: employee-bulk-import-employees-help
### User request patterns
- bulk import employees from CSV
- download the employee import template
- map CSV columns to employee fields
- fix invalid rows before importing employees
- import compliance custom or address fields
- send activation links to imported employees

### Retrieval tags
- employee
- bulk-import
- csv
- mapping
- activation-link
- direct-answer

### Answer objective
Explain the complete employee bulk-import flow and review safeguards.

### Instructions
- Answer directly without calling executable tools.
- Do not claim invalid rows will be imported.

### Direct answer
1. Open [People]({{people_url}}) and choose the bulk import action.
2. Select a work location and download its template. Note: bulk upload now supports CSV and XLS/XLSX; the system will normalize the first worksheet to the canonical CSV representation used by the validation and processing pipeline.
3. Complete and upload the file.
4. Map the uploaded columns to canonical employee fields.
5. Review rows, fix validation issues inline, or remove invalid rows.
6. Review compliance, custom-field, tax-residency, and address values when included.
7. Choose whether to send activation links to imported employees.
8. Start the import and monitor progress and final counts.

If the file exceeds the company’s remaining employee capacity, X-HR shows an upgrade warning. Backend validation errors remain on the review step so they can be corrected before processing. (Note: XLS/XLSX support adds two additional MIME types and a 5 MB / 1000-row limit as part of the enhanced bulk-upload capability.)
