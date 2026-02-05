---
name: release-manager
description: Automated release management skill for uiautomator2-mcp-server. Evaluates codebase status, runs checks, updates documentation, and manages the complete release workflow.
license: Apache-2.0
compatibility: Requires Git repository with proper configuration, Python environment, and GitHub access
metadata:
  author: uiautomator2-mcp-server team
  version: 1.0.0
  purpose: project-specific release automation
  category: development-tool
---

# Release Manager Skill

## ⚠️ CRITICAL: Git Tag Timing & Branch Management

**MOST IMPORTANT**: Git tagging MUST happen at the EXACT LAST MOMENT before pushing to remote, on the main/master branch ONLY.

### The Absolute Rule

**Git tag creation is the FINAL step before pushing - nothing comes after it except `git push`.**

### Tag Timing Rules
❌ **WRONG**: Tag during development/testing phase
❌ **WRONG**: Tag before final validation
❌ **WRONG**: Tag before merging to main/master
❌ **WRONG**: Tag on develop branch
❌ **WRONG**: Tag → then discover uncommitted files
❌ **WRONG**: Tag → then realize tests need to run
✅ **CORRECT**: All work complete → Merged to main/master → Tag (FINAL STEP) → Push

### Branch Management Rules
- **Development happens on**: `develop` branch
- **Release commits created on**: `develop` branch
- **Merge direction**: `develop` → `main` (or `master`)
- **Tag location**: `main` (or `master`) branch ONLY
- **Push order**: Push main branch, then push tag

**Why this matters**:
- Premature tagging creates broken releases where the tag points to incomplete/untested code
- Tags on wrong branches cause version confusion and deployment issues
- Proper branch isolation ensures clean release history
- Tagging as the final step guarantees the tagged commit is exactly what gets published

## Goals

- Automate the complete release workflow from evaluation to publication
- Ensure code quality and documentation completeness before release
- Provide interactive release management with human oversight
- Support both standard and emergency release scenarios
- **CRITICALLY**: Enforce proper git tag timing to prevent broken releases

## Prerequisites

- Git repository with proper remote configuration
- Python development environment with required tools installed
- GitHub account with repository access permissions
- Proper version control setup (main/develop branches)
- Pre-commit hooks configured and working

## Release Workflow Phases

### Phase 1: Codebase Evaluation
1. Assess current Git status and branch position
2. Review recent commits and changes since last release
3. Check version numbers and changelog entries
4. **CRITICAL**: Verify all untracked files are handled (committed or .gitignore'd)
5. Verify working directory is clean (no uncommitted changes)
6. Evaluate overall project health and readiness

⚠️ **NO git operations in this phase**

### Phase 2: Quality Assurance
1. Run comprehensive test suite
2. Execute pre-commit checks and linting
3. Validate documentation completeness
4. Check for breaking changes and migration guides

⚠️ **NO git operations in this phase**

### Phase 3: Preparation
1. Update version numbers if needed
2. Finalize CHANGELOG entries
3. Update README and other documentation
4. Prepare release notes and announcements

⚠️ **Changes made but NOT tagged yet**

### Phase 4: Execution (Critical Timing Phase)

**DEVELOPMENT BRANCH**: develop
**RELEASE BRANCH**: main (or master)

1. **VERIFY** all changes are committed (check `git status` - clean working directory)
2. **CREATE FINAL RELEASE COMMIT** on develop branch
3. **SWITCH to main/master branch**: `git checkout main` (or `master`)
4. **MERGE develop to main/master**: `git merge develop`
5. **VERIFY** merge is clean (fast-forward preferred, or clean merge)
6. **VERIFY** on correct branch (main/master)
7. **VERIFY** working directory is still clean
8. **CREATE GIT TAG** on main/master ← **THE FINAL STEP**
   - This is the LAST action before pushing
   - NOTHING should happen after tagging except push
9. **PUSH main/master branch** to remote
10. **PUSH tag** to remote
11. Monitor CI/CD pipeline status

### Phase 5: Verification
1. Confirm successful GitHub release creation
2. Verify PyPI package publication
3. Check documentation deployment
4. Send release notifications

## Critical Git Tag Timing & Branch Rules

### ✅ **CORRECT SEQUENCE:**
```
1. Make all necessary code/documentation changes (on develop)
2. Verify git status - ensure ALL files are committed
3. Run complete tests and validation
4. Get final approval for release
5. Create final release commit on develop
6. Switch to main/master branch
7. Merge develop to main/master
8. Verify on correct branch (main/master)
9. Verify working directory is clean
10. CREATE GIT TAG on main/master (FINAL STEP - NOTHING AFTER THIS)
11. Push everything to remote
```

### ❌ **INCORRECT SEQUENCES TO AVOID:**
```
❌ Test → Tag → Fix issues → Push (Tag points to broken code)
❌ Develop → Tag → Test → Push (Tag created too early)
❌ Tag → Test → Fix → Push (Backwards workflow)
❌ Tag → Find uncommitted files → Commit → Tag wrong commit (Version confusion)
❌ Tag → Realize need to merge → Merge → Tag wrong commit (Wrong branch)
❌ Merge → Push → Remember to tag → Tag → Push tag (Tag missed the release)
```

## Interactive Decision Points

The skill will pause at key decision points to allow human review:

- ✅ **Pre-flight Check**: Confirm release readiness assessment
- ✅ **Quality Gate**: Approve test results and code quality  
- ✅ **Final Approval**: **CRITICAL** - Authorize git tag creation
- ✅ **Post-release Verification**: Confirm successful deployment

## Error Handling & Rollback

### Common Issues Handled:
- **Tag created on wrong branch**: Delete and recreate on correct branch
- **Uncommitted changes discovered**: Commit and restart tag process
- **Test failures during QA phase**: Fix and re-run tests before tagging
- **Git conflicts during merge**: Resolve and verify clean merge
- **Version numbering inconsistencies**: Validate across all files
- **Documentation validation errors**: Fix before proceeding
- **CI/CD pipeline failures**: Monitor and handle appropriately

### Rollback Procedures:
- Automatic stash/unstash for failed operations
- Branch restoration from backup references
- Tag deletion for failed releases
- Commit reversion with explanatory messages

## Configuration Options

### Release Types:
- **Standard Release**: Full workflow with all checks
- **Hotfix Release**: Accelerated workflow for critical fixes
- **Pre-release**: Alpha/beta/rc versions with limited distribution
- **Dry Run**: Simulation mode without actual publishing

### Safety Levels:
- **Conservative**: Strict checks, manual approvals at every step
- **Balanced**: Reasonable automation with key checkpoints
- **Aggressive**: Maximum automation, minimal human intervention

## Success Criteria

A release is considered successful when:
- ✅ All tests pass consistently
- ✅ Pre-commit checks complete without errors
- ✅ Documentation is complete and accurate
- ✅ **GIT TAG CREATED AT CORRECT MOMENT**
- ✅ Version tags are properly pushed
- ✅ GitHub release is published successfully
- ✅ CI/CD pipelines complete successfully
- ✅ Package is available on PyPI

## Emergency Procedures

For urgent releases:
1. Fast-track critical fixes through abbreviated workflow
2. Bypass non-essential checks with proper justification
3. Coordinate with team for expedited review
4. **STILL FOLLOW PROPER TAG TIMING**
5. Document emergency release rationale
6. Follow up with proper post-release validation

This skill ensures professional, reliable release management while maintaining flexibility for different scenarios and urgency levels.
