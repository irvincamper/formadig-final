import React from 'react';
import { useAppContext } from '../core/AppContext';

export const ReportsDashboard: React.FC = () => {
  const { beneficiaries, appointments, nutritionAlerts, auditLogs } = useAppContext();

  // Cálculos rápidos (KPIs)
  const activeBeneficiaries = beneficiaries.filter(b => b.status === 'Activo').length;
  const inactiveBeneficiaries = beneficiaries.length - activeBeneficiaries;
  
  const pendingAppointments = appointments.filter(a => a.status === 'Pendiente').length;
  const completedAppointments = appointments.filter(a => a.status === 'Completada').length;
  const cancelledAppointments = appointments.filter(a => a.status === 'Cancelada').length;

  const criticalAlerts = nutritionAlerts.filter(a => a.type === 'error').length;
  const warningAlerts = nutritionAlerts.filter(a => a.type === 'warning').length;

  return (
    <div className="slide-up">
      <div className="page-header">
        <div>
          <h2 className="page-title">Reportes y Auditoría</h2>
          <p className="page-subtitle">Monitoreo general del sistema y registro de actividades</p>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card glass-panel dashboard-hero fade-in">
          <div className="card-header">
            <h3 className="card-title">📊 Resumen Estadístico (KPIs)</h3>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {/* KPI Expedientes */}
            <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.5)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary-dark)' }}>
                {beneficiaries.length}
              </div>
              <div style={{ fontWeight: 600, color: 'var(--text-main)', marginTop: '0.5rem' }}>Total Expedientes</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                <span style={{ color: 'var(--success)' }}>{activeBeneficiaries} Activos</span> | <span style={{ color: 'var(--error)' }}>{inactiveBeneficiaries} Inactivos</span>
              </div>
            </div>

            {/* KPI Citas */}
            <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.5)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary-dark)' }}>
                {appointments.length}
              </div>
              <div style={{ fontWeight: 600, color: 'var(--text-main)', marginTop: '0.5rem' }}>Citas Agendadas</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                {pendingAppointments} Pend. | {completedAppointments} Comp. | {cancelledAppointments} Canc.
              </div>
            </div>

            {/* KPI Nutrición */}
            <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.5)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary-dark)' }}>
                {nutritionAlerts.length}
              </div>
              <div style={{ fontWeight: 600, color: 'var(--text-main)', marginTop: '0.5rem' }}>Evals. Nutricionales</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                <span style={{ color: 'var(--error)' }}>{criticalAlerts} Críticas</span> | <span style={{ color: 'var(--warning)' }}>{warningAlerts} Precauciones</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card glass-panel fade-in" style={{ animationDelay: '0.1s', gridColumn: '1 / -1' }}>
          <div className="card-header">
            <h3 className="card-title">🛡️ Log de Auditoría (Actividad en Tiempo Real)</h3>
          </div>
          
          <div className="table-container" style={{ maxHeight: '400px', overflowY: 'auto' }}>
            <table className="table">
              <thead style={{ position: 'sticky', top: 0, background: 'var(--bg-color)', zIndex: 1 }}>
                <tr>
                  <th>Fecha y Hora</th>
                  <th>Usuario</th>
                  <th>Módulo</th>
                  <th>Acción</th>
                  <th>Detalles</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map(log => (
                  <tr key={log.id}>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {new Date(log.timestamp).toLocaleString('es-MX')}
                    </td>
                    <td>
                      <div style={{ fontWeight: 600 }}>{log.userName}</div>
                    </td>
                    <td><span className="badge badge-info">{log.module}</span></td>
                    <td>
                      <span className={`badge ${
                        log.action === 'LOGIN' ? 'badge-success' : 
                        log.action === 'LOGOUT' ? 'badge-warning' : 
                        log.action === 'CREAR' ? 'badge-success' :
                        log.action === 'ACTUALIZAR' ? 'badge-warning' :
                        log.action === 'ALERTA' ? 'badge-error' : 'badge-info'
                      }`}>
                        {log.action}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.9rem' }}>{log.details}</td>
                  </tr>
                ))}
                {auditLogs.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{textAlign: 'center', padding: '2rem', color: 'var(--text-muted)'}}>
                      No hay registros de actividad recientes en el sistema.
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
