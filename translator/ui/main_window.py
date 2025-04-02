"""
Главное окно приложения
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QAction, QMenu, QMenuBar, 
    QStatusBar, QSystemTrayIcon, QApplication
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon

from translator.ui.screen_capture_tab import ScreenCaptureTab
from translator.ui.area_capture_tab import AreaCaptureTab
from translator.ui.file_tab import FileTab
from translator.ui.history_tab import HistoryTab
from translator.ui.settings_tab import SettingsTab
from translator.utils.hotkeys import HotkeyManager

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        """Инициализация главного окна"""
        super().__init__()
        
        # Загрузка настроек
        self.settings = QSettings("TranslatorApp", "Translator")
        
        # Инициализация интерфейса
        self.init_ui()
        
        # Инициализация менеджера горячих клавиш
        self.hotkey_manager = HotkeyManager()
        self.setup_global_hotkeys()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Настройка главного окна
        self.setWindowTitle("Translator Pro")
        self.setMinimumSize(800, 600)
        
        # Основной виджет с вкладками
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Создание вкладок
        self.screen_capture_tab = ScreenCaptureTab()
        self.area_capture_tab = AreaCaptureTab()
        self.file_tab = FileTab()
        self.history_tab = HistoryTab()
        self.settings_tab = SettingsTab()
        
        # Добавление вкладок в виджет
        self.tab_widget.addTab(self.area_capture_tab, "Область экрана")
        self.tab_widget.addTab(self.screen_capture_tab, "Захват окна")
        self.tab_widget.addTab(self.file_tab, "Файлы")
        self.tab_widget.addTab(self.history_tab, "История")
        self.tab_widget.addTab(self.settings_tab, "Настройки")
        
        # Создание меню
        self.create_menu()
        
        # Создание статусной строки
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готов к работе")
        
        # Настройка трея (иконки в системном лотке)
        self.setup_tray()
    
    def create_menu(self):
        """Создание меню приложения"""
        # Создание меню
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        # Действие "Выход"
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Инструменты"
        tools_menu = menubar.addMenu("Инструменты")
        
        # Действие "Захват области экрана"
        area_action = QAction("Захват области экрана", self)
        area_action.setShortcut(self.settings.value("hotkeys/area_capture", "Alt+Shift+C"))
        area_action.triggered.connect(self.area_capture_tab.select_area)
        tools_menu.addAction(area_action)
        
        # Действие "Захват окна"
        window_action = QAction("Захват окна", self)
        window_action.setShortcut(self.settings.value("hotkeys/window_capture", "Alt+Shift+W"))
        window_action.triggered.connect(self.capture_active_window)
        tools_menu.addAction(window_action)
        
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")
        
        # Действие "О программе"
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_tray(self):
        """Настройка иконки в системном лотке"""
        try:
            # Создание иконки в трее
            self.tray_icon = QSystemTrayIcon(self)
            
            # Установка иконки
            # В реальном приложении здесь должна быть загрузка реальной иконки
            self.tray_icon.setIcon(QApplication.style().standardIcon(
                QApplication.style().SP_ComputerIcon)
            )
            
            # Создание меню для трея
            tray_menu = QMenu()
            
            # Добавление действий в меню
            show_action = QAction("Показать", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            # Действие "Захват области"
            area_action = QAction("Захват области экрана", self)
            area_action.triggered.connect(self.area_capture_tab.select_area)
            tray_menu.addAction(area_action)
            
            # Действие "Захват окна"
            window_action = QAction("Захват активного окна", self)
            window_action.triggered.connect(self.capture_active_window)
            tray_menu.addAction(window_action)
            
            tray_menu.addSeparator()
            
            exit_action = QAction("Выход", self)
            exit_action.triggered.connect(QApplication.quit)
            tray_menu.addAction(exit_action)
            
            # Установка меню для иконки в трее
            self.tray_icon.setContextMenu(tray_menu)
            
            # Обработка двойного клика по иконке
            self.tray_icon.activated.connect(self.tray_icon_activated)
            
            # Показать иконку в трее
            self.tray_icon.show()
        except Exception as e:
            print(f"Ошибка при настройке иконки в системном лотке: {e}")
    
    def setup_global_hotkeys(self):
        """Настройка глобальных горячих клавиш"""
        try:
            # Регистрация горячих клавиш
            area_hotkey = self.settings.value("hotkeys/area_capture", "Alt+Shift+C")
            window_hotkey = self.settings.value("hotkeys/window_capture", "Alt+Shift+W")
            show_hide_hotkey = self.settings.value("hotkeys/show_hide", "Alt+Shift+H")
            
            # Регистрация обработчиков
            self.hotkey_manager.register_hotkey(area_hotkey, self.area_capture_tab.select_area)
            self.hotkey_manager.register_hotkey(window_hotkey, self.capture_active_window)
            self.hotkey_manager.register_hotkey(show_hide_hotkey, self.toggle_window)
            
            # Запуск прослушивания
            self.hotkey_manager.start_listening()
        except Exception as e:
            print(f"Ошибка при настройке глобальных горячих клавиш: {e}")
    
    def tray_icon_activated(self, reason):
        """
        Обработка активации иконки в трее
        
        Args:
            reason: причина активации
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
    
    def closeEvent(self, event):
        """
        Обработка события закрытия окна
        
        Args:
            event: событие закрытия
        """
        # Проверка настройки "Сворачивать в трей"
        if self.settings.value("other/minimize_to_tray", True, type=bool):
            # Если настройка включена, просто скрываем окно
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Translator Pro",
                "Приложение продолжает работать в фоне.",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            # Если настройка выключена, закрываем приложение
            # Отмена регистрации всех горячих клавиш
            self.hotkey_manager.unregister_all_hotkeys()
            
            # Продолжаем закрытие
            event.accept()
    
    def show_about(self):
        """Отображение информации о программе"""
        about_text = """
        <h1>Translator Pro</h1>
        <p>Версия: 1.0.0</p>
        <p>Программа для захвата и перевода текста с экрана.</p>
        <p>Поддерживаемые языки: английский, русский, японский.</p>
        <p>Разработано с использованием PyQt и API OpenAI/DeepSeek.</p>
        """
        
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(self, "О программе", about_text)
    
    def capture_active_window(self):
        """Захват активного окна"""
        # Переключение на вкладку захвата окна
        self.tab_widget.setCurrentWidget(self.screen_capture_tab)
        
        # Активация окна приложения
        self.show()
        self.activateWindow()
        
        # Запуск захвата активного окна
        # Получаем список окон
        self.screen_capture_tab.update_window_list()
        
        # Выбираем первое окно в списке (обычно активное)
        if self.screen_capture_tab.window_list.count() > 0:
            self.screen_capture_tab.window_list.setCurrentRow(0)
            
            # Запускаем захват
            self.screen_capture_tab.capture_window()
    
    def toggle_window(self):
        """Показать/скрыть главное окно приложения"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            self.raise_() 