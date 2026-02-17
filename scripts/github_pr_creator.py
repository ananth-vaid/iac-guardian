#!/usr/bin/env python3
"""
GitHub PR Creator
Creates fix PRs automatically using GitHub API
"""

import os
import subprocess
import requests
from typing import Dict, Optional
from datetime import datetime


class GitHubPRCreator:
    """Creates PRs on GitHub with generated fixes"""

    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPOSITORY')  # Format: owner/repo

        if not self.token:
            # Only show warning in terminal mode, not GitHub Actions
            if os.getenv('GITHUB_ACTIONS') != 'true':
                print("⚠️  Warning: GITHUB_TOKEN not set - PR creation will fail")

        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def create_fix_pr(self, fix: Dict, original_pr_number: Optional[int] = None, base_branch: str = 'main') -> Optional[str]:
        """
        Create a PR with the generated fix

        Args:
            fix: Dict from FixGenerator with files, title, body
            original_pr_number: PR number that triggered this fix
            base_branch: Base branch to merge into

        Returns:
            PR URL if successful, None otherwise
        """
        if not self.token or not self.repo:
            if os.getenv('GITHUB_ACTIONS') != 'true':
                print("Cannot create PR: Missing GITHUB_TOKEN or GITHUB_REPOSITORY")
            return self._simulate_pr_creation(fix, original_pr_number)

        try:
            # 1. Create new branch
            branch_name = self._create_fix_branch(fix['fix_type'], original_pr_number)

            # 2. Apply fixes (update files)
            self._apply_fixes(fix['files'], branch_name)

            # 3. Commit changes
            commit_sha = self._commit_changes(fix, branch_name)

            # 4. Push branch
            self._push_branch(branch_name)

            # 5. Create PR
            pr_url = self._create_github_pr(
                title=fix['pr_title'],
                body=fix['pr_body'],
                head=branch_name,
                base=base_branch,
                original_pr=original_pr_number
            )

            return pr_url

        except Exception as e:
            print(f"Error creating PR: {e}")
            return None

    def _create_fix_branch(self, fix_type: str, original_pr: Optional[int] = None) -> str:
        """Create new branch name"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        pr_suffix = f"-pr{original_pr}" if original_pr else ""
        branch_name = f"iac-guardian/fix-{fix_type}{pr_suffix}-{timestamp}"
        return branch_name

    def _apply_fixes(self, files: list, branch_name: str):
        """
        Apply file changes to working directory

        Args:
            files: List of {'path': str, 'content': str}
            branch_name: Git branch to create
        """
        # Ensure we're on main/master first
        subprocess.run(['git', 'checkout', 'main'], check=False, capture_output=True)

        # Create and checkout new branch
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True, capture_output=True)

        # Write each file
        for file_info in files:
            file_path = file_info['path']

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write content
            with open(file_path, 'w') as f:
                f.write(file_info['content'])

            # Stage file
            subprocess.run(['git', 'add', file_path], check=True, capture_output=True)

    def _commit_changes(self, fix: Dict, branch_name: str) -> str:
        """Commit the changes"""
        commit_message = f"""{fix['pr_title']}

{fix['description']}

Co-Authored-By: IaC Guardian <iac-guardian@datadog.com>
"""

        result = subprocess.run(
            ['git', 'commit', '-m', commit_message],
            check=True,
            capture_output=True,
            text=True
        )

        # Get commit SHA
        sha_result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            check=True,
            capture_output=True,
            text=True
        )

        return sha_result.stdout.strip()

    def _push_branch(self, branch_name: str):
        """Push branch to origin"""
        subprocess.run(
            ['git', 'push', '-u', 'origin', branch_name],
            check=True,
            capture_output=True
        )

    def _create_github_pr(self, title: str, body: str, head: str, base: str, original_pr: Optional[int] = None) -> str:
        """
        Create PR via GitHub API

        Args:
            title: PR title
            body: PR description
            head: Branch with changes
            base: Base branch to merge into
            original_pr: Link to original risky PR
        """
        if not self.repo:
            raise ValueError("GITHUB_REPOSITORY not set")

        # Add reference to original PR if provided
        if original_pr:
            body = f"**🔗 Fixes issues in PR #{original_pr}**\n\n{body}"

        url = f"https://api.github.com/repos/{self.repo}/pulls"

        data = {
            'title': title,
            'body': body,
            'head': head,
            'base': base
        }

        response = requests.post(url, headers=self.headers, json=data, timeout=10)
        response.raise_for_status()

        pr_data = response.json()
        pr_url = pr_data['html_url']
        pr_number = pr_data['number']

        print(f"✅ Created fix PR #{pr_number}: {pr_url}")

        # Add label
        self._add_label_to_pr(pr_number, 'iac-guardian-fix')

        return pr_url

    def _add_label_to_pr(self, pr_number: int, label: str):
        """Add label to PR"""
        try:
            url = f"https://api.github.com/repos/{self.repo}/issues/{pr_number}/labels"
            requests.post(url, headers=self.headers, json={'labels': [label]}, timeout=5)
        except:
            pass  # Labels are optional

    def _simulate_pr_creation(self, fix: Dict, original_pr: Optional[int]) -> str:
        """Simulate PR creation for local testing"""
        # Only show verbose output in terminal mode, not GitHub Actions
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'

        if not is_github_actions:
            print("\n" + "="*80)
            print("🔧 SIMULATED PR CREATION (no GitHub token)")
            print("="*80)
            print(f"\n📝 **Title:** {fix['pr_title']}")
            print(f"\n📄 **Files changed:**")
            for file_info in fix['files']:
                print(f"   - {file_info['path']}")
            print(f"\n📖 **Description:**\n{fix['pr_body'][:500]}...")
            print("\n" + "="*80)

        return None  # Don't include simulated URLs in GitHub comments

    def comment_on_pr(self, pr_number: int, comment: str) -> bool:
        """
        Add comment to existing PR

        Args:
            pr_number: PR number to comment on
            comment: Comment text (markdown supported)
        """
        if not self.repo or not self.token:
            print(f"Would comment on PR #{pr_number}:")
            print(comment[:200] + "...")
            return False

        url = f"https://api.github.com/repos/{self.repo}/issues/{pr_number}/comments"

        data = {'body': comment}

        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            print(f"✅ Added comment to PR #{pr_number}")
            return True
        except Exception as e:
            print(f"Error adding comment: {e}")
            return False
