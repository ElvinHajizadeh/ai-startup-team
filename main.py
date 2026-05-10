"""
AI Startup Komandası — Əsas Runner
====================================
Bütün 4 agenti ardıcıl işə salır, nəticələri toplayır
və outputs/ qovluğuna Markdown faylı kimi yazır.

İstifadə:
    python main.py
    python main.py --idea "Startup ideyam"
    python main.py --idea "..." --lang en
"""

import os
import sys
import argparse
import datetime
from pathlib import Path

# Windows UTF-8 fix — emoji ve Azerbaycan herflerinin dogru gosterilmesi ucun
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.rule import Rule
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from dotenv import load_dotenv
from agents import create_agents
from tasks import build_tasks
from file_extractor import extract_and_save_files
from search_tool import get_market_research

# ──────────────────────────────────────────────────────────────
load_dotenv()
console = Console() if RICH_AVAILABLE else None
OUTPUTS_DIR = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────────────────────
# Terminal UI helpers
# ──────────────────────────────────────────────────────────────
def print_header():
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            "[bold cyan]🚀 AI Startup Komandası (6 Agent)[/bold cyan]\n"
            "[dim]CEO • CTO • AI Eng • Frontend • UI/UX • Growth[/dim]\n"
            "[dim]Powered by Groq (Llama 3.3 70B)[/dim]",
            border_style="bright_cyan",
            padding=(1, 4),
        ))
        console.print()
    else:
        print("\n" + "=" * 60)
        print("  🚀 AI Startup Komandası")
        print("  CEO • CTO • AI Eng • Frontend • UI/UX • Growth")
        print("=" * 60 + "\n")


def print_agent_start(agent):
    if RICH_AVAILABLE:
        console.print(Rule(
            f"[bold]{agent.emoji} {agent.name} — {agent.role}[/bold]",
            style="bright_blue"
        ))
    else:
        print(f"\n{'─'*60}\n{agent.emoji} {agent.name} — {agent.role}\n{'─'*60}")


def print_agent_result(agent, result):
    preview = result[:500] + "..." if len(result) > 500 else result
    if RICH_AVAILABLE:
        console.print(f"\n[bold green]✅ {agent.name} tamamladı![/bold green]")
        console.print(Panel(
            preview,
            border_style="green",
            expand=False,
            padding=(0, 1),
        ))
    else:
        print(f"\n✅ {agent.name} tamamladı!\n{preview}\n")


def print_summary(agents, report_path):
    if RICH_AVAILABLE:
        table = Table(title="Komanda Nəticəsi", border_style="cyan")
        table.add_column("Rol", style="bold")
        table.add_column("Agent")
        table.add_column("Status", style="green")
        order = [
            ("ceo", "CEO"),
            ("cto", "CTO"),
            ("ai_engineer", "AI Eng"),
            ("frontend", "Frontend"),
            ("designer", "UI/UX"),
            ("growth", "Growth")
        ]
        for key, short in order:
            if key in agents:
                a = agents[key]
                table.add_row(a.role, a.name, "✅ Tamamlandı")
        console.print()
        console.print(table)
        console.print()
        console.print(Panel(
            f"[bold green]🎉 Komanda işini tamamladı![/bold green]\n\n"
            f"📄 Final hesabat: [cyan]{report_path}[/cyan]",
            border_style="green",
        ))
    else:
        print("\n" + "=" * 60)
        print("🎉 Komanda işini tamamladı!")
        print(f"📄 Final hesabat: {report_path}")
        print("=" * 60 + "\n")


# ──────────────────────────────────────────────────────────────
# Report writer
# ──────────────────────────────────────────────────────────────
def save_report(idea: str, results: dict, agents: dict) -> Path:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = OUTPUTS_DIR / f"startup_report_{timestamp}.md"

    lines = [
        "# 🚀 AI Startup Komandası — Final Report\n",
        f"**Startup İdeyası:** {idea}  \n",
        f"**Tarix:** {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}  \n",
        "\n---\n\n",
    ]

    for key in ["ceo", "cto", "ai_engineer", "frontend", "designer", "growth"]:
        if key in results:
            lines.append(results[key])
            lines.append("\n\n---\n\n")

    lines.append("## 📊 Komanda Xülasəsi\n\n")
    lines.append("| Rol | Agent | Status |\n|-----|-------|--------|\n")
    order = [
        ("ceo", "CEO"),
        ("cto", "CTO"),
        ("ai_engineer", "AI Eng"),
        ("frontend", "Frontend"),
        ("designer", "UI/UX"),
        ("growth", "Growth")
    ]
    for key, short in order:
        if key in agents:
            a = agents[key]
            lines.append(f"| {a.role} | {a.name} | ✅ Tamamlandı |\n")
    lines.append("\n*Bu sənəd AI Startup Komandası tərəfindən avtomatik yaradılmışdır.*\n")

    report_path.write_text("".join(lines), encoding="utf-8")
    return report_path


# ──────────────────────────────────────────────────────────────
# Ana funksiya
# ──────────────────────────────────────────────────────────────
def run_startup_team(startup_idea: str, language: str = "az"):
    print_header()

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your_groq_api_key_here":
        msg = (
            "❌ Xəta: GROQ_API_KEY tapılmadı!\n\n"
            "  1. .env faylını aç\n"
            "  2. GROQ_API_KEY= sətrinə key-ini əlavə et\n"
            "  3. Key al: https://console.groq.com/keys"
        )
        if RICH_AVAILABLE:
            console.print(Panel(msg, border_style="red"))
        else:
            print(msg)
        sys.exit(1)

    agents = create_agents(api_key=api_key, language=language)
    tasks = build_tasks(startup_idea)

    if RICH_AVAILABLE:
        console.print(f"[bold]💡 Startup İdeyası:[/bold] {startup_idea}")
        console.print(f"[dim]{len(agents)} agent • {len(tasks)} tapşırıq • Dil: {language}[/dim]\n")
    else:
        print(f"💡 {startup_idea}\n{len(agents)} agent • {len(tasks)} tapşırıq\n")

    if RICH_AVAILABLE:
        with Progress(SpinnerColumn(), TextColumn("[magenta]🌐 İnternetdə bazar və rəqiblər təhlil edilir...[/magenta]"), transient=True, console=console) as progress:
            progress.add_task("search", total=None)
            market_data = get_market_research(startup_idea)
    else:
        print("🌐 İnternetdə bazar və rəqiblər təhlil edilir...")
        market_data = get_market_research(startup_idea)

    def perform_generation_cycle(context_acc):
        res = {}
        for task in tasks:
            agent = agents[task.agent_key]
            print_agent_start(agent)
            
            safe_context = context_acc[-6000:] if len(context_acc) > 6000 else context_acc
            
            if RICH_AVAILABLE:
                with Progress(SpinnerColumn(), TextColumn(f"[cyan]{agent.name} analiz edir...[/cyan]"), TimeElapsedColumn(), console=console, transient=True) as progress:
                    progress.add_task("work", total=None)
                    output = agent.run(task.description, context=safe_context)
            else:
                print(f"⏳ {agent.name} analiz edir...")
                output = agent.run(task.description, context=safe_context)
                
            res[task.agent_key] = output
            context_acc += f"\n\n### {agent.role} nəticəsi:\n{output}"
            print_agent_result(agent, output)
            
            if task.agent_key != tasks[-1].agent_key:
                if RICH_AVAILABLE:
                    with Progress(SpinnerColumn(), TextColumn("[yellow]API limitini qorumaq üçün 15 saniyə gözlənilir...[/yellow]"), transient=True, console=console) as progress:
                        progress.add_task("wait", total=None)
                        import time
                        time.sleep(15)
                else:
                    import time
                    print("⏳ API limitini qorumaq üçün 15 saniyə gözlənilir...")
                    time.sleep(15)
                    
        rep_path = save_report(startup_idea, res, agents)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        proj_dir = OUTPUTS_DIR / "projects" / f"startup_{timestamp}"
        created = []
        
        for key, r in res.items():
            fls = extract_and_save_files(r, proj_dir)
            created.extend(fls)
            
        if created:
            if RICH_AVAILABLE:
                console.print(Panel(
                    f"[bold green]📂 Auto-Coding Tamamlandı! {len(created)} fayl yaradıldı![/bold green]\nLayihə Qovluğu: [cyan]{proj_dir}[/cyan]",
                    border_style="green"
                ))
            else:
                print(f"\n📂 Auto-Coding Tamamlandı! {len(created)} fayl yaradıldı! \nLayihə Qovluğu: {proj_dir}\n")
                
        print_summary(agents, rep_path)
        return context_acc, rep_path

    context_accumulator = f"--- İNTERNET AXTARIŞI VƏ BAZAR MƏLUMATLARI ---\n{market_data}\n--------------------------------------------\n"
    
    # İlk dəfə komandanı işə salırıq
    chat_context, report_path = perform_generation_cycle(context_accumulator)
    
    # --- İNTERAKTİV SUAL-CAVAB (CHAT) HİSSƏSİ ---
    from agents import call_groq
    
    while True:
        if RICH_AVAILABLE:
            from rich.prompt import Prompt
            console.print()
            user_question = Prompt.ask("[bold cyan]💬 Komandaya əlavə sualınız var? (Məs: 'hamınız işləyin' və ya çıxmaq üçün 'q')[/bold cyan]")
        else:
            user_question = input("\n💬 Komandaya əlavə sualınız var? (Məs: 'hamınız işləyin' və ya çıxmaq üçün 'q'): ")
            
        hq = user_question.strip().lower()
        if not hq or hq in ['q', 'quit', 'exit', 'cix']:
            if RICH_AVAILABLE:
                console.print("[bold green]Təşəkkürlər! Uğurlar arzulayırıq. İş dayandırıldı.[/bold green]")
            else:
                print("Təşəkkürlər! Uğurlar arzulayırıq. İş dayandırıldı.")
            break
            
        if "haminiz isley" in hq or "hamınız işləy" in hq or "haminiz baslayin" in hq:
            if RICH_AVAILABLE:
                console.print("[bold yellow]🔄 Bütün komanda yeni qərarlar əsasında layihəni yenidən qurur...[/bold yellow]")
            else:
                print("\n🔄 Bütün komanda yeni qərarlar əsasında layihəni yenidən qurur...")
            
            chat_context += "\n--- DİQQƏT: YENİDƏN İŞƏ SALINMA (RE-BUILD) ---\nİstifadəçi 'hamınız işləyin' əmrini verdi. Yuxarıdakı bütün söhbət tarixçəsini, edilən dəyişiklikləri və qərarları nəzərə alaraq layihəni sıfırdan YENİDƏN yaradın.\n"
            chat_context, report_path = perform_generation_cycle(chat_context)
            continue
            
        # API limitini (413) asmamaq üçün konteksti son 20000 simvolla məhdudlaşdırırıq
        safe_context = chat_context[-20000:] if len(chat_context) > 20000 else chat_context
        
        chat_prompt = (
            "Aşağıdakı qərarlara və komanda hesabatına əsasən istifadəçinin sualına cavab ver.\n"
            f"KONTEKST:\n{safe_context}\n\n"
            f"İSTİFADƏÇİNİN YENİ SUALI: {user_question}"
        )
        
        system_prompt = (
            "Sən bu 6 nəfərlik AI startup komandasının orkestratorusan. "
            "İstifadəçinin verdiyi sualı oxu, onun komandadakı hansı mütəxəssisə (CEO, CTO, AI Eng, Frontend, UI/UX, yoxsa Growth) aid olduğunu analiz et. "
            "Daha sonra BİRBAŞA HƏMİN ŞƏXSİN ROLUNA GİRƏRƏK cavab ver. "
            "Məsələn, marketinqlə bağlı sualdırsa, 'Mən Fərid (Growth Marketer) olaraq deyirəm ki...' kimi başla və sırf öz işindən danış. "
            "Digər agentlərin işinə qarışma və çox real, sərt, peşəkar bir mütəxəssis kimi cavab ver."
        )
        
        if RICH_AVAILABLE:
            with Progress(SpinnerColumn(), TextColumn("[blue]Müvafiq agent cavab hazırlayır...[/blue]"), transient=True, console=console) as progress:
                progress.add_task("chat", total=None)
                try:
                    answer = call_groq(api_key, system_prompt, chat_prompt)
                except Exception as e:
                    answer = f"Xəta baş verdi: {e}"
        else:
            print("⏳ Müvafiq agent cavab hazırlayır...")
            try:
                answer = call_groq(api_key, system_prompt, chat_prompt)
            except Exception as e:
                answer = f"Xəta baş verdi: {e}"
                
        if RICH_AVAILABLE:
            console.print(Panel(answer, border_style="blue", title="🤖 Komandanın Cavabı"))
        else:
            print(f"\n🤖 Komandanın Cavabı:\n{answer}\n")
            
        # Söhbətin tarixçəsini saxla
        chat_context += f"\n\nİstifadəçi Sualı: {user_question}\nSənin Cavabın: {answer}"

    return None, report_path


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🚀 AI Startup Komandası — 6 agent, 1 AI/SaaS biznes plan"
    )
    parser.add_argument("--idea", type=str, default=None,
                        help="Analiz ediləcək startup ideyası")
    parser.add_argument("--lang", type=str, choices=["az", "en"], default=None,
                        help="Cavab dili: az (Azərbaycan) / en (English)")
    args = parser.parse_args()

    idea = args.idea
    if not idea:
        env_idea = os.getenv("STARTUP_IDEA")
        if env_idea and env_idea.strip() and env_idea != "Azərbaycan kiçik bizneslər üçün AI brending və uyğunluq platformu" and env_idea != "Öz startup ideyası":
            idea = env_idea
        else:
            if RICH_AVAILABLE:
                from rich.prompt import Prompt
                console.print()
                idea = Prompt.ask("[bold cyan]💡 Zəhmət olmasa, startup ideyanızı ətraflı yazın[/bold cyan]")
            else:
                idea = input("\n💡 Zəhmət olmasa, startup ideyanızı ətraflı yazın: ")
                
    if not idea or not idea.strip():
        if RICH_AVAILABLE:
            console.print("[bold red]❌ İdeya daxil edilmədi. Proses dayandırıldı.[/bold red]")
        else:
            print("❌ İdeya daxil edilmədi. Proses dayandırıldı.")
        sys.exit(1)
    lang = args.lang or os.getenv("RESPONSE_LANGUAGE", "az")

    run_startup_team(startup_idea=idea, language=lang)
