import streamlit as st
import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

from agents import create_agents, call_groq
from tasks import build_tasks
from search_tool import get_market_research
from file_extractor import extract_and_save_files
from memory_manager import save_session, list_sessions, load_session
from pdf_exporter import export_to_pdf
from github_pusher import push_to_github
from image_generator import extract_image_prompts, generate_and_save_images
from debate_mode import run_debate, get_debate_preset
from email_sender import send_startup_email, build_investor_email

load_dotenv()

def get_secret(key: str, default: str = "") -> str:
    """Streamlit Cloud Secrets → .env → default sırasıyla oxuyur."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

api_key      = get_secret("GROQ_API_KEY")
hf_token     = get_secret("HF_TOKEN")
github_token = get_secret("GITHUB_TOKEN")
gmail_user   = get_secret("GMAIL_USER")
gmail_pass   = get_secret("GMAIL_APP_PASSWORD")

st.set_page_config(page_title="AI Startup Team", page_icon="🚀", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0d0d1a; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; font-weight: 600; }
div[data-testid="metric-container"] { background: #111827; border-radius:10px; padding:10px; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────
defaults = {
    "chat_history": [], "context_accumulator": "",
    "results": {}, "agents_map": {},
    "created_files_count": 0, "project_dir": "",
    "startup_idea_current": "", "debate_log": [],
    "generated_images": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚀 AI Startup Team")
    st.markdown("---")

    startup_idea = st.text_area("💡 Startup İdeyanız:", height=130,
                                 placeholder="Məsələn: Flutter ilə AI-əsaslı həkim tapma tətbiqi...")

    # 🎤 Səs girişi (Addım 11)
    with st.expander("🎤 Səs ilə giriş (Beta)"):
        audio_val = st.audio_input("Mikrofona danışın:")
        if audio_val is not None:
            try:
                from voice_input import transcribe_audio_bytes
                with st.spinner("Səs tanınır..."):
                    text = transcribe_audio_bytes(audio_val.read(), language="az-AZ")
                if text:
                    startup_idea = text
                    st.success(f"Tanındı: *{text}*")
                else:
                    st.warning("Söz tanınmadı. Yenidən cəhd edin.")
            except Exception as e:
                st.error(f"Xəta: {e}")

    start_btn = st.button("🔥 Komandanı İşə Sal", type="primary", use_container_width=True)
    st.markdown("---")

    if st.session_state.results:
        st.success("✅ Komanda aktivdir")
        c1, c2 = st.columns(2)
        c1.metric("🤖 Agent", len(st.session_state.results))
        c2.metric("📂 Fayl",  st.session_state.created_files_count)

        # PDF yüklə (Addım 5)
        if st.button("📄 PDF Yüklə", use_container_width=True):
            try:
                pdf_bytes = export_to_pdf(
                    st.session_state.startup_idea_current,
                    st.session_state.results,
                    st.session_state.agents_map
                )
                st.download_button("⬇️ PDF-i endir", data=pdf_bytes,
                                   file_name="startup_report.pdf", mime="application/pdf",
                                   use_container_width=True)
            except Exception as e:
                st.error(f"PDF xətası: {e}")

        # GitHub Push (Addım 6)
        with st.expander("🐙 GitHub-a Push"):
            repo = st.text_input("Repo (user/repo-name):", placeholder="elvin/my-startup")
            if st.button("🚀 Push Et", use_container_width=True):
                if repo and st.session_state.project_dir:
                    with st.spinner("GitHub-a göndərilir..."):
                        res = push_to_github(st.session_state.project_dir, repo, github_token)
                    if res["success"]:
                        st.success(f"✅ {res['files_pushed']} fayl push edildi → {res['url']}")
                    else:
                        st.error(f"Xəta: {res.get('error','')}")
                else:
                    st.warning("Repo adını və ya layihə qovluğunu yoxlayın.")

        # Email Göndər (Addım 9)
        with st.expander("📧 Email Göndər"):
            to_email = st.text_input("Alıcı:", placeholder="investor@email.com")
            subj = st.text_input("Mövzu:", value="Startup Layihəsi Haqqında Məlumat")
            body_default = build_investor_email(
                st.session_state.startup_idea_current,
                st.session_state.results.get("ceo", ""),
                "Startup"
            )
            email_body = st.text_area("Mətn:", value=body_default, height=150)
            if st.button("📤 Göndər", use_container_width=True):
                with st.spinner("Göndərilir..."):
                    res = send_startup_email(to_email, subj, email_body, gmail_user, gmail_pass)
                if res["success"]:
                    st.success("✅ Email göndərildi!")
                else:
                    st.error(f"Xəta: {res['error']}")

        st.markdown("---")
        if st.button("🗑️ Sıfırla", use_container_width=True):
            for k in defaults: st.session_state[k] = defaults[k]
            st.rerun()

    # Köhnə layihələr
    st.markdown("### 📚 Köhnə Layihələr")
    sessions = list_sessions()
    for sess in sessions[:6]:
        if st.button(sess["display_name"], key=f"s_{sess['path']}", use_container_width=True):
            data = load_session(sess["path"])
            st.session_state.startup_idea_current = data.get("startup_idea","")
            st.session_state.results = data.get("results",{})
            st.session_state.chat_history = data.get("chat_history",[])
            st.session_state.context_accumulator = data.get("context_snippet","")
            if st.session_state.results and not st.session_state.agents_map:
                st.session_state.agents_map = create_agents(api_key=api_key, language="az")
            st.rerun()


# ── Generation ────────────────────────────────────────────────
def run_generation_cycle(idea: str, is_rebuild: bool = False):
    if not api_key:
        st.error("❌ GROQ_API_KEY tapılmadı!")
        return

    st.session_state.agents_map = create_agents(api_key=api_key, language="az")
    tasks = build_tasks(idea)
    status_box = st.status("🤖 Komanda İşləyir...", expanded=True)

    with status_box:
        if not is_rebuild:
            st.write("🌐 Bazar araşdırması aparılır...")
            market_data = get_market_research(idea)
            st.session_state.context_accumulator = f"--- BAZAR MƏLUMATLARI ---\n{market_data}\n---\n"
        else:
            st.write("🔄 Yenidən quruluş başlayır...")
            st.session_state.context_accumulator += "\n--- RE-BUILD ---\nYuxarıdakı qərarları nəzərə alaraq YENİDƏN yarat.\n"

        results = {}
        bar = st.progress(0, text="Agentlər işə başlayır...")

        for i, task in enumerate(tasks):
            agent = st.session_state.agents_map[task.agent_key]
            st.write(f"⏳ **{agent.emoji} {agent.name}** işləyir...")
            safe_ctx = st.session_state.context_accumulator[-6000:]

            try:
                res = agent.run(task.description, context=safe_ctx)
            except Exception as e:
                res = f"⚠️ XƏTA: {e}"

            results[task.agent_key] = res
            st.session_state.context_accumulator += f"\n\n### {agent.role}:\n{res}"
            bar.progress((i+1)/len(tasks), text=f"{agent.name} ✓")

            if i != len(tasks)-1:
                import time; st.write("*(15 san. gözləmə...)*"); time.sleep(15)

        st.write("📂 Kod faylları yaradılır...")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        proj_dir = Path("outputs") / "projects" / f"startup_{ts}"
        created = []
        for key, r in results.items():
            created.extend(extract_and_save_files(r, proj_dir))

        st.session_state.results = results
        st.session_state.project_dir = str(proj_dir.absolute())
        st.session_state.created_files_count = len(created)
        st.session_state.startup_idea_current = idea

        st.write("💾 Saxlanılır...")
        save_session(idea, results, st.session_state.chat_history, st.session_state.context_accumulator)

    status_box.update(label="✅ Tamamlandı!", state="complete", expanded=False)


# ── Trigger ───────────────────────────────────────────────────
if start_btn:
    if not startup_idea.strip():
        st.sidebar.error("İdeyası daxil edin!")
    else:
        st.session_state.chat_history = []
        st.session_state.debate_log = []
        st.session_state.generated_images = []
        run_generation_cycle(startup_idea.strip())
        st.rerun()


# ── Main Content ──────────────────────────────────────────────
if st.session_state.results:
    idea_short = st.session_state.startup_idea_current[:55]
    st.title(f"🚀 {idea_short}{'...' if len(st.session_state.startup_idea_current)>55 else ''}")
    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────────────
    main_tabs = st.tabs(["📑 Hesabat", "💬 Chat", "🖼️ Şəkillər", "🥊 Debat", "📊 İnvestor"])

    # ──── Tab 1: Hesabat ──────────────────────────────────────
    with main_tabs[0]:
        agent_keys = list(st.session_state.results.keys())
        labels = []
        for k in agent_keys:
            a = st.session_state.agents_map.get(k)
            labels.append(f"{a.emoji} {a.name}" if a else k)

        sub_tabs = st.tabs(labels)
        for i, key in enumerate(agent_keys):
            with sub_tabs[i]:
                a = st.session_state.agents_map.get(key)
                if a:
                    st.caption(f"**{a.role}** — {a.goal}")
                    st.markdown("---")
                st.markdown(st.session_state.results[key])

    # ──── Tab 2: Chat ─────────────────────────────────────────
    with main_tabs[1]:
        st.caption("💡 `hamınız işləyin` yazaraq komandanı yenidən işlədə bilərsən")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_q = st.chat_input("Sualını yaz...")
        if user_q:
            st.session_state.chat_history.append({"role":"user","content":user_q})
            hq = user_q.lower()

            if "haminiz isley" in hq or "hamınız işləy" in hq or "haminiz baslayin" in hq:
                st.session_state.chat_history.append({"role":"assistant","content":"🔄 **RE-BUILD başlayır...**"})
                run_generation_cycle(st.session_state.startup_idea_current, is_rebuild=True)
                st.rerun()
            else:
                with st.chat_message("assistant"):
                    with st.spinner("Cavab hazırlanır..."):
                        safe_ctx = st.session_state.context_accumulator[-20000:]
                        prompt = f"KONTEKST:\n{safe_ctx}\n\nSUAL: {user_q}"
                        sys_p = "Sən 6 nəfərlik AI startup komandasının orkestratorusan. Sualın hansı sahəyə aid olduğunu müəyyən et və həmin agentin rolundan cavab ver."
                        try:
                            ans = call_groq(api_key, sys_p, prompt)
                        except Exception as e:
                            ans = f"Xəta: {e}"
                    st.markdown(ans)
                st.session_state.chat_history.append({"role":"assistant","content":ans})
                st.session_state.context_accumulator += f"\n\nİstifadəçi: {user_q}\nAgent: {ans}"
                save_session(st.session_state.startup_idea_current, st.session_state.results,
                             st.session_state.chat_history, st.session_state.context_accumulator)
                st.rerun()

    # ──── Tab 3: Şəkillər (Addım 7) ──────────────────────────
    with main_tabs[2]:
        st.subheader("🖼️ Marketinq Şəkilləri")
        growth_result = st.session_state.results.get("growth", "")
        prompts = extract_image_prompts(growth_result)

        if prompts:
            st.write(f"**{len(prompts)} image prompt tapıldı:**")
            for i, p in enumerate(prompts, 1):
                st.code(p, language=None)

            if st.button("🎨 Şəkilləri Yarat", type="primary"):
                with st.spinner("Şəkillər yaradılır (HuggingFace)... Bu bir neçə dəqiqə çəkə bilər."):
                    img_dir = Path("outputs") / "images" / f"imgs_{datetime.datetime.now().strftime('%H%M%S')}"
                    # Yalnız HuggingFace istifadə edilir (pulsuz)
                    paths = generate_and_save_images(prompts, img_dir, openai_key=None, hf_token=hf_token or None)
                    st.session_state.generated_images = paths

            if st.session_state.generated_images:
                cols = st.columns(min(len(st.session_state.generated_images), 3))
                for i, img_path in enumerate(st.session_state.generated_images):
                    if Path(img_path).exists():
                        cols[i % 3].image(img_path, caption=f"Şəkil {i+1}", use_container_width=True)
        else:
            st.info("Marketoloğun nəticəsindən image prompt tapılmadı. Əvvəlcə komandanı işə salın.")

    # ──── Tab 4: Debat (Addım 8) ──────────────────────────────
    with main_tabs[3]:
        st.subheader("🥊 Agent Debatı")
        st.caption("2 agent arasında real mübahisə — ən güclü arqument qalır.")

        preset = st.selectbox("Debat ssenarisi seç:", [
            "ceo_vs_cto", "cto_vs_ai", "growth_vs_ceo"
        ], format_func=lambda x: {
            "ceo_vs_cto": "🎯 CEO vs CTO (Texniki yanaşma)",
            "cto_vs_ai": "🤖 CTO vs AI Engineer (Model seçimi)",
            "growth_vs_ceo": "📈 Growth vs CEO (Büdcə bölüşdürməsi)"
        }[x])

        rounds = st.slider("Raund sayı:", 1, 4, 2)

        if st.button("🥊 Debatı Başlat", type="primary"):
            config = get_debate_preset(preset, st.session_state.agents_map,
                                       st.session_state.startup_idea_current)
            a_key = config["agent_a_key"]
            b_key = config["agent_b_key"]
            ag_a = st.session_state.agents_map.get(a_key)
            ag_b = st.session_state.agents_map.get(b_key)

            if ag_a and ag_b:
                with st.spinner(f"🥊 {ag_a.name} vs {ag_b.name} — debat davam edir..."):
                    log = run_debate(
                        api_key,
                        topic=config["topic"],
                        agent_a_name=ag_a.name, agent_a_role=ag_a.role, agent_a_system=ag_a.system_prompt,
                        agent_b_name=ag_b.name, agent_b_role=ag_b.role, agent_b_system=ag_b.system_prompt,
                        rounds=rounds
                    )
                st.session_state.debate_log = log

        if st.session_state.debate_log:
            for entry in st.session_state.debate_log:
                icon = "⚖️" if entry["speaker"] == "⚖️ Hakim" else "💬"
                rnd = f"Raund {entry['round']}" if entry.get("round", 0) > 0 else "Yekun Qiymətləndirmə"
                with st.expander(f"{icon} **{entry['speaker']}** — {rnd}", expanded=(entry.get("round",0)==0)):
                    st.markdown(entry["content"])

    # ──── Tab 5: İnvestor Dashboard (Addım 10) ───────────────
    with main_tabs[4]:
        st.subheader("📊 İnvestor Dashboard")
        ceo = st.session_state.results.get("ceo","")
        cto = st.session_state.results.get("cto","")
        growth = st.session_state.results.get("growth","")

        col1, col2, col3 = st.columns(3)
        col1.metric("🎯 İdeya", st.session_state.startup_idea_current[:25]+"...")
        col2.metric("🤖 Agent", len(st.session_state.results))
        col3.metric("📂 Kod Faylı", st.session_state.created_files_count)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🎯 CEO Vizyon Xülasəsi")
            st.markdown(ceo[:1200] + "..." if len(ceo) > 1200 else ceo)
        with c2:
            st.markdown("### 📈 Marketinq & Böyümə Planı")
            st.markdown(growth[:1200] + "..." if len(growth) > 1200 else growth)

        st.markdown("---")
        st.markdown("### 🧠 CTO Texniki Arxitektura")
        st.markdown(cto[:1500] + "..." if len(cto) > 1500 else cto)


else:
    st.markdown("""
    <div style="text-align:center;padding:80px 20px;">
        <h1>🚀 AI Startup Team</h1>
        <p style="font-size:1.1rem;color:#888;max-width:600px;margin:0 auto;">
            6 peşəkar AI agent bir yerdə çalışır.<br><br>
            <b>← Sol paneldən</b> ideyanızı yazıb komandanı işə salın.
        </p>
        <br><br>
        <p style="color:#555;font-size:0.95rem;">
            🌐 Bazar araşdırması &nbsp;|&nbsp; 💻 Avtomatik kod &nbsp;|&nbsp; 🖼️ Şəkil yaratma<br>
            🥊 Agent debatı &nbsp;|&nbsp; 📄 PDF export &nbsp;|&nbsp; 📧 Email göndərmə
        </p>
    </div>
    """, unsafe_allow_html=True)
