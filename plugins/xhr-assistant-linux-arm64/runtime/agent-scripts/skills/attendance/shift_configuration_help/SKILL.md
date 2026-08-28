---
name: attendance-shift-configuration-help
description: Explain Attendance shift configuration. Use when the user asks how to create shifts, assign employees, configure vacation schedule type, or enable overtime on shifts.
---

# Shift Configuration Help

## Intent: attendance-shift-configuration-help
### User request patterns
- create an attendance shift
- assign employees to a shift
- remove employees from a shift
- configure vacation schedule type
- enable overtime for a shift

### Retrieval tags
- attendance
- shifts
- schedule
- employee-assignment
- direct-answer

### Answer objective
Explain shift setup and employee assignment behavior.

### Instructions
- Answer directly for help questions.
- Use shift executable leaves only when the user asks to create, assign, remove, or fetch live shift data.

### Direct answer
Open [Attendance Configuration]({{attendance_configuration_url}}) to manage shifts.

Attendance shifts define scheduling and attendance expectations for employees. Authorized users can create shifts, assign or remove employees, configure schedule types such as vacation where supported, and enable overtime settings when the shift should calculate extra work time.

If the user wants to perform a real shift action, confirm the target shift, employees, dates, and required settings before using the executable attendance skill.
