# Release Manager - Usage Examples

This document demonstrates how to use the release-manager skill with AI-driven command execution.

## ⚠️ CRITICAL: Git Tag Timing Protocol

**MOST IMPORTANT CONCEPT**: Git tags must be created at the EXACT right moment - AFTER all validation, BEFORE pushing to remote.

### The Golden Rule Examples:

✅ **CORRECT**:
```bash
# 1. Make changes and test
git add .
git commit -m "Finalize v0.2.0 release"

# 2. Run complete validation
pytest && pre-commit run --all-files

# 3. Get final approval
# [Human approval step]

# 4. CREATE TAG - THE CRITICAL MOMENT
git tag -a v0.2.0 -m "Release v0.2.0"

# 5. Push everything
git push origin main
git push origin v0.2.0
```

❌ **INCORRECT**:
```bash
# WRONG: Tag created before testing/validation
git tag -a v0.2.0 -m "Release v0.2.0"  # ← TOO EARLY!
pytest  # Tests might fail!
# Now tag points to potentially broken code
```

## AI-Driven Usage (Primary Method)

### Example 1: Standard Release
Simply ask your AI client:

```
Prepare and execute release v0.2.0 following proper tag timing
```

The AI will:
1. Evaluate codebase status (git status, branch, commits)
2. Run quality checks (tests, pre-commit, linting)
3. Update and validate documentation
4. **CRITICAL**: Get explicit approval before git tag creation
5. Execute release workflow with proper timing
6. Provide comprehensive release report

### Example 2: Dry Run Simulation
```
Run a dry-run release simulation for v0.2.0 with tag timing verification
```

This executes all phases without actual publishing, useful for:
- Validating the release process
- Training new team members
- Testing process changes
- **Verifying proper tag timing understanding**

### Example 3: Hotfix Release
```
Execute a hotfix release for v0.2.1 with critical security fix - ensure proper tag timing
```

Uses accelerated workflow:
- Focused testing on affected areas
- Expedited review process
- Minimal feature changes allowed
- **STILL FOLLOWS EXACT TAG TIMING PROTOCOL**

### Example 4: Conservative Safety Release
```
Run a conservative safety release with manual approval at each checkpoint
```

Maximum human oversight:
- Manual approval at every phase
- Strict validation requirements
- Zero tolerance for warnings

## Interactive Session Example

Here's how a typical AI-driven release session might look:

```markdown
📋 Phase 1: Codebase Evaluation
--------------------------------------------------
✅ Git status: Clean (no uncommitted changes)
✅ Current branch: develop
✅ Remote synchronization: Up to date
✅ Version number: 0.2.0 (consistent across files)
✅ CHANGELOG: Complete with proper formatting

📊 Recent commits since v0.1.3:
  - d49d7d4 change license to apache-2.0
  - ca101f6 feat(android-ui-test): add dual-purpose Android UI test skill
  - 71d0604 feat(cli): add short options and update documentation
  ... (15 commits)

🧪 Phase 2: Quality Assurance
--------------------------------------------------
Running pre-commit checks...
✅ check for case conflicts
✅ check for added large files
✅ detect private key
✅ ruff (legacy alias)
✅ ruff format
✅ mypy
All 17 checks passed!

Running test suite...
✅ 51 unit tests passed (coverage: 53%)
⚠️  Integration tests skipped (no device connected)

✅ Documentation validation passed
✅ Breaking changes documented with migration guide

📝 Phase 3: Preparation
--------------------------------------------------
✅ CHANGELOG.md ready for 0.2.0 release
✅ README.md contains migration guide
✅ All version numbers consistent

⚠️  HUMAN REVIEW REQUIRED
Please review:
  - CHANGELOG.md entry for 0.2.0
  - Breaking changes section
  - Migration guide completeness

Continue to execution phase? (y/n):
```

## Release Type Comparison

| Type | Use Case | Workflow | Safety | Tag Timing |
|------|----------|----------|--------|------------|
| **Standard** | Regular releases | Full workflow | Configurable | **CRITICAL** |
| **Hotfix** | Critical fixes | Accelerated | Balanced+ | **STILL CRITICAL** |
| **Pre-release** | Alpha/Beta/RC | Limited dist | Conservative | **MANDATORY** |
| **Dry Run** | Testing/Training | Full simulation | N/A | **VERIFIED** |

## Safety Level Comparison

| Level | Automation | Checkpoints | Tag Timing Emphasis |
|-------|-----------|-------------|-------------------|
| **Conservative** | Minimal | Every phase | **MAXIMUM OVERSIGHT** |
| **Balanced** | Moderate | Key decisions | **MANUAL APPROVAL REQUIRED** |
| **Aggressive** | Maximum | Final only | **AUTOMATED BUT VALIDATED** |

## Error Recovery Examples

### Premature Tag Creation Detected
```markdown
❌ CRITICAL ERROR: Git tag created before final validation!

Current state:
- Tag v0.2.0 created pointing to commit abc123
- Tests not yet run on this commit
- Documentation not fully reviewed

⚠️  IMMEDIATE ACTION REQUIRED:
1. Delete the premature tag: git tag -d v0.2.0
2. Run complete test suite on current commit
3. Get proper human approval
4. Recreate tag at correct moment
5. Document this incident for process improvement

Would you like to proceed with corrective actions? (y/n):
```

### Tag on Wrong Commit
```markdown
❌ ERROR: Git tag points to wrong commit!

Issue detected:
- Tag v0.2.0 points to commit def456
- But release commit is abc123
- Version inconsistency detected

🔧 RECOVERY OPTIONS:
1. Delete incorrect tag and recreate on correct commit
2. Create new patch version (v0.2.1) with proper tagging
3. Abort release and restart process

Recommended: Option 1 - Delete and recreate tag
This maintains version continuity while fixing the error.

Proceed with tag correction? (y/n):
```

### Test Failure During QA
```markdown
🧪 Phase 2: Quality Assurance
--------------------------------------------------
❌ Test failures detected!

Failed tests:
  - tests/integration/test_device.py::test_connection
  - tests/unit/test_element.py::test_element_scroll

Last 500 characters of output:
  ==================== short test summary info ====================
  FAILED tests/integration/test_device.py::test_connection - AssertionError: Device not found

⚠️  HUMAN INTERVENTION REQUIRED
Options:
  1. Fix issues and restart phase
  2. Skip integration tests and proceed (not recommended)
  3. Abort release entirely

Recommendation: Fix test issues or skip integration tests if device unavailable
```

### Git Merge Conflict
```markdown
⚡ Phase 4: Release Execution
--------------------------------------------------
❌ Git merge conflict detected!

Conflict files:
  - CHANGELOG.md
  - README.md

⚠️  HUMAN INTERVENTION REQUIRED
Options:
  1. Manual conflict resolution
  2. Abort and rollback to pre-merge state
  3. Skip merge and tag on develop branch (not recommended)

Recommendation: Resolve conflicts manually to ensure proper main branch state
```

## Best Practices

### Before Starting a Release
1. ✅ Ensure you have proper repository permissions
2. ✅ Verify your development environment is clean
3. ✅ Check that all dependencies are up to date
4. ✅ Review recent commits and changes
5. ✅ Confirm CI/CD pipeline is healthy
6. ✅ **UNDERSTAND THAT GIT TAG TIMING IS CRITICAL**

### During Release Execution
1. ✅ Monitor progress closely, especially in early phases
2. ✅ Don't skip human review steps in conservative mode
3. ✅ Keep detailed notes of any manual interventions
4. ✅ Have rollback plan ready for critical phases
5. ✅ **PAUSE AT GIT TAG CREATION - THIS IS THE MOST CRITICAL MOMENT**
6. ✅ Communicate with team during longer operations

### After Successful Release
1. ✅ Verify release artifacts are accessible
2. ✅ Monitor initial user feedback and bug reports
3. ✅ Update project documentation if needed
4. ✅ Share release announcement with community
5. ✅ **CONDUCT RETROSPECTIVE ON TAG TIMING COMPLIANCE**
6. ✅ Document any deviations or lessons learned

## Troubleshooting Common Issues

### "Git status check failed"
```bash
# Verify Git configuration
git config --get user.name
git config --get user.email
git remote -v

# Check repository connection
git status
git log --oneline -5
```

### "Tests failed" during QA
```bash
# Investigate test failures
pytest -v --tb=long

# Re-run specific tests after fixes
pytest tests/unit/test_specific_feature.py -v
```

### "Pre-commit checks failed"
```bash
# Run pre-commit manually for detailed errors
pre-commit run --all-files

# Fix individual hook failures
pre-commit run ruff --all-files
pre-commit run mypy --all-files
```

### "Permission denied" errors
```bash
# Check repository push permissions
git push --dry-run origin develop

# Verify GitHub authentication
gh auth status
# or
ssh -T git@github.com
```

## Success Metrics

A successful release should achieve:
- ✅ All automated checks passing (tests, linting, pre-commit)
- ✅ Documentation complete and accurate
- ✅ **GIT TAG CREATED AT EXACTLY THE RIGHT MOMENT**
- ✅ Version tags properly created and pushed
- ✅ GitHub release published with assets
- ✅ CI/CD pipelines completing successfully
- ✅ Package available on PyPI
- ✅ **ZERO TAG TIMING VIOLATIONS**

This skill enables professional, reliable release management through AI-driven automation with appropriate human oversight and **CRITICAL ATTENTION TO PROPER GIT TAG TIMING**.
