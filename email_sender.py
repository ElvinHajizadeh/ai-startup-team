"""
email_sender.py — Addım 9: Gmail SMTP vasitəsilə email göndərir
Requires: GMAIL_USER and GMAIL_APP_PASSWORD in .env
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_startup_email(
    to_email: str,
    subject: str,
    body: str,
    gmail_user: str = None,
    gmail_password: str = None,
) -> dict:
    """
    Gmail SMTP vasitəsilə email göndərir.
    Returns: {"success": bool, "error": str}
    """
    user = gmail_user or os.getenv("GMAIL_USER", "")
    password = gmail_password or os.getenv("GMAIL_APP_PASSWORD", "")

    if not user or not password:
        return {
            "success": False,
            "error": "GMAIL_USER və GMAIL_APP_PASSWORD .env faylında mövcud deyil."
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = user
        msg["To"] = to_email

        # Plain text versiyası
        text_part = MIMEText(body, "plain", "utf-8")

        # HTML versiyası (daha gözəl görünüş)
        html_body = body.replace("\n", "<br>").replace("##", "<h3>").replace("#", "<h4>")
        html_content = f"""
        <html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:20px;">
        <div style="background:#0f0f1a;color:#fff;padding:16px;border-radius:8px;margin-bottom:20px;">
            <h2 style="margin:0;">🚀 AI Startup Team Report</h2>
        </div>
        <div style="color:#222;line-height:1.7;">{html_body}</div>
        <hr style="margin-top:30px;">
        <p style="color:#999;font-size:12px;">Bu email AI Startup Team sistemi tərəfindən avtomatik göndərilmişdir.</p>
        </body></html>
        """
        html_part = MIMEText(html_content, "html", "utf-8")

        msg.attach(text_part)
        msg.attach(html_part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(user, password)
            server.sendmail(user, to_email, msg.as_string())

        return {"success": True, "error": ""}

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "error": "Gmail autentifikasiya xətası. App Password düzgündürmü? (myaccount.google.com/apppasswords)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def build_investor_email(startup_idea: str, ceo_result: str, startup_name: str = "Startup") -> str:
    """CEO nəticəsinə əsasən investor emaili üçün template yaradır."""
    summary = ceo_result[:800] if len(ceo_result) > 800 else ceo_result
    return f"""Hörmətli İnvestor,

{startup_name} komandası olaraq sizinlə bir fürsəti bölüşmək istərdik.

Layihəmiz: {startup_idea}

Qısa Xülasə:
{summary}

Bu layihə haqqında ətraflı məlumat almaq üçün cavab verməyinizi gözləyirik.

Hörmətlə,
{startup_name} Komandası
(AI Startup Team sistemi tərəfindən hazırlanmışdır)
"""
