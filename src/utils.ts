/** Convertit les chaînes littérales "\n" en vrais retours à la ligne */
export function normalizeNewlines(s: string): string {
  return s.replace(/\\n/g, "\n");
}

/**
 * Nettoie une clé pour qu'elle ne contienne :
 * - aucun espace
 * - aucun accent
 * - aucun caractère spécial
 * Autorisés : [A-Za-z0-9_]
 */
export function sanitizeKey(key: string): string {
  let s = String(key ?? "");
  s = s.normalize("NFKD").replace(/[\u0300-\u036f]/g, "");
  s = s.replace(/\s+/g, "_");
  s = s.replace(/[^0-9A-Za-z_]/g, "");
  s = s.replace(/_+/g, "_").replace(/^_+|_+$/g, "");
  if (!s) return "";
  if (/^\d/.test(s)) s = `k_${s}`;
  return s;
}
