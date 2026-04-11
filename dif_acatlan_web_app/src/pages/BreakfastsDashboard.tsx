import React, { useState } from 'react';
import { useAppContext, type BreakfastRegistration } from '../core/AppContext';

type Sector = 'frios' | 'calientes' | 'eaeyd' | null;
type Tab = 'info' | 'records' | 'new_record';

export const BreakfastsDashboard: React.FC = () => {
  const { breakfastRegistrations, addBreakfastRegistration, currentUser } = useAppContext();
  const [selectedSector, setSelectedSector] = useState<Sector>(null);
  const [activeTab, setActiveTab] = useState<Tab>('info');

  // Form State
  const [beneficiaryName, setBeneficiaryName] = useState('');
  const [curp, setCurp] = useState('');
  const [tutorName, setTutorName] = useState('');
  const [tutorIne, setTutorIne] = useState('');
  const [curpFile, setCurpFile] = useState<File | null>(null);
  const [ineFile, setIneFile] = useState<File | null>(null);
  const [error, setError] = useState('');

  const sectors = [
    { 
      id: 'frios' as const, 
      title: 'Desayunos Fríos', 
      icon: '❄️', 
      color: 'info',
      description: 'Programas de apoyo alimentario con insumos no procesados y leche.',
      docs: [
        'Acta de nacimiento del menor',
        'CURP del menor y tutor',
        'Comprobante de domicilio',
        'Estudio socioeconómico',
        'Copia de Credencial de Elector del Padre/Tutor'
      ],
      info: {
        population: 'Niñas, niños y adolescentes en condiciones de vulnerabilidad.',
        delivery: 'Entregas mensuales en los centros escolares asignados.'
      }
    },
    { 
      id: 'calientes' as const, 
      title: 'Desayunos Calientes', 
      icon: '🔥', 
      color: 'warning',
      description: 'Raciones alimentarias preparadas con altos estándares nutricionales.',
      docs: [
        'Constancia de Inscripción escolar vigente',
        'Recibo de cuota de recuperación',
        'Carta compromiso de participación en el comité',
        'Copia de Credencial de Elector del Padre/Tutor'
      ],
      info: {
        population: 'NNA en escuelas con cocina comunitaria instalada.',
        delivery: 'Preparación diaria en el plantel escolar.'
      }
    },
    { 
      id: 'eaeyd' as const, 
      title: 'Espacios EAEyD', 
      icon: '🍎', 
      color: 'success',
      description: 'Asistencia Alimentaria a Grupos en Situación de Vulnerabilidad.',
      docs: [
        'Identificación oficial (INE) del beneficiario o tutor',
        'CURP',
        'Certificado médico original (en caso de discapacidad)',
        'Comprobante de ingresos mensual'
      ],
      info: {
        population: 'Personas con discapacidad, adultos mayores y mujeres embarazadas.',
        delivery: 'Apoyos bimestrales directos en las oficinas del DIF.'
      }
    }
  ];

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    if (!beneficiaryName || !curp || !tutorName || !tutorIne) {
      setError('Por favor completa todos los campos obligatorios del registro.');
      return;
    }

    if (!currentUser || !selectedSector) return;

    const newReg: BreakfastRegistration = {
      id: `BRK-${Date.now()}`,
      beneficiaryName,
      curp,
      tutorName,
      tutorIne,
      sector: selectedSector,
      documentsProvided: [],
      date: new Date().toISOString().split('T')[0],
      createdBy: currentUser.name
    };

    console.log("Simulating file upload for:", curpFile?.name, ineFile?.name);
    addBreakfastRegistration(newReg);
    
    // Reset form
    setBeneficiaryName('');
    setCurp('');
    setTutorName('');
    setTutorIne('');
    setCurpFile(null);
    setIneFile(null);
    setError('');
    setActiveTab('records');
  };

  const renderSelection = () => (
    <div className="slide-up">
      <div className="page-header">
        <div>
          <h2 className="page-title">Programas de Alimentación</h2>
          <p className="page-subtitle">Selecciona el sector al que deseas ingresar para gestionar registros e información</p>
        </div>
      </div>

      <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginTop: '2rem' }}>
        {sectors.map(sector => (
          <div 
            key={sector.id} 
            className="card glass-panel fade-in sector-card"
            onClick={() => { setSelectedSector(sector.id); setActiveTab('info'); }}
            style={{ 
              cursor: 'pointer', 
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center',
              padding: '3rem 2rem'
            }}
          >
            <div style={{ 
              fontSize: '4rem', marginBottom: '1.5rem',
              background: `var(--${sector.color}-bg)`, width: '100px', height: '100px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderRadius: '50%', boxShadow: `0 10px 20px -5px var(--${sector.color})`
            }}>
              {sector.icon}
            </div>
            <h3 className="card-title" style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>{sector.title}</h3>
            <p style={{ color: 'var(--text-muted)', lineHeight: '1.6' }}>{sector.description}</p>
            <div style={{ marginTop: '2rem' }}>
              <button className={`btn btn-${sector.color}`}>Ingresar al Sector</button>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .sector-card:hover { transform: translateY(-10px); box-shadow: 0 20px 40px rgba(0,0,0,0.1); border-color: var(--primary); }
      `}</style>
    </div>
  );

  const renderDetail = () => {
    const sector = sectors.find(s => s.id === selectedSector);
    if (!sector) return null;

    const sectorRecords = breakfastRegistrations.filter(r => r.sector === sector.id);

    return (
      <div className="slide-up">
        <div className="page-header" style={{ marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button 
              onClick={() => setSelectedSector(null)}
              className="btn btn-secondary"
              style={{ padding: '0.5rem 1rem' }}
            >
              ⬅️ Volver
            </button>
            <div>
              <h2 className="page-title">{sector.icon} {sector.title}</h2>
              <p className="page-subtitle">Gestión operativa del padrón de beneficiarios</p>
            </div>
          </div>
        </div>

        <div className="tabs" style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border-color)', marginBottom: '2rem' }}>
          <button className={`tab-btn ${activeTab === 'info' ? 'active' : ''}`} onClick={() => setActiveTab('info')} style={tabStyle(activeTab === 'info')}>
            Información y Requisitos
          </button>
          <button className={`tab-btn ${activeTab === 'records' ? 'active' : ''}`} onClick={() => setActiveTab('records')} style={tabStyle(activeTab === 'records')}>
            Padrón Existente ({sectorRecords.length})
          </button>
          <button className={`tab-btn ${activeTab === 'new_record' ? 'active' : ''}`} onClick={() => setActiveTab('new_record')} style={tabStyle(activeTab === 'new_record')}>
            + Nuevo Registro
          </button>
        </div>

        {activeTab === 'info' && (
          <div className="dashboard-grid fade-in">
            <div className="card glass-panel" style={{ gridColumn: '1 / -1' }}>
              <h3 className="card-title">🗒️ Descripción General</h3>
              <p style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>{sector.description}</p>
              <div style={{ marginTop: '1.5rem', padding: '1.5rem', background: `var(--${sector.color}-bg)`, borderLeft: `6px solid var(--${sector.color})` }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: `var(--${sector.color})` }}>Población Objetivo:</h4>
                <p style={{ margin: 0, fontWeight: 500 }}>{sector.info.population}</p>
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                  <p style={{ margin: 0 }}><strong>Logística:</strong> {sector.info.delivery}</p>
                </div>
              </div>
            </div>
            <div className="card glass-panel" style={{ gridColumn: '1 / -1' }}>
               <h3 className="card-title">✅ Documentos Obligatorios para Registro</h3>
               <ul style={{ listStyle: 'none', padding: 0, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                 {sector.docs.map((doc, idx) => (
                   <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', background: 'rgba(255,255,255,0.4)' }}>
                     <span style={{ color: 'var(--success)' }}>✔</span> {doc}
                   </li>
                 ))}
               </ul>
            </div>
          </div>
        )}

        {activeTab === 'records' && (
          <div className="card glass-panel fade-in">
            <h3 className="card-title">Lista de Beneficiarios Inscritos</h3>
            {sectorRecords.length === 0 ? (
              <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem 0' }}>No hay beneficiarios registrados en este sector aún.</p>
            ) : (
              <table className="data-table" style={{ width: '100%', marginTop: '1rem' }}>
                <thead>
                  <tr style={{ background: 'var(--bg-color)', textAlign: 'left' }}>
                    <th style={{ padding: '1rem' }}>Fecha</th>
                    <th style={{ padding: '1rem' }}>Beneficiario</th>
                    <th style={{ padding: '1rem' }}>CURP</th>
                    <th style={{ padding: '1rem' }}>Tutor Legal</th>
                  </tr>
                </thead>
                <tbody>
                  {sectorRecords.map(r => (
                    <tr key={r.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ padding: '1rem' }}>{r.date}</td>
                      <td style={{ padding: '1rem', fontWeight: 600 }}>{r.beneficiaryName}</td>
                      <td style={{ padding: '1rem' }}>{r.curp}</td>
                      <td style={{ padding: '1rem' }}>{r.tutorName}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === 'new_record' && (
          <form className="card glass-panel fade-in" onSubmit={handleRegister}>
            <h3 className="card-title">Formulario de Inscripción al Programa</h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem', marginTop: '1.5rem' }}>
              <div className="form-group">
                <label className="form-label">Nombre completo del Beneficiario *</label>
                <input type="text" className="form-control" value={beneficiaryName} onChange={e=>setBeneficiaryName(e.target.value)} placeholder="Nombre del menor o persona" required />
              </div>
              <div className="form-group">
                <label className="form-label">CURP del Beneficiario *</label>
                <input type="text" className="form-control" value={curp} onChange={e=>setCurp(e.target.value)} maxLength={18} placeholder="18 Caracteres" style={{ textTransform: 'uppercase' }} required />
              </div>
              <div className="form-group">
                <label className="form-label">Nombre del Padre o Tutor Legal *</label>
                <input type="text" className="form-control" value={tutorName} onChange={e=>setTutorName(e.target.value)} placeholder="Madre, Padre o Tutor" required />
              </div>
              <div className="form-group">
                <label className="form-label">Clave Elector (INE) del Tutor *</label>
                <input type="text" className="form-control" value={tutorIne} onChange={e=>setTutorIne(e.target.value)} placeholder="Aparece en la credencial para votar" required />
                <small style={{ color: 'var(--text-muted)' }}>* Es obligatorio presentar credencial vigente para el registro.</small>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem', padding: '1.5rem', border: '1px dashed var(--border-color)', borderRadius: 'var(--radius-sm)' }}>
              <div className="form-group">
                <label className="form-label" htmlFor="curpFile">Subir Documento CURP (PDF o Imagen)</label>
                <input 
                  type="file" 
                  id="curpFile"
                  className="form-control" 
                  accept=".pdf,.png,.jpg,.jpeg" 
                  onChange={e => setCurpFile(e.target.files ? e.target.files[0] : null)}
                  style={{ padding: '0.6rem' }}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="ineFile">Subir Documento INE Tutor (PDF o Imagen)</label>
                <input 
                  type="file" 
                  id="ineFile"
                  className="form-control" 
                  accept=".pdf,.png,.jpg,.jpeg" 
                  onChange={e => setIneFile(e.target.files ? e.target.files[0] : null)}
                  style={{ padding: '0.6rem' }}
                />
              </div>
            </div>

            {error && <div className="error-text" style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(244, 67, 54, 0.1)', borderLeft: '4px solid var(--error)' }}>{error}</div>}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
              <button type="button" className="btn btn-secondary" onClick={() => setActiveTab('records')}>Cancelar</button>
              <button type="submit" className="btn btn-primary" style={{ padding: '0.8rem 2rem', fontSize: '1.1rem' }}>Guardar Registro Definitivo</button>
            </div>
          </form>
        )}
      </div>
    );
  };

  return selectedSector ? renderDetail() : renderSelection();
};

const tabStyle = (isActive: boolean) => ({
  padding: '1rem 1.5rem',
  background: 'transparent',
  border: 'none',
  borderBottom: isActive ? '3px solid var(--primary)' : '3px solid transparent',
  color: isActive ? 'var(--primary-dark)' : 'var(--text-muted)',
  fontWeight: isActive ? 600 : 500,
  fontSize: '1rem',
  cursor: 'pointer',
  transition: 'all 0.2s',
});
