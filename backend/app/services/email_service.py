"""
Service d'envoi d'emails transactionnels via Resend.
Gère les templates HTML et l'envoi pour : bienvenue, vérification d'email, réinitialisation de mot de passe.
"""
import logging
import resend
from app.core.config import settings

logger = logging.getLogger(__name__)


def _init_resend():
    """Initialize the Resend API key."""
    resend.api_key = settings.RESEND_API_KEY


def _base_template(content: str) -> str:
    """Wrap email content in a responsive, branded HTML layout."""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArtisanGestion</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f7; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f7;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width: 560px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 32px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;">ArtisanGestion</h1>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            {content}
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 24px 40px; background-color: #f9fafb; border-top: 1px solid #e5e7eb; text-align: center;">
                            <p style="margin: 0; font-size: 13px; color: #9ca3af; line-height: 1.5;">
                                © 2024 ArtisanGestion — Gestion simplifiée pour artisans &amp; PME
                            </p>
                            <p style="margin: 8px 0 0 0; font-size: 12px; color: #d1d5db;">
                                Vous recevez cet email car vous avez un compte ArtisanGestion.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


def _button(url: str, text: str) -> str:
    """Generate a styled CTA button for emails."""
    return f"""<table role="presentation" cellpadding="0" cellspacing="0" style="margin: 28px auto;">
        <tr>
            <td style="border-radius: 8px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
                <a href="{url}" target="_blank" style="display: inline-block; padding: 14px 32px; color: #ffffff; text-decoration: none; font-size: 15px; font-weight: 600; letter-spacing: 0.3px;">{text}</a>
            </td>
        </tr>
    </table>"""


async def send_welcome_email(to: str, prenom: str) -> bool:
    """
    Envoie un email de bienvenue après la création du compte.
    """
    _init_resend()

    content = f"""
        <h2 style="margin: 0 0 16px 0; color: #111827; font-size: 20px; font-weight: 600;">Bienvenue, {prenom} ! 🎉</h2>
        <p style="margin: 0 0 16px 0; color: #4b5563; font-size: 15px; line-height: 1.6;">
            Votre compte ArtisanGestion a été créé avec succès. Nous sommes ravis de vous compter parmi nous !
        </p>
        <p style="margin: 0 0 8px 0; color: #4b5563; font-size: 15px; line-height: 1.6;">
            Voici comment démarrer en quelques étapes :
        </p>
        <table role="presentation" cellpadding="0" cellspacing="0" style="margin: 16px 0 24px 0; width: 100%;">
            <tr>
                <td style="padding: 12px 16px; background-color: #eff6ff; border-radius: 8px; border-left: 4px solid #3b82f6;">
                    <p style="margin: 0 0 8px 0; color: #1e40af; font-size: 14px; font-weight: 600;">1. Configurez votre entreprise</p>
                    <p style="margin: 0 0 8px 0; color: #1e40af; font-size: 14px; font-weight: 600;">2. Ajoutez vos premiers clients</p>
                    <p style="margin: 0; color: #1e40af; font-size: 14px; font-weight: 600;">3. Créez votre premier devis ou facture</p>
                </td>
            </tr>
        </table>
        {_button(settings.FRONTEND_URL + '/app', 'Accéder à mon espace')}
        <p style="margin: 0; color: #9ca3af; font-size: 13px; text-align: center;">
            Si vous avez des questions, n'hésitez pas à nous contacter.
        </p>
    """

    try:
        resend.Emails.send({
            "from": f"ArtisanGestion <{settings.EMAIL_FROM}>",
            "to": [to],
            "subject": f"Bienvenue sur ArtisanGestion, {prenom} ! 🎉",
            "html": _base_template(content),
        })
        logger.info(f"Welcome email sent to {to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to}: {e}")
        return False


async def send_verification_email(to: str, prenom: str, token: str) -> bool:
    """
    Envoie un email de vérification d'adresse email avec un lien de confirmation.
    """
    _init_resend()

    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    content = f"""
        <h2 style="margin: 0 0 16px 0; color: #111827; font-size: 20px; font-weight: 600;">Vérifiez votre adresse email</h2>
        <p style="margin: 0 0 16px 0; color: #4b5563; font-size: 15px; line-height: 1.6;">
            Bonjour {prenom},
        </p>
        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 15px; line-height: 1.6;">
            Pour finaliser votre inscription et sécuriser votre compte, veuillez confirmer votre adresse email en cliquant sur le bouton ci-dessous.
        </p>
        {_button(verification_url, 'Vérifier mon adresse email')}
        <p style="margin: 0 0 8px 0; color: #9ca3af; font-size: 13px; text-align: center;">
            Ce lien est valide pendant {settings.EMAIL_VERIFICATION_EXPIRE_HOURS} heures.
        </p>
        <p style="margin: 16px 0 0 0; color: #9ca3af; font-size: 12px; text-align: center; word-break: break-all;">
            Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br>
            <a href="{verification_url}" style="color: #3b82f6;">{verification_url}</a>
        </p>
    """

    try:
        resend.Emails.send({
            "from": f"ArtisanGestion <{settings.EMAIL_FROM}>",
            "to": [to],
            "subject": "Confirmez votre adresse email — ArtisanGestion",
            "html": _base_template(content),
        })
        logger.info(f"Verification email sent to {to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {to}: {e}")
        return False


async def send_password_reset_email(to: str, prenom: str, token: str) -> bool:
    """
    Envoie un email de réinitialisation de mot de passe avec un lien sécurisé.
    """
    _init_resend()

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    content = f"""
        <h2 style="margin: 0 0 16px 0; color: #111827; font-size: 20px; font-weight: 600;">Réinitialisation de votre mot de passe</h2>
        <p style="margin: 0 0 16px 0; color: #4b5563; font-size: 15px; line-height: 1.6;">
            Bonjour {prenom},
        </p>
        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 15px; line-height: 1.6;">
            Vous avez demandé la réinitialisation de votre mot de passe. Cliquez sur le bouton ci-dessous pour choisir un nouveau mot de passe.
        </p>
        {_button(reset_url, 'Réinitialiser mon mot de passe')}
        <p style="margin: 0 0 8px 0; color: #9ca3af; font-size: 13px; text-align: center;">
            Ce lien est valide pendant {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.
        </p>
        <table role="presentation" cellpadding="0" cellspacing="0" style="margin: 24px 0 0 0; width: 100%;">
            <tr>
                <td style="padding: 12px 16px; background-color: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                    <p style="margin: 0; color: #92400e; font-size: 13px; line-height: 1.5;">
                        ⚠️ Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email. Votre mot de passe restera inchangé.
                    </p>
                </td>
            </tr>
        </table>
        <p style="margin: 16px 0 0 0; color: #9ca3af; font-size: 12px; text-align: center; word-break: break-all;">
            Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br>
            <a href="{reset_url}" style="color: #3b82f6;">{reset_url}</a>
        </p>
    """

    try:
        resend.Emails.send({
            "from": f"ArtisanGestion <{settings.EMAIL_FROM}>",
            "to": [to],
            "subject": "Réinitialisation de votre mot de passe — ArtisanGestion",
            "html": _base_template(content),
        })
        logger.info(f"Password reset email sent to {to}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to}: {e}")
        return False
