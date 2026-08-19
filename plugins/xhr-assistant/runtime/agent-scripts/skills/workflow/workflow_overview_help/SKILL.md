---
name: workflow-workflow-overview-help
description: Answer direct workflow FAQ questions about workflow overview help in X-HR. Use when the user asks these workflow questions without requesting live workflow execution.
---

# Workflow Overview Help

Use this direct-answer leaf when the user asks about workflow overview help.

# Intent Map

## Intent: workflow-workflow-overview-help
### User request patterns
- What is a workflow and when should I use it?
- Do I need any technical or coding skills to create a workflow?
- What can trigger a workflow in X-HR?
- What happens if I don’t set any conditions for workflow?
- What actions can a workflow perform automatically?

### Retrieval tags
- workflow
- overview
- automation
- direct-answer

### Answer objective
Answer directly with the documented workflow guidance.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
**Getting Started with Workflows in X-HR**

Workflows in X-HR help you automate approvals, notifications, and actions across your organization — **without coding**.

Think of a workflow as:

> **When something happens → check conditions → then do something automatically**


**What Is a Workflow?**

A workflow consists of **three core parts**:

- **Trigger** – What starts the workflow  
- **Conditions** – Optional rules to decide when it should run  
- **Actions** – What the system should do automatically  

**Example**

> When an employee submits a leave request →  
> If the leave is longer than 3 days →  
> Send it to the manager for approval → Notify HR

**Workflow Building Blocks**

**1️⃣ Trigger (Start Event)**

A trigger defines **when the workflow starts**.

**Common triggers include:**

- Leave request submitted  
- Employee created or updated
- Employment record submitted for approval
- Document expiry
- Payroll ready for approval
- Date-based employee lifecycle events
- Approval approved / rejected  

> ⚠️ Each workflow has **exactly one trigger**.

Date-based workflows can run several steps at different times around the same reference date.

**2️⃣ Conditions (Optional)**

Conditions let you control **whether the workflow should continue**.

**Examples:**

- Leave duration > 3 days  
- Request created by Manager  
- Leave Type is Sick Leave  

You can:

- Add multiple conditions  
- Combine them using **AND / OR**  
- Skip conditions if you want the workflow to always run  

> 💡 If no condition is set, the workflow runs **every time** the trigger happens.

**3️⃣ Actions (What Happens Next)**

Actions define **what the system does automatically**.

**Common actions:**

- Send approval request  
- Auto Approve  
- Auto Reject  
- Notify a user or group  
- Send Email
- Ask a user to fill a form
- Ask a user to upload a document
- Ask a user to update contact or emergency-contact information
- Assign a task-list template
