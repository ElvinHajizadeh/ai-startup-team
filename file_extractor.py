import os
import re
from pathlib import Path

def extract_and_save_files(text: str, base_dir: Path) -> list:
    """
    Markdown mətnindəki <file path="...">...</file> etiketlərini axtarır,
    faylların tərkibini çıxarır və real qovluqda saxlayır.
    Yaradılmış faylların siyahısını qaytarır.
    """
    # Create the base directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Regex to find <file path="..."> content </file>
    # It also handles optional markdown code blocks inside the file tag
    pattern = re.compile(r'<file\s+path="([^"]+)">\s*(?:```[\w]*\n)?(.*?)(?:\n```\s*)?</file>', re.DOTALL)
    
    matches = pattern.findall(text)
    created_files = []
    
    for file_path_str, content in matches:
        # Prevent path traversal attacks (e.g., path="../../etc/passwd")
        clean_path = file_path_str.lstrip('./\\')
        if '..' in clean_path:
            continue
            
        full_path = base_dir / clean_path
        
        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
            
        created_files.append(str(full_path))
        
    return created_files
