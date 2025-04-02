"""
Главное окно приложения-переводчика
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, 
    QFileDialog, QApplication, QMessageBox, QStatusBar, QAction,
    QMenuBar, QMenu, QCheckBox, QGroupBox, QRadioButton, QScrollArea
)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap, QScreen, QCursor

from translator.ui.theme import CatppuccinTheme
from translator.ui.screen_capture_tab import ScreenCaptureTab
from translator.ui.area_capture_tab import AreaCaptureTab
from translator.ui.file_tab import FileTab
from translator.ui.history_tab import HistoryTab
from translator.ui.settings_tab import SettingsTab

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        """Инициализация главного окна"""
        super().__init__()
        
        # Настройка основного окна
        self.setWindowTitle("Translator")
        self.setMinimumSize(900, 600)
        
        # Загрузка темы
        self.apply_theme()
        
        # Инициализация меню
        self.init_menu()
        
        # Инициализация вкладок
        self.init_tabs()
        
        # Инициализация строки состояния
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        # Центрирование окна
        self.center_window()
    
    def apply_theme(self, theme_name='mocha'):
        """
        Применение темы к интерфейсу
        
        Args:
            theme_name: название темы ('mocha', 'latte', 'frappe', 'macchiato')
        """
        style_sheet = CatppuccinTheme.get_style_sheet(theme_name)
        self.setStyleSheet(style_sheet)
    
    def init_menu(self):
        """Инициализация главного меню"""
        # Создание меню
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)
        
        # Меню "Файл"
        file_menu = QMenu("&Файл", self)
        menu_bar.addMenu(file_menu)
        
        # Действия меню "Файл"
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Правка"
        edit_menu = QMenu("&Правка", self)
        menu_bar.addMenu(edit_menu)
        
        # Действия меню "Правка"
        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(lambda: self.tabs.setCurrentIndex(4))  # Вкладка настроек
        edit_menu.addAction(settings_action)
        
        # Меню "Вид"
        view_menu = QMenu("&Вид", self)
        menu_bar.addMenu(view_menu)
        
        # Подменю для тем
        themes_menu = QMenu("Темы", self)
        view_menu.addMenu(themes_menu)
        
        mocha_action = QAction("Mocha (темная)", self)
        mocha_action.triggered.connect(lambda: self.apply_theme('mocha'))
        themes_menu.addAction(mocha_action)
        
        latte_action = QAction("Latte (светлая)", self)
        latte_action.triggered.connect(lambda: self.apply_theme('latte'))
        themes_menu.addAction(latte_action)
        
        frappe_action = QAction("Frappe", self)
        frappe_action.triggered.connect(lambda: self.apply_theme('frappe'))
        themes_menu.addAction(frappe_action)
        
        macchiato_action = QAction("Macchiato", self)
        macchiato_action.triggered.connect(lambda: self.apply_theme('macchiato'))
        themes_menu.addAction(macchiato_action)
        
        # Меню "Справка"
        help_menu = QMenu("&Справка", self)
        menu_bar.addMenu(help_menu)
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_tabs(self):
        """Инициализация вкладок"""
        # Создание виджета вкладок
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Добавление вкладок
        self.tabs.addTab(ScreenCaptureTab(), "Захват окна")
        self.tabs.addTab(AreaCaptureTab(), "Область экрана")
        self.tabs.addTab(FileTab(), "Файлы")
        self.tabs.addTab(HistoryTab(), "История")
        self.tabs.addTab(SettingsTab(), "Настройки")
        
        # Настройка вкладок
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)
        self.tabs.setDocumentMode(True)
    
    def center_window(self):
        """Центрирование окна на экране"""
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        window_size = self.frameGeometry()
        center_point = screen.center()
        window_size.moveCenter(center_point)
        self.move(window_size.topLeft())
    
    def show_about(self):
        """Отображение окна "О программе" """
        QMessageBox.about(
            self, 
            "О программе", 
            "<h3>Translator App</h3>"
            "<p>Приложение для мгновенного перевода текста с экрана.</p>"
            "<p>Версия: 0.1.0</p>"
            "<p>© 2025 Translator Team</p>"
        )
    
    def closeEvent(self, event):
        """
        Обработка события закрытия окна
        
        Args:
            event: событие закрытия
        """
        reply = QMessageBox.question(
            self, 
            "Подтверждение выхода", 
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore() 