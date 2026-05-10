"""
web_deployer.py — Avtomatik Website Deploy (Netlify API)
Agent-in yazdığı HTML/CSS/JS fayllarını Netlify-a deploy edib link qaytarır.
Requires: NETLIFY_TOKEN in .env or Streamlit Secrets
"""
import os
import io
import re
import zipfile
import requests
from pathlib import Path


NETLIFY_API = "https://api.netlify.com/api/v1"


def extract_web_files(agent_result: str) -> dict[str, str]:
    """
    Agent nəticəsindən HTML/CSS/JS fayllarını çıxarır.
    Returns: {"index.html": "...", "style.css": "...", ...}
    """
    files = {}

    # 1. XML <file path="..."> formatı
    xml_matches = re.findall(r'<file path="([^"]+\.(html|css|js))">\s*\n(.*?)</file>', agent_result, re.DOTALL)
    for path, ext, content in xml_matches:
        filename = Path(path).name
        files[filename] = content.strip()

    # 2. Markdown ```html ... ``` blokları (yalnız index.html tapılmayıbsa)
    if "index.html" not in files:
        html_match = re.search(r"```html\s*\n(.*?)```", agent_result, re.DOTALL)
        if html_match:
            files["index.html"] = html_match.group(1).strip()

    if "style.css" not in files:
        css_match = re.search(r"```css\s*\n(.*?)```", agent_result, re.DOTALL)
        if css_match:
            files["style.css"] = css_match.group(1).strip()

    if "script.js" not in files and "main.js" not in files:
        js_match = re.search(r"```javascript\s*\n(.*?)```", agent_result, re.DOTALL)
        if js_match:
            files["script.js"] = js_match.group(1).strip()

    # 3. CSS-i HTML içinə yerləşdir (əgər ayrı fayldırsa)
    if "index.html" in files and "style.css" in files:
        css_link = '<link rel="stylesheet" href="style.css">'
        if css_link not in files["index.html"] and "</head>" in files["index.html"]:
            files["index.html"] = files["index.html"].replace(
                "</head>", f"  {css_link}\n</head>"
            )

    return files


def create_zip(files: dict[str, str]) -> bytes:
    """
    Fayl lüğətini zip bytes-a çevirir.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files.items():
            zf.writestr(filename, content)
    return buf.getvalue()


def deploy_to_netlify(files: dict[str, str], token: str, site_name: str = None) -> dict:
    """
    Faylları Netlify-a deploy edir.
    Returns: {"success": bool, "url": str, "site_id": str, "error": str}
    """
    if not token:
        return {
            "success": False,
            "url": "",
            "site_id": "",
            "error": "NETLIFY_TOKEN tapılmadı. .env faylına əlavə edin."
        }

    if not files or "index.html" not in files:
        return {
            "success": False,
            "url": "",
            "site_id": "",
            "error": "index.html faylı tapılmadı. Agent HTML yaratmadı."
        }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/zip"
    }

    zip_bytes = create_zip(files)

    try:
        # Yeni site yarat və deploy et
        resp = requests.post(
            f"{NETLIFY_API}/sites",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"name": site_name} if site_name else {},
            timeout=30
        )

        if resp.status_code not in (200, 201):
            # Site yaratmadan birbaşa deploy
            resp = requests.post(
                f"{NETLIFY_API}/sites",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )

        site_data = resp.json()
        site_id = site_data.get("id")

        if not site_id:
            # Mövcud site-a deploy
            deploy_resp = requests.post(
                f"{NETLIFY_API}/sites",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            site_id = deploy_resp.json().get("id", "")

        # Zip-i deploy et
        deploy_resp = requests.post(
            f"{NETLIFY_API}/sites/{site_id}/deploys",
            headers=headers,
            data=zip_bytes,
            timeout=120
        )

        if deploy_resp.status_code in (200, 201):
            deploy_data = deploy_resp.json()
            url = deploy_data.get("deploy_ssl_url") or deploy_data.get("deploy_url") or deploy_data.get("url", "")
            site_url = site_data.get("ssl_url") or site_data.get("url", url)
            return {
                "success": True,
                "url": site_url or url,
                "site_id": site_id,
                "error": ""
            }
        else:
            return {
                "success": False,
                "url": "",
                "site_id": site_id,
                "error": f"Deploy xətası ({deploy_resp.status_code}): {deploy_resp.text[:300]}"
            }

    except Exception as e:
        return {
            "success": False,
            "url": "",
            "site_id": "",
            "error": f"Şəbəkə xətası: {e}"
        }


def quick_website_deploy(idea: str, agent_result: str, token: str) -> dict:
    """
    Agent nəticəsindən sayt çıxarır və deploy edir.
    Əsas istifadə funksiyası.
    """
    files = extract_web_files(agent_result)

    if not files:
        return {
            "success": False,
            "url": "",
            "files": {},
            "error": "Agent-in nəticəsindən heç bir web fayl tapılmadı."
        }

    result = deploy_to_netlify(files, token)
    result["files"] = files
    return result
