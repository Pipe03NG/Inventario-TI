/**
 * app.js — Utilidades compartidas para el frontend de Inventario TI
 * Se carga en todas las páginas antes de los scripts inline.
 */

const API_BASE = '';   // vacío porque la API corre en el mismo origen

/**
 * Wrapper fetch para la API REST.
 * @param {string} endpoint  - Ruta relativa, ej: '/api/usuarios'
 * @param {string} method    - GET | POST | PUT | PATCH | DELETE
 * @param {object|null} body - Cuerpo de la solicitud (se serializa a JSON)
 * @returns {Promise<any>}   - Respuesta JSON parseada (puede ser undefined en 204)
 * @throws {Error}           - Lanza con el mensaje de error del servidor
 */
async function apiFetch(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };

  if (body !== null) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(API_BASE + endpoint, options);

  // 204 No Content — sin cuerpo
  if (response.status === 204) return;

  const data = await response.json();

  if (!response.ok) {
    // FastAPI devuelve los errores en { detail: "..." }
    const message = data?.detail || `Error ${response.status}`;
    throw new Error(message);
  }

  return data;
}
