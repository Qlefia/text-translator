from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class FileTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Временная заглушка
        label = QLabel("Вкладка работы с файлами")
        layout.addWidget(label)
        
        self.setLayout(layout) 