"""
memory_manager.py — Startup layihə yaddaşı (Persistent Session Manager)
Hər tamamlanan generation cycle diska JSON formatında yazılır.
Köhnə layihələr siyahısı gətirilir və yüklənir.
"""
import json
import datetime
from pathlib import Path

MEMORY_DIR = Path("outputs/sessions")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def save_session(startup_idea: str, results: dict, chat_history: list, context: str) -> str:
    """
    Mevcut session-u JSON-a yazır.
    Returns: Saxlanan faylın path-i
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in startup_idea[:40]).strip()
    filename = MEMORY_DIR / f"{timestamp}_{safe_name}.json"
    
    data = {
        "timestamp": timestamp,
        "startup_idea": startup_idea,
        "results": results,
        "chat_history": chat_history,
        "context_snippet": context[-3000:],  # Son 3000 simvolu saxla
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    return str(filename)


def list_sessions() -> list:
    """
    Saxlanılmış bütün session-ların siyahısını qaytarır.
    Returns: [{"name": ..., "timestamp": ..., "path": ...}, ...]
    """
    sessions = []
    
    for file in sorted(MEMORY_DIR.glob("*.json"), reverse=True):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            sessions.append({
                "display_name": f"📁 {data.get('startup_idea', 'Naməlum')[:50]}...",
                "timestamp": data.get("timestamp", ""),
                "path": str(file),
            })
        except Exception:
            continue
            
    return sessions


def load_session(path: str) -> dict:
    """
    Verilmiş path-dəki session-u yükləyir.
    Returns: {startup_idea, results, chat_history, context_snippet}
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
