#!/usr/bin/env python3
"""
Chairman Monthly Audit Script
Runs against all Connected Agents AI orgs, checks repo health, detects drift.
Outputs a report.md and exits with code 1 if drift detected (triggers GH issue).

Usage: python3 chairman_audit.py --orgs ORG1,ORG2 --output report.md
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

REQUIRED_TOPICS_MIN = 2
REQUIRED_FIELDS = ['description']
STALE_DAYS = 180
DRIFT_MARKERS = []

def run_gh(args: list, org: str = None) -> dict | list | None:
    cmd = ['gh'] + args
    env = {**os.environ, 'GITHUB_TOKEN': ''}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except Exception:
        return result.stdout.strip()

def check_repo(org: str, repo: dict) -> dict:
    name = repo['name']
    issues = []
    now = datetime.now(timezone.utc)

    # Check description
    if not repo.get('description'):
        issues.append('missing description')
        DRIFT_MARKERS.append(f'{org}/{name}: no description')

    # Check topics
    topics = repo.get('repositoryTopics') or []
    if topics and isinstance(topics[0], dict):
        topic_names = [t.get('topic', {}).get('name', t.get('name', '')) for t in topics]
    else:
        topic_names = [t for t in topics if isinstance(t, str)]
    if len(topic_names) < REQUIRED_TOPICS_MIN:
        issues.append(f'only {len(topic_names)} topics (need {REQUIRED_TOPICS_MIN}+)')
        DRIFT_MARKERS.append(f'{org}/{name}: insufficient topics')

    # Check staleness
    pushed_at = repo.get('pushedAt', '')
    if pushed_at:
        pushed = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
        days_since = (now - pushed).days
        if days_since > STALE_DAYS:
            issues.append(f'stale ({days_since}d since last push)')
            DRIFT_MARKERS.append(f'{org}/{name}: stale {days_since}d')

    return {
        'name': name,
        'org': org,
        'topics': len(topic_names),
        'has_description': bool(repo.get('description')),
        'pushed_at': pushed_at[:10] if pushed_at else 'never',
        'is_fork': repo.get('isFork', False),
        'is_private': repo.get('isPrivate', True),
        'issues': issues,
        'health': '🟢 OK' if not issues else f'🔴 {len(issues)} issue(s)',
    }

def audit_org(org: str) -> list:
    repos = run_gh([
        'repo', 'list', org, '--limit', '200',
        '--json', 'name,description,isArchived,isFork,isPrivate,pushedAt,repositoryTopics',
        '--jq', '[.[] | select(.isArchived==false)]'
    ])
    if not repos:
        print(f'  ⚠️  Cannot access {org} or no repos found')
        return []
    return [check_repo(org, r) for r in repos]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--orgs', default='connectedagents-ai,Connected-Energy-AI')
    parser.add_argument('--output', default='report.md')
    args = parser.parse_args()

    orgs = [o.strip() for o in args.orgs.split(',')]
    now = datetime.now(timezone.utc)
    all_results = []

    print(f'🏛️  Chairman Monthly Audit — {now.strftime("%Y-%m-%d %H:%M UTC")}')
    print(f'   Orgs: {orgs}\n')

    for org in orgs:
        print(f'  Scanning {org}...')
        results = audit_org(org)
        all_results.extend(results)
        ok = sum(1 for r in results if not r['issues'])
        bad = len(results) - ok
        print(f'    {len(results)} repos: {ok} OK, {bad} issues\n')

    # Generate report
    report_lines = [
        f'# 🏛️ Chairman Monthly Audit Report',
        f'*Generated: {now.strftime("%Y-%m-%d %H:%M UTC")} | Orgs: {", ".join(orgs)}*',
        f'',
        f'## Summary',
        f'',
        f'| Metric | Value |',
        f'|--------|-------|',
        f'| Total repos audited | {len(all_results)} |',
        f'| Repos passing all checks | {sum(1 for r in all_results if not r["issues"])} |',
        f'| Repos with issues | {sum(1 for r in all_results if r["issues"])} |',
        f'| Total drift markers | {len(DRIFT_MARKERS)} |',
        f'',
    ]

    if DRIFT_MARKERS:
        report_lines += [
            '## ⚠️ DRIFT DETECTED',
            '',
            '| Repo | Issues |',
            '|------|--------|',
        ]
        for r in all_results:
            if r['issues']:
                report_lines.append(f'| `{r["org"]}/{r["name"]}` | {", ".join(r["issues"])} |')
        report_lines.append('')
    else:
        report_lines += ['## ✅ No Drift Detected\n', 'All repos are healthy.\n']

    report_lines += [
        '## Full Repo Health Table',
        '',
        '| Repo | Org | Topics | Desc | Last Push | Health |',
        '|------|-----|--------|------|-----------|--------|',
    ]
    for r in sorted(all_results, key=lambda x: (bool(x['issues']), x['org'], x['name']), reverse=True):
        desc_icon = '✅' if r['has_description'] else '❌'
        report_lines.append(
            f'| `{r["name"]}` | {r["org"]} | {r["topics"]} | {desc_icon} | {r["pushed_at"]} | {r["health"]} |'
        )

    report = '\n'.join(report_lines)
    Path(args.output).write_text(report)
    print(f'✅ Report written to {args.output}')

    if DRIFT_MARKERS:
        print(f'\n⚠️  DRIFT DETECTED — {len(DRIFT_MARKERS)} issues found')
        sys.exit(1)
    else:
        print('✅ All repos healthy — no drift detected')
        sys.exit(0)

if __name__ == '__main__':
    main()
