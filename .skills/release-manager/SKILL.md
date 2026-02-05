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

## ⚠️ CRITICAL: Git Tag Timing Warning

**MOST IMPORTANT**: Git tagging MUST happen at the EXACT right moment:

❌ **WRONG**: Tag during development/testing phase  
❌ **WRONG**: Tag before final validation  
✅ **CORRECT**: Tag only AFTER all changes are finalized and validated  

**Why this matters**: Premature tagging creates broken releases where the tag points to incomplete/untested code.

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
4. Evaluate overall project health and readiness

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
1. **CREATE FINAL RELEASE COMMIT** with all validated changes
2. **MERGE to main branch** (if using GitFlow)
3. **CREATE GIT TAG** ← **THE CRITICAL MOMENT**
4. **PUSH changes and tag to GitHub**
5. Monitor CI/CD pipeline status

### Phase 5: Verification
1. Confirm successful GitHub release creation
2. Verify PyPI package publication
3. Check documentation deployment
4. Send release notifications

## Critical Git Tag Timing Rules

### ✅ **CORRECT SEQUENCE:**
```
1. Make all necessary code/documentation changes
2. Run complete tests and validation
3. Get final approval for release
4. Create final release commit
5. CREATE GIT TAG (this is the critical moment!)
6. Push everything to remote
```

### ❌ **INCORRECT SEQUENCES TO AVOID:**
```
❌ Test → Tag → Fix issues → Push (Tag points to broken code)
❌ Develop → Tag → Test → Push (Tag created too early)
❌ Tag → Test → Fix → Push (Backwards workflow)
```

## Interactive Decision Points

The skill will pause at key decision points to allow human review:

- ✅ **Pre-flight Check**: Confirm release readiness assessment
- ✅ **Quality Gate**: Approve test results and code quality  
- ✅ **Final Approval**: **CRITICAL** - Authorize git tag creation
- ✅ **Post-release Verification**: Confirm successful deployment

## Error Handling & Rollback

### Common Issues Handled:
- Test failures during QA phase
- Git conflicts during merge
- Version numbering inconsistencies
- Documentation validation errors
- CI/CD pipeline failures

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
