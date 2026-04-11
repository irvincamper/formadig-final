import React from 'react';

export const TrasladosDashboard: React.FC = () => {
  return (
    <div className="slide-up">
      <div className="page-header">
        <div>
          <h2 className="page-title">Coordinación de Traslados</h2>
          <p className="page-subtitle">Gestión de ambulancias y traslados programados</p>
        </div>
        <div className="badge badge-info">Área Médica / Socorros</div>
      </div>

      <div className="dashboard-grid">
        <div className="card glass-panel fade-in">
          <div className="card-header">
            <h3 className="card-title">🚑 Unidades Disponibles</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ padding: '1rem', background: 'var(--success-bg)', borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--success)' }}>
              <div style={{ fontWeight: 'bold' }}>Ambulancia 01</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Estado: Operativa - En Base</div>
            </div>
            <div style={{ padding: '1rem', background: 'var(--warning-bg)', borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--warning)' }}>
              <div style={{ fontWeight: 'bold' }}>Ambulancia 02</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Estado: En Traslado (Pachuca)</div>
            </div>
          </div>
        </div>

        <div className="card glass-panel fade-in" style={{ animationDelay: '0.1s' }}>
          <div className="card-header">
            <h3 className="card-title">📅 Próximos Traslados</h3>
          </div>
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>
            No hay traslados programados para hoy.
          </p>
          <button className="btn btn-primary w-100">+ Programar Nuevo Traslado</button>
        </div>

        <div className="card glass-panel fade-in" style={{ animationDelay: '0.2s', gridColumn: '1 / -1' }}>
          <div className="card-header">
            <h3 className="card-title">👥 Equipo de guardia</h3>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div className="user-profile" style={{ background: 'rgba(255,255,255,0.5)', padding: '0.8rem', borderRadius: 'var(--radius-sm)' }}>
              <div className="avatar">P</div>
              <div>
                <div style={{ fontWeight: 600 }}>Pedro Chofer</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Operador de Unidad</div>
              </div>
            </div>
            <div className="user-profile" style={{ background: 'rgba(255,255,255,0.5)', padding: '0.8rem', borderRadius: 'var(--radius-sm)' }}>
              <div className="avatar">M</div>
              <div>
                <div style={{ fontWeight: 600 }}>Ma. Elena</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Paramédico</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card glass-panel fade-in" style={{ marginTop: '2rem', textAlign: 'center', borderStyle: 'dashed', borderColor: 'var(--primary-light)' }}>
         <h3 style={{ color: 'var(--primary)' }}>🚧 Módulo en Construcción</h3>
         <p>El administrador de traslados definirá las funciones específicas de este panel próximamente.</p>
      </div>

      <style>{`
        .w-100 { width: 100%; }
      `}</style>
    </div>
  );
};
