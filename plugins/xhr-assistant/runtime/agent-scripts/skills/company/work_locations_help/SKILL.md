---
name: work-locations-help
description: Answer direct how-to questions about creating and managing company work locations in X-HR. Use when the user asks how to add, configure, or select work locations without requesting live company data.
---

# Work Locations Help

Use this direct-answer leaf when the user asks how to set up or manage company work locations.

# Intent Map

## Intent: work-locations-help
### User request patterns
- How to set up or manage company work locations (office address, site, workplace)?

### Retrieval tags
- company
- work-locations
- office-locations
- direct-answer

### Answer objective
Answer directly with the documented steps for managing company work locations.

### Instructions
- Answer directly in text using the guidance below.
- Do not call executable tools for this skill.

### Direct answer
**Instructions:**
- Go to [Workspace -> Work Locations]({{work_locations_url}})
- Click Add New Work Location
- Enter the required Location details (e.g., location name, address, country, city, ZIP, timezone)
- Save the new location
- Alternative: While adding a new employee profile, you can select an existing location from the dropdown or create a new one directly

**Prerequisites:** User must have Admin role to create or manage work locations

**Common Errors & Solutions:**
- "Permission denied" → Ensure you have Admin rights
- "Missing required fields" → Verify all mandatory fields (e.g., location name, country) are filled in
- "Duplicate location" → Check if the location already exists in the list before creating a new one
