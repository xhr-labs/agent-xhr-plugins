---
name: forms-publish-share-form-help
description: Explain how to publish and share a public form securely in X-HR. Use when the user asks about public form links, passwords, expiration, regenerating links, copying links, or unpublishing access.
---

# Publish and Share Form Help

## Intent: forms-publish-share-form-help
### User request patterns
- share a form with a public link
- password protect a public form
- set an expiration for a form link
- generate a new public form link
- stop access to a public form

### Retrieval tags
- forms
- public-link
- password
- expiration
- sharing
- direct-answer

### Answer objective
Explain the public form sharing and security controls.

### Instructions
- Answer directly without calling executable tools.
- Note that workflow-assigned forms are completed through Task Hub and may not expose public sharing.
- Public sharing applies to eligible published forms, not Review forms or assigned-step forms.
- Do not expose or request the raw token separately from the generated link.

### Direct answer
1. Open [Forms]({{forms_url}}) and publish an eligible form.
2. Open its public sharing settings from the Forms list or after publishing.
3. Optionally set a password and link expiration.
4. Select **Generate new link**, then copy the active link.
5. Regenerating creates a fresh active link using the saved security settings. Copy Link reuses an existing active URL when one is already available.
6. The current Forms frontend does not expose a standalone **Unpublish** action. If public access must stop, explain this limitation and verify the supported share-revocation policy rather than claiming that a button exists.

The public access token is carried in the link fragment (`#token=...`) and sent to the service in a request header. Do not copy, log, or expose the token separately. Passwords are sent only when configured.
