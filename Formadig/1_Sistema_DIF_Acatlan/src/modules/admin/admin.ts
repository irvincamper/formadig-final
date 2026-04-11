/**
 * Módulo Administrativo: Gestión de Expedientes
 * Lógica para validación de formularios y tabla interactiva.
 */

// Interface simulada para base de datos FASE 1
interface Beneficiary {
    id: string;
    fullName: string;
    curp: string;
    birthDate: string;
    status: 'Activo' | 'Inactivo';
}

// Datos simulados (Mock)
let beneficiariesDb: Beneficiary[] = [
    { id: 'BN-001', fullName: 'María García López', curp: 'GALM800101MDFRRN01', birthDate: '1980-01-01', status: 'Activo' },
    { id: 'BN-002', fullName: 'Juan Pérez Ramos', curp: 'PERJ850505HDFRRN01', birthDate: '1985-05-05', status: 'Inactivo' },
];

document.addEventListener('DOMContentLoaded', () => {
    // --- Referencias UI ---
    const form = document.getElementById('beneficiaryForm') as HTMLFormElement;
    const inputName = document.getElementById('fullName') as HTMLInputElement;
    const inputCurp = document.getElementById('curp') as HTMLInputElement;
    const inputDate = document.getElementById('birthDate') as HTMLInputElement;
    
    const searchInput = document.getElementById('searchBeneficiary') as HTMLInputElement;
    const statusFilter = document.getElementById('filterStatus') as HTMLSelectElement;
    const tableBody = document.querySelector('#beneficiariesTable .table__body') as HTMLTableSectionElement;

    // --- Renderizado Inicial ---
    renderTable(beneficiariesDb);

    // --- Eventos de Validación y Submit ---
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        let isValid = true;
        
        // 1. Sanitizar y Validar Nombre
        const rawName = inputName.value;
        const cleanName = SecurityUtils.sanitizeInput(rawName);
        if (cleanName.length < 3) {
            showError(inputName, 'fullNameError');
            isValid = false;
        } else {
            hideError(inputName, 'fullNameError');
        }

        // 2. Validar CURP (18 caracteres)
        const curpVal = SecurityUtils.sanitizeInput(inputCurp.value).toUpperCase();
        const curpRegex = /^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$/;
        if (!curpRegex.test(curpVal)) {
            showError(inputCurp, 'curpError');
            isValid = false;
        } else {
            hideError(inputCurp, 'curpError');
        }

        // 3. Validar Fecha (No futura)
        const dateVal = new Date(inputDate.value);
        const today = new Date();
        if (isNaN(dateVal.getTime()) || dateVal > today) {
            showError(inputDate, 'dateError');
            isValid = false;
        } else {
            hideError(inputDate, 'dateError');
        }

        if (isValid) {
            // Guardar registro
            const newBen: Beneficiary = {
                id: `BN-00${beneficiariesDb.length + 1}`,
                fullName: cleanName,
                curp: curpVal,
                birthDate: inputDate.value,
                status: 'Activo'
            };
            
            beneficiariesDb.push(newBen);
            
            // Actualizar tabla y limpiar form
            renderTable(beneficiariesDb);
            form.reset();
            alert('¡Beneficiario registrado con éxito!');
            
            // Disparar evento para que el módulo de nutrición actualice su select
            window.dispatchEvent(new CustomEvent('beneficiariesUpdated'));
        }
    });

    // --- Filtros Interactivos ---
    searchInput.addEventListener('input', applyFilters);
    statusFilter.addEventListener('change', applyFilters);

    function applyFilters() {
        const term = SecurityUtils.sanitizeInput(searchInput.value).toLowerCase();
        const status = statusFilter.value;

        const filtered = beneficiariesDb.filter(b => {
            const matchText = b.fullName.toLowerCase().includes(term) || b.curp.toLowerCase().includes(term);
            const matchStatus = status === 'all' || b.status === status;
            return matchText && matchStatus;
        });

        renderTable(filtered);
    }

    // --- Dom Utils ---
    function renderTable(data: Beneficiary[]) {
        if (!tableBody) return;
        tableBody.innerHTML = '';
        
        if (data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="6" class="table__td" style="text-align:center;">No se encontraron registros</td></tr>`;
            return;
        }

        data.forEach(b => {
            const tr = document.createElement('tr');
            tr.className = 'table__tr';
            tr.innerHTML = `
                <td class="table__td">${b.id}</td>
                <td class="table__td"><strong>${b.fullName}</strong></td>
                <td class="table__td">${b.curp}</td>
                <td class="table__td">${b.birthDate}</td>
                <td class="table__td">
                    <span class="badge ${b.status === 'Activo' ? 'badge--active' : 'badge--inactive'}">${b.status}</span>
                </td>
                <td class="table__td">
                    <button class="button button--secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Ver</button>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    }

    function showError(inputElement: HTMLInputElement, errorId: string) {
        inputElement.classList.add('form__input--invalid');
        const errorEl = document.getElementById(errorId);
        if (errorEl) errorEl.classList.add('form__error--active');
    }

    function hideError(inputElement: HTMLInputElement, errorId: string) {
        inputElement.classList.remove('form__input--invalid');
        const errorEl = document.getElementById(errorId);
        if (errorEl) errorEl.classList.remove('form__error--active');
    }
});
