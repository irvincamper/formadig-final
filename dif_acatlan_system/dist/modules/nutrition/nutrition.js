"use strict";
/**
 * Módulo de Nutrición: Gestión de Programas
 * Lógica para cálculos antropométricos (IMC) y alertas visuales.
 */
document.addEventListener('DOMContentLoaded', () => {
    const nutriForm = document.getElementById('nutritionForm');
    const beneficiarySelect = document.getElementById('nutriBeneficiary');
    const inputWeight = document.getElementById('weight');
    const inputHeight = document.getElementById('height');
    const alertsContainer = document.getElementById('nutritionAlerts');
    // --- Llenar Select ---
    function populateBeneficiaries() {
        beneficiarySelect.innerHTML = '<option value="">-- Seleccione un beneficiario --</option>';
        // Accedemos a los datos simulados que viven en el namespace global (por ahora en admin.ts)
        // En un entorno de producción, esto sería una llamada AJAX al backend.
        if (typeof window.beneficiariesDb !== 'undefined') {
            const actives = window.beneficiariesDb.filter((b) => b.status === 'Activo');
            actives.forEach((b) => {
                const opt = document.createElement('option');
                opt.value = b.fullName;
                opt.textContent = `${b.fullName} (${b.curp})`;
                beneficiarySelect.appendChild(opt);
            });
        }
    }
    // Lo exponemos globalmente para hackear el acceso desde este script en fase 1
    // (En fase 2 esto usaría endpoints de API)
    window.beneficiariesDb = [
        { id: 'BN-001', fullName: 'María García López', curp: 'GALM800101MDFRRN01', birthDate: '1980-01-01', status: 'Activo' },
        { id: 'BN-002', fullName: 'Juan Pérez Ramos', curp: 'PERJ850505HDFRRN01', birthDate: '1985-05-05', status: 'Inactivo' },
    ];
    populateBeneficiaries();
    window.addEventListener('beneficiariesUpdated', populateBeneficiaries);
    // --- Evaluar Formulario ---
    nutriForm.addEventListener('submit', (e) => {
        e.preventDefault();
        let isValid = true;
        const name = beneficiarySelect.value;
        const weightStr = SecurityUtils.sanitizeInput(inputWeight.value);
        const heightStr = SecurityUtils.sanitizeInput(inputHeight.value);
        const weight = parseFloat(weightStr);
        const height = parseFloat(heightStr);
        if (!name) {
            showError(beneficiarySelect, 'nutriBeneficiaryError');
            isValid = false;
        }
        else {
            hideError(beneficiarySelect, 'nutriBeneficiaryError');
        }
        if (isNaN(weight) || weight <= 0 || weight > 300) {
            showError(inputWeight, 'weightError');
            isValid = false;
        }
        else {
            hideError(inputWeight, 'weightError');
        }
        if (isNaN(height) || height <= 0 || height > 2.5) {
            showError(inputHeight, 'heightError');
            isValid = false;
        }
        else {
            hideError(inputHeight, 'heightError');
        }
        if (isValid) {
            calcularIMC(name, weight, height);
            nutriForm.reset();
        }
    });
    // --- Lógica de Alertas Nutricionales ---
    function calcularIMC(nombre, peso, talla) {
        // Fórmula IMC = Peso(kg) / (Talla(m) * Talla(m))
        const imc = peso / (talla * talla);
        const imcFormat = imc.toFixed(1);
        let clasificacion = '';
        let tipoAlerta = ''; // info, success, warning, error
        if (imc < 18.5) {
            clasificacion = 'Bajo peso (Riesgo de desnutrición)';
            tipoAlerta = 'warning';
        }
        else if (imc >= 18.5 && imc < 25) {
            clasificacion = 'Peso normal (Saludable)';
            tipoAlerta = 'success';
        }
        else if (imc >= 25 && imc < 30) {
            clasificacion = 'Sobrepeso (Requiere seguimiento)';
            tipoAlerta = 'warning';
        }
        else {
            clasificacion = 'Obesidad (Alerta prioritaria)';
            tipoAlerta = 'error';
        }
        generarAlertaUICard(nombre, peso, talla, imcFormat, clasificacion, tipoAlerta);
    }
    function generarAlertaUICard(nombre, peso, talla, imc, clasificacion, tipo) {
        const emptyMsg = document.getElementById('emptyNutritionMsg');
        if (emptyMsg)
            emptyMsg.style.display = 'none';
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert--${tipo}`;
        const date = new Date().toLocaleDateString('es-MX');
        alertDiv.innerHTML = `
            <h4 class="alert__title">Evaluación de ${SecurityUtils.sanitizeInput(nombre)} <span class="text-muted" style="float:right; font-size:0.8rem; font-weight:normal;">${date}</span></h4>
            <p class="alert__message">
                <strong>Peso:</strong> ${peso} kg | <strong>Talla:</strong> ${talla} m <br>
                <strong>IMC:</strong> ${imc} -> <strong>${clasificacion}</strong>
            </p>
        `;
        // Agregar al principio
        alertsContainer.prepend(alertDiv);
    }
    function showError(inputElement, errorId) {
        inputElement.classList.add('form__input--invalid');
        const errorEl = document.getElementById(errorId);
        if (errorEl)
            errorEl.classList.add('form__error--active');
    }
    function hideError(inputElement, errorId) {
        inputElement.classList.remove('form__input--invalid');
        const errorEl = document.getElementById(errorId);
        if (errorEl)
            errorEl.classList.remove('form__error--active');
    }
});
