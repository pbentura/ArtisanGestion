/**
 * Configuration de l'API pour le frontend.
 * Utilise la variable d'environnement VITE_API_BASE_URL définie dans .env.
 * Si la variable n'est pas définie, utilise 'http://localhost:8000' par défaut.
 */

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
}

/**
 * Session expirée.
 *
 * Le jeton vit une semaine, l'essai quatorze jours : au huitième jour, la
 * garde du routeur voyait toujours un jeton en localStorage et laissait entrer
 * dans l'app, où chaque appel repartait en 401 sans que rien ne le dise.
 * L'artisan trouvait une application vide, au milieu de son essai.
 *
 * On coupe donc au seul endroit qui voit toutes les réponses : le jeton mort
 * est effacé et la connexion redemandée.
 */
let redirectionEnCours = false;

function sessionExpiree() {
  if (redirectionEnCours) return;
  redirectionEnCours = true;

  try {
    localStorage.removeItem('token');
  } catch {
    // Stockage bloqué : la redirection suffit.
  }

  // Déjà sur l'écran de connexion : rien à faire, sinon on boucle.
  if (window.location.pathname.startsWith('/auth')) {
    redirectionEnCours = false;
    return;
  }

  // `replace` plutôt que `href` : le retour arrière ne doit pas ramener sur
  // une page d'application désormais inaccessible.
  window.location.replace('/auth?session=expiree');
}

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}/api/${endpoint.replace(/^\//, '')}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {}),
    },
  });

  if (response.status === 401) {
    sessionExpiree();
  }

  return response;
}
