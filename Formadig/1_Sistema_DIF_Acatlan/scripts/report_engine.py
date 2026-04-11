import json
from datetime import datetime

class ReportEngine:
    """
    Report Engine: Estructura modular para generar un reporte de auditoría.
    En la Fase 1, genera un reporte en texto plano estructurado.
    En la Fase 2, se puede extender para utilizar ReportLab (PDF) o Pandas (Excel).
    """
    def __init__(self):
        self.report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_audit_report(self, beneficiaries):
        report_lines = []
        report_lines.append("="*60)
        report_lines.append("SISTEMA DE GESTIÓN DIF ACATLÁN".center(60))
        report_lines.append("REPORTE DE AUDITORÍA ADMINISTRATIVA".center(60))
        report_lines.append(f"Fecha de Generación: {self.report_date}".center(60))
        report_lines.append("="*60)
        
        total = len(beneficiaries)
        activos = sum(1 for b in beneficiaries if b.get('status') == 'Activo')
        inactivos = total - activos
        
        report_lines.append(f"\nRESUMEN EJECUTIVO:")
        report_lines.append(f"- Total de Beneficiarios Registrados: {total}")
        report_lines.append(f"- Beneficiarios Activos: {activos}")
        report_lines.append(f"- Beneficiarios Inactivos: {inactivos}")
        
        report_lines.append("\nDETALLE DE EXPEDIENTES:")
        report_lines.append("-" * 60)
        for b in beneficiaries:
            report_lines.append(f"ID:   {b.get('id', 'N/A')}")
            report_lines.append(f"Nom:  {b.get('fullName', 'N/A')}")
            report_lines.append(f"CURP: {b.get('curp', 'N/A')}")
            report_lines.append(f"Est:  {b.get('status', 'N/A')}")
            report_lines.append("-" * 60)
            
        report_lines.append("\n--- FIN DEL REPORTE ---")
        
        return "\n".join(report_lines)

if __name__ == "__main__":
    print("--- Test: Report Engine Script ---")
    mock_db = [
        {"id": "BN-001", "fullName": "María García López", "curp": "GALM800101MDFRRN01", "status": "Activo"},
        {"id": "BN-002", "fullName": "Juan Pérez Ramos", "curp": "PERJ850505HDFRRN01", "status": "Inactivo"},
        {"id": "BN-003", "fullName": "Ana López Sánchez", "curp": "LOSA900202MDFRRX05", "status": "Activo"}
    ]
    
    engine = ReportEngine()
    informe = engine.generate_audit_report(mock_db)
    print(informe)
