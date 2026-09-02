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


def _envoyer(to: str, subject: str, content: str) -> bool:
    """Envoi d'un email déjà mis en page. Un échec est journalisé, jamais levé."""
    try:
        resend.Emails.send({
            "from": f"ArtisanGestion <{settings.EMAIL_FROM}>",
            "to": [to],
            "subject": subject,
            "html": _base_template(content),
        })
        logger.info("Email « %s » envoyé à %s", subject, to)
        return True
    except Exception as e:
        logger.error("Échec de l'envoi de « %s » à %s : %s", subject, to, e)
        return False


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


async def send_support_email(
    user_name: str,
    user_email: str,
    subject: str,
    message: str,
    category: str = "Question générale",
    societe_name: str = None,
) -> bool:
    """
    Envoie un message de support ou une question formulée par un utilisateur vers l'adresse support.
    """
    _init_resend()

    societe_html = f"""
    <tr>
        <td style="padding: 6px 0; color: #64748b; font-size: 14px; width: 120px;"><strong>Société :</strong></td>
        <td style="padding: 6px 0; color: #1e293b; font-size: 14px; font-weight: 500;">{societe_name}</td>
    </tr>
    """ if societe_name else ""

    content = f"""
        <div style="width: 56px; height: 56px; background-color: #eff6ff; border-radius: 50%; margin: 0 auto 20px auto; text-align: center; line-height: 56px;">
            <span style="font-size: 26px;">💬</span>
        </div>

        <h1 style="margin: 0 0 8px 0; color: #111827; font-size: 22px; font-weight: 700; text-align: center;">Nouveau message de support</h1>
        <p style="margin: 0 0 24px 0; color: #64748b; font-size: 14px; text-align: center;">Reçu depuis l'espace paramètres de l'application</p>
        
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px 0; background-color: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; padding: 18px 20px;">
            <tr>
                <td style="padding: 6px 0; color: #64748b; font-size: 14px; width: 120px;"><strong>Expéditeur :</strong></td>
                <td style="padding: 6px 0; color: #1e293b; font-size: 14px; font-weight: 600;">{user_name}</td>
            </tr>
            <tr>
                <td style="padding: 6px 0; color: #64748b; font-size: 14px;"><strong>Email :</strong></td>
                <td style="padding: 6px 0; color: #2563eb; font-size: 14px; font-weight: 500;">
                    <a href="mailto:{user_email}" style="color: #2563eb; text-decoration: none;">{user_email}</a>
                </td>
            </tr>
            {societe_html}
            <tr>
                <td style="padding: 6px 0; color: #64748b; font-size: 14px;"><strong>Catégorie :</strong></td>
                <td style="padding: 6px 0;">
                    <span style="display: inline-block; background-color: #dbeafe; color: #1e40af; padding: 3px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600;">
                        {category}
                    </span>
                </td>
            </tr>
            <tr>
                <td style="padding: 6px 0; color: #64748b; font-size: 14px;"><strong>Sujet :</strong></td>
                <td style="padding: 6px 0; color: #0f172a; font-size: 14px; font-weight: 600;">{subject}</td>
            </tr>
        </table>

        <div style="margin: 0 0 24px 0; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <h3 style="margin: 0 0 12px 0; font-size: 14px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700;">Message transmis :</h3>
            <div style="color: #1e293b; font-size: 15px; line-height: 1.6; white-space: pre-wrap; font-family: inherit;">{message}</div>
        </div>

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px 0; background-color: #eff6ff; border-radius: 8px; border-left: 4px solid #3b82f6;">
            <tr>
                <td style="padding: 14px 18px;">
                    <p style="margin: 0; color: #1e40af; font-size: 13px; line-height: 1.5;">
                        💡 <strong>Action rapide :</strong> Cliquez simplement sur <strong>« Répondre »</strong> dans votre messagerie pour écrire directement à {user_email}.
                    </p>
                </td>
            </tr>
        </table>
    """

    support_destination = getattr(settings, "SUPPORT_EMAIL", "pinhasbent@gmail.com")

    try:
        resend.Emails.send({
            "from": f"Support ArtisanGestion <{settings.EMAIL_FROM}>",
            "to": [support_destination],
            "reply_to": user_email,
            "subject": f"[Support ArtisanGestion - {category}] {subject}",
            "html": _base_template(content),
        })
        logger.info(f"Support message from {user_email} successfully sent to {support_destination}")
        return True
    except Exception as e:
        logger.error(f"Failed to send support email from {user_email}: {e}")
        return False




async def send_signature_request(
    to: str,
    client_nom: str,
    artisan_nom: str,
    artisan_email: str,
    numero_devis: str,
    montant_ttc: str,
    objet: str,
    token: str,
    jours_validite: int,
) -> bool:
    """
    Envoie au client le lien lui permettant de signer un devis à distance.
    Le Reply-To est l'email de l'artisan pour que les réponses lui parviennent.
    """
    _init_resend()

    url_signature = f"{settings.FRONTEND_URL}/signer/{token}"
    ligne_objet = f"<br><em>{objet}</em>" if objet else ""

    content = f"""
        <div style="width: 64px; height: 64px; background-color: #eff6ff; border-radius: 50%; margin: 0 auto 24px auto; text-align: center; line-height: 64px;">
            <span style="font-size: 28px;">✍️</span>
        </div>

        <h1 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; text-align: center;">Votre devis est prêt à être signé</h1>

        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6; text-align: center;">
            Bonjour {client_nom},<br><br>
            {artisan_nom} vous a transmis le devis <strong>{numero_devis}</strong> pour un montant de
            <strong>{montant_ttc} € TTC</strong>.{ligne_objet}
        </p>

        <p style="margin: 0 0 8px 0; color: #4b5563; font-size: 16px; line-height: 1.6; text-align: center;">
            Vous pouvez le consulter et le signer en ligne, depuis votre ordinateur ou votre téléphone.
        </p>

        {_button(url_signature, 'Consulter et signer le devis')}

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 32px 0; background-color: #f9fafb; border-radius: 12px; border-left: 4px solid #3b82f6;">
            <tr>
                <td style="padding: 16px;">
                    <p style="margin: 0; color: #4b5563; font-size: 14px; line-height: 1.5;">
                        Ce lien est personnel et valable {jours_validite} jours. Votre signature vaut
                        acceptation du devis. Pour toute question, répondez simplement à cet email.
                    </p>
                </td>
            </tr>
        </table>
    """

    try:
        resend.Emails.send({
            "from": f"{artisan_nom} via ArtisanGestion <{settings.EMAIL_FROM}>",
            "to": [to],
            "reply_to": artisan_email or settings.SUPPORT_EMAIL,
            "subject": f"Devis {numero_devis} à signer — {artisan_nom}",
            "html": _base_template(content),
        })
        logger.info("Signature request sent to %s for devis %s", to, numero_devis)
        return True
    except Exception as e:
        logger.error("Failed to send signature request to %s: %s", to, e)
        return False


async def send_signature_confirmation(
    to: str,
    artisan_nom: str,
    client_nom: str,
    numero_devis: str,
    signataire: str,
) -> bool:
    """Prévient l'artisan que son devis vient d'être signé."""
    _init_resend()

    content = f"""
        <div style="width: 64px; height: 64px; background-color: #ecfdf5; border-radius: 50%; margin: 0 auto 24px auto; text-align: center; line-height: 64px;">
            <span style="font-size: 28px;">✅</span>
        </div>

        <h1 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; text-align: center;">Devis signé</h1>

        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6; text-align: center;">
            Bonne nouvelle {artisan_nom},<br><br>
            Le devis <strong>{numero_devis}</strong> destiné à <strong>{client_nom}</strong> vient d'être
            signé par <strong>{signataire}</strong>.
        </p>

        {_button(f"{settings.FRONTEND_URL}/app/devis", 'Voir le devis signé')}

        <p style="margin: 0 0 32px 0; color: #6b7280; font-size: 14px; line-height: 1.6; text-align: center;">
            Vous pouvez maintenant le transformer en facture en un clic.
        </p>
    """

    try:
        resend.Emails.send({
            "from": f"ArtisanGestion <{settings.EMAIL_FROM}>",
            "to": [to],
            "subject": f"Devis {numero_devis} signé par {signataire}",
            "html": _base_template(content),
        })
        return True
    except Exception as e:
        logger.error("Failed to send signature confirmation to %s: %s", to, e)
        return False


async def send_relance_facture(
    to: str,
    client_nom: str,
    artisan_nom: str,
    artisan_email: str,
    numero_facture: str,
    montant_ttc: str,
    date_echeance: str,
    jours_de_retard: int,
    niveau: int,
    payment_url: str = None,
) -> bool:
    """
    Relance pour une facture impayée.

    Le ton se durcit progressivement selon le niveau, sans jamais devenir
    agressif : la première relance suppose un oubli, la dernière rappelle les
    pénalités légales.
    """
    _init_resend()

    if niveau <= 1:
        emoji, fond = "🔔", "#eff6ff"
        titre = "Petit rappel"
        intro = (
            f"Sauf erreur de notre part, la facture <strong>{numero_facture}</strong> "
            f"d'un montant de <strong>{montant_ttc} € TTC</strong>, échue le {date_echeance}, "
            f"n'a pas encore été réglée."
        )
        note = "Il s'agit peut-être d'un simple oubli. Si le règlement a déjà été effectué, merci d'ignorer ce message."
        couleur_note = "#3b82f6"
        objet = f"Rappel — facture {numero_facture}"
    elif niveau == 2:
        emoji, fond = "⏰", "#fffbeb"
        titre = "Facture toujours en attente de règlement"
        intro = (
            f"La facture <strong>{numero_facture}</strong> d'un montant de "
            f"<strong>{montant_ttc} € TTC</strong> est échue depuis le {date_echeance}, "
            f"soit <strong>{jours_de_retard} jours de retard</strong>."
        )
        note = "Nous vous remercions de bien vouloir procéder au règlement dans les meilleurs délais."
        couleur_note = "#f59e0b"
        objet = f"Relance — facture {numero_facture} échue depuis {jours_de_retard} jours"
    else:
        emoji, fond = "⚠️", "#fef2f2"
        titre = "Dernier rappel avant recouvrement"
        intro = (
            f"Malgré nos précédentes relances, la facture <strong>{numero_facture}</strong> "
            f"d'un montant de <strong>{montant_ttc} € TTC</strong> reste impayée, "
            f"avec <strong>{jours_de_retard} jours de retard</strong>."
        )
        note = (
            "Conformément à l'article L441-10 du code de commerce, tout retard de paiement "
            "entraîne de plein droit des pénalités de retard ainsi qu'une indemnité forfaitaire "
            "de 40 € pour frais de recouvrement. Nous vous invitons à régulariser cette situation "
            "sous huitaine."
        )
        couleur_note = "#ef4444"
        objet = f"Dernier rappel — facture {numero_facture}"

    bouton = _button(payment_url, 'Régler la facture en ligne') if payment_url else ""

    content = f"""
        <div style="width: 64px; height: 64px; background-color: {fond}; border-radius: 50%; margin: 0 auto 24px auto; text-align: center; line-height: 64px;">
            <span style="font-size: 28px;">{emoji}</span>
        </div>

        <h1 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; text-align: center;">{titre}</h1>

        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6; text-align: center;">
            Bonjour {client_nom},<br><br>
            {intro}
        </p>

        {bouton}

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 32px 0; background-color: {fond}; border-radius: 12px; border-left: 4px solid {couleur_note};">
            <tr>
                <td style="padding: 16px;">
                    <p style="margin: 0; color: #4b5563; font-size: 14px; line-height: 1.5;">{note}</p>
                </td>
            </tr>
        </table>

        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6; text-align: center;">
            {artisan_nom} — pour toute question, répondez directement à cet email.
        </p>
    """

    try:
        resend.Emails.send({
            "from": f"{artisan_nom} via ArtisanGestion <{settings.EMAIL_FROM}>",
            "to": [to],
            "reply_to": artisan_email or settings.SUPPORT_EMAIL,
            "subject": objet,
            "html": _base_template(content),
        })
        logger.info("Relance niveau %s envoyée à %s pour %s", niveau, to, numero_facture)
        return True
    except Exception as e:
        logger.error("Échec de la relance pour %s (%s): %s", numero_facture, to, e)
        return False


# ── Accompagnement de la période d'essai ──
#
# Ces messages ne sont pas décoratifs : sans eux, un artisan qui s'inscrit
# disparaît silencieusement. Ils sont envoyés une seule fois chacun, la trace
# étant tenue en base (cf. app/models/email_cycle_vie.py).


async def send_activation_reminder(to: str, prenom: str) -> bool:
    """
    Relance un artisan inscrit qui n'a encore créé aucun document.

    C'est la fuite la plus coûteuse d'une campagne payante : le clic est
    facturé, le compte est créé, et rien ne se passe ensuite.
    """
    _init_resend()

    content = f"""
        <h1 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; text-align: center;">Votre premier rapport en 2 minutes, {prenom}</h1>

        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            Vous avez créé votre compte ArtisanGestion mais vous n'avez pas encore établi de document.
            Le plus simple pour commencer : un rapport d'intervention.
        </p>

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px 0; background-color: #eff6ff; border-radius: 12px; border-left: 4px solid #3b82f6;">
            <tr>
                <td style="padding: 20px 24px; color: #1e3a8a; font-size: 15px; line-height: 1.7;">
                    1. Choisissez le type d'intervention<br>
                    2. Décrivez en quelques mots ce que vous avez fait<br>
                    3. L'IA rédige le rapport, vous le relisez et l'envoyez
                </td>
            </tr>
        </table>

        <p style="margin: 0 0 8px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            Pas besoin d'avoir renseigné toute votre entreprise pour essayer.
        </p>

        {_button(f"{settings.FRONTEND_URL}/app/rapports/new", "Créer mon premier rapport")}

        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6; text-align: center;">
            Une question, un blocage ? Répondez simplement à cet email.
        </p>
    """

    return _envoyer(to, f"{prenom}, créez votre premier rapport en 2 minutes", content)


async def send_trial_ending_soon(to: str, prenom: str, jours_restants: int) -> bool:
    """Prévient avant la fin de l'essai, pour éviter le blocage-surprise."""
    _init_resend()

    jour = "jour" if jours_restants <= 1 else "jours"

    content = f"""
        <h1 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; text-align: center;">
            Il vous reste {jours_restants} {jour} d'essai
        </h1>

        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            Bonjour {prenom}, votre essai gratuit d'ArtisanGestion se termine dans {jours_restants} {jour}.
            Passé ce délai, vous ne pourrez plus créer de nouveaux devis, factures ou rapports —
            mais vous conserverez l'accès à tout ce que vous avez déjà produit.
        </p>

        <p style="margin: 0 0 8px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            Pour continuer sans interruption, l'abonnement démarre à <strong>19&nbsp;€ HT par mois</strong>,
            sans engagement et résiliable en deux clics.
        </p>

        {_button(f"{settings.FRONTEND_URL}/app/settings?tab=abonnement", "Choisir mon abonnement")}

        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6; text-align: center;">
            Vous hésitez ou il vous manque quelque chose ? Répondez à cet email, nous lisons tout.
        </p>
    """

    return _envoyer(
        to, f"Votre essai ArtisanGestion se termine dans {jours_restants} {jour}", content
    )


async def send_trial_ended(to: str, prenom: str) -> bool:
    """Envoyé le jour où l'essai se termine."""
    _init_resend()

    content = f"""
        <h1 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; text-align: center;">
            Votre essai est terminé
        </h1>

        <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            Bonjour {prenom}, vos 14 jours d'essai gratuit viennent de s'achever.
            Vos documents restent accessibles : rien n'est supprimé. Pour en créer de nouveaux,
            il suffit de choisir un abonnement.
        </p>

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px 0; background-color: #f8fafc; border-radius: 12px; border-left: 4px solid #3b82f6;">
            <tr>
                <td style="padding: 20px 24px; color: #334155; font-size: 15px; line-height: 1.7;">
                    <strong>Indépendant — 19&nbsp;€ HT/mois</strong><br>
                    Rapports IA, devis et factures illimités, signature sur place.<br><br>
                    <strong>Équipe — 39&nbsp;€ HT/mois</strong><br>
                    Collaborateurs, signature à distance, relances d'impayés automatiques.
                </td>
            </tr>
        </table>

        {_button(f"{settings.FRONTEND_URL}/app/settings?tab=abonnement", "Reprendre là où j'en étais")}

        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6; text-align: center;">
            ArtisanGestion ne vous convient pas ? Dites-nous pourquoi en répondant à cet email —
            c'est ce qui nous aide le plus à l'améliorer.
        </p>
    """

    return _envoyer(to, "Votre essai ArtisanGestion est terminé", content)
