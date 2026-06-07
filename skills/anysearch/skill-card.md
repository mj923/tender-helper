## Description: <br>
Real-time search engine supporting web search, vertical domain search, parallel batch search, and URL content extraction. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[anysearch-ai](https://clawhub.ai/user/anysearch-ai) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and agent users use AnySearch to add real-time information retrieval, fact-checking, vertical domain search, parallel batch search, and URL content extraction to an AI agent workflow. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Search terms, URLs selected for extraction, and any configured AnySearch API key are sent to AnySearch. <br>
Mitigation: Do not use the skill for secrets, private internal URLs, regulated data, or confidential investigations unless the provider and workspace secret handling are trusted. <br>
Risk: The skill requires sensitive credential handling when an API key is configured. <br>
Mitigation: Prefer environment variables or a local .env file for ANYSEARCH_API_KEY, avoid pasting keys in chat, and confirm before saving any newly issued key. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/anysearch-ai/anysearch) <br>
- [Publisher profile](https://clawhub.ai/user/anysearch-ai) <br>
- [AnySearch API key console](https://anysearch.com/console/api-keys) <br>
- [AnySearch MCP API endpoint](https://api.anysearch.com/mcp) <br>
- [README](README.md) <br>
- [CLI documentation spec](scripts/shared/doc_spec.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown, JSON API responses, command-line output, and configuration guidance] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Search results and extracted pages are returned from a remote AnySearch API; anonymous access is supported with lower rate limits, and an optional API key enables higher limits.] <br>

## Skill Version(s): <br>
2.1.0 (source: SKILL.md frontmatter and server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
