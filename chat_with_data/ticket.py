import os
import requests
from dotenv import load_dotenv

load_dotenv()

def create_support_ticket(user_q: str, bot_a: str, ticket_description: str = "") -> str:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")
    user = os.getenv("GITHUB_USER")

    if not token or not repo:
        print("[TICKET] Missing GITHUB_TOKEN or GITHUB_REPO in .env")
        return "GitHub credentials missing. Check .env file."

    url = f"https://api.github.com/repos/{user}/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {
        "title": f"Chat issue – {user_q[:100]}",
        "body": f"**User query:**\n{user_q}\n\n**Bot answer:**\n{bot_a}\n\n**User description:**\n{ticket_description}"
    }

    print(f"[TICKET] Creating issue in {repo}...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            issue_url = response.json().get("html_url")
            print(f"[TICKET] Success → {issue_url}")
            return f"Support ticket created!\n{issue_url}"
        else:
            error_msg = response.json().get("message", "Unknown error")
            print(f"[TICKET] Failed: {response.status_code} – {error_msg}")
            return f"Failed to create ticket: {response.status_code} – {error_msg}"
    except Exception as e:
        print(f"[TICKET] Exception: {e}")
        return f"Error creating ticket: {str(e)}"