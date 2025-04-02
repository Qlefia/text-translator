"""
Основной файл для запуска приложения переводчика
"""

import sys
import os
import sqlite3
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings

from translator.ui.main_window import MainWindow
from translator.utils.ocr import OCREngine
from translator.models.translator import LLMTranslator

def init_database():
    """Инициализация базы данных"""
    # Путь к базе данных в папке приложения
    db_dir = os.path.join(os.path.expanduser("~"), ".translator")
    
    # Создаем директорию, если ее нет
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    db_path = os.path.join(db_dir, "translations.db")
    
    # Инициализация базы данных для истории переводов
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создание таблицы для истории переводов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_text TEXT,
        target_text TEXT,
        source_lang TEXT,
        target_lang TEXT,
        provider TEXT,
        timestamp DATETIME
    )
    ''')
    
    conn.commit()
    conn.close()
    
    return db_path

def load_settings():
    """Загрузка настроек приложения"""
    settings = QSettings("TranslatorApp", "Translator")
    
    # Если первый запуск, установить значения по умолчанию
    if not settings.contains("translator/provider"):
        # API и переводчики
        settings.setValue("translator/provider", "deepseek")
        settings.setValue("openai/base_url", "https://api.openai.com/v1")
        settings.setValue("openai/model", "gpt-4")
        settings.setValue("deepseek/base_url", "https://api.aiguoguo199.com/v1")
        settings.setValue("deepseek/model", "deepseek-chat")
        
        # Языки
        settings.setValue("language/ui", "Русский")
        settings.setValue("language/source", "Английский")
        settings.setValue("language/target", "Русский")
        
        # Горячие клавиши
        settings.setValue("hotkeys/area_capture", "Alt+Shift+C")
        settings.setValue("hotkeys/window_capture", "Alt+Shift+W")
        settings.setValue("hotkeys/show_hide", "Alt+Shift+H")
        settings.setValue("hotkeys/close_overlay", "Alt+Shift+X")
        settings.setValue("hotkeys/copy_translation", "Ctrl+C")
        
        # Внешний вид
        settings.setValue("appearance/theme", "Mocha (темная)")
        settings.setValue("appearance/overlay_transparency", "30%")
        settings.setValue("appearance/overlay_duration", "5 секунд")
        settings.setValue("appearance/show_animations", True)
        settings.setValue("appearance/rounded_corners", True)
        
        # OCR
        settings.setValue("ocr/engine", "Tesseract OCR")
        if os.name == 'nt':  # Windows
            settings.setValue("ocr/tesseract_path", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        settings.setValue("ocr/update_interval", "1 секунда")
        settings.setValue("ocr/max_duration", "1 минута")
        
        # Прочие
        settings.setValue("other/autostart", False)
        settings.setValue("other/minimize_to_tray", True)
        settings.setValue("other/confirm_exit", True)
        settings.setValue("other/error_logging", True)

def init_ocr():
    """Инициализация движка OCR"""
    settings = QSettings("TranslatorApp", "Translator")
    
    # Путь к Tesseract
    tesseract_path = settings.value("ocr/tesseract_path", "")
    
    # Инициализация OCR движка
    ocr_engine = OCREngine(tesseract_path)
    
    return ocr_engine

def init_translator(db_path):
    """Инициализация переводчика"""
    settings = QSettings("TranslatorApp", "Translator")
    
    # Создание переводчика
    translator = LLMTranslator(db_path)
    
    # Выбор провайдера по умолчанию
    default_provider = settings.value("translator/provider", "openai")
    translator.set_default_provider(default_provider)
    
    # Установка API ключей
    openai_api_key = settings.value("openai/api_key", "")
    openai_base_url = settings.value("openai/base_url", "https://api.openai.com/v1")
    if openai_api_key:
        translator.set_api_key("openai", openai_api_key, openai_base_url)
    
    deepseek_api_key = settings.value("deepseek/api_key", "")
    deepseek_base_url = settings.value("deepseek/base_url", "https://api.aiguoguo199.com/v1")
    if deepseek_api_key:
        translator.set_api_key("deepseek", deepseek_api_key, deepseek_base_url)
    
    return translator

def main():
    """Основная функция для запуска приложения"""
    # Инициализация приложения
    app = QApplication(sys.argv)
    app.setApplicationName("Translator Pro")
    app.setApplicationVersion("2.0.0")
    
    # Загрузка или создание настроек
    load_settings()
    
    # Инициализация базы данных
    db_path = init_database()
    
    # Инициализация OCR движка и переводчика
    ocr_engine = init_ocr()
    translator = init_translator(db_path)
    
    # Создание главного окна
    main_window = MainWindow()
    main_window.setWindowTitle("Translator Pro 2025")
    main_window.show()
    
    # Запуск цикла событий
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 