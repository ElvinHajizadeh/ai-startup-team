"""
debate_mode.py — Addım 8: İki agent arasında debat rejimi
CEO vs CTO və ya istənilən 2 agent arasında mübahisə orkestrasyonu.
"""
from agents import call_groq


def run_debate(
    api_key: str,
    topic: str,
    agent_a_name: str,
    agent_a_role: str,
    agent_a_system: str,
    agent_b_name: str,
    agent_b_role: str,
    agent_b_system: str,
    rounds: int = 3
) -> list[dict]:
    """
    İki agent arasında debat keçirir.
    Returns: [{"speaker": name, "role": role, "content": text}, ...]
    """
    history = []
    context = f"MÜZAKİRƏ MÖVZUSU: {topic}\n\n"

    for round_num in range(1, rounds + 1):
        for agent_name, agent_role, agent_system, opponent_name in [
            (agent_a_name, agent_a_role, agent_a_system, agent_b_name),
            (agent_b_name, agent_b_role, agent_b_system, agent_a_name),
        ]:
            prompt = (
                f"{context}"
                f"Sən {agent_name} ({agent_role}) olaraq {opponent_name}-ə cavab verirsən.\n"
                f"Bu, {round_num}-ci raunddu ({rounds} raunddan). "
                "Öz baxışını güclü dəlillərlə müdafiə et, lakin qarşı tərəfin gətirib çıxardığı "
                "HƏQİQİ nöqtələri qəbul etməkdən qorxma. Konkret ol, emosional yox, faktlara əsaslan. "
                "Cavabını maksimum 200 sözdə ver."
            )

            try:
                reply = call_groq(api_key, agent_system, prompt)
            except Exception as e:
                reply = f"[Xəta: {e}]"

            history.append({
                "speaker": agent_name,
                "role": agent_role,
                "round": round_num,
                "content": reply
            })
            context += f"\n\n{agent_name}: {reply}\n"

    # Final qiymətləndirmə
    verdict_prompt = (
        f"Aşağıdakı debatı oxu və qərəzsiz bir mühəkkim kimi qiymətləndir:\n\n{context}\n\n"
        "Kimin arqumentləri daha güclü idi? Ən yaxşı 3 nöqtəni qeyd et və yekun tövsiyəni yaz."
    )
    verdict_system = "Sən qərəzsiz startup məsləhətçisisən. Yalnız fakta əsaslanan qiymətləndirmə apar."

    try:
        verdict = call_groq(api_key, verdict_system, verdict_prompt)
    except Exception as e:
        verdict = f"[Qiymətləndirmə xətası: {e}]"

    history.append({
        "speaker": "⚖️ Hakim",
        "role": "Qərəzsiz Qiymətləndirici",
        "round": 0,
        "content": verdict
    })

    return history


def get_debate_preset(preset: str, agents_map: dict, startup_idea: str) -> dict:
    """
    Hazır debat ssenariləri qaytarır.
    preset: "ceo_vs_cto" | "cto_vs_ai" | "growth_vs_ceo"
    """
    presets = {
        "ceo_vs_cto": {
            "topic": f"'{startup_idea}' layihəsi üçün hansı texniki yanaşma daha düzgündür?",
            "agent_a_key": "ceo",
            "agent_b_key": "cto",
        },
        "cto_vs_ai": {
            "topic": f"'{startup_idea}' üçün AI modeli seçimi: Öz modelimizi trainləyək yoxsa hazır API istifadə edək?",
            "agent_a_key": "cto",
            "agent_b_key": "ai_engineer",
        },
        "growth_vs_ceo": {
            "topic": f"'{startup_idea}' üçün ilk 3 ayın büdcəsini marketinqə yatıraq yoxsa məhsul inkişafına?",
            "agent_a_key": "growth",
            "agent_b_key": "ceo",
        },
    }
    return presets.get(preset, presets["ceo_vs_cto"])
