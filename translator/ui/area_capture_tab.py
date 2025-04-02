from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class AreaCaptureTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Временная заглушка
        label = QLabel("Вкладка захвата области")
        layout.addWidget(label)
        
        self.setLayout(layout) 