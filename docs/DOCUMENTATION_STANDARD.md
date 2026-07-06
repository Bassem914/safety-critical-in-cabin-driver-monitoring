# Documentation Standard

---

# Purpose

This document defines the documentation standards used throughout the
**Safety-Critical In-Cabin Driver Monitoring** repository.

The objective is to ensure that every milestone is:

- reproducible
- understandable
- maintainable
- scalable
- reviewable by another Robotics Vision / Perception Engineer

Documentation is considered part of the implementation and is required for every milestone.

---

# Documentation Philosophy

This repository follows an engineering-first philosophy.

Every implementation milestone should explain:

- What was implemented.
- Why it was implemented.
- How it was implemented.
- How it was validated.

Documentation should allow another engineer to understand the milestone without reading the source code first.

---

# Engineering Principles

The repository follows these principles:

1. Preserve previous milestones.
2. Prefer modular implementations over monolithic scripts.
3. Separate perception, decision, visualization, experiments, and utilities.
4. Document engineering decisions.
5. Validate every milestone.
6. Keep implementations reproducible.
7. Design every milestone for future scalability.
8. Treat documentation as part of the engineering process.

---

# Naming Convention

Implementation documents

```text
docs/implementation/path_XX_milestone_XX_<short_title>.md
```

Validation documents

```text
docs/validation/path_XX_milestone_XX_<short_title>_validation.md
```

Templates

```text
docs/templates/implementation_template.md
docs/templates/validation_template.md
```

---

# Required Engineering Perspectives

Every implementation document must include the following perspectives.

## Software Perspective

Describe:

- software modules
- architecture
- interfaces
- dependencies

Purpose:

Explain how the software is organized.

---

## Computer Vision Perspective

Describe:

- inputs
- outputs
- algorithms
- image processing
- landmarks
- coordinate systems

Purpose:

Explain the perception pipeline.

---

## Python Perspective

Describe:

- classes
- functions
- typing
- modules
- package organization

Purpose:

Maintain readable, reusable Python code.

---

## Engineering Perspective

Describe:

- design decisions
- engineering trade-offs
- maintainability
- runtime considerations
- modularity

Purpose:

Document engineering reasoning rather than implementation only.

---

# Validation Philosophy

Every milestone must be reproducible by another engineer.

Validation documents should include:

- test environment
- test configuration
- test cases
- results
- evidence
- known issues
- engineering assessment

---

# Evidence Storage

Generated outputs belong inside the corresponding implementation path.

Example

```text
paths/01_fast_prototype/outputs/
```

Recommended folders

```text
outputs/
├── figures/
├── videos/
└── logs/
```

---

# Git Workflow

Whenever practical, milestones should use separate commits for:

1. implementation
2. documentation
3. validation

Small related changes may be combined when this improves clarity.

Commit messages should clearly describe the engineering change.

---

# Milestone Completion Checklist

Every milestone should finish with:

- [ ] Software implementation completed
- [ ] Computer vision functionality verified
- [ ] Validation completed
- [ ] Documentation completed
- [ ] Git commit completed
- [ ] GitHub updated
- [ ] Ready for next milestone