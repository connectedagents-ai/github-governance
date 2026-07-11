# 🏛️ GitHub Chairman — Governance System

[![Stale Detector](https://img.shields.io/github/actions/workflow/status/connectedagents-ai/github-governance/stale-detector.yml?label=stale-detector&style=flat-square)](https://github.com/connectedagents-ai/github-governance/actions/workflows/stale-detector.yml)
[![Secret Scan](https://img.shields.io/github/actions/workflow/status/connectedagents-ai/github-governance/secret-scan.yml?label=secret-scan&style=flat-square)](https://github.com/connectedagents-ai/github-governance/actions/workflows/secret-scan.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

> Automated governance, security scanning, and hygiene enforcement for the **connectedagents-ai** GitHub organization.

---

## 📋 Overview

The **GitHub Chairman Governance System** is the central enforcement layer for all repositories under the `connectedagents-ai` organization. It provides:

- 🔍 **Automated stale repository detection** — monthly audits to identify repos that have gone dormant
- 🔐 **Secret scanning** — continuous TruffleHog scans on every push and PR to prevent credential leaks
- 📐 **Repo standards enforcement** — standardized templates, issue forms, and PR workflows via [repo-template](https://github.com/connectedagents-ai/repo-template)
- 📊 **Audit trails** — all governance actions are logged via GitHub Actions run history

This repo is part of the **GitHub Chairman** project — a fully automated multi-agent system for GitHub organization governance.

---

## ⚙️ Automated Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **Stale Repo Detector** | [`stale-detector.yml`](.github/workflows/stale-detector.yml) | Monthly (1st @ 09:00 UTC) + manual | Lists all repos not pushed to in 180+ days. Outputs a formatted report for review. |
| **Secret Scan** | [`secret-scan.yml`](.github/workflows/secret-scan.yml) | Every push & PR (all branches) | Runs TruffleHog to detect verified leaked secrets. Blocks merges if secrets are found. |

### Workflow Details

#### 🗂️ Stale Repo Detector
- **Schedule:** `0 9 1 * *` (1st of every month, 09:00 UTC)
- **Manual Trigger:** Yes — configurable `days_threshold` input (default: 180 days)
- **Output:** Markdown table of stale repos with last push date, days since push, and visibility
- **Action on stale repos:** Report only — no automatic archiving (human review required)

#### 🔐 Secret Scan (TruffleHog)
- **Trigger:** `push` to any branch + `pull_request` targeting any branch
- **Tool:** [TruffleHog](https://github.com/trufflesecurity/trufflehog) — scans git history for verified secrets
- **Mode:** `--only-verified` — reduces false positives by only flagging live, active credentials
- **On detection:** Workflow fails with remediation instructions; PR merge is blocked

---

## 🖐️ Manual Audit

To run a governance audit manually:

### Run Stale Detector On-Demand

```bash
# Trigger via GitHub CLI
GITHUB_TOKEN="<your-token>" gh workflow run stale-detector.yml \
  --repo connectedagents-ai/github-governance \
  --field days_threshold=180
```

### Check Workflow Run Status

```bash
GITHUB_TOKEN="<your-token>" gh run list \
  --repo connectedagents-ai/github-governance \
  --workflow stale-detector.yml \
  --limit 5
```

### View Last Run Logs

```bash
GITHUB_TOKEN="<your-token>" gh run view \
  --repo connectedagents-ai/github-governance \
  --log
```

---

## 📐 Repo Template

All new repositories in the `connectedagents-ai` organization should be created from the **[repo-template](https://github.com/connectedagents-ai/repo-template)**, which includes:

| Asset | Description |
|-------|-------------|
| `README.md` | Professional template with badges, sections, and configuration table |
| `.gitignore` | Comprehensive ignore rules for Python + Node.js + macOS + AI tools |
| `.github/workflows/validate.yml` | PR validation — README check + Python/Node lint |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Structured bug report form |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Structured feature request form |
| `.github/pull_request_template.md` | PR checklist template |

**To create a new repo from the template:**

```bash
GITHUB_TOKEN="<your-token>" gh repo create connectedagents-ai/new-repo-name \
  --template connectedagents-ai/repo-template \
  --private
```

---

## 👤 Maintainer

| Field | Value |
|-------|-------|
| **Owner** | [Robert Bailey](https://github.com/rbailey713) |
| **Organization** | [Connected Agents AI](https://github.com/connectedagents-ai) |
| **Contact** | rbailey@powerconnection.com |
| **Last Updated** | 2026-07-04 |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  🤖 Automated by <strong>GitHub Chairman</strong> — Connected Agents AI Governance Platform
</p>
