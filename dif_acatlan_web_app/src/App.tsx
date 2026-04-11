import { useState } from 'react';
import { AppProvider, useAppContext } from './core/AppContext';
import { LoginScreen } from './pages/LoginScreen';
import { AdminDashboard } from './pages/AdminDashboard';
import { NutritionDashboard } from './pages/NutritionDashboard';
import { AppointmentsDashboard } from './pages/AppointmentsDashboard';
import { BreakfastsDashboard } from './pages/BreakfastsDashboard';
import { TrasladosDashboard } from './pages/TrasladosDashboard';

function MainLayout() {
  const { currentUser, logout } = useAppContext();
  const [activeView, setActiveView] = useState<'admin' | 'nutrition' | 'appointments' | 'reports' | 'breakfasts' | 'traslados'>('admin');

  // Si no hay usuario, forzamos Login
  if (!currentUser) return <LoginScreen />;

  // Control de Acceso (RBAC)
  const canViewAdmin = currentUser.role === 'Admin' || currentUser.role === 'Recepcion';
  const canViewNutrition = currentUser.role === 'Admin' || currentUser.role === 'Nutriologo';
  const canViewAppointments = currentUser.role === 'Admin' || currentUser.role === 'Recepcion' || currentUser.role === 'Nutriologo';
  const canViewReports = currentUser.role === 'Admin';
  const canViewBreakfasts = currentUser.role === 'Admin' || currentUser.role === 'Admin_Desayunos' || currentUser.role === 'Trabajador_Desayunos';
  const canViewTraslados = currentUser.role === 'Admin' || currentUser.role === 'Admin_Traslados' || currentUser.role === 'Trabajador_Traslados';

  // Render condicional de la vista principal según el menú activo y permisos
  const renderActiveView = () => {
    switch (activeView) {
      case 'admin':
        return canViewAdmin ? <AdminDashboard /> : <div className="p-4">Acceso Denegado</div>;
      case 'nutrition':
        return canViewNutrition ? <NutritionDashboard /> : <div className="p-4">Acceso Denegado</div>;
      case 'appointments':
        return canViewAppointments ? <AppointmentsDashboard /> : <div className="p-4">Acceso Denegado</div>;
      case 'reports':
        return canViewReports ? <div className="p-4">Módulo de Reportes (En construcción)</div> : null;
      case 'breakfasts':
        return canViewBreakfasts ? <BreakfastsDashboard /> : <div className="p-4">Acceso Denegado</div>;
      case 'traslados':
        return canViewTraslados ? <TrasladosDashboard /> : <div className="p-4">Acceso Denegado</div>;
      default:
        return <div>Vista no encontrada</div>;
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">DIF</div>
          <div className="sidebar-title">
            Sistema de <br /> Gestión Acatlán
          </div>
        </div>
        
        <nav className="nav-menu">
          {canViewAdmin && (
            <div 
              className={`nav-item ${activeView === 'admin' ? 'active' : ''}`}
              onClick={() => setActiveView('admin')}
            >
              <span className="nav-item-icon">🗂️</span>
              <span>Expedientes</span>
            </div>
          )}
          
          {canViewAppointments && (
            <div 
              className={`nav-item ${activeView === 'appointments' ? 'active' : ''}`}
              onClick={() => setActiveView('appointments')}
            >
              <span className="nav-item-icon">📅</span>
              <span>Agenda y Citas</span>
            </div>
          )}

          {canViewNutrition && (
            <div 
              className={`nav-item ${activeView === 'nutrition' ? 'active' : ''}`}
              onClick={() => setActiveView('nutrition')}
            >
              <span className="nav-item-icon">🥗</span>
              <span>Nutrición</span>
            </div>
          )}

          {canViewBreakfasts && (
            <div 
              className={`nav-item ${activeView === 'breakfasts' ? 'active' : ''}`}
              onClick={() => setActiveView('breakfasts')}
            >
              <span className="nav-item-icon">🍱</span>
              <span>Desayunos</span>
            </div>
          )}

          {canViewTraslados && (
            <div 
              className={`nav-item ${activeView === 'traslados' ? 'active' : ''}`}
              onClick={() => setActiveView('traslados')}
            >
              <span className="nav-item-icon">🚑</span>
              <span>Traslados</span>
            </div>
          )}

          {canViewReports && (
            <div 
              className={`nav-item ${activeView === 'reports' ? 'active' : ''}`}
              onClick={() => setActiveView('reports')}
            >
              <span className="nav-item-icon">📊</span>
              <span>Reportes y Auditoría</span>
            </div>
          )}
        </nav>

        <div className="user-profile">
          <div className="avatar">{currentUser.name.charAt(0)}</div>
          <div style={{ flex: 1 }}>
            <div style={{fontSize: '0.85rem', color: 'rgba(255,255,255,0.7)'}}>{currentUser.role}</div>
            <div style={{fontWeight: 600, fontSize: '0.90rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
              {currentUser.name}
            </div>
          </div>
          <button 
            onClick={logout} 
            className="btn btn-secondary" 
            style={{ padding: '0.4rem', fontSize: '0.8rem', background: 'rgba(255,255,255,0.1)', color: 'white', border: 'none' }}
            title="Cerrar Sessión"
          >
            ❌
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        {renderActiveView()}
      </main>
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <MainLayout />
    </AppProvider>
  );
}

export default App;
