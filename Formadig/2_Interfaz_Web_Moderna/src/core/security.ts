export class SecurityUtils {
    /**
     * Sanitizes an input string by escaping dangerous HTML characters to prevent XSS.
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
