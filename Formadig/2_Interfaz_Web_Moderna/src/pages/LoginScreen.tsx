import React, { useState } from 'react';
import { useAppContext, MOCK_USERS, type User, type Role } from '../core/AppContext';
import logoFormadig from '../assets/logo/logo_formadig.png';

export const LoginScreen: React.FC = () => {
  const { login } = useAppContext();
  const [mode, setMode] = useState<'select' | 'signup'>('select');
  const [selectedUserId, setSelectedUserId] = useState<string>('');
  const [newUserName, setNewUserName] = useState<string>('');
  const [newUserRole, setNewUserRole] = useState<Role>('Trabajador_Desayunos');
  const [error, setError] = useState<string>('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUserId) {
      setError('Por favor, selecciona un perfil para ingresar.');
      return;
    }

    const userToLogin = MOCK_USERS.find(u => u.id === selectedUserId);
    if (userToLogin) {
      login(userToLogin);
    } else {
      setError('Usuario no encontrado.');
    }
  };

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUserName.trim()) {
      setError('Por favor, ingresa tu nombre.');
      return;
    }

    // Simulamos la creación de cuenta
    const simulatedUser: User = {
      id: `U-SIM-${Date.now()}`,
      name: newUserName,
      role: newUserRole,
      area: newUserRole.includes('Desayunos') ? 'Desayunos' : newUserRole.includes('Traslados') ? 'Traslados' : 'General'
    };
    
    login(simulatedUser);
  };

  const roles = [
    { value: 'Admin_Desayunos', label: 'Administrador de Desayunos' },
    { value: 'Admin_Traslados', label: 'Administrador de Traslados' },
    { value: 'Trabajador_Desayunos', label: 'Trabajador de Desayunos' },
    { value: 'Trabajador_Traslados', label: 'Trabajador de Traslados' },
  ];

  return (
    <div className="login-container">
      <div className="login-box glass-panel fade-in">
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <img 
            src={logoFormadig} 
            alt="Formadig Logo" 
            style={{ 
              margin: '0 auto 10px', 
              width: '150px', 
              height: 'auto', 
              display: 'block'
            }} 
          />
          <h2 style={{ color: 'var(--primary-dark)', margin: 0 }}>Acceso al Sistema</h2>
          <p style={{ color: 'var(--text-muted)' }}>Gestión DIF Acatlán</p>
        </div>

        <div className="login-tabs">
          <button 
            className={`tab-btn ${mode === 'select' ? 'active' : ''}`}
            onClick={() => { setMode('select'); setError(''); }}
          >
            Seleccionar Perfil
          </button>
          <button 
            className={`tab-btn ${mode === 'signup' ? 'active' : ''}`}
            onClick={() => { setMode('signup'); setError(''); }}
          >
            Crear Cuenta (Simulado)
          </button>
        </div>

        {mode === 'select' ? (
          <form onSubmit={handleLogin} className="slide-up">
            <div className="form-group">
              <label className="form-label">Elige un perfil existente:</label>
              <select 
                className={`form-control ${error ? 'error' : ''}`}
                value={selectedUserId}
                onChange={e => {
                  setSelectedUserId(e.target.value);
                  setError('');
                }}
              >
                <option value="">-- Seleccionar --</option>
                {MOCK_USERS.map(user => (
                  <option key={user.id} value={user.id}>
                    {user.name} ({user.role})
                  </option>
                ))}
              </select>
            </div>
            <button type="submit" className="btn btn-primary w-100">Ingresar</button>
          </form>
        ) : (
          <form onSubmit={handleSignup} className="slide-up">
            <div className="form-group">
              <label className="form-label">Nombre Completo:</label>
              <input 
                type="text" 
                className="form-control"
                placeholder="Ej. Juan Pérez"
                value={newUserName}
                onChange={e => setNewUserName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Cargo / Área:</label>
              <select 
                className="form-control"
                value={newUserRole}
                onChange={e => setNewUserRole(e.target.value as Role)}
              >
                {roles.map(r => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>
            <button type="submit" className="btn btn-success w-100">Crear e Ingresar</button>
          </form>
        )}

        {error && <div className="error-text" style={{ marginTop: '1rem', textAlign: 'center' }}>{error}</div>}

        <div style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-light)' }}>
          <p>🔒 Entorno de Demostración Segura</p>
        </div>
      </div>

      <style>{`
        .login-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, var(--bg-app) 0%, #e2e8f0 100%);
          padding: 1rem;
        }
        .login-box {
          background: white;
          max-width: 450px;
          width: 100%;
          padding: 2.5rem 2rem;
          border-radius: var(--radius-lg);
          box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        }
        .login-tabs {
          display: flex;
          background: #f0f2f5;
          padding: 0.3rem;
          border-radius: var(--radius-md);
          margin-bottom: 2rem;
        }
        .tab-btn {
          flex: 1;
          padding: 0.7rem;
          border: none;
          background: transparent;
          cursor: pointer;
          border-radius: var(--radius-sm);
          font-weight: 500;
          color: var(--text-muted);
          transition: all 0.3s ease;
        }
        .tab-btn.active {
          background: white;
          color: var(--primary);
          box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        .form-group {
           margin-bottom: 1.5rem;
        }
        .w-100 {
          width: 100%;
        }
      `}</style>
    </div>
  );
};
