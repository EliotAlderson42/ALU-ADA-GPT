/** Convertit les chaînes littérales "\n" en vrais retours à la ligne */
export function normalizeNewlines(s: string): string {
  return s.replace(/\\n/g, "\n");
}
