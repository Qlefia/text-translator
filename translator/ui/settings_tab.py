"""
Settings tab for the application
"""

import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QLineEdit, QTabWidget, QGroupBox, QRadioButton,
    QCheckBox, QFormLayout, QScrollArea, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QSettings

class SettingsTab(QWidget):
    """Settings tab for the application"""
    
    def __init__(self):
        """Initialize the settings tab"""
        super().__init__()
        
        # Initialize settings
        self.settings = QSettings("TranslatorApp", "Translator")
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create tabs for settings sections
        self.settings_tabs = QTabWidget()
        main_layout.addWidget(self.settings_tabs)
        
        # Add tabs for different settings groups
        self.settings_tabs.addTab(self.create_api_tab(), "API and translators")
        self.settings_tabs.addTab(self.create_language_tab(), "Languages")
        self.settings_tabs.addTab(self.create_hotkeys_tab(), "Hotkeys")
        self.settings_tabs.addTab(self.create_appearance_tab(), "Appearance")
        self.settings_tabs.addTab(self.create_ocr_tab(), "OCR and recognition")
        self.settings_tabs.addTab(self.create_other_tab(), "Other settings")
        
        # Save/cancel buttons
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        
        # Save settings button
        self.save_button = QPushButton("Save settings")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        # Cancel changes button
        self.cancel_button = QPushButton("Cancel changes")
        self.cancel_button.clicked.connect(self.load_settings)
        button_layout.addWidget(self.cancel_button)
        
        # Load settings
        self.load_settings()
    
    def create_api_tab(self):
        """
        Create API settings tab
        
        Returns:
            QWidget: tab widget
        """
        api_widget = QWidget()
        api_layout = QVBoxLayout()
        api_widget.setLayout(api_layout)
        
        # Translator provider selection
        provider_group = QGroupBox("Translator provider")
        provider_layout = QVBoxLayout()
        provider_group.setLayout(provider_layout)
        
        # Radio buttons for provider selection
        self.openai_radio = QRadioButton("OpenAI (GPT)")
        self.deepseek_radio = QRadioButton("DeepSeek")
        provider_layout.addWidget(self.openai_radio)
        provider_layout.addWidget(self.deepseek_radio)
        
        # OpenAI settings group
        openai_group = QGroupBox("OpenAI settings")
        openai_layout = QFormLayout()
        openai_group.setLayout(openai_layout)
        
        self.openai_api_key = QLineEdit()
        self.openai_api_key.setEchoMode(QLineEdit.Password)  # Hide key
        openai_layout.addRow("API key:", self.openai_api_key)
        
        self.openai_base_url = QLineEdit()
        self.openai_base_url.setText("https://api.openai.com/v1")
        openai_layout.addRow("Base URL:", self.openai_base_url)
        
        self.openai_model = QComboBox()
        self.openai_model.addItems(["gpt-4", "gpt-3.5-turbo"])
        openai_layout.addRow("Model:", self.openai_model)
        
        # DeepSeek settings group
        deepseek_group = QGroupBox("DeepSeek settings")
        deepseek_layout = QFormLayout()
        deepseek_group.setLayout(deepseek_layout)
        
        self.deepseek_api_key = QLineEdit()
        self.deepseek_api_key.setEchoMode(QLineEdit.Password)  # Hide key
        deepseek_layout.addRow("API key:", self.deepseek_api_key)
        
        self.deepseek_base_url = QLineEdit()
        self.deepseek_base_url.setText("https://api.aiguoguo199.com/v1")
        deepseek_layout.addRow("Base URL:", self.deepseek_base_url)
        
        self.deepseek_model = QComboBox()
        self.deepseek_model.addItems(["deepseek-chat"])
        deepseek_layout.addRow("Model:", self.deepseek_model)
        
        # Add groups to the tab
        api_layout.addWidget(provider_group)
        api_layout.addWidget(openai_group)
        api_layout.addWidget(deepseek_group)
        
        # API key test button
        test_button = QPushButton("Test API key")
        test_button.clicked.connect(self.test_api_key)
        api_layout.addWidget(test_button)
        
        api_layout.addStretch()
        
        return api_widget
    
    def create_language_tab(self):
        """
        Create language settings tab
        
        Returns:
            QWidget: tab widget
        """
        language_widget = QWidget()
        language_layout = QVBoxLayout()
        language_widget.setLayout(language_layout)
        
        # Interface language group
        ui_lang_group = QGroupBox("Interface language")
        ui_lang_layout = QVBoxLayout()
        ui_lang_group.setLayout(ui_lang_layout)
        
        self.ui_language = QComboBox()
        self.ui_language.addItems(["Russian", "English"])
        ui_lang_layout.addWidget(self.ui_language)
        
        # Default translation languages group
        default_langs_group = QGroupBox("Default translation languages")
        default_langs_layout = QFormLayout()
        default_langs_group.setLayout(default_langs_layout)
        
        self.source_language = QComboBox()
        self.source_language.addItems(["English", "Japanese", "Russian"])
        default_langs_layout.addRow("Source language:", self.source_language)
        
        self.target_language = QComboBox()
        self.target_language.addItems(["Russian", "English", "Japanese"])
        default_langs_layout.addRow("Translation language:", self.target_language)
        
        # Additional settings
        autodect_check = QCheckBox("Automatic language detection of the source text")
        autodect_check.setChecked(True)
        
        # Add groups to the tab
        language_layout.addWidget(ui_lang_group)
        language_layout.addWidget(default_langs_group)
        language_layout.addWidget(autodect_check)
        language_layout.addStretch()
        
        return language_widget
    
    def create_hotkeys_tab(self):
        """
        Create hotkeys settings tab
        
        Returns:
            QWidget: tab widget
        """
        hotkeys_widget = QWidget()
        hotkeys_layout = QFormLayout()
        hotkeys_widget.setLayout(hotkeys_layout)
        
        # Hotkey fields
        self.area_capture_hotkey = QLineEdit("Alt+Shift+C")
        hotkeys_layout.addRow("Screen capture:", self.area_capture_hotkey)
        
        self.window_capture_hotkey = QLineEdit("Alt+Shift+W")
        hotkeys_layout.addRow("Window capture:", self.window_capture_hotkey)
        
        self.show_hide_hotkey = QLineEdit("Alt+Shift+H")
        hotkeys_layout.addRow("Show/hide application:", self.show_hide_hotkey)
        
        self.close_overlay_hotkey = QLineEdit("Alt+Shift+X")
        hotkeys_layout.addRow("Close overlay:", self.close_overlay_hotkey)
        
        self.copy_translation_hotkey = QLineEdit("Ctrl+C")
        hotkeys_layout.addRow("Copy translation:", self.copy_translation_hotkey)
        
        # Warning
        warning_label = QLabel("Note: changing hotkeys requires application restart.")
        warning_label.setWordWrap(True)
        hotkeys_layout.addRow(warning_label)
        
        return hotkeys_widget
    
    def create_appearance_tab(self):
        """
        Create appearance settings tab
        
        Returns:
            QWidget: tab widget
        """
        appearance_widget = QWidget()
        appearance_layout = QVBoxLayout()
        appearance_widget.setLayout(appearance_layout)
        
        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        theme_group.setLayout(theme_layout)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Mocha (dark)", "Latte (light)", "Frappe", "Macchiato"])
        theme_layout.addWidget(self.theme_combo)
        
        # Overlay settings
        overlay_group = QGroupBox("Translation overlay settings")
        overlay_layout = QFormLayout()
        overlay_group.setLayout(overlay_layout)
        
        self.overlay_transparency = QComboBox()
        self.overlay_transparency.addItems(["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%"])
        self.overlay_transparency.setCurrentText("30%")
        overlay_layout.addRow("Background transparency:", self.overlay_transparency)
        
        self.overlay_duration = QComboBox()
        self.overlay_duration.addItems(["3 seconds", "5 seconds", "10 seconds", "15 seconds", "Infinite"])
        overlay_layout.addRow("Display duration:", self.overlay_duration)
        
        # Additional options
        self.show_animations = QCheckBox("Show animations")
        self.show_animations.setChecked(True)
        
        self.rounded_corners = QCheckBox("Rounded interface corners")
        self.rounded_corners.setChecked(True)
        
        # Add groups to the tab
        appearance_layout.addWidget(theme_group)
        appearance_layout.addWidget(overlay_group)
        appearance_layout.addWidget(self.show_animations)
        appearance_layout.addWidget(self.rounded_corners)
        appearance_layout.addStretch()
        
        return appearance_widget
    
    def create_ocr_tab(self):
        """
        Create OCR settings tab
        
        Returns:
            QWidget: tab widget
        """
        ocr_widget = QWidget()
        ocr_layout = QVBoxLayout()
        ocr_widget.setLayout(ocr_layout)
        
        # OCR engine selection
        engine_group = QGroupBox("OCR engine")
        engine_layout = QVBoxLayout()
        engine_group.setLayout(engine_layout)
        
        self.ocr_engine = QComboBox()
        self.ocr_engine.addItems(["Tesseract OCR"])
        engine_layout.addWidget(self.ocr_engine)
        
        # Tesseract path
        tesseract_group = QGroupBox("Tesseract OCR settings")
        tesseract_layout = QFormLayout()
        tesseract_group.setLayout(tesseract_layout)
        
        self.tesseract_path = QLineEdit()
        if os.name == 'nt':  # Windows
            self.tesseract_path.setText(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.tesseract_path)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_tesseract)
        path_layout.addWidget(browse_button)
        tesseract_layout.addRow("Tesseract path:", path_layout)
        
        # Real-time settings
        realtime_group = QGroupBox("Real-time mode")
        realtime_layout = QFormLayout()
        realtime_group.setLayout(realtime_layout)
        
        self.update_interval = QComboBox()
        self.update_interval.addItems(["0.5 seconds", "1 second", "2 seconds", "3 seconds", "5 seconds"])
        realtime_layout.addRow("Update interval:", self.update_interval)
        
        self.max_duration = QComboBox()
        self.max_duration.addItems(["30 seconds", "1 minute", "2 minutes", "5 minutes", "Infinite"])
        realtime_layout.addRow("Maximum duration:", self.max_duration)
        
        # Add groups to the tab
        ocr_layout.addWidget(engine_group)
        ocr_layout.addWidget(tesseract_group)
        ocr_layout.addWidget(realtime_group)
        ocr_layout.addStretch()
        
        return ocr_widget
    
    def create_other_tab(self):
        """
        Create other settings tab
        
        Returns:
            QWidget: tab widget
        """
        other_widget = QWidget()
        other_layout = QVBoxLayout()
        other_widget.setLayout(other_layout)
        
        # Auto-start
        self.autostart = QCheckBox("Start with system startup")
        other_layout.addWidget(self.autostart)
        
        # Minimize to tray
        self.minimize_to_tray = QCheckBox("Minimize to tray instead of closing")
        self.minimize_to_tray.setChecked(True)
        other_layout.addWidget(self.minimize_to_tray)
        
        # Confirm exit
        self.confirm_exit = QCheckBox("Confirm exit from application")
        self.confirm_exit.setChecked(True)
        other_layout.addWidget(self.confirm_exit)
        
        # Error logging
        self.error_logging = QCheckBox("Enable error logging")
        self.error_logging.setChecked(True)
        other_layout.addWidget(self.error_logging)
        
        # Clear history
        clear_history_button = QPushButton("Clear translation history")
        clear_history_button.clicked.connect(self.clear_history)
        other_layout.addWidget(clear_history_button)
        
        # Version
        version_label = QLabel("Application version: 0.1.0")
        other_layout.addWidget(version_label)
        
        other_layout.addStretch()
        
        return other_widget
    
    def browse_tesseract(self):
        """Open dialog to select Tesseract path"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Tesseract executable", 
            "", 
            "Executable (*.exe);;All Files (*)"
        )
        if file_path:
            self.tesseract_path.setText(file_path)
    
    def test_api_key(self):
        """Test API key"""
        try:
            if self.openai_radio.isChecked():
                api_key = self.openai_api_key.text()
                base_url = self.openai_base_url.text()
                provider = "openai"
            else:
                api_key = self.deepseek_api_key.text()
                base_url = self.deepseek_base_url.text()
                provider = "deepseek"
                
            if not api_key:
                QMessageBox.warning(
                    self, 
                    "Error", 
                    f"API key for {provider} not specified"
                )
                return
                
            # Initialize translator
            import os
            from translator.models.translator import LLMTranslator
            
            # Create translator
            db_dir = os.path.join(os.path.expanduser("~"), ".translator")
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            db_path = os.path.join(db_dir, "translations.db")
            
            translator = LLMTranslator(db_path)
            translator.set_api_key(provider, api_key, base_url)
            
            # Test request
            test_text = "Hello world"
            source_lang = "en"
            target_lang = "ru"
            
            result = translator.translate(test_text, source_lang, target_lang, provider)
            
            if result and result != f"Translation error:":
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"API key works correctly!\n\nTest translation:\n{test_text} → {result}"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Error", 
                    f"Failed to perform test translation. Check API key and URL."
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error checking API key: {e}"
            )
    
    def clear_history(self):
        """Clear translation history"""
        reply = QMessageBox.question(
            self, 
            "Confirmation", 
            "Are you sure you want to clear all translation history?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Here should be the actual history clearing
            QMessageBox.information(
                self, 
                "Information", 
                "Translation history cleared"
            )
    
    def save_settings(self):
        """Save settings"""
        # Translator provider
        self.settings.setValue("translator/provider", "openai" if self.openai_radio.isChecked() else "deepseek")
        
        # API keys and URLs
        self.settings.setValue("openai/api_key", self.openai_api_key.text())
        self.settings.setValue("openai/base_url", self.openai_base_url.text())
        self.settings.setValue("openai/model", self.openai_model.currentText())
        
        self.settings.setValue("deepseek/api_key", self.deepseek_api_key.text())
        self.settings.setValue("deepseek/base_url", self.deepseek_base_url.text())
        self.settings.setValue("deepseek/model", self.deepseek_model.currentText())
        
        # Languages
        self.settings.setValue("language/ui", self.ui_language.currentText())
        self.settings.setValue("language/source", self.source_language.currentText())
        self.settings.setValue("language/target", self.target_language.currentText())
        
        # Hotkeys
        self.settings.setValue("hotkeys/area_capture", self.area_capture_hotkey.text())
        self.settings.setValue("hotkeys/window_capture", self.window_capture_hotkey.text())
        self.settings.setValue("hotkeys/show_hide", self.show_hide_hotkey.text())
        self.settings.setValue("hotkeys/close_overlay", self.close_overlay_hotkey.text())
        self.settings.setValue("hotkeys/copy_translation", self.copy_translation_hotkey.text())
        
        # Appearance
        self.settings.setValue("appearance/theme", self.theme_combo.currentText())
        self.settings.setValue("appearance/overlay_transparency", self.overlay_transparency.currentText())
        self.settings.setValue("appearance/overlay_duration", self.overlay_duration.currentText())
        self.settings.setValue("appearance/show_animations", self.show_animations.isChecked())
        self.settings.setValue("appearance/rounded_corners", self.rounded_corners.isChecked())
        
        # OCR
        self.settings.setValue("ocr/engine", self.ocr_engine.currentText())
        self.settings.setValue("ocr/tesseract_path", self.tesseract_path.text())
        self.settings.setValue("ocr/update_interval", self.update_interval.currentText())
        self.settings.setValue("ocr/max_duration", self.max_duration.currentText())
        
        # Other
        self.settings.setValue("other/autostart", self.autostart.isChecked())
        self.settings.setValue("other/minimize_to_tray", self.minimize_to_tray.isChecked())
        self.settings.setValue("other/confirm_exit", self.confirm_exit.isChecked())
        self.settings.setValue("other/error_logging", self.error_logging.isChecked())
        
        QMessageBox.information(
            self, 
            "Information", 
            "Settings saved successfully"
        )
    
    def load_settings(self):
        """Load saved settings"""
        # Translator provider
        provider = self.settings.value("translator/provider", "openai")
        if provider == "openai":
            self.openai_radio.setChecked(True)
        else:
            self.deepseek_radio.setChecked(True)
        
        # API keys and URLs
        self.openai_api_key.setText(self.settings.value("openai/api_key", ""))
        self.openai_base_url.setText(self.settings.value("openai/base_url", "https://api.openai.com/v1"))
        self.openai_model.setCurrentText(self.settings.value("openai/model", "gpt-4"))
        
        self.deepseek_api_key.setText(self.settings.value("deepseek/api_key", ""))
        self.deepseek_base_url.setText(self.settings.value("deepseek/base_url", "https://api.aiguoguo199.com/v1"))
        self.deepseek_model.setCurrentText(self.settings.value("deepseek/model", "deepseek-chat"))
        
        # Languages
        self.ui_language.setCurrentText(self.settings.value("language/ui", "Russian"))
        self.source_language.setCurrentText(self.settings.value("language/source", "English"))
        self.target_language.setCurrentText(self.settings.value("language/target", "Russian"))
        
        # Hotkeys
        self.area_capture_hotkey.setText(self.settings.value("hotkeys/area_capture", "Alt+Shift+C"))
        self.window_capture_hotkey.setText(self.settings.value("hotkeys/window_capture", "Alt+Shift+W"))
        self.show_hide_hotkey.setText(self.settings.value("hotkeys/show_hide", "Alt+Shift+H"))
        self.close_overlay_hotkey.setText(self.settings.value("hotkeys/close_overlay", "Alt+Shift+X"))
        self.copy_translation_hotkey.setText(self.settings.value("hotkeys/copy_translation", "Ctrl+C"))
        
        # Appearance
        self.theme_combo.setCurrentText(self.settings.value("appearance/theme", "Mocha (dark)"))
        self.overlay_transparency.setCurrentText(self.settings.value("appearance/overlay_transparency", "30%"))
        self.overlay_duration.setCurrentText(self.settings.value("appearance/overlay_duration", "5 seconds"))
        self.show_animations.setChecked(self.settings.value("appearance/show_animations", True, type=bool))
        self.rounded_corners.setChecked(self.settings.value("appearance/rounded_corners", True, type=bool))
        
        # OCR
        self.ocr_engine.setCurrentText(self.settings.value("ocr/engine", "Tesseract OCR"))
        
        default_tesseract_path = ""
        if os.name == 'nt':  # Windows
            default_tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        self.tesseract_path.setText(self.settings.value("ocr/tesseract_path", default_tesseract_path))
        self.update_interval.setCurrentText(self.settings.value("ocr/update_interval", "1 second"))
        self.max_duration.setCurrentText(self.settings.value("ocr/max_duration", "1 minute"))
        
        # Other
        self.autostart.setChecked(self.settings.value("other/autostart", False, type=bool))
        self.minimize_to_tray.setChecked(self.settings.value("other/minimize_to_tray", True, type=bool))
        self.confirm_exit.setChecked(self.settings.value("other/confirm_exit", True, type=bool))
        self.error_logging.setChecked(self.settings.value("other/error_logging", True, type=bool)) 