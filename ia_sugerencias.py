import csv
from collections import Counter
from pathlib import Path

# Umbral mínimo de recurrencia para sugerir algo
THRESHOLD = 2  # poner en 1 si querés ver TODO

CSV_PATH = Path("data/events_demo.csv")  # ajustár el nombre si tu CSV se llama distinto

def cargar_eventos(csv_path: Path):
    print(f"[DEBUG] Buscando CSV en: {csv_path.resolve()}")
    if not csv_path.exists():
        print("[ERROR] No se encontró el archivo CSV. Verificá la ruta y el nombre.")
        return []

    eventos = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print(f"[DEBUG] Columnas detectadas: {reader.fieldnames}")
        for row in reader:
            # Usamos los nombres EXACTOS de tu CSV
            evento = {
                "timestamp": row.get("Timestamp", ""),
                "ip": row.get("IP", ""),
                "port": row.get("Port", ""),
                "method": row.get("Method", ""),
                "path": row.get("Path", ""),
                "status": row.get("Status", ""),
                "rule_id": row.get("Rule ID", ""),
                "rule_message": row.get("Rule Message", ""),
                "rule_severity": row.get("Rule Severity", ""),
                "rule_data": row.get("Rule Data", ""),
            }
            eventos.append(evento)

    print(f"[DEBUG] Eventos cargados: {len(eventos)}")
    return eventos

def agrupar(eventos):
    contador = Counter()
    for ev in eventos:
        key = (ev["rule_id"], ev["path"], ev["status"])
        contador[key] += 1
    print(f"[DEBUG] Claves agrupadas: {len(contador)}")
    return contador

def generar_sugerencias(contador):
    sugerencias = []
    for (rule_id, path, status), count in contador.items():
        if not rule_id or not path:
            continue
        if count < THRESHOLD:
            continue

        # Consideramos bloqueos cuando el status es 403 o el mensaje suele implicar bloqueo
        status_str = str(status)
        bloquea = status_str.startswith("403")

        if bloquea:
            descripcion = (
                f"La regla {rule_id} se disparó {count} veces devolviendo estado {status} "
                f"en la ruta {path}. Posible falso positivo; revisar el contexto y parámetros."
            )
        else:
            descripcion = (
                f"La regla {rule_id} se disparó {count} veces en la ruta {path} con estado {status}. "
                f"Sugerencia: evaluar si corresponde endurecer la regla para este endpoint."
            )

        snippet = (
            f'SecRule REQUEST_URI "@beginsWith {path}" '
            f'"id:{rule_id}01,phase:2,pass,t:none,ctl:ruleRemoveById={rule_id}"'
        )

        sugerencias.append({
            "rule_id": rule_id,
            "path": path,
            "status": status,
            "count": count,
            "descripcion": descripcion,
            "snippet": snippet,
        })

    print(f"[DEBUG] Sugerencias generadas: {len(sugerencias)}")
    return sugerencias

def main():
    print("=== Módulo IA ligera: análisis de eventos WAF ===")
    eventos = cargar_eventos(CSV_PATH)
    if not eventos:
        print("[WARN] No se cargaron eventos desde el CSV.")
        return

    contador = agrupar(eventos)
    sugerencias = generar_sugerencias(contador)

    if not sugerencias:
        print("No se encontraron patrones recurrentes que ameriten sugerencias.")
        return

    print("\n=== Sugerencias de reglas ===\n")
    for s in sugerencias:
        print(f"- Regla {s['rule_id']} en {s['path']} (ocurrencias: {s['count']}, status {s['status']})")
        print(f"  {s['descripcion']}")
        print("  Snippet sugerido:")
        print(f"    {s['snippet']}\n")

if __name__ == "__main__":
    main()
