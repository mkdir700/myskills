#!/usr/bin/env python3
"""
Generate decision logs from git commits or conversation context.

Usage:
    python generate_decision_log.py --from-git [--days N]
    python generate_decision_log.py --from-text "code change description"
"""

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


def generate_from_git(days=1):
    """Extract decision logs from recent git commits."""
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    try:
        # Get commits since date
        result = subprocess.run(
            ["git", "log", f"--since={since_date}", "--pretty=format:%H|%ai|%s|%b"],
            capture_output=True,
            text=True,
            check=True
        )
        
        commits = result.stdout.strip().split("\n")
        decisions = []
        
        for commit in commits:
            if not commit:
                continue
                
            parts = commit.split("|")
            if len(parts) < 3:
                continue
                
            commit_hash, commit_date, subject = parts[0], parts[1], parts[2]
            body = parts[3] if len(parts) > 3 else ""
            
            # Parse existing decision log if present
            if "[Decision Log]" in body or "[decision]" in body.lower():
                decisions.append({
                    "date": commit_date[:16],
                    "summary": subject,
                    "body": body
                })
            else:
                # Generate minimal decision log
                timestamp = commit_date[:16]
                decisions.append({
                    "date": timestamp,
                    "summary": subject,
                    "why": "See commit message for details",
                    "risk": "none"
                })
        
        return decisions
        
    except subprocess.CalledProcessError as e:
        print(f"Error reading git log: {e}", file=sys.stderr)
        return []


def generate_from_text(description):
    """Generate decision log from text description."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Simple heuristic: extract main action
    summary = description.split(".")[0].strip()
    
    return {
        "date": timestamp,
        "summary": summary,
        "why": "Manual entry - see description",
        "risk": "none"
    }


def format_decision(decision):
    """Format decision as standardized log entry."""
    if isinstance(decision, dict):
        if "body" in decision and "[Decision Log]" in decision.get("body", ""):
            # Already formatted
            return f"[{decision['date']}] {decision['summary']}\n{decision['body']}"
        else:
            # Generate format
            why = decision.get("why", "")
            risk = decision.get("risk", "none")
            return f"[{decision['date']}] {decision['summary']}\n- Why: {why}\n- Risk: {risk}"
    return str(decision)


def save_to_decisions_dir(decisions, output_dir=".decisions"):
    """Save decisions to dated files in .decisions/ directory."""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Group by date
    by_date = {}
    for decision in decisions:
        date = decision["date"][:10]  # YYYY-MM-DD
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(decision)
    
    # Write to files
    for date, day_decisions in by_date.items():
        filepath = Path(output_dir) / f"{date}.md"
        with open(filepath, "a") as f:
            for decision in day_decisions:
                f.write(format_decision(decision) + "\n\n")
        print(f"Appended {len(day_decisions)} decisions to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Generate decision logs")
    parser.add_argument("--from-git", action="store_true", help="Extract from git commits")
    parser.add_argument("--days", type=int, default=1, help="Days of git history to scan")
    parser.add_argument("--from-text", type=str, help="Generate from text description")
    parser.add_argument("--output", type=str, default=".decisions", help="Output directory")
    parser.add_argument("--print", action="store_true", help="Print to stdout instead of saving")
    
    args = parser.parse_args()
    
    decisions = []
    
    if args.from_git:
        decisions = generate_from_git(args.days)
    elif args.from_text:
        decisions = [generate_from_text(args.from_text)]
    else:
        parser.print_help()
        sys.exit(1)
    
    if not decisions:
        print("No decisions found.", file=sys.stderr)
        sys.exit(0)
    
    if args.print:
        for decision in decisions:
            print(format_decision(decision))
            print()
    else:
        save_to_decisions_dir(decisions, args.output)


if __name__ == "__main__":
    main()
