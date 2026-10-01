---
name: exm-expense-receipts-help
description: Explain expense receipts and invoices - accepted file types and size, AI receipt scanning and its warnings, previewing or downloading an attachment, and why receipts cannot be sent through chat.
---

# Expense Receipts and Scanning

## Intent: exm-expense-receipts-help
### User request patterns
- what file types can I upload as an expense receipt
- how big can an expense receipt file be
- how does receipt scanning work
- can I send you my receipt to submit the expense
- how do I download the receipt attached to an expense
- why did my receipt scan fail
- can I attach an invoice instead of a receipt

### Retrieval tags
- exm
- expense-management
- receipts
- invoice
- receipt-scanning
- file-upload
- direct-answer

### Answer objective
Explain how receipts are attached, scanned, and read back, and set the expectation that the file itself must be handled in the app.

### Instructions
- Answer directly without calling executable tools.
- Files cannot be transferred through chat. When the user offers to send a receipt, say the upload happens in the app and do not invent an upload link, document ID, or storage URL.
- `skills/exm/get_expense` lists a receipt's file name but deliberately never returns a download link; direct the user to the app to open the file.

### Direct answer
Receipts and invoices are attached in the Submit Expense dialog in [My Expenses]({{expenses_my_expenses_url}}). Drag a file in or click the upload area. JPG, PNG, and PDF are accepted, up to 5MB per file, and one expense can carry several attachments, each marked as a receipt or an invoice.

Once a file is uploaded you can **scan** it. The scan extracts the merchant, date, amount, currency, and a suggested category, and fills the form in for you. It never silently overwrites a field you already edited - it asks before applying. When several uploaded receipts disagree, the form warns you specifically (different currencies, merchants, dates, or suggested categories) and asks you to set that field yourself. A scan can also fail on a single file; manual entry is always still available, and you can **Rescan** or **Replace** the file.

An upload that is still running or has failed blocks submission: wait for it, retry it, or remove the file. Every uploaded receipt also needs an amount before the expense can be submitted.

To view an attachment later, open the expense in the app and use the preview or download control on the receipt. Receipt files cannot be uploaded or delivered through this chat, and the stored file links are short-lived, so they are never quoted here.
