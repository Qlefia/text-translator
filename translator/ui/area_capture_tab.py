"""
Вкладка захвата произвольной области экрана
"""

import os
import sys
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QGroupBox, QApplication, QDesktopWidget, QComboBox
)
from PyQt5.QtCore import Qt, QSettings, QTimer, pyqtSignal, QThread, QRect
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter, QCursor

from translator.utils.screenshot import ScreenCapture
from translator.utils.ocr import OCREngine
from translator.models.translator import LLMTranslator
from translator.utils.hotkeys import HotkeyManager

class SelectAreaDialog(QWidget):
    """Диалог для выбора области экрана"""
    area_selected = pyqtSignal(int, int, int, int)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setWindowState(Qt.WindowFullScreen)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
        self.setMouseTracking(True)
        
        # Начальные координаты выделения
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.is_selecting = False
        
        # Добавляем инструкцию для пользователя
        instruction = QLabel("Перетащите для выделения области. Нажмите Esc для отмены.", self)
        instruction.setStyleSheet("color: white; font-size: 16px; background-color: rgba(0, 0, 0, 150);")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setGeometry(0, 10, self.width(), 30)
    
    def paintEvent(self, event):
        """Отрисовка интерфейса выделения области"""
        painter = QPainter(self)
        painter.setPen(QColor(0, 150, 255))
        painter.setBrush(QColor(0, 150, 255, 40))
        
        if self.is_selecting or (self.start_x != self.end_x and self.start_y != self.end_y):
            x = min(self.start_x, self.end_x)
            y = min(self.start_y, self.end_y)
            width = abs(self.end_x - self.start_x)
            height = abs(self.end_y - self.start_y)
            painter.drawRect(x, y, width, height)
    
    def mousePressEvent(self, event):
        """Обработка нажатия кнопки мыши"""
        if event.button() == Qt.LeftButton:
            self.start_x = event.pos().x()
            self.start_y = event.pos().y()
            self.end_x = self.start_x
            self.end_y = self.start_y
            self.is_selecting = True
    
    def mouseMoveEvent(self, event):
        """Обработка движения мыши"""
        if self.is_selecting:
            self.end_x = event.pos().x()
            self.end_y = event.pos().y()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.end_x = event.pos().x()
            self.end_y = event.pos().y()
            self.is_selecting = False
            
            # Отправляем сигнал с координатами выделенной области
            self.area_selected.emit(
                min(self.start_x, self.end_x),
                min(self.start_y, self.end_y),
                max(self.start_x, self.end_x),
                max(self.start_y, self.end_y)
            )
            self.close()
    
    def keyPressEvent(self, event):
        """Обработка нажатия клавиш"""
        if event.key() == Qt.Key_Escape:
            self.close()

class AreaCaptureThread(QThread):
    """Поток для захвата области экрана и выполнения OCR + перевода"""
    result_ready = pyqtSignal(str, str)
    preview_ready = pyqtSignal(QPixmap)
    
    def __init__(self, x1, y1, x2, y2, settings):
        super().__init__()
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.settings = settings
        self.screenshot = ScreenCapture()
        self.ocr = OCREngine(settings.value("ocr/tesseract_path", ""))
        
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
        # Захват области экрана
        try:
            screenshot_path = self.screenshot.capture_area(self.x1, self.y1, self.x2, self.y2)
            
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
            self.result_ready.emit("Ошибка при обработке области", str(e))

class AreaCaptureTab(QWidget):
    """Вкладка захвата произвольной области экрана"""
    
    def __init__(self):
        """Инициализация вкладки захвата области экрана"""
        super().__init__()
        
        # Загрузка настроек
        self.settings = QSettings("TranslatorApp", "Translator")
        
        # Создание интерфейса
        self.init_ui()
        
        # Инициализация переменных
        self.capture_thread = None
        self.select_dialog = None
        self.last_capture_coords = None
        
        # Инициализация менеджера горячих клавиш
        self.hotkey_manager = HotkeyManager()
        
        # Регистрация глобальной горячей клавиши для захвата области
        self.register_hotkeys()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Инструкции для пользователя
        instruction_label = QLabel("Используйте горячие клавиши для выделения области экрана или нажмите кнопку ниже.")
        layout.addWidget(instruction_label)
        
        # Отображение горячих клавиш
        hotkey_label = QLabel(f"Горячие клавиши: {self.settings.value('hotkeys/area_capture', 'Alt+Shift+C')}")
        layout.addWidget(hotkey_label)
        
        # Кнопка выделения области
        area_button = QPushButton("Выделить область экрана")
        area_button.clicked.connect(self.select_area)
        layout.addWidget(area_button)
        
        # Группа "Последнее выделение"
        last_capture_group = QGroupBox("Последнее выделение")
        last_capture_layout = QVBoxLayout()
        last_capture_group.setLayout(last_capture_layout)
        
        # Метка для отображения скриншота
        self.preview_label = QLabel("Ещё нет выделений")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        last_capture_layout.addWidget(self.preview_label)
        
        # Добавление группы в основной лейаут
        layout.addWidget(last_capture_group)
        
        # Группа "Результаты"
        results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        # Горизонтальный лейаут для языков
        lang_layout = QHBoxLayout()
        
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
        
        results_layout.addLayout(lang_layout)
        
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
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        
        copy_button = QPushButton("Копировать перевод")
        copy_button.clicked.connect(self.copy_translation)
        buttons_layout.addWidget(copy_button)
        
        overlay_button = QPushButton("Показать в оверлее")
        overlay_button.clicked.connect(self.show_overlay)
        buttons_layout.addWidget(overlay_button)
        
        results_layout.addLayout(buttons_layout)
        
        # Добавление группы в основной лейаут
        layout.addWidget(results_group)
    
    def register_hotkeys(self):
        """Регистрация глобальных горячих клавиш"""
        try:
            # Получение настроенной горячей клавиши для захвата области
            hotkey = self.settings.value("hotkeys/area_capture", "Alt+Shift+C")
            
            # Регистрация горячей клавиши
            self.hotkey_manager.register_hotkey(hotkey, self.global_area_select_hotkey)
            
            # Запуск прослушивания
            self.hotkey_manager.start_listening()
        except Exception as e:
            print(f"Ошибка при регистрации горячих клавиш: {e}")
    
    def global_area_select_hotkey(self):
        """Обработчик глобальной горячей клавиши для захвата области"""
        # Показать диалог выбора области
        self.select_area()
    
    def select_area(self):
        """Запуск диалога выбора области экрана"""
        self.select_dialog = SelectAreaDialog()
        self.select_dialog.area_selected.connect(self.on_area_selected)
        self.select_dialog.show()
    
    def on_area_selected(self, x1, y1, x2, y2):
        """Обработка выбранной области"""
        
        # Сохраняем координаты для возможного повторного захвата
        self.last_capture_coords = (x1, y1, x2, y2)
        
        # Обновление значений языков в настройках
        self.settings.setValue("language/source", self.source_lang.currentText())
        self.settings.setValue("language/target", self.target_lang.currentText())
        
        # Создаем и запускаем поток захвата
        self.capture_thread = AreaCaptureThread(x1, y1, x2, y2, self.settings)
        self.capture_thread.result_ready.connect(self.on_result_ready)
        self.capture_thread.preview_ready.connect(self.on_preview_ready)
        self.capture_thread.start()
        
        # Показываем сообщение о процессе
        self.original_text.setText("Захват области и распознавание текста...")
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
        """Показ перевода в оверлее поверх выделенной области"""
        # В будущей версии здесь будет код для отображения оверлея
        # Сейчас просто показываем сообщение
        original_color = self.translated_text.styleSheet()
        self.translated_text.setStyleSheet("background-color: #505050;")
        self.translated_text.setText(
            self.translated_text.toPlainText() + "\n\n(Отображение оверлея будет доступно в следующей версии)"
        )
        QTimer.singleShot(200, lambda: self.translated_text.setStyleSheet(original_color)) 