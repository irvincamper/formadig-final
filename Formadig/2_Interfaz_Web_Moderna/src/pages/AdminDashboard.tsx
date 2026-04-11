import React, { useState } from 'react';
import { SecurityUtils } from '../core/security';
import { useAppContext, type Beneficiary } from '../core/AppContext';

export const AdminDashboard: React.FC = () => {
  const { beneficiaries, addBeneficiary, currentUser } = useAppContext();
  const [searchTerm, setSearchTerm] = useState('');
  
  const initialForm = {
    fullName: '',
    curp: '',
    birthDate: '',
    phone: '',
    email: '',
    address: '',
    program: 'Despensas'
  };

  const [formData, setFormData] = useState(initialForm);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    const name = SecurityUtils.sanitizeInput(formData.fullName).trim();
    const curp = SecurityUtils.sanitizeInput(formData.curp).toUpperCase().trim();
    const phone = formData.phone.trim();
    const email = formData.email.trim();
    const address = formData.address.trim();
    
    // Name validation
    if (name.length < 3) {
      newErrors.fullName = "El nombre es obligatorio (min 3 caracteres)";
    } else if (/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/.test(name)) {
      newErrors.fullName = "El nombre no debe contener números ni caracteres especiales";
    }
    
    // CURP validation
    const curpRegex = /^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$/;
    if (!curpRegex.test(curp)) newErrors.curp = "Formato de CURP inválido (18 caracteres)";
    
    // Date validation
    if (!formData.birthDate) {
      newErrors.birthDate = "La fecha de nacimiento es obligatoria";
    } else {
      const dateVal = new Date(formData.birthDate);
      const today = new Date();
      if (isNaN(dateVal.getTime()) || dateVal > today) {
        newErrors.birthDate = "Fecha de nacimiento inválida";
      }
    }

    // Phone validation (10 digits)
    const phoneRegex = /^\d{10}$/;
    if (!phoneRegex.test(phone)) newErrors.phone = "El teléfono debe tener 10 dígitos numéricos";

    // Email validation (optional but if provided must be valid)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email && !emailRegex.test(email)) newErrors.email = "Formato de correo inválido";

    // Address
    if (address.length < 5) newErrors.address = "La dirección es obligatoria (min 5 caracteres)";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm() && currentUser) {
      const newBen: Beneficiary = {
        id: `BN-${Date.now().toString().slice(-6)}`,
        fullName: SecurityUtils.sanitizeInput(formData.fullName).trim(),
        curp: SecurityUtils.sanitizeInput(formData.curp).toUpperCase().trim(),
        birthDate: formData.birthDate,
        phone: formData.phone.trim(),
        email: formData.email.trim(),
        address: formData.address.trim(),
        program: formData.program,
        status: 'Activo',
        registeredBy: currentUser.id,
        registrationDate: new Date().toISOString()
      };
      
      addBeneficiary(newBen);
      setFormData(initialForm);
      alert("¡Beneficiario registrado exitosamente!");
    }
  };

  const filteredBeneficiaries = beneficiaries.filter(b => 
    b.fullName.toLowerCase().includes(searchTerm.toLowerCase()) || 
    b.curp.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="slide-up">
      <div className="page-header">
        <div>
          <h2 className="page-title">Gestión de Expedientes</h2>
          <p className="page-subtitle">Administra el padrón de beneficiarios del DIF</p>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card glass-panel dashboard-hero fade-in">
          <div className="card-header">
            <h3 className="card-title">📝 Registro de Beneficiarios</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Nombre Completo <span style={{color: 'var(--error)'}}>*</span></label>
              <input 
                type="text" 
                className={`form-control ${errors.fullName ? 'error' : ''}`}
                value={formData.fullName}
                onChange={e => {
                   setFormData({...formData, fullName: e.target.value});
                   if(errors.fullName) setErrors({...errors, fullName: ''});
                }}
                placeholder="Ej. Ana Pérez López..."
              />
              {errors.fullName && <span className="error-text">{errors.fullName}</span>}
            </div>
            
            <div className="form-row">
              <div className="form-group form-col">
                <label className="form-label">CURP <span style={{color: 'var(--error)'}}>*</span></label>
                <input 
                  type="text" 
                  className={`form-control ${errors.curp ? 'error' : ''}`}
                  value={formData.curp}
                  onChange={e => {
                    setFormData({...formData, curp: e.target.value.toUpperCase()});
                    if(errors.curp) setErrors({...errors, curp: ''});
                  }}
                  placeholder="18 caracteres alfanuméricos"
                  maxLength={18}
                />
                {errors.curp && <span className="error-text">{errors.curp}</span>}
              </div>
              <div className="form-group form-col">
                <label className="form-label">Fecha de Nacimiento <span style={{color: 'var(--error)'}}>*</span></label>
                <input 
                  type="date" 
                  className={`form-control ${errors.birthDate ? 'error' : ''}`}
                  value={formData.birthDate}
                  onChange={e => {
                    setFormData({...formData, birthDate: e.target.value});
                    if(errors.birthDate) setErrors({...errors, birthDate: ''});
                  }}
                />
                {errors.birthDate && <span className="error-text">{errors.birthDate}</span>}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group form-col">
                <label className="form-label">Teléfono (Celular / Casa) <span style={{color: 'var(--error)'}}>*</span></label>
                <input 
                  type="tel" 
                  className={`form-control ${errors.phone ? 'error' : ''}`}
                  value={formData.phone}
                  onChange={e => {
                    setFormData({...formData, phone: e.target.value.replace(/\D/g, '').slice(0, 10)});
                    if(errors.phone) setErrors({...errors, phone: ''});
                  }}
                  placeholder="10 dígitos numéricos"
                />
                {errors.phone && <span className="error-text">{errors.phone}</span>}
              </div>
              <div className="form-group form-col">
                <label className="form-label">Correo Electrónico (Opcional)</label>
                <input 
                  type="email" 
                  className={`form-control ${errors.email ? 'error' : ''}`}
                  value={formData.email}
                  onChange={e => {
                    setFormData({...formData, email: e.target.value});
                    if(errors.email) setErrors({...errors, email: ''});
                  }}
                  placeholder="ejemplo@correo.com"
                />
                {errors.email && <span className="error-text">{errors.email}</span>}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Dirección Completa <span style={{color: 'var(--error)'}}>*</span></label>
              <input 
                type="text" 
                className={`form-control ${errors.address ? 'error' : ''}`}
                value={formData.address}
                onChange={e => {
                  setFormData({...formData, address: e.target.value});
                  if(errors.address) setErrors({...errors, address: ''});
                }}
                placeholder="Calle, Número, Colonia, Municipio"
              />
              {errors.address && <span className="error-text">{errors.address}</span>}
            </div>

            <div className="form-group">
              <label className="form-label">Programa Asignado</label>
              <select 
                className="form-control"
                value={formData.program}
                onChange={e => setFormData({...formData, program: e.target.value})}
              >
                <option value="Despensas">Programa de Despensas</option>
                <option value="Sillas de Ruedas">Apoyo Funcional (Sillas de Ruedas)</option>
                <option value="Atención Médica">Atención Médica y Dental</option>
                <option value="Terapia Psicológica">Terapia Psicológica</option>
                <option value="Apoyo Legal">Asesoría Jurídica</option>
              </select>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
              <button type="submit" className="btn btn-primary" style={{ padding: '0.8rem 1.5rem', fontSize: '1rem' }}>
                Guardar Expediente
              </button>
            </div>
          </form>
        </div>

        <div className="card glass-panel dashboard-hero fade-in" style={{animationDelay: '0.1s'}}>
          <div className="card-header">
            <h3 className="card-title">🗂️ Directorio Activo</h3>
          </div>
          
          <div className="search-wrapper">
             <span className="search-icon">🔍</span>
             <input 
               type="text" 
               className="form-control search-input" 
               placeholder="Buscar por nombre o CURP..."
               value={searchTerm}
               onChange={e => setSearchTerm(e.target.value)}
             />
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre Completo</th>
                  <th>CURP / Contacto</th>
                  <th>Programa</th>
                  <th>Estatus</th>
                </tr>
              </thead>
              <tbody>
                {filteredBeneficiaries.map(b => (
                  <tr key={b.id}>
                    <td><strong>{b.id}</strong></td>
                    <td>
                      <div style={{fontWeight: 500}}>{b.fullName}</div>
                      <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Reg: {new Date(b.registrationDate).toLocaleDateString()}</div>
                    </td>
                    <td>
                      <div style={{fontFamily: 'monospace', opacity: 0.9, fontSize: '0.85rem'}}>{b.curp}</div>
                      <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>📞 {b.phone}</div>
                    </td>
                    <td>
                      <span className="badge badge-info">{b.program}</span>
                    </td>
                    <td>
                      <span className={`badge ${b.status === 'Activo' ? 'badge-success' : 'badge-warning'}`}>
                        {b.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {filteredBeneficiaries.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{textAlign: 'center', padding: '2rem', color: 'var(--text-muted)'}}>
                      No hay beneficiarios registrados en el padrón.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
