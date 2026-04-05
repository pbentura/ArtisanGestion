/**
 * Configuration de l'API pour le frontend.
 * Utilise la variable d'environnement VITE_API_BASE_URL définie dans .env.
 * Si la variable n'est pas définie, utilise 'http://localhost:8000' par défaut.
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
