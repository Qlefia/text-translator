"""
Tab for capturing application windows
"""

import os
import sys
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QComboBox, QTextEdit, QGroupBox,
    QApplication
)
from PyQt5.QtCore import Qt, QSettings, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter

from translator.utils.screenshot import ScreenCapture
from translator.utils.ocr import OCREngine
from translator.models.translator import LLMTranslator
from translator.utils.window_manager import WindowManager

class WindowCaptureThread(QThread):
    """Thread for window capture and OCR + translation"""
    result_ready = pyqtSignal(str, str)
    preview_ready = pyqtSignal(QPixmap)
    
    def __init__(self, window_title, settings):
        super().__init__()
        self.window_title = window_title
        self.settings = settings
        self.screenshot = ScreenCapture()
        self.ocr = OCREngine(settings.value("ocr/tesseract_path", ""))
        self.window_manager = WindowManager()
        
        # Create translator
        db_dir = os.path.join(os.path.expanduser("~"), ".translator")
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        db_path = os.path.join(db_dir, "translations.db")
        
        self.translator = LLMTranslator(db_path)
        
        # Set up API keys
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
        # Window capture
        try:
            # Get current window list
            self.window_manager.get_window_list()
            
            # Get coordinates of the window to capture
            window_rect = self.window_manager.capture_window(self.window_title)
            
            if window_rect:
                # Capture the specified area
                x, y, width, height = window_rect
                screenshot_path = self.screenshot.capture_area(x, y, x + width, y + height)
            else:
                # Fallback: use fullscreen capture
                screenshot_path = self.screenshot.capture_fullscreen()
            
            # Send preview
            pixmap = QPixmap(screenshot_path)
            self.preview_ready.emit(pixmap)
            
            # OCR
            text = self.ocr.recognize_text(screenshot_path)
            
            # Define languages
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
            
            # Get languages from settings
            source_lang_text = self.settings.value("language/source", "Английский")
            target_lang_text = self.settings.value("language/target", "Русский")
            
            source_lang = source_lang_map.get(source_lang_text, "en")
            target_lang = target_lang_map.get(target_lang_text, "ru")
            
            # Translation
            translated = self.translator.translate(
                text, source_lang, target_lang, 
                self.settings.value("translator/provider", "openai")
            )
            
            # Send results
            self.result_ready.emit(text, translated)
            
        except Exception as e:
            self.result_ready.emit("Error processing window", str(e))

class ScreenCaptureTab(QWidget):
    """Window capture tab"""
    
    def __init__(self):
        """Initialize the window capture tab"""
        super().__init__()
        
        # Load settings
        self.settings = QSettings("TranslatorApp", "Translator")
        
        # Create UI
        self.init_ui()
        
        # Initialize objects for working with windows
        self.window_manager = WindowManager()
        self.capture_thread = None
        
        # Update window list on startup
        self.update_window_list()
    
    def init_ui(self):
        """Initialize the interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # "Window Selection" section
        window_group = QGroupBox("Window Selection")
        window_layout = QVBoxLayout()
        window_group.setLayout(window_layout)
        
        # List of available windows
        window_layout.addWidget(QLabel("Available windows:"))
        self.window_list = QListWidget()
        window_layout.addWidget(self.window_list)
        
        # Refresh button
        refresh_button = QPushButton("Refresh List")
        refresh_button.clicked.connect(self.update_window_list)
        window_layout.addWidget(refresh_button)
        
        # Capture button
        capture_button = QPushButton("Capture Window")
        capture_button.clicked.connect(self.capture_window)
        window_layout.addWidget(capture_button)
        
        # "Preview" section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        preview_group.setLayout(preview_layout)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setText("Preview will appear here...")
        preview_layout.addWidget(self.preview_label)
        
        # "Language" section
        lang_group = QGroupBox("Languages")
        lang_layout = QHBoxLayout()
        lang_group.setLayout(lang_layout)
        
        # Source language
        lang_layout.addWidget(QLabel("Source language:"))
        self.source_lang = QComboBox()
        self.source_lang.addItems(["Английский", "Русский", "Японский"])
        self.source_lang.setCurrentText(self.settings.value("language/source", "Английский"))
        lang_layout.addWidget(self.source_lang)
        
        # Target language
        lang_layout.addWidget(QLabel("Target language:"))
        self.target_lang = QComboBox()
        self.target_lang.addItems(["Русский", "Английский", "Японский"])
        self.target_lang.setCurrentText(self.settings.value("language/target", "Русский"))
        lang_layout.addWidget(self.target_lang)
        
        # "Results" section
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        # Original text
        results_layout.addWidget(QLabel("Original text:"))
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setPlaceholderText("Original text will appear here...")
        results_layout.addWidget(self.original_text)
        
        # Translated text
        results_layout.addWidget(QLabel("Translation:"))
        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        self.translated_text.setPlaceholderText("Translation will appear here...")
        results_layout.addWidget(self.translated_text)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        copy_button = QPushButton("Copy Translation")
        copy_button.clicked.connect(self.copy_translation)
        actions_layout.addWidget(copy_button)
        
        overlay_button = QPushButton("Show in Overlay")
        overlay_button.clicked.connect(self.show_overlay)
        actions_layout.addWidget(overlay_button)
        
        results_layout.addLayout(actions_layout)
        
        # Add all sections to the main layout
        layout.addWidget(window_group)
        layout.addWidget(preview_group)
        layout.addWidget(lang_group)
        layout.addWidget(results_group)
    
    def update_window_list(self):
        """Update the list of available windows"""
        # Clear the list
        self.window_list.clear()
        
        try:
            # Get the list of real windows
            windows = self.window_manager.get_window_list()
            
            # If the list is empty or an error occurred, add examples for demonstration
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
                # Add real windows to the list
                for window in windows:
                    self.window_list.addItem(window)
        except Exception as e:
            # In case of error, show a message
            self.window_list.addItem(f"Error getting window list: {e}")
            self.window_list.addItem("Install required libraries: pip install pywin32 psutil")
    
    def capture_window(self):
        """Capture the selected window"""
        # Check if a window is selected
        selected_items = self.window_list.selectedItems()
        if not selected_items:
            self.original_text.setText("Error: no window selected for capture")
            return
        
        window_title = selected_items[0].text()
        
        # Update language values in settings
        self.settings.setValue("language/source", self.source_lang.currentText())
        self.settings.setValue("language/target", self.target_lang.currentText())
        
        # Create and start the capture thread
        self.capture_thread = WindowCaptureThread(window_title, self.settings)
        self.capture_thread.result_ready.connect(self.on_result_ready)
        self.capture_thread.preview_ready.connect(self.on_preview_ready)
        self.capture_thread.start()
        
        # Show process message
        self.original_text.setText("Capturing window and recognizing text...")
        self.translated_text.setText("Please wait...")
    
    def on_preview_ready(self, pixmap):
        """Handle the ready preview"""
        # Scale the image to fit the label size
        scaled_pixmap = pixmap.scaled(
            self.preview_label.width(), self.preview_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)
    
    def on_result_ready(self, original, translated):
        """Handle the recognition and translation results"""
        self.original_text.setText(original)
        self.translated_text.setText(translated)
    
    def copy_translation(self):
        """Copy translation to clipboard"""
        text = self.translated_text.toPlainText()
        if text and text != "Please wait...":
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Visual indication that text was copied
            original_color = self.translated_text.styleSheet()
            self.translated_text.setStyleSheet("background-color: #505050;")
            QTimer.singleShot(200, lambda: self.translated_text.setStyleSheet(original_color))
    
    def show_overlay(self):
        """Show translation in overlay above the window"""
        # In future version, there will be code for displaying overlay
        # Now just show a message
        original_color = self.translated_text.styleSheet()
        self.translated_text.setStyleSheet("background-color: #505050;")
        self.translated_text.setText(
            self.translated_text.toPlainText() + "\n\n(Overlay display will be available in the next version)"
        )
        QTimer.singleShot(200, lambda: self.translated_text.setStyleSheet(original_color)) 