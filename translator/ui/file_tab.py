"""
Вкладка для работы с файлами изображений и документов
"""

import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QGroupBox, QFileDialog, QApplication, QComboBox
)
from PyQt5.QtCore import Qt, QSettings, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter, QCursor, QDragEnterEvent, QDropEvent

from translator.utils.ocr import OCREngine
from translator.models.translator import LLMTranslator

class FileProcessThread(QThread):
    """Поток для обработки файла и выполнения OCR + перевода"""
    result_ready = pyqtSignal(str, str)
    preview_ready = pyqtSignal(QPixmap)
    
    def __init__(self, file_path, settings):
        super().__init__()
        self.file_path = file_path
        self.settings = settings
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
        # Обработка файла
        try:
            # Проверяем, является ли файл изображением
            if self.file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                # Отправляем превью
                pixmap = QPixmap(self.file_path)
                self.preview_ready.emit(pixmap)
                
                # OCR
                text = self.ocr.recognize_text(self.file_path)
            else:
                # Для других типов файлов в будущих версиях
                self.preview_ready.emit(QPixmap())
                self.result_ready.emit("Тип файла не поддерживается", "Поддерживаются только изображения (.png, .jpg, .jpeg, .bmp, .tiff)")
                return
            
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
            self.result_ready.emit("Ошибка при обработке файла", str(e))

class FileTab(QWidget):
    """Вкладка для работы с файлами"""
    
    def __init__(self):
        """Инициализация вкладки файлов"""
        super().__init__()
        
        # Загрузка настроек
        self.settings = QSettings("TranslatorApp", "Translator")
        
        # Создание интерфейса
        self.init_ui()
        
        # Инициализация переменных
        self.process_thread = None
        self.current_file = None
        
        # Настройка поддержки drag-and-drop
        self.setAcceptDrops(True)
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Кнопки для выбора файла
        file_buttons_layout = QHBoxLayout()
        
        select_file_button = QPushButton("Выбрать файл")
        select_file_button.clicked.connect(self.select_file)
        file_buttons_layout.addWidget(select_file_button)
        
        layout.addLayout(file_buttons_layout)
        
        # Область для drag-and-drop
        dropzone_group = QGroupBox("Перетащите файл сюда")
        dropzone_layout = QVBoxLayout()
        dropzone_group.setLayout(dropzone_layout)
        
        # Метка с информацией
        dropzone_label = QLabel("или нажмите кнопку 'Выбрать файл'")
        dropzone_label.setAlignment(Qt.AlignCenter)
        dropzone_layout.addWidget(dropzone_label)
        
        # Метка для отображения файла
        self.file_preview = QLabel()
        self.file_preview.setAlignment(Qt.AlignCenter)
        self.file_preview.setMinimumHeight(200)
        dropzone_layout.addWidget(self.file_preview)
        
        # Добавление группы в основной лейаут
        layout.addWidget(dropzone_group)
        
        # Группа "Языки"
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
        
        # Кнопка перевода
        translate_button = QPushButton("Распознать и перевести")
        translate_button.clicked.connect(self.process_file)
        lang_layout.addWidget(translate_button)
        
        # Добавление группы в основной лейаут
        layout.addWidget(lang_group)
        
        # Группа "Результаты"
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
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        
        copy_original_button = QPushButton("Копировать оригинал")
        copy_original_button.clicked.connect(self.copy_original)
        actions_layout.addWidget(copy_original_button)
        
        copy_translation_button = QPushButton("Копировать перевод")
        copy_translation_button.clicked.connect(self.copy_translation)
        actions_layout.addWidget(copy_translation_button)
        
        export_button = QPushButton("Экспорт перевода")
        export_button.clicked.connect(self.export_translation)
        actions_layout.addWidget(export_button)
        
        results_layout.addLayout(actions_layout)
        
        # Добавление группы в основной лейаут
        layout.addWidget(results_group)
    
    def select_file(self):
        """Открытие диалога выбора файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите изображение", 
            "", 
            "Изображения (*.png *.jpg *.jpeg *.bmp *.tiff);;PDF (*.pdf);;Все файлы (*)"
        )
        
        if file_path:
            self.current_file = file_path
            # Показываем имя файла
            self.file_preview.setText(f"Выбран файл: {os.path.basename(file_path)}")
            
            # Если это изображение, показываем превью
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                pixmap = QPixmap(file_path)
                # Масштабируем для отображения
                scaled_pixmap = pixmap.scaled(
                    self.file_preview.width(), self.file_preview.height(),
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.file_preview.setPixmap(scaled_pixmap)
            
            # Автоматически запускаем обработку
            self.process_file()
    
    def process_file(self):
        """Обработка выбранного файла"""
        if not self.current_file:
            self.original_text.setText("Ошибка: файл не выбран")
            return
        
        # Обновление значений языков в настройках
        self.settings.setValue("language/source", self.source_lang.currentText())
        self.settings.setValue("language/target", self.target_lang.currentText())
        
        # Создаем и запускаем поток обработки
        self.process_thread = FileProcessThread(self.current_file, self.settings)
        self.process_thread.result_ready.connect(self.on_result_ready)
        self.process_thread.preview_ready.connect(self.on_preview_ready)
        self.process_thread.start()
        
        # Показываем сообщение о процессе
        self.original_text.setText("Обработка файла и распознавание текста...")
        self.translated_text.setText("Пожалуйста, подождите...")
    
    def on_preview_ready(self, pixmap):
        """Обработка готового предпросмотра"""
        if not pixmap.isNull():
            # Масштабируем изображение, чтобы оно вписалось в размер метки
            scaled_pixmap = pixmap.scaled(
                self.file_preview.width(), self.file_preview.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.file_preview.setPixmap(scaled_pixmap)
    
    def on_result_ready(self, original, translated):
        """Обработка результатов распознавания и перевода"""
        self.original_text.setText(original)
        self.translated_text.setText(translated)
    
    def copy_original(self):
        """Копирование оригинального текста в буфер обмена"""
        text = self.original_text.toPlainText()
        if text and text != "Обработка файла и распознавание текста...":
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Визуальная индикация, что текст скопирован
            original_color = self.original_text.styleSheet()
            self.original_text.setStyleSheet("background-color: #505050;")
            QTimer.singleShot(200, lambda: self.original_text.setStyleSheet(original_color))
    
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
    
    def export_translation(self):
        """Экспорт перевода в текстовый файл"""
        if not self.current_file or not self.translated_text.toPlainText() or self.translated_text.toPlainText() == "Пожалуйста, подождите...":
            return
            
        # Подготовка имени файла для сохранения
        original_name = os.path.basename(self.current_file)
        base_name, _ = os.path.splitext(original_name)
        export_name = f"{base_name}_translated.txt"
        
        # Открытие диалога сохранения
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить перевод", 
            export_name, 
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.translated_text.toPlainText())
                    
                # Визуальная индикация успешного сохранения
                original_color = self.translated_text.styleSheet()
                self.translated_text.setStyleSheet("background-color: #505050;")
                QTimer.singleShot(200, lambda: self.translated_text.setStyleSheet(original_color))
            except Exception as e:
                self.translated_text.setText(f"{self.translated_text.toPlainText()}\n\nОшибка при сохранении: {e}")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Обработка события перетаскивания файла на область"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Обработка события сброса файла на область"""
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            
            # Проверка, является ли файл изображением или PDF
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.pdf')
            if file_path.lower().endswith(valid_extensions):
                self.current_file = file_path
                # Показываем имя файла
                self.file_preview.setText(f"Выбран файл: {os.path.basename(file_path)}")
                
                # Если это изображение, показываем превью
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                    pixmap = QPixmap(file_path)
                    # Масштабируем для отображения
                    scaled_pixmap = pixmap.scaled(
                        self.file_preview.width(), self.file_preview.height(),
                        Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.file_preview.setPixmap(scaled_pixmap)
                
                # Автоматически запускаем обработку
                self.process_file()
            else:
                self.file_preview.setText("Неподдерживаемый формат файла. Поддерживаются только изображения и PDF.")
                self.current_file = None 