# Error Recovery

Recovery procedures for `confluence-guide-writer`. Loaded just-in-time when a phase stalls.

## Source Material Is Incomplete or Ambiguous

```
Symptom: Spec page describes system design but not user workflow; critical steps missing.

Recovery:
1. Stop — do not guess or invent missing steps
2. List gaps explicitly in a CLARIFICATION REQUEST to the user
3. Ask targeted questions: "The spec describes two export options but doesn't
   indicate which is available to end-users. Can you clarify?"
4. Draft known sections and mark gaps: [CLARIFICATION NEEDED: describe the gap]
5. Do not publish until all gaps are resolved
```

## Target Confluence Space or Page Not Found

```
Symptom: confluence_get_page returns 404 or permission error; ambiguous parent page.

Recovery:
1. Ask the user for the exact space key and parent page URL or ID
2. Use confluence_search with narrower terms to find the correct space
3. List candidate pages for user selection if multiple matches exist
4. If access denied, flag that MCP connection may need re-authentication
5. Do not create pages in the wrong location — confirm parent before publishing
```

## Audience Tier Not Specified

```
Symptom: Request says "write a user guide" with no audience specified.

Recovery:
1. Ask: "Who is the primary audience — end-users (daily operators),
   clients/stakeholders (business-level), or power users/admins?"
2. Default to End-User if the user cannot specify — state the assumption explicitly
3. Note the assumed audience in the state block
```
