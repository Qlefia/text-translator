from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Временная заглушка
        label = QLabel("Вкладка истории переводов")
        layout.addWidget(label)
        
        self.setLayout(layout) 