from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class ScreenCaptureTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Временная заглушка
        label = QLabel("Вкладка захвата окна")
        layout.addWidget(label)
        
        self.setLayout(layout) 