"""
Вкладка захвата окна приложения
"""

import os
import sys
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QComboBox, QTextEdit, QGroupBox
)
from PyQt5.QtCore import Qt, QSettings, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter

from translator.utils.screenshot import ScreenCapture
from translator.utils.ocr import OCREngine
from translator.models.translator import LLMTranslator
from translator.utils.window_manager import WindowManager

class WindowCaptureThread(QThread):
    """Поток для захвата окна и выполнения OCR + перевода"""
    result_ready = pyqtSignal(str, str)
    preview_ready = pyqtSignal(QPixmap)
    
    def __init__(self, window_title, settings):
        super().__init__()
        self.window_title = window_title
        self.settings = settings
        self.screenshot = ScreenCapture()
        self.ocr = OCREngine(settings.value("ocr/tesseract_path", ""))
        self.window_manager = WindowManager()
        
        # Создание переводчика
        db_dir = os.path.join(os.path.expanduser("~"), ".translator")
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        db_path = os.path.join(db_dir, "translations.db")
        
        self.translator = LLMTranslator(db_path)
        
        # Настройка API ключей
        provider = self.settings.value("translator/provider", "openai")
        
        if provider == "openai":
            api_key = self.settings.value("openai/api_key", "")
            base_url = self.settings.value("openai/base_url", "https://api.openai.com/v1")
            if api_key:
                self.translator.set_api_key("openai", api_key, base_url)
        else:
            api_key = self.settings.value("deepseek/api_key", "")
            base_url = self.settings.value("deepseek/base_url", "https://api.aiguoguo199.com/v1")
            if api_key:
                self.translator.set_api_key("deepseek", api_key, base_url)
                
        self.translator.set_default_provider(provider)
    
    def run(self):
        # Захват окна
        try:
            # Получение текущего списка окон
            self.window_manager.get_window_list()
            
            # Получение координат окна для захвата
            window_rect = self.window_manager.capture_window(self.window_title)
            
            if window_rect:
                # Захват указанной области
                x, y, width, height = window_rect
                screenshot_path = self.screenshot.capture_area(x, y, x + width, y + height)
            else:
                # Fallback: использовать захват всего экрана
                screenshot_path = self.screenshot.capture_fullscreen()
            
            # Отправляем превью
            pixmap = QPixmap(screenshot_path)
            self.preview_ready.emit(pixmap)
            
            # OCR
            text = self.ocr.recognize_text(screenshot_path)
            
            # Определение языков
            source_lang_map = {
                "Английский": "en",
                "Русский": "ru",
                "Японский": "ja"
            }
            
            target_lang_map = {
                "Английский": "en",
                "Русский": "ru",
                "Японский": "ja"
            }
            
            # Получение языков из настроек
            source_lang_text = self.settings.value("language/source", "Английский")
            target_lang_text = self.settings.value("language/target", "Русский")
            
            source_lang = source_lang_map.get(source_lang_text, "en")
            target_lang = target_lang_map.get(target_lang_text, "ru")
            
            # Перевод
            translated = self.translator.translate(
                text, source_lang, target_lang, 
                self.settings.value("translator/provider", "openai")
            )
            
            # Отправка результатов
            self.result_ready.emit(text, translated)
            
        except Exception as e:
            self.result_ready.emit("Ошибка при обработке окна", str(e))

class ScreenCaptureTab(QWidget):
    """Вкладка захвата окна"""
    
    def __init__(self):
        """Инициализация вкладки захвата окна"""
        super().__init__()
        
        # Загрузка настроек
        self.settings = QSettings("TranslatorApp", "Translator")
        
        # Создание интерфейса
        self.init_ui()
        
        # Инициализация объектов для работы с окнами
        self.window_manager = WindowManager()
        self.capture_thread = None
        
        # Обновление списка окон при запуске
        self.update_window_list()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Секция "Выбор окна"
        window_group = QGroupBox("Выбор окна")
        window_layout = QVBoxLayout()
        window_group.setLayout(window_layout)
        
        # Список доступных окон
        window_layout.addWidget(QLabel("Доступные окна:"))
        self.window_list = QListWidget()
        window_layout.addWidget(self.window_list)
        
        # Кнопка обновления списка
        refresh_button = QPushButton("Обновить список")
        refresh_button.clicked.connect(self.update_window_list)
        window_layout.addWidget(refresh_button)
        
        # Кнопка захвата
        capture_button = QPushButton("Захватить окно")
        capture_button.clicked.connect(self.capture_window)
        window_layout.addWidget(capture_button)
        
        # Секция "Предпросмотр"
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout()
        preview_group.setLayout(preview_layout)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setText("Предпросмотр появится здесь...")
        preview_layout.addWidget(self.preview_label)
        
        # Секция "Язык оригинала и перевода"
        lang_group = QGroupBox("Языки")
        lang_layout = QHBoxLayout()
        lang_group.setLayout(lang_layout)
        
        # Язык оригинала
        lang_layout.addWidget(QLabel("Язык оригинала:"))
        self.source_lang = QComboBox()
        self.source_lang.addItems(["Английский", "Русский", "Японский"])
        self.source_lang.setCurrentText(self.settings.value("language/source", "Английский"))
        lang_layout.addWidget(self.source_lang)
        
        # Язык перевода
        lang_layout.addWidget(QLabel("Язык перевода:"))
        self.target_lang = QComboBox()
        self.target_lang.addItems(["Русский", "Английский", "Японский"])
        self.target_lang.setCurrentText(self.settings.value("language/target", "Русский"))
        lang_layout.addWidget(self.target_lang)
        
        # Секция "Результаты"
        results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        # Оригинальный текст
        results_layout.addWidget(QLabel("Оригинальный текст:"))
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setPlaceholderText("Оригинальный текст появится здесь...")
        results_layout.addWidget(self.original_text)
        
        # Переведенный текст
        results_layout.addWidget(QLabel("Перевод:"))
        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        self.translated_text.setPlaceholderText("Перевод появится здесь...")
        results_layout.addWidget(self.translated_text)
        
        # Кнопки действий с переводом
        actions_layout = QHBoxLayout()
        
        copy_button = QPushButton("Копировать перевод")
        copy_button.clicked.connect(self.copy_translation)
        actions_layout.addWidget(copy_button)
        
        overlay_button = QPushButton("Показать в оверлее")
        overlay_button.clicked.connect(self.show_overlay)
        actions_layout.addWidget(overlay_button)
        
        results_layout.addLayout(actions_layout)
        
        # Добавление всех секций в основной лейаут
        layout.addWidget(window_group)
        layout.addWidget(preview_group)
        layout.addWidget(lang_group)
        layout.addWidget(results_group)
    
    def update_window_list(self):
        """Обновление списка доступных окон"""
        # Очистка списка
        self.window_list.clear()
        
        try:
            # Получение списка реальных окон
            windows = self.window_manager.get_window_list()
            
            # Если список пуст или возникла ошибка, добавляем примеры для демонстрации
            if not windows:
                sample_windows = [
                    "python",
                    "SHONDO STOP DON'T SAY THAT!!! - YouTube - Google Chrome",
                    "requirements.txt - ocr project - Cursor",
                    "#аниме | Beroobeen's stream - Discord",
                    "Интерфейс ввода Windows",
                    "NVIDIA GeForce Overlay",
                    "AsusDownLoadLicenseBar2357",
                    "Program Manager"
                ]
                
                for window in sample_windows:
                    self.window_list.addItem(window)
            else:
                # Добавление реальных окон в список
                for window in windows:
                    self.window_list.addItem(window)
        except Exception as e:
            # В случае ошибки показываем сообщение
            self.window_list.addItem(f"Ошибка получения списка окон: {e}")
            self.window_list.addItem("Установите необходимые библиотеки: pip install pywin32 psutil")
    
    def capture_window(self):
        """Захват выбранного окна"""
        # Проверяем, выбрано ли окно
        selected_items = self.window_list.selectedItems()
        if not selected_items:
            self.original_text.setText("Ошибка: не выбрано окно для захвата")
            return
        
        window_title = selected_items[0].text()
        
        # Обновление значений языков в настройках
        self.settings.setValue("language/source", self.source_lang.currentText())
        self.settings.setValue("language/target", self.target_lang.currentText())
        
        # Создаем и запускаем поток захвата
        self.capture_thread = WindowCaptureThread(window_title, self.settings)
        self.capture_thread.result_ready.connect(self.on_result_ready)
        self.capture_thread.preview_ready.connect(self.on_preview_ready)
        self.capture_thread.start()
        
        # Показываем сообщение о процессе
        self.original_text.setText("Захват окна и распознавание текста...")
        self.translated_text.setText("Пожалуйста, подождите...")
    
    def on_preview_ready(self, pixmap):
        """Обработка готового предпросмотра"""
        # Масштабируем изображение, чтобы оно вписалось в размер метки
        scaled_pixmap = pixmap.scaled(
            self.preview_label.width(), self.preview_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)
    
    def on_result_ready(self, original, translated):
        """Обработка результатов распознавания и перевода"""
        self.original_text.setText(original)
        self.translated_text.setText(translated)
    
    def copy_translation(self):
        """Копирование перевода в буфер обмена"""
        text = self.translated_text.toPlainText()
        if text and text != "Пожалуйста, подождите...":
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Визуальная индикация, что текст скопирован
            original_color = self.translated_text.styleSheet()
            self.translated_text.setStyleSheet("background-color: #505050;")
            QTimer.singleShot(200, lambda: self.translated_text.setStyleSheet(original_color))
    
    def show_overlay(self):
        """Показ перевода в оверлее поверх окна"""
        # В будущей версии здесь будет код для отображения оверлея
        # Сейчас просто показываем сообщение
        original_color = self.translated_text.styleSheet()
        self.translated_text.setStyleSheet("background-color: #505050;")
        self.translated_text.setText(
            self.translated_text.toPlainText() + "\n\n(Отображение оверлея будет доступно в следующей версии)"
        )
        QTimer.singleShot(200, lambda: self.translated_text.setStyleSheet(original_color)) 