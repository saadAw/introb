import os

# Projektstruktur als Dictionary
PROJECT_STRUCTURE = {
    "src": {
        "__init__.py": "# Initialisierung des src-Ordners",
        "main.py": """# Hauptprogramm für die Simulation

def main():
    print('Simulation der Intelligenten Robotik startet...')

if __name__ == '__main__':
    main()
""",
        "algorithms": {
            "__init__.py": "# Initialisierung des algorithms-Ordners",
            "a_star.py": """# A*-Algorithmus Implementierung

# Diese Datei enthält den Code für den A*-Algorithmus zur Pfadsuche in 2D-Umgebungen.
""",
            "reinforcement_learning.py": """# Reinforcement Learning Implementierung

# Diese Datei enthält Implementierungen grundlegender Reinforcement Learning-Algorithmen,
# wie z. B. Q-Learning oder Policy Gradient Methoden, die für die Simulation genutzt werden können.
""",
            "common.py": """# Gemeinsame Funktionen für Algorithmen

# Diese Datei enthält Hilfsmethoden und Tools, die von mehreren Algorithmen verwendet werden können,
# z. B. Heuristik-Berechnungen oder Datenstrukturen.
""",
        },
        "environment": {
            "__init__.py": "# Initialisierung des environment-Ordners",
            "map1.py": """# Karte 1: Definition der ersten Simulationsumgebung

# Diese Datei beschreibt die Eigenschaften und die Struktur der ersten Karte.
""",
            "map2.py": """# Karte 2: Definition der zweiten Simulationsumgebung

# Diese Datei beschreibt die Eigenschaften und die Struktur der zweiten Karte.
""",
            "obstacles.py": """# Hindernisdefinitionen

# Diese Datei enthält Funktionen oder Klassen zur Definition und Verwaltung von Hindernissen in der Umgebung.
""",
        },
        "utils": {
            "__init__.py": "# Initialisierung des utils-Ordners",
            "visualization.py": """# Visualisierungsfunktionen

# Diese Datei enthält Funktionen zur Visualisierung der Simulation und der Algorithmen mittels Pygame.
""",
            "logger.py": """# Logging-Funktionen

# Diese Datei enthält Funktionen zum Logging, um Ergebnisse oder Debugging-Informationen zu speichern.
""",
        },
        "tests": {
            "__init__.py": "# Initialisierung des tests-Ordners",
            "test_algorithms.py": """# Tests für Algorithmen

# Diese Datei enthält Unit-Tests zur Überprüfung der Algorithmen.
""",
            "test_environment.py": """# Tests für die Umgebung

# Diese Datei enthält Tests zur Überprüfung der Kartengenerierung und anderer Umgebungsfunktionen.
""",
        },
    },
    "data": {
        "maps": {
            "map1_config.json": "{\n  \"description\": \"Konfigurationsdatei für Karte 1\",\n  \"obstacles\": []\n}",
            "map2_config.json": "{\n  \"description\": \"Konfigurationsdatei für Karte 2\",\n  \"obstacles\": []\n}",
        },
        "logs": {
            "simulation.log": "# Log-Datei für Simulationsergebnisse\n",
        },
    },
    "docs": {
        "overview.md": """# Übersicht

Dieses Dokument enthält eine Beschreibung der Simulation sowie der Ziele und Anforderungen des Projekts.
""",
        "algorithm_comparison.md": """# Algorithmus-Vergleich

Dieses Dokument beschreibt die verschiedenen Algorithmen, die in der Simulation verwendet werden,
und vergleicht deren Leistung.
""",
    },
    ".gitignore": """# Gitignore-Datei

# Python-bezogene Ignorierungen
__pycache__/
*.pyc
*.pyo

# Logs
data/logs/

# Virtuelle Umgebungen
env/
venv/
""",
    "README.md": """# Introb - Intelligente Robotik Simulation

Dieses Projekt dient als Framework für die Simulation von Algorithmen in einer 2D-Umgebung mit Hindernissen.
Es ist Teil des Master-Kurses Intelligente Robotik im Studium der Künstlichen Intelligenz.

## Projektziele
- Implementierung und Vergleich von klassischen Algorithmen wie A* mit Reinforcement Learning-Ansätzen.
- Entwicklung einer flexiblen Simulationsumgebung mit Pygame.

## Installation
1. Installiere die Abhängigkeiten:
pip install -r requirements.txt
2. Starte die Simulation:
python src/main.py

## Struktur
- **src/**: Der Quellcode des Projekts.
- **data/**: Kartenkonfigurationen und Logdateien.
- **docs/**: Dokumentationen und Analysen.
""",
 "requirements.txt": """# Projektabhängigkeiten

pygamep
numpy
""",
}

# Funktion zum Erstellen von Dateien und Ordnern
def create_structure(base_path, structure):
 for name, content in structure.items():
     path = os.path.join(base_path, name)
     if isinstance(content, dict):  # Es ist ein Ordner
         os.makedirs(path, exist_ok=True)
         create_structure(path, content)
     else:  # Es ist eine Datei
         with open(path, "w", encoding="utf-8") as f:
             f.write(content)

# Hauptfunktion
def main():
 base_path = os.getcwd()  # Aktuelles Verzeichnis
 create_structure(base_path, PROJECT_STRUCTURE)
 print("Projektstruktur für 'introb' erfolgreich erstellt!")

if __name__ == "__main__":
 main()