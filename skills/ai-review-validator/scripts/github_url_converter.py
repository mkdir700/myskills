#!/usr/bin/env python3
"""
Convert GitHub PR comment URLs to GitHub API URLs

Usage:
    python github_url_converter.py <github_url>

Examples:
    Input:  https://github.com/UniClipboard/UniClipboard/pull/158#discussion_r2734386595
    Output: https://api.github.com/repos/UniClipboard/UniClipboard/pulls/comments/2734386595
    
    Input:  https://github.com/owner/repo/pull/123#issuecomment-456789
    Output: https://api.github.com/repos/owner/repo/issues/comments/456789
"""

import re
import sys


def convert_github_url_to_api(url):
    """
    Convert GitHub web URL to GitHub API URL
    
    Args:
        url: GitHub PR comment URL in web format
        
    Returns:
        API URL string if conversion successful, None otherwise
    """
    # PR review comment pattern: #discussion_r{comment_id}
    pr_review = re.match(
        r'https://github\.com/([^/]+)/([^/]+)/pull/\d+#discussion_r(\d+)',
        url
    )
    if pr_review:
        owner, repo, comment_id = pr_review.groups()
        return f"https://api.github.com/repos/{owner}/{repo}/pulls/comments/{comment_id}"
    
    # Issue/PR comment pattern: #issuecomment-{comment_id}
    issue_comment = re.match(
        r'https://github\.com/([^/]+)/([^/]+)/(?:pull|issues)/\d+#issuecomment-(\d+)',
        url
    )
    if issue_comment:
        owner, repo, comment_id = issue_comment.groups()
        return f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}"
    
    # Already an API URL - return as is
    if url.startswith('https://api.github.com/'):
        return url
    
    return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python github_url_converter.py <github_url>", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    api_url = convert_github_url_to_api(url)
    
    if api_url:
        print(api_url)
    else:
        print(f"Error: Unable to convert URL: {url}", file=sys.stderr)
        print("Supported formats:", file=sys.stderr)
        print("  - PR review comment: https://github.com/owner/repo/pull/123#discussion_r456", file=sys.stderr)
        print("  - Issue comment: https://github.com/owner/repo/pull/123#issuecomment-456", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
