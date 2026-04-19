# Security Policy

## Supported Versions

Raw-Gent is still evolving quickly, so security fixes are most likely to land on the latest version in the default branch.

At the moment:

- Latest `main`: supported
- Older snapshots or forks: best effort only

## Reporting a Vulnerability

Please do not report security vulnerabilities in public GitHub issues.

Use one of these private channels instead:

1. GitHub private vulnerability reporting, if it is enabled for this repository.
2. Email the maintainer at `arpanmondal572@gmail.com` with the subject line `Raw-Gent security report`.

Please include:

- a clear description of the issue
- affected files, routes, or components
- steps to reproduce the problem
- proof of concept, logs, or screenshots when helpful
- any suggested mitigation if you already have one

## What to Expect

- Initial acknowledgment target: within 7 days
- Triage and severity assessment: as soon as practical
- Fix timeline: depends on impact, reproducibility, and release complexity

If the report is accepted as a valid security issue, the goal is to coordinate a fix before public disclosure.

## Scope

Examples of issues that should be reported privately:

- authentication bypass
- cookie or session handling flaws
- GitHub token exposure
- unsafe webhook handling
- secret leakage
- command execution or sandbox escape paths
- dependency or deployment misconfigurations with real security impact

Examples of things that usually do not need private reporting:

- documentation typos
- general code quality concerns without security impact
- feature requests
- minor configuration questions

## Safe Harbor

Good-faith security research aimed at helping improve the project is appreciated. Please avoid:

- accessing data that does not belong to you
- modifying or deleting other users' data
- disrupting availability for real users or deployments
- publicly disclosing details before there is time to investigate and respond
