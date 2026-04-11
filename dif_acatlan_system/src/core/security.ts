/**
 * ESTÁNDAR ECMA-262 (TypeScript/JavaScript)
 * Módulo de Seguridad: Sanitización de Entradas para prevenir XSS.
 * Principio de Responsabilidad Única (SRP) - Core Utilities.
 */

class SecurityUtils {
    /**
     * Sanitiza una cadena de texto escapando caracteres HTML peligrosos.
     * @param input Cadena a sanitizar
     * @returns Cadena segura para insertar en el DOM o enviar al backend
     */
    static sanitizeInput(input: string): string {
        if (!input) return '';
        const map: { [key: string]: string } = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            "/": '&#x2F;',
        };
        const reg = /[&<>"'/]/ig;
        return input.trim().replace(reg, (match) => (map[match]));
    }
}
