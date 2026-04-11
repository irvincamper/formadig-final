import React, { createContext, useContext, useState, useEffect } from 'react';

// --- Tipos de Datos ---
export type Role = 'Admin' | 'Recepcion' | 'Nutriologo' | 'Admin_Desayunos' | 'Admin_Traslados' | 'Trabajador_Desayunos' | 'Trabajador_Traslados';

export interface User {
  id: string;
  name: string;
  role: Role;
  area?: 'Desayunos' | 'Traslados' | 'General';
}

export interface Beneficiary {
  id: string;
  fullName: string;
  curp: string;
  birthDate: string;
  phone: string;
  email: string;
  address: string;
  program: string;
  status: 'Activo' | 'Inactivo';
  registeredBy: string; // User ID
  registrationDate: string;
}

export interface Appointment {
  id: string;
  beneficiaryId: string;
  beneficiaryName: string;
  date: string; // YYYY-MM-DD
  time: string; // HH:MM
  area: 'Nutrición' | 'Psicología' | 'Trabajo Social' | 'General';
  reason: string;
  status: 'Pendiente' | 'Completada' | 'Cancelada';
  createdBy: string; // User ID
  createdAt: string;
}

export interface NutritionAlert {
  id: string;
  beneficiaryId: string;
  beneficiaryName: string;
  date: string;
  weight: number;
  height: number;
  imc: string;
  classification: string;
  type: 'success' | 'warning' | 'error' | 'info';
  createdBy: string;
}

export interface AuditLog {
  id: string;
  action: string;
  module: string;
  userId: string;
  userName: string;
  timestamp: string;
  details: string;
}

export interface BreakfastRegistration {
  id: string;
  beneficiaryName: string;
  curp: string;
  tutorName: string;
  tutorIne: string;
  sector: 'frios' | 'calientes' | 'eaeyd';
  documentsProvided: string[];
  date: string;
  createdBy: string;
}

// --- Interfaz del Contexto ---
interface AppContextType {
  currentUser: User | null;
  login: (user: User) => void;
  logout: () => void;
  
  beneficiaries: Beneficiary[];
  addBeneficiary: (b: Beneficiary) => void;
  updateBeneficiaryStatus: (id: string, status: 'Activo' | 'Inactivo') => void;
  
  appointments: Appointment[];
  addAppointment: (a: Appointment) => void;
  updateAppointmentStatus: (id: string, status: Appointment['status']) => void;
  
  nutritionAlerts: NutritionAlert[];
  addNutritionAlert: (alert: NutritionAlert) => void;
  
  auditLogs: AuditLog[];
  addAuditLog: (action: string, module: string, details: string) => void;
  
  breakfastRegistrations: BreakfastRegistration[];
  addBreakfastRegistration: (r: BreakfastRegistration) => void;
}

// Inicialización
const AppContext = createContext<AppContextType | undefined>(undefined);

const initialUsers: User[] = [
  { id: 'U-004', name: 'Laura Desayunos', role: 'Admin_Desayunos', area: 'Desayunos' },
  { id: 'U-006', name: 'Juan Apoyo', role: 'Trabajador_Desayunos', area: 'Desayunos' },
  { id: 'U-005', name: 'Carlos Traslados', role: 'Admin_Traslados', area: 'Traslados' },
  { id: 'U-007', name: 'Pedro Chofer', role: 'Trabajador_Traslados', area: 'Traslados' },
];

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Estado local
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [nutritionAlerts, setNutritionAlerts] = useState<NutritionAlert[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [breakfastRegistrations, setBreakfastRegistrations] = useState<BreakfastRegistration[]>([]);

  // Cargar de LocalStorage al inicio
  useEffect(() => {
    const savedUser = localStorage.getItem('dif_user');
    const savedBeneficiaries = localStorage.getItem('dif_beneficiaries');
    const savedAppointments = localStorage.getItem('dif_appointments');
    const savedAlerts = localStorage.getItem('dif_alerts');
    const savedLogs = localStorage.getItem('dif_logs');
    const savedBreakfasts = localStorage.getItem('dif_breakfasts');

    if (savedUser) setCurrentUser(JSON.parse(savedUser));
    if (savedBeneficiaries) setBeneficiaries(JSON.parse(savedBeneficiaries));
    if (savedAppointments) setAppointments(JSON.parse(savedAppointments));
    if (savedAlerts) setNutritionAlerts(JSON.parse(savedAlerts));
    if (savedLogs) setAuditLogs(JSON.parse(savedLogs));
    if (savedBreakfasts) setBreakfastRegistrations(JSON.parse(savedBreakfasts));
  }, []);

  // Efectos para guardar en LocalStorage cada vez que cambien
  useEffect(() => localStorage.setItem('dif_user', JSON.stringify(currentUser)), [currentUser]);
  useEffect(() => localStorage.setItem('dif_beneficiaries', JSON.stringify(beneficiaries)), [beneficiaries]);
  useEffect(() => localStorage.setItem('dif_appointments', JSON.stringify(appointments)), [appointments]);
  useEffect(() => localStorage.setItem('dif_alerts', JSON.stringify(nutritionAlerts)), [nutritionAlerts]);
  useEffect(() => localStorage.setItem('dif_logs', JSON.stringify(auditLogs)), [auditLogs]);
  useEffect(() => localStorage.setItem('dif_breakfasts', JSON.stringify(breakfastRegistrations)), [breakfastRegistrations]);

  // Funciones y Helpers
  const _addAuditLog = (action: string, module: string, details: string, user: User | null) => {
    if (!user) return;
    const newLog: AuditLog = {
      id: `LOG-${Date.now()}`,
      action,
      module,
      userId: user.id,
      userName: user.name,
      timestamp: new Date().toISOString(),
      details
    };
    setAuditLogs(prev => [newLog, ...prev]);
  };

  const addAuditLog = (action: string, module: string, details: string) => {
    _addAuditLog(action, module, details, currentUser);
  };

  const login = (user: User) => {
    setCurrentUser(user);
    _addAuditLog('LOGIN', 'Auth', 'Inicio de sesión exitoso', user);
  };

  const logout = () => {
    _addAuditLog('LOGOUT', 'Auth', 'Cierre de sesión', currentUser);
    setCurrentUser(null);
  };

  const addBeneficiary = (b: Beneficiary) => {
    setBeneficiaries(prev => [...prev, b]);
    addAuditLog('CREAR', 'Expedientes', `Expediente creado: ${b.fullName} (${b.id})`);
  };

  const updateBeneficiaryStatus = (id: string, status: 'Activo' | 'Inactivo') => {
    setBeneficiaries(prev => prev.map(b => b.id === id ? { ...b, status } : b));
    addAuditLog('ACTUALIZAR', 'Expedientes', `Status actualizado a ${status} para expediente ID: ${id}`);
  };

  const addAppointment = (a: Appointment) => {
    setAppointments(prev => [...prev, a]);
    addAuditLog('CREAR', 'Citas', `Cita agendada para ${a.beneficiaryName} en ${a.area}`);
  };

  const updateAppointmentStatus = (id: string, status: Appointment['status']) => {
    setAppointments(prev => prev.map(a => a.id === id ? { ...a, status } : a));
    addAuditLog('ACTUALIZAR', 'Citas', `Status actualizado a ${status} para cita ID: ${id}`);
  };

  const addNutritionAlert = (alert: NutritionAlert) => {
    setNutritionAlerts(prev => [alert, ...prev]);
    addAuditLog('ALERTA', 'Nutrición', `Alerta nutricional generada para: ${alert.beneficiaryName} [${alert.classification}]`);
  };

  const addBreakfastRegistration = (r: BreakfastRegistration) => {
    setBreakfastRegistrations(prev => [r, ...prev]);
    addAuditLog('CREAR', 'Desayunos', `Registro de desayuno en sector ${r.sector} creado para: ${r.beneficiaryName}`);
  };

  return (
    <AppContext.Provider value={{
      currentUser,
      login,
      logout,
      beneficiaries,
      addBeneficiary,
      updateBeneficiaryStatus,
      appointments,
      addAppointment,
      updateAppointmentStatus,
      nutritionAlerts,
      addNutritionAlert,
      auditLogs,
      addAuditLog,
      breakfastRegistrations,
      addBreakfastRegistration
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext debe usarse dentro de un AppProvider');
  }
  return context;
};

// Exportar usuarios simulados para el login
export const MOCK_USERS = initialUsers;
