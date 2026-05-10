"""
image_generator.py — Addım 7: Marketinq promptlarından şəkil yaradır
Primary: Hugging Face free Inference API (Stable Diffusion XL)
Optional: OpenAI DALL-E 3 (OPENAI_API_KEY varsa)
"""
import os
import requests
from pathlib import Path
import datetime
import re


HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
OPENAI_API_URL = "https://api.openai.com/v1/images/generations"


def extract_image_prompts(marketing_result: str) -> list[str]:
    """
    Marketoloğun nəticəsindən Image Prompt-ları çıxarır.
    """
    prompts = []

    # marketing faylları içindəki promptları axtarır
    # Tipik format: midjourney_prompts.txt içindəki "1. ...", "2. ..." sıralar
    sections = re.split(r"\n\d+\.\s+", marketing_result)
    for s in sections[1:]:  # İlk split əvvəl boş olur
        line = s.strip().split("\n")[0]
        if len(line) > 30 and any(w in line.lower() for w in ["photo", "image", "illustration", "design", "logo", "poster", "mockup", "scene", "background", "portrait"]):
            prompts.append(line[:400])  # Max 400 simvol

    # Alternativ: "Image Prompt" başlığından sonrakı hissə
    if not prompts:
        match = re.search(r"[Ii]mage [Pp]rompt[s]?[:\n]+(.+?)(\n\n|\Z)", marketing_result, re.DOTALL)
        if match:
            raw = match.group(1).strip()
            prompts = [p.strip() for p in re.split(r"\n\d+[\.\)]\s*", raw) if len(p.strip()) > 20]

    return prompts[:3]  # Max 3 şəkil


def generate_image_hf(prompt: str, hf_token: str = None) -> bytes | None:
    """
    HuggingFace Inference API ilə şəkil yaradır (pulsuz, amma yavaş).
    """
    headers = {}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"

    try:
        resp = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": prompt, "parameters": {"width": 768, "height": 512}},
            timeout=60
        )
        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
            return resp.content
        return None
    except Exception:
        return None


def generate_image_openai(prompt: str, openai_key: str) -> str | None:
    """
    OpenAI DALL-E 3 ilə şəkil yaradır. URL qaytarır.
    """
    try:
        resp = requests.post(
            OPENAI_API_URL,
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
            json={"model": "dall-e-3", "prompt": prompt, "n": 1, "size": "1024x1024"},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json()["data"][0]["url"]
        return None
    except Exception:
        return None


def generate_and_save_images(prompts: list[str], output_dir: Path, openai_key: str = None, hf_token: str = None) -> list[str]:
    """
    Verilmiş promptlar üçün şəkillər yaradıb diska saxlayır.
    Returns: Saxlanan şəkil path-lərinin siyahısı
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    for i, prompt in enumerate(prompts, 1):
        filepath = output_dir / f"marketing_image_{i}.png"

        # OpenAI varsa, onu istifadə et
        if openai_key:
            url = generate_image_openai(prompt, openai_key)
            if url:
                img_resp = requests.get(url, timeout=30)
                if img_resp.status_code == 200:
                    filepath.write_bytes(img_resp.content)
                    saved.append(str(filepath))
                    continue

        # HuggingFace fallback
        img_bytes = generate_image_hf(prompt, hf_token)
        if img_bytes:
            filepath.write_bytes(img_bytes)
            saved.append(str(filepath))

    return saved
