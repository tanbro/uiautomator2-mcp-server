# Release Manager Skill

Automated release management system specifically designed for the uiautomator2-mcp-server project.

## 🎯 Purpose

This skill automates the complete software release lifecycle, from initial evaluation through final verification, ensuring consistent, reliable, and high-quality releases.

## 🚀 Key Features

### Automated Workflow
- **Complete Lifecycle Management**: End-to-end release orchestration
- **Multi-phase Execution**: Evaluation → QA → Preparation → Execution → Verification
- **Automatic GitHub Release**: CI creates releases with CHANGELOG notes and attached wheels
- **Automatic PyPI Publishing**: Trusted Publishing for secure, credential-free uploads
- **Flexible Release Types**: Standard, Hotfix, Pre-release, and Dry-run modes
- **Configurable Safety Levels**: Conservative, Balanced, and Aggressive options

### Quality Assurance
- **Comprehensive Testing**: Full test suite execution with detailed reporting
- **Pre-commit Validation**: Automated code quality and style checking
- **Documentation Verification**: README, CHANGELOG, and release note validation
- **Dependency Analysis**: Security scanning and version compatibility checking

### Human Oversight
- **Interactive Decision Points**: Strategic pause points for human review
- **Granular Control**: Approval requirements based on safety level
- **Error Recovery**: Automated rollback and recovery procedures
- **Progress Transparency**: Real-time status updates and logging

## 📁 Structure

```
release-manager/
├── SKILL.md                 # Core skill definition and metadata
├── README.md               # This file
├── references/             # Detailed specifications and documentation
│   └── release-process.md  # Complete process specification
└── examples/               # Usage examples and best practices
    └── usage-examples.md   # Comprehensive usage documentation
```

## 🛠️ Usage Examples

### Quick Start
Simply ask your AI client to execute a release:

```
Prepare and execute release v0.2.0
```

### Advanced Usage
```
# Dry run to test the process
Run a dry-run release simulation for v0.2.0

# Hotfix release with expedited workflow
Execute a hotfix release for v0.2.1

# Conservative release with maximum safety
Run a conservative safety release with manual approval at each checkpoint
```

## ⚙️ Configuration Options

### Release Types
- **Standard**: Full release workflow with all checks
- **Hotfix**: Accelerated workflow for critical fixes
- **Pre-release**: Alpha/beta/rc versions with limited distribution
- **Dry-run**: Simulation mode without actual publishing

### Safety Levels
- **Conservative**: Maximum human oversight, strict validation
- **Balanced**: Reasonable automation with key checkpoints (default)
- **Aggressive**: Maximum automation, minimal intervention

## 📊 Success Criteria

A release is considered successful when all phases complete with:
- ✅ All tests passing consistently
- ✅ Pre-commit checks completing without errors
- ✅ Documentation being complete and accurate
- ✅ Version tags properly created and pushed
- ✅ CI/CD automatically creating GitHub Release with:
  - Release notes from CHANGELOG
  - Wheel and source distribution files attached
- ✅ CI/CD automatically publishing to PyPI
- ✅ All pipelines completing successfully

## 🆘 Error Handling

Built-in recovery mechanisms for common issues:
- **Test failures**: Detailed reporting with restart options
- **Git conflicts**: Automatic backup and manual resolution workflow
- **Version inconsistencies**: Validation and correction suggestions
- **Pipeline failures**: Real-time monitoring and retry logic

## 🎓 Learning Resources

- [`references/release-process.md`](references/release-process.md) - Complete process specification
- [`examples/usage-examples.md`](examples/usage-examples.md) - Detailed usage examples and patterns

## 💡 Design Philosophy

This skill follows the principle of **direct command execution** - the AI executes git and project commands directly without wrapper scripts. This approach:

- **Simpler**: No Python wrapper code to maintain
- **Transparent**: Each command is visible and auditable
- **Flexible**: Easy to adapt to project-specific needs
- **Educational**: Users can see and understand each step

The skill specification provides the structure and checkpoints, while the AI handles command execution and decision-making.

This skill transforms release management from a manual, error-prone process into an automated, reliable workflow while maintaining appropriate human oversight for quality assurance.
