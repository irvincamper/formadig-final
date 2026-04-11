import json
import re

def clean_data(json_payload):
    """
    Data Cleaner: Recibe JSON, normaliza textos 
    (remueve espacios extra, capitalización adecuada).
    Principio SRP: Esta función solo se encarga de limpiar y estructurar los datos.
    """
    try:
        data = json.loads(json_payload)
    except json.JSONDecodeError:
        return {"error": "Formato JSON inválido"}

    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Usar regex para limpiar múltiples espacios continuos a uno solo
            clean_str = re.sub(r'\s+', ' ', value).strip()
            
            if key in ["fullName", "nombre"]:
                # Convertir a Title Case (ej: "juan perez" -> "Juan Perez")
                clean_str = clean_str.title()
            elif key == "curp":
                clean_str = clean_str.upper()
                
            cleaned_data[key] = clean_str
        else:
            cleaned_data[key] = value

    return cleaned_data

if __name__ == "__main__":
    print("--- Test: Data Cleaner Script ---")
    mock_payload = '{"fullName": "  JUAN   perez  RAMOS ", "curp": " perJ850505Hdfrrn01 ", "status": "Activo"}'
    print("Payload Original:", mock_payload)
    cleaned = clean_data(mock_payload)
    print("Payload Limpio:", json.dumps(cleaned, indent=2, ensure_ascii=False))
