# Security Policy

## Reporting Security Vulnerabilities

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them privately:
- Open a security advisory on GitHub
- Or email the maintainers directly

We take all security reports seriously and will respond promptly.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| 2.0.0-alpha | :white_check_mark: |

## Security Best Practices

### For Users

1. **Never commit credentials to git**
   - Always use `.env` files (which are gitignored)
   - Use environment variables in production
   - Consider using a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)

2. **Protect session files**
   - Session files in `data/sessions/` contain authentication tokens
   - They are gitignored by default - keep them private
   - Delete old sessions periodically

3. **Review .gitignore before pushing**
   - Ensure `.env` is listed
   - Ensure `data/` is listed
   - Double-check no credentials in code

4. **API Security**
   - Set `API_KEY` in production
   - Use HTTPS in production
   - Restrict CORS origins (`CORS_ORIGINS` env var)

5. **Rotate credentials regularly**
   - Change passwords periodically
   - Rotate API keys
   - Clear old sessions

### For Developers

1. **Code Review**
   - Never hardcode credentials in code
   - Use placeholders like `your_email@example.com`
   - Review PRs for credential leaks

2. **Sensitive Data**
   - Use `getpass` for CLI password input
   - Never log passwords or tokens
   - Sanitize error messages

3. **Dependencies**
   - Keep dependencies updated
   - Review dependency security advisories
   - Use `pip-audit` or similar tools

4. **Session Management**
   - Session files use file locking to prevent corruption
   - Don't store sensitive data beyond auth tokens
   - Implement session expiry

## Common Security Issues

### Issue: Credentials in Git History

**Prevention:**
- Use `.gitignore` properly
- Review commits before pushing
- Use pre-commit hooks

**If it happens:**
```bash
# Remove from history (dangerous!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (coordinate with team!)
git push origin --force --all

# Then rotate all exposed credentials immediately!
```

### Issue: Session Hijacking

**Prevention:**
- Keep session files private (in `.gitignore`)
- Don't share session files
- Use secure file permissions

**Mitigation:**
- Delete compromised sessions
- Change account password
- Review account activity

### Issue: Rate Limiting / IP Bans

**Prevention:**
- Add delays between requests
- Respect robots.txt
- Use reasonable timeouts
- Implement exponential backoff

## Disclosure Policy

- Security researchers: We appreciate responsible disclosure
- Embargo period: We request 90 days to fix critical issues
- Credit: We will credit researchers in release notes (if desired)

## Security Updates

Security updates will be:
- Released as patch versions (1.0.x)
- Announced in GitHub Releases
- Tagged with "security" label
- Documented in CHANGELOG.md

## Questions?

For security questions (not vulnerabilities), please open a Discussion or Issue.

Thank you for helping keep this project secure! 🔒
