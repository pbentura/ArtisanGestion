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
<body style="margin: 0; padding: 0; background-color: #f4f4f7; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f7; padding: 40px 20px;">
        <tr>
            <td align="center">
                <!-- Main Container -->
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
                    
                    <!-- Header with Gradient and Logo -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); padding: 40px 40px; text-align: center;">
                            <img src="{settings.FRONTEND_URL}/logo.svg" alt="Logo ArtisanGestion" style="display: block; margin: 0 auto 16px auto; width: 64px; height: 64px;" />
                            <span style="display: block; margin: 0 auto; max-width: 100%; height: auto; font-size: 28px; color: #ffffff; font-weight: bold; letter-spacing: -0.5px;">ArtisanGestion</span>
                        </td>
                    </tr>
                    
                    <!-- Body Content -->
                    <tr>
                        <td style="padding: 48px 40px 40px 40px;">
                            {content}
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 32px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0 0 12px 0; color: #64748b; font-size: 14px; line-height: 1.5;">
                                Si vous avez des questions ou besoin d'aide, n'hésitez pas à répondre directement à cet email.
                            </p>
                            <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                &copy; 2026 ArtisanGestion. Tous droits réservés.<br>
                                Paris, France
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
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 32px 0;">
        <tr>
            <td align="center">
                <table role="presentation" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="border-radius: 8px; background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">
                            <a href="{url}" target="_blank" style="display: inline-block; padding: 16px 36px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; letter-spacing: 0.3px;">{text}</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>"""


async def send_welcome_email(to: str, prenom: str) -> bool:
    """
    Envoie un email de bienvenue après la création du compte.
    """
    _init_resend()

    content = f"""
        <h1 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; text-align: center;">Bienvenue, {prenom} ! 🎉</h1>
        
        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6; text-align: center;">
            Votre compte <strong>ArtisanGestion</strong> a été créé avec succès. Nous sommes ravis de vous compter parmi nous et de vous accompagner dans la gestion de votre activité.
        </p>
        
        <!-- Steps Box -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 32px 0; background-color: #eff6ff; border-radius: 12px; border-left: 4px solid #3b82f6;">
            <tr>
                <td style="padding: 24px;">
                    <h3 style="margin: 0 0 16px 0; color: #1e40af; font-size: 16px; font-weight: 600;">Voici comment démarrer :</h3>
                    <p style="margin: 0 0 12px 0; color: #1e40af; font-size: 15px;">
                        <strong style="display: inline-block; background: #3b82f6; color: white; width: 24px; height: 24px; text-align: center; border-radius: 50%; line-height: 24px; font-size: 13px; margin-right: 8px;">1</strong> Configurez les informations de votre entreprise
                    </p>
                    <p style="margin: 0 0 12px 0; color: #1e40af; font-size: 15px;">
                        <strong style="display: inline-block; background: #3b82f6; color: white; width: 24px; height: 24px; text-align: center; border-radius: 50%; line-height: 24px; font-size: 13px; margin-right: 8px;">2</strong> Ajoutez vos premiers clients
                    </p>
                    <p style="margin: 0; color: #1e40af; font-size: 15px;">
                        <strong style="display: inline-block; background: #3b82f6; color: white; width: 24px; height: 24px; text-align: center; border-radius: 50%; line-height: 24px; font-size: 13px; margin-right: 8px;">3</strong> Créez votre premier devis ou facture
                    </p>
                </td>
            </tr>
        </table>

        {_button(settings.FRONTEND_URL + '/app', 'Accéder à mon espace')}
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
        <div style="width: 64px; height: 64px; background-color: #eff6ff; border-radius: 50%; margin: 0 auto 24px auto; text-align: center; line-height: 64px;">
            <span style="font-size: 28px;">✉️</span>
        </div>

        <h1 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; text-align: center;">Vérifiez votre adresse email</h1>
        
        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6; text-align: center;">
            Bonjour <strong>{prenom}</strong>,<br><br>
            Bienvenue sur ArtisanGestion ! Pour activer votre compte et sécuriser votre accès, veuillez cliquer sur le bouton ci-dessous pour confirmer votre adresse email.
        </p>
        
        {_button(verification_url, 'Confirmer mon email')}

        <p style="margin: 0; color: #6b7280; font-size: 14px; text-align: center; line-height: 1.5;">
            Si vous n'avez pas créé de compte ArtisanGestion, vous pouvez ignorer cet email en toute sécurité.
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
        <div style="width: 64px; height: 64px; background-color: #fef2f2; border-radius: 50%; margin: 0 auto 24px auto; text-align: center; line-height: 64px;">
            <span style="font-size: 28px;">🔒</span>
        </div>

        <h1 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; text-align: center;">Réinitialisation du mot de passe</h1>
        
        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6; text-align: center;">
            Bonjour {prenom},<br><br>
            Nous avons reçu une demande de réinitialisation de votre mot de passe pour votre compte ArtisanGestion. Ce lien est valable pendant {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.
        </p>
        
        {_button(reset_url, 'Créer un nouveau mot de passe')}

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 32px 0; background-color: #fef2f2; border-radius: 12px; border-left: 4px solid #ef4444;">
            <tr>
                <td style="padding: 16px;">
                    <p style="margin: 0; color: #b91c1c; font-size: 14px; line-height: 1.5;">
                        Si vous n'êtes pas à l'origine de cette demande, veuillez ignorer cet email. Votre mot de passe restera inchangé.
                    </p>
                </td>
            </tr>
        </table>
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


async def send_transactional_document(
    to: str,
    subject: str,
    message: str,
    artisan_name: str,
    artisan_email: str,
    pdf_bytes: bytes,
    filename: str,
    payment_url: str = None,
) -> bool:
    """
    Envoie un document transactionnel (devis, facture, rapport) par email à un client.
    L'expéditeur est générique, mais le Reply-To est l'email de l'artisan.
    Si payment_url est fourni, ajoute un bouton de paiement en ligne.
    """
    _init_resend()

    payment_button = ""
    if payment_url:
        payment_button = f"""
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 32px 0;">
            <tr>
                <td align="center">
                    <table role="presentation" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="border-radius: 8px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">
                                <a href="{payment_url}" target="_blank" style="display: inline-block; padding: 16px 36px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; letter-spacing: 0.3px;">💳 Payer cette facture en ligne</a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td align="center" style="padding-top: 12px;">
                    <p style="margin: 0; color: #6b7280; font-size: 12px;">Paiement sécurisé par carte bancaire via Stripe</p>
                </td>
            </tr>
        </table>
        """

    content = f"""
        <h1 style="margin: 0 0 20px 0; color: #111827; font-size: 20px; font-weight: 700;">Nouveau document de {artisan_name}</h1>
        
        <div style="margin: 0 0 24px 0; color: #4b5563; font-size: 15px; line-height: 1.6; white-space: pre-line;">
            {message}
        </div>
        
        {payment_button}

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 32px 0; background-color: #eff6ff; border-radius: 12px; border-left: 4px solid #3b82f6;">
            <tr>
                <td style="padding: 16px;">
                    <p style="margin: 0; color: #1e40af; font-size: 14px; line-height: 1.5;">
                        <strong>Note :</strong> Ce document vous a été envoyé par <strong>{artisan_name}</strong> via ArtisanGestion. Vous pouvez répondre directement à cet email pour le contacter.
                    </p>
                </td>
            </tr>
        </table>
    """
    # Extraire le domaine de l'email configuré
    try:
        domain = settings.EMAIL_FROM.split('@')[1]
    except Exception:
        domain = "artisangestion.com"

    sender_email = f"document@{domain}"
    try:
        resend.Emails.send({
            "from": f"{artisan_name} (via artisangestion) <{sender_email}>",
            "to": [to],
            "reply_to": artisan_email,
            "subject": subject,
            "html": _base_template(content),
            "attachments": [
                {
                    "filename": filename,
                    "content": list(pdf_bytes)
                }
            ]
        })
        logger.info(f"Transactional document {filename} sent to {to} from {artisan_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send transactional document {filename} to {to}: {e}")
        return False

