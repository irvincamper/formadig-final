import React, { useState } from 'react';
import { useAppContext, type NutritionAlert } from '../core/AppContext';

export const NutritionDashboard: React.FC = () => {
  const { beneficiaries, nutritionAlerts, addNutritionAlert, currentUser } = useAppContext();
  
  const [formData, setFormData] = useState({ beneficiaryId: '', weight: '', height: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Filtrar solo beneficiarios activos
  const activeBeneficiaries = beneficiaries.filter(b => b.status === "Activo");

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    const { beneficiaryId, weight, height } = formData;
    
    if (!beneficiaryId) newErrors.beneficiaryId = "Seleccione un beneficiario";
    
    const w = parseFloat(weight);
    if (isNaN(w) || w <= 0 || w > 300) newErrors.weight = "Peso numérico inválido (1-300 kg)";
    
    const h = parseFloat(height);
    if (isNaN(h) || h <= 0.4 || h > 2.5) newErrors.height = "Talla numérica inválida (0.4-2.5 m)";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const calculateIMC = (peso: number, talla: number) => {
    const imc = peso / (talla * talla);
    const imcFormat = imc.toFixed(1);
    
    let classification = '';
    let type: 'success' | 'warning' | 'error' | 'info' = 'info';
    
    if (imc < 18.5) {
        classification = 'Bajo peso (Riesgo de desnutrición)';
        type = 'warning';
    } else if (imc >= 18.5 && imc < 25) {
        classification = 'Peso normal (Saludable)';
        type = 'success';
    } else if (imc >= 25 && imc < 30) {
        classification = 'Sobrepeso (Requiere seguimiento)';
        type = 'warning';
    } else {
        classification = 'Obesidad (Alerta prioritaria)';
        type = 'error';
    }
    
    return { imc: imcFormat, classification, type };
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm() && currentUser) {
      const ben = beneficiaries.find(b => b.id === formData.beneficiaryId);
      if (!ben) return;

      const w = parseFloat(formData.weight);
      const h = parseFloat(formData.height);
      const { imc, classification, type } = calculateIMC(w, h);
      
      const newAlert: NutritionAlert = {
        id: `IMC-${Date.now().toString().slice(-6)}`,
        beneficiaryId: ben.id,
        beneficiaryName: ben.fullName,
        date: new Date().toLocaleDateString('es-MX'),
        weight: w,
        height: h,
        imc,
        classification,
        type,
        createdBy: currentUser.id
      };

      addNutritionAlert(newAlert);
      setFormData({...formData, weight: '', height: ''});
    }
  };

  return (
    <div className="slide-up">
      <div className="page-header">
        <div>
          <h2 className="page-title">Seguimiento Nutricional</h2>
          <p className="page-subtitle">Captura antropométrica y cálculo de alertas de salud</p>
        </div>
      </div>

      <div className="dashboard-grid" style={{gridTemplateColumns: '1fr 1fr'}}>
        {/* Form Column */}
        <div className="card glass-panel fade-in">
          <div className="card-header">
            <h3 className="card-title">⚖️ Captura Antropométrica</h3>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Beneficiario Activo <span style={{color: 'var(--error)'}}>*</span></label>
              <select 
                className={`form-control ${errors.beneficiaryId ? 'error' : ''}`}
                value={formData.beneficiaryId}
                onChange={e => {
                  setFormData({...formData, beneficiaryId: e.target.value});
                  if(errors.beneficiaryId) setErrors({...errors, beneficiaryId: ''});
                }}
              >
                <option value="">-- Seleccione un beneficiario --</option>
                {activeBeneficiaries.map(b => (
                  <option key={b.id} value={b.id}>{b.fullName} ({b.curp})</option>
                ))}
              </select>
              {errors.beneficiaryId && <span className="error-text">{errors.beneficiaryId}</span>}
              {activeBeneficiaries.length === 0 && (
                <span className="error-text" style={{color: 'var(--warning)', marginTop: '0.5rem'}}>
                  No hay beneficiarios activos. Regístrelos en el módulo Administrativo.
                </span>
              )}
            </div>
            
            <div className="form-row">
              <div className="form-group form-col">
                <label className="form-label">Peso (kg) <span style={{color: 'var(--error)'}}>*</span></label>
                <input 
                  type="number" 
                  step="0.1"
                  className={`form-control ${errors.weight ? 'error' : ''}`}
                  placeholder="Ej. 65.5"
                  value={formData.weight}
                  onChange={e => {
                    setFormData({...formData, weight: e.target.value});
                    if(errors.weight) setErrors({...errors, weight: ''});
                  }}
                />
                {errors.weight && <span className="error-text">{errors.weight}</span>}
              </div>
              <div className="form-group form-col">
                <label className="form-label">Talla (m) <span style={{color: 'var(--error)'}}>*</span></label>
                <input 
                  type="number" 
                  step="0.01"
                  className={`form-control ${errors.height ? 'error' : ''}`}
                  placeholder="Ej. 1.70"
                  value={formData.height}
                  onChange={e => {
                    setFormData({...formData, height: e.target.value});
                    if(errors.height) setErrors({...errors, height: ''});
                  }}
                />
                {errors.height && <span className="error-text">{errors.height}</span>}
              </div>
            </div>

            <div style={{ marginTop: '1.5rem' }}>
              <button type="submit" className="btn btn-secondary" style={{width: '100%'}}>
                Calcular IMC y Generar Historial
              </button>
            </div>
          </form>
        </div>

        {/* Alerts Column */}
        <div className="card glass-panel fade-in" style={{animationDelay: '0.1s'}}>
          <div className="card-header">
            <h3 className="card-title">🔔 Historial de Evaluaciones</h3>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {nutritionAlerts.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                No hay evaluaciones recientes. Llene el formulario para registrar el estado de un beneficiario.
              </div>
            ) : (
              nutritionAlerts.map(alert => (
                <div key={alert.id} className="slide-up" style={{
                  padding: '1.25rem',
                  borderRadius: 'var(--radius-sm)',
                  borderLeft: `4px solid var(--${alert.type})`,
                  backgroundColor: `var(--${alert.type}-bg)`,
                  boxShadow: '0 2px 5px rgba(0,0,0,0.02)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <h4 style={{ margin: 0, fontWeight: 600, color: 'var(--text-main)' }}>{alert.beneficiaryName}</h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{alert.date}</span>
                  </div>
                  <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-main)' }}>
                    <strong>Peso:</strong> {alert.weight} kg | <strong>Talla:</strong> {alert.height} m
                  </p>
                  <div style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className={`badge badge-${alert.type}`}>IMC: {alert.imc}</span>
                    <strong style={{ color: `var(--${alert.type})`, fontSize: '0.9rem' }}>{alert.classification}</strong>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
