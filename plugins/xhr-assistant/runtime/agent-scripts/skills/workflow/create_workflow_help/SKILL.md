---
name: workflow-create-workflow-help
description: Answer direct workflow FAQ questions about create workflow help in X-HR. Use when the user asks these workflow questions without requesting live workflow execution.
---

# Create Workflow Help

Use this direct-answer leaf when the user asks about create workflow help.

# Intent Map

## Intent: workflow-create-workflow-help
### User request patterns
- How to create a Workflow
- What are the steps to create a workflow?
- How do I create my first automation?
- How do I create a workflow step by step?

### Retrieval tags
- workflow
- create
- automation
- direct-answer

### Answer objective
Answer directly with the documented workflow guidance.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
**Step 1: Open Workflow Builder**

- Go to [Workflows]({{workflows_url}})
- Click **Create Workflow**

**Step 2: Choose a Trigger**

- Choose **Event-based** for an immediate business event or **Date-based** for automation around an employee or document date.
- For date-based workflows, select the reference date field and timezone.

**Step 3: Add Conditions (Optional)**

- Define rules if needed  
- **Example:** Leave days > 3

**Step 4: Add Actions**

- Choose what should happen  

**Example actions:**
- Send approval to Manager  
- Notify HR after approval
- Send an email or in-app notification
- Ask a user to fill a form or upload a document
- Ask a user to update contact or emergency-contact information

For date-based workflows, configure **Trigger Timing** on each step to run it before, on, or after the reference date.

**Step 5: Save & Activate**

- Give your workflow a clear name  
- Activate it to make it live  

✅ **That’s it — your workflow is now running automatically.**

**Example Workflows:**

**Leave Approval Workflow**

- **Trigger:** Leave request submitted  
- **Condition:** Leave > 2 days  
- **Actions:**
  - Request approval from Manager  
  - Notify employee after decision

**Probation Review Workflow**

- **Trigger:** Date-based employee probation event
- **Reference date:** Probation end date
- **Actions:**
  - Notify the manager before the end date
  - Assign a review form on the end date
