# test_map.py
from src.environment.map1 import Map

def test_map():
    # Erstelle eine Karte mit festen Dimensionen
    game_map = Map(5, 5)
    
    # Füge 3 Hindernisse hinzu
    game_map.add_obstacles(3)
    
    # Stelle sicher, dass es Hindernisse gibt
    obstacles_count = sum(row.count(1) for row in game_map.grid)
    print(f"Anzahl der Hindernisse: {obstacles_count}")
    
    # Platziere einen Roboter an Position (2, 2)
    game_map.place_robot(2, 2)
    
    # Überprüfe, ob der Roboter korrekt platziert wurde
    assert game_map.grid[2][2] == 'R', "Roboter wurde nicht korrekt platziert"
    
    # Platziere ein Ziel
    game_map.place_goal(4, 4)
    
    # Überprüfe, ob das Ziel korrekt platziert wurde
    assert game_map.grid[4][4] == 'G', "Ziel wurde nicht korrekt platziert"
    
    print("Map Test bestanden!")

# Testausführung
if __name__ == "__main__":
    test_map()