# 🚀 AI Startup Komandası

> **4 AI agent** — CEO, CTO, Marketing, Product Manager — startup ideyandan tam biznes planı yaradır.

## Necə İşləyir?

```
Sən bir ideya verirsən
       ↓
🎯 CEO Agent → Strategiya sənədi
       ↓
🔧 CTO Agent → Texniki arxitektura planı
       ↓
📢 Marketing Agent → GTM strategiyası
       ↓
📋 Product Agent → PRD + Roadmap
       ↓
📄 outputs/startup_report_*.md
```

---

## Quraşdırma

### 1. API Key alın (Pulsuzdur)
→ https://aistudio.google.com/app/apikey

### 2. `.env` faylını redaktə edin
```
GEMINI_API_KEY=buraya_key_yapistir
STARTUP_IDEA=Azərbaycan fermerləri üçün AI marketpleys
RESPONSE_LANGUAGE=az
```

### 3. İşə salın
```bash
cd ai-startup-team
python main.py
```

---

## Əlavə Seçimlər

```bash
# Öz ideyanı CLI-dan ver
python main.py --idea "Bakıda çatdırılma xidməti üçün AI platforma"

# İngilis dilində
python main.py --idea "My startup idea" --lang en

# Hər ikisi
python main.py --idea "Startup ideyası" --lang az
```

---

## Nəticə

`outputs/` qovluğunda Markdown formatında tam biznes planı yaranır:
- CEO strategiya sənədi
- CTO texniki roadmap
- Marketing GTM planı
- PRD + 3 aylıq sprint planı

---

## Fayl Strukturu

```
ai-startup-team/
├── main.py        ← Əsas runner
├── agents.py      ← 4 agent tərifi
├── tasks.py       ← Tapşırıq şablonları
├── .env           ← API key (git-ə commit etmə!)
├── requirements.txt
└── outputs/       ← Nəticə faylları
```
