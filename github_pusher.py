"""
github_pusher.py — Addım 6: Yaradılmış kod fayllarını GitHub-a push edir
Requires: GITHUB_TOKEN and GITHUB_REPO in .env
"""
import os
import base64
from pathlib import Path


def push_to_github(project_dir: str, repo_name: str, token: str, commit_msg: str = "AI Startup Team: Auto-generated code") -> dict:
    """
    project_dir içindəki bütün faylları GitHub repo-suna push edir.
    repo_name format: "username/repo-name"
    Returns: {"success": bool, "url": str, "files_pushed": int}
    """
    import requests

    if not token:
        return {"success": False, "url": "", "files_pushed": 0, "error": "GITHUB_TOKEN tapılmadı."}

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    base_url = f"https://api.github.com/repos/{repo_name}/contents"

    proj_path = Path(project_dir)
    if not proj_path.exists():
        return {"success": False, "url": "", "files_pushed": 0, "error": f"Qovluq tapılmadı: {project_dir}"}

    files_pushed = 0
    errors = []

    for file_path in proj_path.rglob("*"):
        if not file_path.is_file():
            continue

        relative = file_path.relative_to(proj_path)
        github_path = str(relative).replace("\\", "/")

        try:
            content_bytes = file_path.read_bytes()
            content_b64 = base64.b64encode(content_bytes).decode("utf-8")

            # Mövcud faylın SHA-sını al (update üçün lazım olur)
            sha = None
            check_resp = requests.get(f"{base_url}/{github_path}", headers=headers, timeout=15)
            if check_resp.status_code == 200:
                sha = check_resp.json().get("sha")

            payload = {
                "message": f"{commit_msg} — {github_path}",
                "content": content_b64,
            }
            if sha:
                payload["sha"] = sha

            resp = requests.put(f"{base_url}/{github_path}", headers=headers, json=payload, timeout=30)

            if resp.status_code in (200, 201):
                files_pushed += 1
            else:
                errors.append(f"{github_path}: {resp.json().get('message', resp.text)}")

        except Exception as e:
            errors.append(f"{github_path}: {e}")

    repo_url = f"https://github.com/{repo_name}"
    success = files_pushed > 0

    return {
        "success": success,
        "url": repo_url,
        "files_pushed": files_pushed,
        "errors": errors
    }
