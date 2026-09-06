<script setup lang="ts">
/**
 * Moyen de paiement manquant sur une facture.
 *
 * Le PDF n'imprime le bloc « RÈGLEMENT PAR VIREMENT » que si l'IBAN est
 * renseigné, et le bouton « Payer par carte » n'apparaît dans l'email que si
 * Stripe Connect est actif. Sans l'un ni l'autre, la facture part sans aucun
 * moyen d'être réglée, et rien ne le signale.
 *
 * Deux partis pris :
 *
 * 1. **Les deux, pas l'un ou l'autre.** L'IBAN est gratuit et reste le
 *    standard du bâtiment ; la carte se paie en commission et n'a de sens que
 *    sur les petits montants. Le client final choisit — l'artisan n'a pas à
 *    trancher à sa place.
 * 2. **On prévient, on ne bloque pas.** Une facture sans IBAN reste une
 *    facture valable. « Plus tard » laisse toujours passer.
 */
import { ref } from 'vue'
import { Landmark, CreditCard, Loader2, ArrowRight } from 'lucide-vue-next'
import { apiFetch } from '@/lib/api'
import { dataStore, uiStore } from '@/lib/store'

const form = ref({ iban: '', bic: '', nom_banque: '' })
const enregistrement = ref(false)
const stripeEnCours = ref(false)
const erreur = ref('')

/** IBAN français : 27 caractères. Les autres pays vont de 15 à 34. */
function ibanValide(valeur: string): boolean {
  const brut = valeur.replace(/\s+/g, '').toUpperCase()
  return /^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/.test(brut)
}

function reinitialiser() {
  form.value = { iban: '', bic: '', nom_banque: '' }
  erreur.value = ''
  enregistrement.value = false
  stripeEnCours.value = false
}

async function enregistrer() {
  const iban = form.value.iban.replace(/\s+/g, '').toUpperCase()

  if (!ibanValide(iban)) {
    erreur.value = "Cet IBAN ne semble pas valide. Vérifiez la saisie (il commence par deux lettres, par exemple FR76)."
    return
  }

  const societe = dataStore.user.data?.societes?.[0]
  if (!societe) {
    erreur.value = "Votre entreprise n'est pas encore enregistrée."
    return
  }

  enregistrement.value = true
  erreur.value = ''

  try {
    const res = await apiFetch(`societes/${societe.id}`, {
      method: 'PUT',
      body: JSON.stringify({
        iban,
        bic: form.value.bic.replace(/\s+/g, '').toUpperCase() || null,
        nom_banque: form.value.nom_banque.trim() || null,
      }),
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || "L'enregistrement a échoué.")
    }

    // Le store porte l'IBAN utilisé par `sansMoyenDePaiement` : sans ce
    // rafraîchissement, la modale se rouvrirait au document suivant.
    await dataStore.fetchUser(true)

    const suite = uiStore.onPaiementConfigure
    uiStore.closePaiementModal()
    reinitialiser()
    suite?.()
  } catch (e: any) {
    erreur.value = e.message || "L'enregistrement a échoué."
  } finally {
    enregistrement.value = false
  }
}

async function activerStripe() {
  stripeEnCours.value = true
  erreur.value = ''
  try {
    const res = await apiFetch('stripe-connect/onboarding', { method: 'POST' })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || "L'activation a échoué.")
    }
    const data = await res.json()
    if (data.onboarding_url) {
      // Départ vers Stripe : l'artisan revient par /app/stripe-connect/return.
      window.location.href = data.onboarding_url
      return
    }
    await dataStore.fetchUser(true)
    uiStore.closePaiementModal()
    reinitialiser()
  } catch (e: any) {
    erreur.value = e.message || "L'activation a échoué."
    stripeEnCours.value = false
  }
}

function plusTard() {
  const suite = uiStore.onPaiementConfigure
  uiStore.closePaiementModal()
  reinitialiser()
  suite?.()
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="uiStore.showPaiementModal"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4"
      >
        <div class="absolute inset-0 bg-background/80 backdrop-blur-sm" @click="plusTard" />

        <div class="relative w-full max-w-lg bg-background rounded-3xl shadow-2xl border border-border/60 max-h-[92vh] overflow-y-auto z-10">
          <div class="p-6 sm:p-8 space-y-6">

            <div class="text-center">
              <div class="inline-flex items-center justify-center p-3.5 rounded-2xl bg-primary/10 text-primary mb-3 shadow-inner shadow-primary/20">
                <Landmark class="w-7 h-7" />
              </div>
              <h2 class="text-2xl font-bold text-foreground mb-1.5">
                Comment votre client vous paiera-t-il ?
              </h2>
              <p class="text-muted-foreground text-sm leading-relaxed max-w-sm mx-auto">
                Votre facture ne porte aucune coordonnée de règlement. Ajoutez votre IBAN :
                il s'imprimera sur toutes vos factures.
              </p>
            </div>

            <div class="space-y-3">
              <div class="space-y-1.5">
                <label for="paiement-iban" class="text-sm font-medium text-foreground">
                  IBAN <span class="text-destructive">*</span>
                </label>
                <input
                  id="paiement-iban"
                  v-model="form.iban"
                  type="text"
                  autocomplete="off"
                  placeholder="FR76 1234 5678 9012 3456 7890 123"
                  class="w-full px-3 py-2.5 bg-background border border-input rounded-lg font-mono uppercase tracking-wider text-sm focus:ring-2 focus:ring-primary outline-none"
                  @keyup.enter="enregistrer"
                />
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="space-y-1.5">
                  <label for="paiement-bic" class="text-sm font-medium text-foreground">BIC</label>
                  <input
                    id="paiement-bic"
                    v-model="form.bic"
                    type="text"
                    autocomplete="off"
                    placeholder="BNPAFRPP"
                    class="w-full px-3 py-2.5 bg-background border border-input rounded-lg font-mono uppercase text-sm focus:ring-2 focus:ring-primary outline-none"
                  />
                </div>
                <div class="space-y-1.5">
                  <label for="paiement-banque" class="text-sm font-medium text-foreground">Banque</label>
                  <input
                    id="paiement-banque"
                    v-model="form.nom_banque"
                    type="text"
                    autocomplete="off"
                    placeholder="Crédit Agricole"
                    class="w-full px-3 py-2.5 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none"
                  />
                </div>
              </div>

              <p class="text-xs text-muted-foreground">
                Ces coordonnées ne servent qu'à figurer sur vos factures. Modifiables à tout
                moment dans <span class="font-medium text-foreground">Mon Entreprise</span>.
              </p>
            </div>

            <p v-if="erreur" class="text-sm text-destructive text-center">{{ erreur }}</p>

            <button
              type="button"
              class="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-primary text-primary-foreground font-semibold transition-all hover:bg-primary/90 disabled:opacity-60"
              :disabled="enregistrement || stripeEnCours"
              @click="enregistrer"
            >
              <Loader2 v-if="enregistrement" class="w-4 h-4 animate-spin" />
              Enregistrer mon IBAN
            </button>

            <!-- Option carte, présentée comme un complément et non une
                 alternative : le parcours Stripe demande un justificatif
                 d'identité, on ne l'impose pas à quelqu'un en période d'essai. -->
            <div class="pt-1 border-t border-border/60">
              <button
                type="button"
                class="w-full flex items-center gap-3 p-3 mt-3 rounded-xl border border-border hover:border-primary/50 hover:bg-accent/50 transition-colors text-left disabled:opacity-60"
                :disabled="enregistrement || stripeEnCours"
                @click="activerStripe"
              >
                <div class="p-2 rounded-lg bg-primary/10 text-primary flex-shrink-0">
                  <CreditCard class="w-5 h-5" />
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-foreground">
                    Ajouter aussi le paiement par carte
                  </p>
                  <p class="text-xs text-muted-foreground">
                    Un bouton « Payer » dans l'email. Idéal sur les petits montants ;
                    une commission s'applique.
                  </p>
                </div>
                <Loader2 v-if="stripeEnCours" class="w-4 h-4 animate-spin text-muted-foreground flex-shrink-0" />
                <ArrowRight v-else class="w-4 h-4 text-muted-foreground flex-shrink-0" />
              </button>
            </div>

            <button
              type="button"
              class="w-full text-sm text-muted-foreground hover:text-foreground transition-colors"
              :disabled="enregistrement || stripeEnCours"
              @click="plusTard"
            >
              Plus tard — envoyer sans coordonnées de paiement
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
