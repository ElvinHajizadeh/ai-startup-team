"""
sandbox_runner.py — Addım 12: Yaradılan Python kodunu təhlükəsiz sandbox-da işlədir
Yalnız outputs/sandbox/ qovluğunda işləyir. Timeout 30 san.
Path traversal hücumlarına qarşı qorunub.
"""
import subprocess
import tempfile
import os
import re
from pathlib import Path

SANDBOX_DIR = Path("outputs/sandbox")
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
TIMEOUT_SECONDS = 30

BLOCKED_PATTERNS = [
    r"import\s+os",
    r"import\s+sys",
    r"import\s+subprocess",
    r"import\s+shutil",
    r"__import__",
    r"open\s*\(",
    r"exec\s*\(",
    r"eval\s*\(",
    r"\.\.\/",           # Path traversal
    r"rm\s+-rf",
    r"del\s+",
]


def is_safe_code(code: str) -> tuple[bool, str]:
    """
    Kodu təhlükəsizlik baxımından yoxlayır.
    Returns: (is_safe, reason)
    """
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Qadağan olan əməliyyat aşkarlandı: `{pattern}`"
    return True, ""


def run_python_code(code: str) -> dict:
    """
    Verilen Python kodunu təhlükəsiz sandbox-da işlədir.
    Returns: {"success": bool, "stdout": str, "stderr": str, "timed_out": bool}
    """
    safe, reason = is_safe_code(code)
    if not safe:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"🚫 Təhlükəsizlik xətası: {reason}",
            "timed_out": False
        }

    # Müvəqqəti fayla yaz
    tmp_path = SANDBOX_DIR / "_sandbox_run.py"
    tmp_path.write_text(code, encoding="utf-8")

    try:
        result = subprocess.run(
            ["python", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            cwd=str(SANDBOX_DIR),  # Working dir = sandbox only
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[:3000],
            "stderr": result.stderr[:1000],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"⏱️ Timeout: Kod {TIMEOUT_SECONDS} saniyə ərzində tamamlanmadı.",
            "timed_out": True,
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"İcra xətası: {e}",
            "timed_out": False,
        }
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


def extract_python_from_result(agent_result: str) -> list[str]:
    """
    Agent nəticəsindən Python kod bloklarını çıxarır.
    Returns: list of code strings
    """
    blocks = re.findall(r"```python\s*\n(.*?)```", agent_result, re.DOTALL)
    # XML fayllar içindəki Python-u da yoxla
    xml_blocks = re.findall(r'<file path="[^"]*\.py">\s*\n(.*?)</file>', agent_result, re.DOTALL)
    return blocks + xml_blocks
