import React, { useState } from 'react';
import { useAppContext, type Appointment } from '../core/AppContext';

export const AppointmentsDashboard: React.FC = () => {
  const { appointments, addAppointment, updateAppointmentStatus, beneficiaries, currentUser } = useAppContext();
  
  const initialForm = {
    beneficiaryId: '',
    date: '',
    time: '',
    area: 'Nutrición' as Appointment['area'],
    reason: ''
  };

  const [formData, setFormData] = useState(initialForm);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [filterMode, setFilterMode] = useState<'all' | 'pending' | 'completed' | 'cancelled'>('all');

  // Filtrar solo beneficiarios activos para agendar
  const activeBeneficiaries = beneficiaries.filter(b => b.status === 'Activo');

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.beneficiaryId) newErrors.beneficiaryId = "Debes seleccionar un beneficiario";
    
    if (!formData.date) {
      newErrors.date = "La fecha es obligatoria";
    } else {
      const selectedDate = new Date(formData.date);
      const today = new Date();
      today.setHours(0, 0, 0, 0); // Comparar a nivel día
      
      // Permitir citas para hoy o para el futuro, sumando un día a la validacion por el huso horario
      const localDate = new Date(selectedDate.getTime() + Math.abs(selectedDate.getTimezoneOffset() * 60000));
      if (localDate < today) {
        newErrors.date = "No puedes agendar citas en el pasado";
      }
    }

    if (!formData.time) {
      newErrors.time = "La hora es obligatoria";
    }

    if (!formData.reason || formData.reason.trim().length < 5) {
      newErrors.reason = "Describe el motivo de la cita (min 5 caracteres)";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm() && currentUser) {
      const ben = beneficiaries.find(b => b.id === formData.beneficiaryId);
      if (!ben) return;

      const newAppt: Appointment = {
        id: `APT-${Date.now().toString().slice(-6)}`,
        beneficiaryId: ben.id,
        beneficiaryName: ben.fullName,
        date: formData.date,
        time: formData.time,
        area: formData.area,
        reason: formData.reason.trim(),
        status: 'Pendiente',
        createdBy: currentUser.id,
        createdAt: new Date().toISOString()
      };
      
      addAppointment(newAppt);
      setFormData(initialForm);
      alert(`¡Cita agendada para ${ben.fullName} exitosamente!`);
    }
  };

  // Filtrar las citas que puede ver el usuario actual
  // Simplificaremos: Nutriólogo solo ve Nutrición. Los demás ven todo.
  const visibleAppointments = appointments.filter(a => {
    if (currentUser?.role === 'Nutriologo' && a.area !== 'Nutrición') return false;
    
    if (filterMode === 'pending') return a.status === 'Pendiente';
    if (filterMode === 'completed') return a.status === 'Completada';
    if (filterMode === 'cancelled') return a.status === 'Cancelada';
    return true; // all
  }).sort((a, b) => new Date(`${a.date}T${a.time}`).getTime() - new Date(`${b.date}T${b.time}`).getTime());

  return (
    <div className="slide-up">
      <div className="page-header">
        <div>
          <h2 className="page-title">Agenda y Citas</h2>
          <p className="page-subtitle">Programa y gestiona las citas de los beneficiarios</p>
        </div>
      </div>

      <div className="dashboard-grid">
        {(currentUser?.role === 'Admin' || currentUser?.role === 'Recepcion') && (
          <div className="card glass-panel dashboard-hero fade-in">
            <div className="card-header">
              <h3 className="card-title">📅 Agendar Nueva Cita</h3>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Beneficiario <span style={{color: 'var(--error)'}}>*</span></label>
                <select 
                  className={`form-control ${errors.beneficiaryId ? 'error' : ''}`}
                  value={formData.beneficiaryId}
                  onChange={e => {
                    setFormData({...formData, beneficiaryId: e.target.value});
                    if(errors.beneficiaryId) setErrors({...errors, beneficiaryId: ''});
                  }}
                >
                  <option value="">-- Selecciona el Expediente --</option>
                  {activeBeneficiaries.map(b => (
                    <option key={b.id} value={b.id}>{b.fullName} ({b.curp})</option>
                  ))}
                </select>
                {errors.beneficiaryId && <span className="error-text">{errors.beneficiaryId}</span>}
                {activeBeneficiaries.length === 0 && (
                  <span className="error-text" style={{color: 'var(--warning)', marginTop: '0.5rem'}}>
                    No hay beneficiarios activos registrados.
                  </span>
                )}
              </div>
              
              <div className="form-row">
                <div className="form-group form-col">
                  <label className="form-label">Fecha <span style={{color: 'var(--error)'}}>*</span></label>
                  <input 
                    type="date" 
                    className={`form-control ${errors.date ? 'error' : ''}`}
                    value={formData.date}
                    onChange={e => {
                      setFormData({...formData, date: e.target.value});
                      if(errors.date) setErrors({...errors, date: ''});
                    }}
                  />
                  {errors.date && <span className="error-text">{errors.date}</span>}
                </div>
                <div className="form-group form-col">
                  <label className="form-label">Hora <span style={{color: 'var(--error)'}}>*</span></label>
                  <input 
                    type="time" 
                    className={`form-control ${errors.time ? 'error' : ''}`}
                    value={formData.time}
                    onChange={e => {
                      setFormData({...formData, time: e.target.value});
                      if(errors.time) setErrors({...errors, time: ''});
                    }}
                  />
                  {errors.time && <span className="error-text">{errors.time}</span>}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group form-col">
                  <label className="form-label">Área de Atención <span style={{color: 'var(--error)'}}>*</span></label>
                  <select 
                    className="form-control"
                    value={formData.area}
                    onChange={e => setFormData({...formData, area: e.target.value as Appointment['area']})}
                  >
                    <option value="Nutrición">Nutrición</option>
                    <option value="Psicología">Psicología</option>
                    <option value="Trabajo Social">Trabajo Social</option>
                    <option value="General">Atención General</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Motivo de la Cita <span style={{color: 'var(--error)'}}>*</span></label>
                <textarea 
                  className={`form-control ${errors.reason ? 'error' : ''}`}
                  value={formData.reason}
                  onChange={e => {
                    setFormData({...formData, reason: e.target.value});
                    if(errors.reason) setErrors({...errors, reason: ''});
                  }}
                  placeholder="Ej. Valoración inicial, Seguimiento de despensa, etc."
                  rows={3}
                />
                {errors.reason && <span className="error-text">{errors.reason}</span>}
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
                <button type="submit" className="btn btn-primary" style={{ padding: '0.8rem 1.5rem', fontSize: '1rem' }}>
                  Agendar Cita
                </button>
              </div>
            </form>
          </div>
        )}

        <div className={`card glass-panel fade-in ${(currentUser?.role === 'Nutriologo') ? 'col-span-full' : ''}`} style={{animationDelay: '0.1s'}}>
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
            <h3 className="card-title">🧾 Agenda de Citas</h3>
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
              <button 
                className={`btn ${filterMode === 'all' ? 'btn-primary' : 'btn-secondary'}`} 
                onClick={() => setFilterMode('all')}
                style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}
              >Todas</button>
              <button 
                className={`btn ${filterMode === 'pending' ? 'btn-primary' : 'btn-secondary'}`} 
                onClick={() => setFilterMode('pending')}
                style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}
              >Pendientes</button>
            </div>
          </div>
          
          <div className="table-container" style={{ marginTop: '1rem' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Fecha/Hora</th>
                  <th>Beneficiario</th>
                  <th>Área / Motivo</th>
                  <th>Estatus</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {visibleAppointments.map(a => (
                  <tr key={a.id}>
                    <td>
                      <div style={{fontWeight: 600}}>{a.date}</div>
                      <div style={{fontSize: '0.85rem', color: 'var(--text-muted)'}}>🕣 {a.time} hrs</div>
                    </td>
                    <td>
                      <div style={{fontWeight: 500}}>{a.beneficiaryName}</div>
                      <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Folio: <span style={{fontFamily: 'monospace'}}>{a.beneficiaryId}</span></div>
                    </td>
                    <td>
                      <span className="badge badge-info">{a.area}</span>
                      <div style={{fontSize: '0.85rem', color: 'var(--text-main)', marginTop: '0.3rem', maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}} title={a.reason}>
                        {a.reason}
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${
                        a.status === 'Pendiente' ? 'badge-warning' : 
                        a.status === 'Completada' ? 'badge-success' : 'badge-error'
                      }`}>
                        {a.status}
                      </span>
                    </td>
                    <td>
                      {a.status === 'Pendiente' && (
                        <div style={{ display: 'flex', gap: '0.4rem' }}>
                          <button 
                            className="btn btn-secondary" 
                            style={{padding: '0.4rem 0.5rem', fontSize: '0.8rem', color: 'var(--success)'}}
                            onClick={() => {
                              if(window.confirm(`¿Marcar la cita como COMPLETADA?`)) {
                                updateAppointmentStatus(a.id, 'Completada');
                              }
                            }}
                            title="Completar"
                          >
                            ✓
                          </button>
                          <button 
                            className="btn btn-secondary" 
                            style={{padding: '0.4rem 0.5rem', fontSize: '0.8rem', color: 'var(--error)'}}
                            onClick={() => {
                              if(window.confirm(`¿Seguro que deseas CANCELAR esta cita?`)) {
                                updateAppointmentStatus(a.id, 'Cancelada');
                              }
                            }}
                            title="Cancelar"
                          >
                            ×
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
                {visibleAppointments.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{textAlign: 'center', padding: '2rem', color: 'var(--text-muted)'}}>
                      No hay citas programadas para mostrar.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <style>{`
        .col-span-full { grid-column: 1 / -1; }
      `}</style>
    </div>
  );
};
