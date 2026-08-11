import stripe
import sys

# Replace with the key from your .env
stripe.api_key = "sk_test_..." # We will read it from settings
from app.core.config import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

def get_errors():
    try:
        # On va lister les PaymentIntents pour voir s'il y a des erreurs
        intents = stripe.PaymentIntent.list(limit=5)
        print("--- Payment Intents récents sur le compte principal ---")
        for pi in intents.data:
            if pi.last_payment_error:
                print(f"Erreur trouvée: {pi.last_payment_error.message}")
            else:
                print(f"PI {pi.id} : {pi.status}")
                
        print("\n--- Sessions Checkout récentes ---")
        sessions = stripe.checkout.Session.list(limit=5)
        for s in sessions.data:
            print(f"Session {s.id} : {s.payment_status} (Compte: {s.stripe_account})")
            if s.stripe_account:
                print(f" -> Pour voir l'erreur, il faut lister les PI sur le compte {s.stripe_account}")
                try:
                    # On liste les PI sur le compte connecté
                    connected_intents = stripe.PaymentIntent.list(
                        limit=5, 
                        stripe_account=s.stripe_account
                    )
                    for c_pi in connected_intents.data:
                        if c_pi.last_payment_error:
                            print(f"   [!] ERREUR SUR LE COMPTE CONNECTÉ: {c_pi.last_payment_error.message} (Code: {c_pi.last_payment_error.code})")
                        else:
                            print(f"   PI Connecté {c_pi.id} : {c_pi.status}")
                except Exception as e:
                    print(f"   Erreur lecture compte connecté: {e}")
                print("-" * 20)

    except Exception as e:
        print(f"Erreur du script : {e}")

if __name__ == "__main__":
    get_errors()
