import sys
import os
import firebase_admin
from firebase_admin import credentials, firestore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QVBoxLayout, QWidget, QLabel, QTableWidgetItem, QPushButton)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal

class GameWindow(QMainWindow):
    mostrarMenuPrincipal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_firebase()
        self.init_ui()

    def init_firebase(self):
        if not firebase_admin._apps:  # Verificar si no hay aplicaciones inicializadas
            base_path = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_path, 'leaderboard.json')

            cred = credentials.Certificate(json_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def init_ui(self):
        self.setWindowTitle("Leaderboard")

        window_width = 900
        window_height = 400
        self.resize(window_width, window_height)

        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        self.move(x, y)

        self.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title = QLabel("LEADERBOARD")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 20px;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["User", "Games won", "Games lost", "Total games", "Win ratio"])
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 150)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #3c3c3c;
                color: #ffffff;
                gridline-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #555555;
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #ffffff;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #555555;
                border: 1px solid #ffffff;
            }
        """)
        layout.addWidget(self.table)

        self.populate_table()

        # Agregar botón de BACK
        back_button = QPushButton("BACK")
        back_button.setFont(QFont("Arial", 14))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: #ffffff;
                border: 1px solid #ffffff;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        back_button.clicked.connect(self.back_button_clicked)
        layout.addWidget(back_button)

    def populate_table(self):
        print("Fetching player data...")
        players = self.get_players()
        if not players:
            print("No players fetched.")
            return
        self.process_games(players)
        self.quicksort(players, 0, len(players) - 1)
        self.table.setRowCount(len(players))
        for row, player in enumerate(players):
            self.table.setItem(row, 0, QTableWidgetItem(player.get('usuario')))
            self.table.setItem(row, 1, QTableWidgetItem(str(player['juegos_ganados'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(player['juegos_perdidos'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(player['total_juegos'])))
            self.table.setItem(row, 4, QTableWidgetItem(f"{player['win_ratio']:.2f}%"))

    def get_players(self):
        try:
            print("Connecting to Firestore...")
            players_ref = self.db.collection('players')
            docs = players_ref.stream()

            players = []
            for doc in docs:
                player = doc.to_dict()
                print(f"Player data: {player}")  
                players.append(player)

            print(f"Fetched {len(players)} players from the database.")
            return players
        except Exception as e:
            print(f"Error fetching players: {e}")
            return []

    def process_games(self, players):
        for player in players:
            player['usuario'] = player.get('user', 'N/A')
            player['juegos_ganados'] = player.get('wins', 0)
            player['juegos_perdidos'] = player.get('losses', 0)
            player['total_juegos'] = player.get('games_played', player['juegos_ganados'] + player['juegos_perdidos'])
            player['win_ratio'] = (player['juegos_ganados'] / player['total_juegos']) * 100 if player['total_juegos'] != 0 else 0

    def quicksort(self, players, low, high):
        if low < high:
            pi = self.partition(players, low, high)
            self.quicksort(players, low, pi - 1)
            self.quicksort(players, pi + 1, high)

    def partition(self, players, low, high):
        pivot = players[high]["juegos_ganados"]
        i = low - 1
        for j in range(low, high):
            if players[j]["juegos_ganados"] > pivot:
                i += 1
                players[i], players[j] = players[j], players[i]
        players[i + 1], players[high] = players[high], players[i + 1]
        return i + 1

    def back_button_clicked(self):
        self.mostrarMenuPrincipal.emit()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())
