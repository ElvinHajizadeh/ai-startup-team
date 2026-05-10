"""
AI Startup Komandası — Tapşırıqlar Modulu
==========================================
Hər agent üçün ardıcıl 6 mərhələli AI/SaaS startup tapşırıq şablonları.
"""

from dataclasses import dataclass

@dataclass
class Task:
    """Bir agent tapşırığını təmsil edir."""
    agent_key: str
    title: str
    description: str
    expected_output: str

def build_tasks(startup_idea: str) -> list:
    """
    Verilən startup ideyası üçün 6 agentin tapşırıqlarını yaradır.
    """
    return [
        Task(
            agent_key="ceo",
            title="Sərt İdeya Təhlili və Vizyonun Qurulması",
            description=f"""
STARTUP İDEYASI:
{startup_idea}

Tapşırıq:
1. Sən sadəcə danışan CEO yox, İCRA EDƏN CEO-san. Bu ideyanı sənə veriləcək REAL İNTERNET MƏLUMATLARINA (bazar və rəqiblər) əsaslanaraq qlobal VC baxış bucağından SƏRT şəkildə təhlil et.
2. İnternetdən tapılan mövcud rəqiblərin adlarını xüsusi vurğulayaraq investisiya potensialı, qazanc (Monetization) modeli və əsas KPI-ları qərarlaşdır.
3. Biznes planı və pitch deck məzmununu formalaşdır.

ÇOX VACİB QAYDA (AUTO-CODING):
Sən aşağıdakı materialları MÜTLƏQ real fayllar olaraq XML formatında yaratmalısan:
<file path="business/pitch_deck_məzmunu.md">
Pitch deck slaydlarının məzmunu...
</file>
<file path="business/maliyyə_modeli.md">
Maliyyə planı və xərclər...
</file>
""",
            expected_output="CEO Strategiya və Vizyon Sənədi (Sərt təhlil, biznes modeli, komandaya göstərişlər)",
        ),

        Task(
            agent_key="cto",
            title="Real Production Arxitekturası və Əsas Kod Bazası",
            description=f"""
STARTUP İDEYASI:
{startup_idea}

Tapşırıq:
1. Sən sadəcə nəzəriyyə danışan yox, KOD YAZAN CTO-san. CEO-nun strateji qərarlarını nəzərə alaraq, startup-ın tələb etdiyi İSTƏNİLƏN TEXNİKİ SAHƏDƏ (Web Backend, Mobile App - Flutter/Swift, Desktop App, AI/ML, Embedded Systems və s.) real istehsalata (production) çıxacaq sistemin arxitekturasını qur.
2. Həmin texniki sahəyə uyğun olaraq proyektin tam qovluq (folder) strukturunu yaz.
3. Layihənin tələb etdiyi əsas texnologiya növünə uyğun olaraq (məs: Mobile App üçün main.dart / ContentView.swift, Backend üçün əsas server kodu, Desktop üçün UI kodları) ən kritik KOD BAZASINI (Core Codebase) tam şəkildə yaz.
4. Əgər lazımdırsa, məlumat bazası şemalarını və mühit/deployment konfiqurasiyalarını (Docker, requirements.txt, pubspec.yaml və s.) kod olaraq təqdim et.
DİQQƏT: Ümumi sözlər istəmirəm! Seçdiyin sahə fərq etməz, sırf COPY-PASTE edib işlədə biləcəyim real kodlar və konfiqurasiyalar ver.

ÇOX VACİB QAYDA (AUTO-CODING):
Hər hansı bir kod və ya fayl yazarkən onu MÜTLƏQ aşağıdakı XML formatında yazmalısan. Əgər bunu etməsən, sistem çökəcək:
<file path="qovluq_adi/fayl_adi.ext">
Sənin kodun bura gələcək...
</file>
Məsələn:
<file path="backend/main.py">
from fastapi import FastAPI
...
</file>
""",
            expected_output="CTO Real Kod Bazası (Qovluq strukturu, Backend Kodu, DB Şeması, Docker)",
        ),

        Task(
            agent_key="ai_engineer",
            title="AI Workflows, RAG və LLM Memarlığı",
            description=f"""
STARTUP İDEYASI:
{startup_idea}

Tapşırıq:
1. Sən sadəcə nəzəriyyəçi yox, KOD YAZAN AI Mühəndisisən. CTO-nun seçdiyi texniki sahəyə (Web, Mobile və s.) uyğun AI "beynini" və model arxitekturasını qur.
2. Ən yaxşı modelləri (GPT-4, Claude, Gemini) və limitləri (Rate limits) təyin et.
3. RAG (Retrieval-Augmented Generation), Vector DB inteqrasiyasını və Prompt Mühəndisliyini (Prompt Engineering) kod olaraq yaz.
4. AI-ın "Hallucination" (yalan danışma) ehtimalını sıfıra endirəcək təhlükəsizlik kodlarını əlavə et.

ÇOX VACİB QAYDA (AUTO-CODING):
Yaratdığın bütün AI məntiqlərini, RAG qurulumunu və əsas System Prompt-larını MÜTLƏQ aşağıdakı XML formatında fayllara çevir:
<file path="ai_core/rag_pipeline.py">
from langchain import ...
</file>
<file path="ai_core/system_prompts.txt">
Sənin əsas promptların...
</file>
""",
            expected_output="AI & LLM Mühəndisliyi Planı (Modellər, RAG, Memory, Hallucination qorunması)",
        ),

        Task(
            agent_key="frontend",
            title="Web App / Dashboard Kodları və UI Tətbiqi",
            description=f"""
STARTUP İDEYASI:
{startup_idea}

Tapşırıq:
1. Sən də sadəcə danışan yox, YAZAN Frontend Mühəndisisən. AI Mühəndisinin və CTO-nun qurduğu sistemin Frontend (React, Next.js, Vue və ya HTML/CSS/JS) strukturunu qur.
2. Əsas səhifənin (Landing Page) və ya istifadəçi panelinin (Dashboard) tam və işlək UI kodunu (komponentlərini) Markdown kod blokunda yaz.
3. API ilə necə əlaqə quracağını (fetch/axios məntiqi) real kodla göstər.
4. Gözəl və müasir (TailwindCSS/CSS) dizaynla birgə istifadəçi təcrübəsini təmin edən kodları ver.

ÇOX VACİB QAYDA (AUTO-CODING):
Frontend fayllarını (HTML, CSS, JS, JSX) yazarkən onları MÜTLƏQ aşağıdakı XML formatında təqdim et:
<file path="qovluq_adi/fayl_adi.ext">
Sənin kodun bura gələcək...
</file>
Məsələn:
<file path="frontend/src/App.jsx">
import React from 'react';
...
</file>
""",
            expected_output="Frontend İşlək Kodları (UI Komponentləri, API inteqrasiyası, Tailwind/CSS kodları)",
        ),

        Task(
            agent_key="designer",
            title="SaaS UX Psixologiyası və User Flow",
            description=f"""
STARTUP İDEYASI:
{startup_idea}

Tapşırıq:
1. Sən sadəcə rəng seçən yox, MƏHSULU DİZAYN EDƏN UI/UX ekspertisən. İstifadəçinin bu məhsulla necə tanış olacağını (User Journey) və Onboarding axınını qur.
2. SaaS-da pul ödəməyə inandıran "Conversion UX" taktikalarını tətbiq et.
3. Məhsulun marka kimliyini (Brand Identity), rəng palitrasını (HEX kodları ilə) və tipoqrafiyasını hazırla.
4. Komponentlərin arxitekturasını dizayn sistemi kimi qur.

ÇOX VACİB QAYDA (AUTO-CODING):
Dizayn qaydalarını və UI detallarını MÜTLƏQ fayllara çevir:
<file path="design/theme.css">
:root {{ --primary-color: #ff0000; --font: 'Inter', sans-serif; }}
</file>
<file path="design/user_journey_flow.md">
İstifadəçi səyahəti bura gələcək...
</file>
""",
            expected_output="UI/UX və Brending Strategiyası (User Journey, Onboarding, SaaS UX)",
        ),

        Task(
            agent_key="growth",
            title="Tam Paket Marketinq Materialları (Video, Şəkil, Mətn və Satış)",
            description=f"""
STARTUP İDEYASI:
{startup_idea}

Tapşırıq:
1. Sən tam təchizatlı (Full-Stack) Marketinq Menecerisən. Sənə veriləcək REAL İNTERNET MƏLUMATLARINA (Rəqiblər və trendlər) baxaraq fərqlilik yaradan hazır materiallar yarat. Mənə marketinq "nəzəriyyəsi" lazım deyil!
2. Rəqiblərdən daha yaxşı olan və fərqlənən Instagram Reels / TikTok / YouTube Shorts üçün ən azı 2 ədəd detallı VİDEO SSENARİSİ (hansı saniyədə ekranda nə görünəcək, səs effekti nə olacaq, danışıq mətni nədir) yaz.
3. Paylaşılacaq postlar üçün Süni İntellekt (Midjourney/DALL-E) şəkil yaradılması məqsədilə 3 ədəd mükəmməl İNGİLİS DİLİNDƏ "Image Prompt" yaz.
4. Bütün platformalar (LinkedIn, Instagram, TikTok) üçün cəlbedici post mətnlərini və hashtag-ləri yaz.
5. Potensial B2B müştərilərə və ya investorlara göndəriləcək tam təsirli 'Cold Email' (soyuq satış məktubu) şablonu hazırla.

ÇOX VACİB QAYDA (AUTO-CODING):
Sən yaratdığın bütün bu real mətnləri, ssenariləri və email şablonlarını MÜTLƏQ aşağıdakı XML formatında fayllara çevirməlisən. Hər bir material üçün ayrı fayl yarat:
<file path="marketing/tiktok_ssenari_1.md">
Sənin videonun ssenarisi bura gələcək...
</file>

<file path="marketing/midjourney_prompts.txt">
Şəkil promptları bura gələcək...
</file>
""",
            expected_output="Hazır Marketinq Paketi (Video Ssenarilər, Şəkil Promptları, Email və Post Mətnləri - Fayl formatında)",
        ),
    ]
