# Ethical Guidelines for Quid MCP Usage

## Our Principles

Quid MCP is designed to **democratize information access** while **respecting boundaries**, legal requirements, and ethical standards. This document outlines the principles and best practices for responsible use.

## Core Principles

### 1. Respect Terms of Service

**Always comply with website Terms of Service (ToS).**

- Read and understand the ToS of any website you access through Quid
- If ToS explicitly prohibits automated access or scraping, don't use Quid for that site
- When in doubt, contact the website owner for clarification

### 2. Honor Robots.txt

**Respect the Robot Exclusion Protocol.**

- Check `robots.txt` before creating a plugin
- If a site disallows automated access, respect that decision
- Some sites may allow authenticated users but not bots - authenticate with your own credentials

### 3. Rate Limiting

**Never overwhelm target servers.**

- Use conservative `requests_per_minute` settings in plugin configs
- Implement delays between requests (human-like behavior)
- Monitor server responses and back off if you receive rate limit errors
- Default to `requests_per_minute: 10` unless the site explicitly allows more

### 4. Attribution & Acknowledgment

**Acknowledge content sources.**

- Always cite the original source when using scraped content
- Provide links back to the original content when possible
- Respect copyright and licensing terms

### 5. Personal Use Focus

**Quid is primarily for personal research and AI assistance.**

- Designed for individual users to access their own accounts
- Not intended for bulk commercial data extraction
- Not intended for creating competing services or databases

### 6. Respect Privacy

**Protect personal and sensitive information.**

- Never share credentials or session tokens
- Don't extract or share personal information of other users
- Be mindful of GDPR and other privacy regulations

## Paywall Ethics

Paywalls exist for good reasons - they support journalists, researchers, and content creators. However, there are ethical ways to access paywalled content:

### Ethical Approaches

✅ **Subscribe**: Support quality content by paying for it

✅ **Library Access**: Many libraries provide free access to academic journals and news

✅ **Open Access**: Look for open access versions (arXiv, PubMed Central, author websites)

✅ **Author Copies**: Many authors share preprints or copies on request

✅ **Archive.org**: The Internet Archive may have archived versions

✅ **Preview/Summary**: Some paywalls allow limited preview or summary access

✅ **Accessibility**: Screen reader modes or accessibility features

### Problematic Approaches

❌ **Bypassing paywalls to avoid payment**: Unethical and often illegal

❌ **Sharing credentials**: Violates ToS and harms content creators

❌ **Bulk extraction**: Creating competing databases or services

❌ **Commercial resale**: Selling or redistributing paywalled content

### The Gray Area

Some techniques exist in a gray area:

- **Browser-based access**: Using your own authenticated session (this is what Quid does)
- **RSS feeds**: Accessing content through official feeds
- **Web archives**: Historical snapshots may have different access rules

**When in doubt**: Ask yourself:
1. Am I using my own legitimate credentials?
2. Would the content owner approve of this use?
3. Am I harming the sustainability of the content source?

## Use Case Guidelines

### ✅ Appropriate Uses

- **Academic Research**: Accessing papers through your institutional login
- **Legal Research**: Searching case law and regulatory databases you have access to
- **Medical Information**: Looking up drug information on databases you're authorized to use
- **Environmental Data**: Querying government environmental databases
- **Personal Documentation**: Accessing your own reports, permits, or records
- **AI-Assisted Research**: Using Claude or other AI to help analyze content you have legitimate access to

### ⚠️ Use with Caution

- **News Aggregation**: Be mindful of copyright and fair use
- **Competitive Intelligence**: Ensure you're complying with ToS
- **Market Research**: Consider licensing agreements
- **Price Monitoring**: Check if ToS allows automated access

### ❌ Inappropriate Uses

- **Credential Sharing**: Never share logins or bypass authentication for others
- **Bulk Downloading**: Mass extraction of databases
- **Commercial Resale**: Selling or redistributing extracted content
- **Creating Competing Services**: Building a service that competes with the source
- **Circumventing Technical Protections**: Bypassing CAPTCHA or DRM
- **Violating Copyright**: Extracting copyrighted content without permission

## Legal Considerations

### Know the Law

Different jurisdictions have different laws regarding web scraping and data access:

- **United States**: Computer Fraud and Abuse Act (CFAA), copyright law
- **European Union**: GDPR, Database Directive, Copyright Directive
- **United Kingdom**: Computer Misuse Act, GDPR UK
- **Other**: Check local laws in your jurisdiction

### When in Doubt

- Consult a lawyer
- Contact the website owner
- Err on the side of caution
- Use official APIs when available

## Best Practices for Plugin Developers

### When Creating Plugins

1. **Check Legality**: Ensure automated access is legally permitted
2. **Review ToS**: Confirm the site allows authenticated scraping
3. **Test Respectfully**: Use conservative rate limits during development
4. **Document Clearly**: Explain credential requirements and limitations
5. **Provide Attribution**: Include proper attribution in plugin README
6. **License Appropriately**: Use appropriate license for your plugin code

### Red Flags

Don't create plugins for:
- Sites that explicitly forbid scraping in ToS
- Sites with aggressive anti-bot measures (unless you have permission)
- Sites that offer official APIs instead
- Illegal content sources
- Sites where access would violate privacy laws

## Transparency

Quid MCP is open source and transparent:

- **No Hidden Features**: All code is public and auditable
- **User-Controlled**: You control your credentials and data
- **No Data Collection**: Quid doesn't collect or transmit your data to third parties
- **Local Execution**: Runs on your machine, not in the cloud

## Community Standards

### As a User

- Use Quid responsibly and ethically
- Report security vulnerabilities privately
- Share feedback to improve ethical safeguards
- Respect the community Code of Conduct

### As a Plugin Developer

- Follow these ethical guidelines
- Document your plugin thoroughly
- Test with realistic, respectful rate limits
- Respond to ethical concerns raised by the community

## Enforcement

While Quid is open source and we can't control how it's used, we:

- **Will not merge** plugins that violate ethical guidelines
- **Will remove** plugins found to violate ToS or laws
- **Will document** reported misuse in our issue tracker
- **Will cooperate** with legitimate legal requests

## Resources

### Legal & Ethical Resources

- [EFF: Coders' Rights Project](https://www.eff.org/issues/coders)
- [Creative Commons](https://creativecommons.org/)
- [GDPR Information Portal](https://gdpr.eu/)
- [The Curious Reader's Guide to Ethically Bypassing Paywalls](https://thelegalvoice.in/the-curious-readers-guide-to-ethically-bypassing-paywalls/)

### Alternative Access Methods

- [Unpaywall](https://unpaywall.org/) - Legal open access to research papers
- [Internet Archive Scholar](https://scholar.archive.org/) - Free access to scholarly articles
- [Open Access Button](https://openaccessbutton.org/) - Find legal free access
- [Library Genesis](https://en.wikipedia.org/wiki/Library_Genesis) - (Legal status varies by jurisdiction)

## Questions?

If you're unsure whether a use case is ethical or legal:

1. Open a [GitHub Discussion](https://github.com/yourusername/quid/discussions)
2. Ask in our community forums
3. Consult the documentation
4. Contact a lawyer for legal advice

## Updates

This document may be updated as:
- Laws and regulations change
- Community standards evolve
- New ethical considerations emerge
- Best practices are established

---

**Remember**: Just because you *can* access something doesn't mean you *should*. Use Quid responsibly, respectfully, and ethically.

*Last updated: November 2025*
