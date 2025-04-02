"""
Вкладка истории переводов
"""

import os
import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QGroupBox, QApplication, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QDialog, QSplitter
)
from PyQt5.QtCore import Qt, QSettings, QTimer, pyqtSignal, QDateTime
from PyQt5.QtGui import QIcon, QFont

class TranslationDetailsDialog(QDialog):
    """Диалог для отображения деталей перевода"""
    
    def __init__(self, translation_data, parent=None):
        """
        Инициализация диалога деталей перевода
        
        Args:
            translation_data: словарь с данными о переводе
            parent: родительский виджет
        """
        super().__init__(parent)
        self.translation_data = translation_data
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Детали перевода")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Информация о переводе
        info_layout = QHBoxLayout()
        
        # Дата и время
        timestamp = datetime.fromisoformat(self.translation_data['timestamp'])
        info_layout.addWidget(QLabel(f"Дата: {timestamp.strftime('%d.%m.%Y %H:%M:%S')}"))
        
        # Языки
        info_layout.addWidget(QLabel(f"Языки: {self.translation_data['source_lang']} → {self.translation_data['target_lang']}"))
        
        # Провайдер
        info_layout.addWidget(QLabel(f"Провайдер: {self.translation_data['provider']}"))
        
        layout.addLayout(info_layout)
        
        # Разделитель с оригиналом и переводом
        splitter = QSplitter(Qt.Vertical)
        
        # Исходный текст
        source_group = QGroupBox("Оригинал")
        source_layout = QVBoxLayout()
        source_group.setLayout(source_layout)
        
        self.source_text = QTextEdit()
        self.source_text.setText(self.translation_data['source_text'])
        self.source_text.setReadOnly(True)
        source_layout.addWidget(self.source_text)
        
        source_buttons = QHBoxLayout()
        copy_source_button = QPushButton("Копировать оригинал")
        copy_source_button.clicked.connect(self.copy_source)
        source_buttons.addWidget(copy_source_button)
        source_layout.addLayout(source_buttons)
        
        splitter.addWidget(source_group)
        
        # Переведенный текст
        target_group = QGroupBox("Перевод")
        target_layout = QVBoxLayout()
        target_group.setLayout(target_layout)
        
        self.target_text = QTextEdit()
        self.target_text.setText(self.translation_data['target_text'])
        self.target_text.setReadOnly(True)
        target_layout.addWidget(self.target_text)
        
        target_buttons = QHBoxLayout()
        copy_target_button = QPushButton("Копировать перевод")
        copy_target_button.clicked.connect(self.copy_target)
        target_buttons.addWidget(copy_target_button)
        target_layout.addLayout(target_buttons)
        
        splitter.addWidget(target_group)
        
        layout.addWidget(splitter, 1)
        
        # Кнопки внизу диалога
        buttons_layout = QHBoxLayout()
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
    
    def copy_source(self):
        """Копирование исходного текста в буфер обмена"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.source_text.toPlainText())
        
        # Визуальная индикация
        original_color = self.source_text.styleSheet()
        self.source_text.setStyleSheet("background-color: #505050;")
        QTimer.singleShot(200, lambda: self.source_text.setStyleSheet(original_color))
    
    def copy_target(self):
        """Копирование переведенного текста в буфер обмена"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.target_text.toPlainText())
        
        # Визуальная индикация
        original_color = self.target_text.styleSheet()
        self.target_text.setStyleSheet("background-color: #505050;")
        QTimer.singleShot(200, lambda: self.target_text.setStyleSheet(original_color))

class HistoryTab(QWidget):
    """Вкладка истории переводов"""
    
    def __init__(self):
        """Инициализация вкладки истории"""
        super().__init__()
        
        # Загрузка настроек
        self.settings = QSettings("TranslatorApp", "Translator")
        
        # Путь к базе данных
        db_dir = os.path.join(os.path.expanduser("~"), ".translator")
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        self.db_path = os.path.join(db_dir, "translations.db")
        
        # Создание интерфейса
        self.init_ui()
        
        # Загрузка истории при запуске
        self.load_history()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Панель поиска и фильтров
        search_group = QGroupBox("Поиск и фильтры")
        search_layout = QHBoxLayout()
        search_group.setLayout(search_layout)
        
        # Поле поиска
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.textChanged.connect(self.filter_history)
        search_layout.addWidget(self.search_input)
        
        # Фильтр по языку оригинала
        search_layout.addWidget(QLabel("Язык оригинала:"))
        self.source_lang_filter = QComboBox()
        self.source_lang_filter.addItems(["Все", "Английский", "Русский", "Японский"])
        self.source_lang_filter.currentTextChanged.connect(self.filter_history)
        search_layout.addWidget(self.source_lang_filter)
        
        # Фильтр по языку перевода
        search_layout.addWidget(QLabel("Язык перевода:"))
        self.target_lang_filter = QComboBox()
        self.target_lang_filter.addItems(["Все", "Русский", "Английский", "Японский"])
        self.target_lang_filter.currentTextChanged.connect(self.filter_history)
        search_layout.addWidget(self.target_lang_filter)
        
        # Добавление панели поиска в основной лейаут
        layout.addWidget(search_group)
        
        # Таблица истории
        self.history_table = QTableWidget(0, 5)  # 0 строк, 5 столбцов
        self.history_table.setHorizontalHeaderLabels([
            "Дата", "Языки", "Провайдер", "Оригинал", "Перевод"
        ])
        
        # Настройка размеров столбцов
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Дата
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Языки
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Провайдер
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Оригинал
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Перевод
        
        # Двойной клик для отображения деталей
        self.history_table.itemDoubleClicked.connect(self.show_translation_details)
        
        layout.addWidget(self.history_table)
        
        # Кнопки управления историей
        buttons_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Обновить историю")
        refresh_button.clicked.connect(self.load_history)
        buttons_layout.addWidget(refresh_button)
        
        delete_button = QPushButton("Удалить выбранные")
        delete_button.clicked.connect(self.delete_selected)
        buttons_layout.addWidget(delete_button)
        
        clear_button = QPushButton("Очистить историю")
        clear_button.clicked.connect(self.clear_history)
        buttons_layout.addWidget(clear_button)
        
        layout.addLayout(buttons_layout)
    
    def load_history(self):
        """Загрузка истории переводов из базы данных"""
        try:
            # Подключение к базе данных
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Запрос к базе данных
            cursor.execute(
                "SELECT * FROM translations ORDER BY timestamp DESC LIMIT 500"
            )
            translations = cursor.fetchall()
            
            # Очистка таблицы
            self.history_table.setRowCount(0)
            
            # Заполнение таблицы данными
            for row_idx, translation in enumerate(translations):
                self.history_table.insertRow(row_idx)
                
                # Преобразование timestamp
                timestamp = datetime.fromisoformat(translation['timestamp'])
                date_item = QTableWidgetItem(timestamp.strftime("%d.%m.%Y %H:%M"))
                
                # Получение языков
                source_lang = translation['source_lang']
                target_lang = translation['target_lang']
                langs_item = QTableWidgetItem(f"{source_lang} → {target_lang}")
                
                # Получение провайдера
                provider_item = QTableWidgetItem(translation['provider'])
                
                # Усечение исходного текста
                source_text = translation['source_text']
                if len(source_text) > 100:
                    source_text = source_text[:97] + "..."
                source_item = QTableWidgetItem(source_text)
                
                # Усечение переведенного текста
                target_text = translation['target_text']
                if len(target_text) > 100:
                    target_text = target_text[:97] + "..."
                target_item = QTableWidgetItem(target_text)
                
                # Установка элементов в таблицу
                self.history_table.setItem(row_idx, 0, date_item)
                self.history_table.setItem(row_idx, 1, langs_item)
                self.history_table.setItem(row_idx, 2, provider_item)
                self.history_table.setItem(row_idx, 3, source_item)
                self.history_table.setItem(row_idx, 4, target_item)
                
                # Сохранение ID записи в элементе для последующей работы
                date_item.setData(Qt.UserRole, translation['id'])
                
                # Установка флага только для чтения
                for col in range(5):
                    item = self.history_table.item(row_idx, col)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            
            conn.close()
            
        except Exception as e:
            print(f"Ошибка при загрузке истории: {e}")
    
    def filter_history(self):
        """Фильтрация истории по поисковому запросу и фильтрам"""
        search_text = self.search_input.text().lower()
        source_lang_filter = self.source_lang_filter.currentText()
        target_lang_filter = self.target_lang_filter.currentText()
        
        # Отображение/скрытие строк таблицы
        for row in range(self.history_table.rowCount()):
            show_row = True
            
            # Фильтр по поисковому запросу
            if search_text:
                original_text = self.history_table.item(row, 3).text().lower()
                translated_text = self.history_table.item(row, 4).text().lower()
                
                if search_text not in original_text and search_text not in translated_text:
                    show_row = False
            
            # Фильтр по языку оригинала
            if source_lang_filter != "Все":
                langs_text = self.history_table.item(row, 1).text()
                source_lang = langs_text.split(" → ")[0]
                
                # Приведение кодов языков к удобочитаемым названиям
                if source_lang == "en":
                    source_lang = "Английский"
                elif source_lang == "ru":
                    source_lang = "Русский"
                elif source_lang == "ja":
                    source_lang = "Японский"
                
                if source_lang != source_lang_filter:
                    show_row = False
            
            # Фильтр по языку перевода
            if target_lang_filter != "Все":
                langs_text = self.history_table.item(row, 1).text()
                target_lang = langs_text.split(" → ")[1]
                
                # Приведение кодов языков к удобочитаемым названиям
                if target_lang == "en":
                    target_lang = "Английский"
                elif target_lang == "ru":
                    target_lang = "Русский"
                elif target_lang == "ja":
                    target_lang = "Японский"
                
                if target_lang != target_lang_filter:
                    show_row = False
            
            # Отображение или скрытие строки
            self.history_table.setRowHidden(row, not show_row)
    
    def show_translation_details(self, item):
        """Отображение диалога с деталями перевода"""
        row = item.row()
        translation_id = self.history_table.item(row, 0).data(Qt.UserRole)
        
        try:
            # Получение полных данных о переводе
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM translations WHERE id = ?",
                (translation_id,)
            )
            translation = cursor.fetchone()
            conn.close()
            
            if translation:
                # Создание диалога с деталями
                translation_data = {
                    'id': translation['id'],
                    'source_text': translation['source_text'],
                    'target_text': translation['target_text'],
                    'source_lang': translation['source_lang'],
                    'target_lang': translation['target_lang'],
                    'provider': translation['provider'],
                    'timestamp': translation['timestamp']
                }
                
                details_dialog = TranslationDetailsDialog(translation_data, self)
                details_dialog.exec_()
        except Exception as e:
            print(f"Ошибка при отображении деталей перевода: {e}")
    
    def delete_selected(self):
        """Удаление выбранных переводов из истории"""
        selected_rows = set()
        
        # Получение выбранных строк
        for item in self.history_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        # Получение ID выбранных записей
        translation_ids = []
        for row in selected_rows:
            translation_id = self.history_table.item(row, 0).data(Qt.UserRole)
            translation_ids.append(translation_id)
        
        try:
            # Удаление записей из базы данных
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for translation_id in translation_ids:
                cursor.execute(
                    "DELETE FROM translations WHERE id = ?",
                    (translation_id,)
                )
            
            conn.commit()
            conn.close()
            
            # Обновление таблицы
            self.load_history()
        except Exception as e:
            print(f"Ошибка при удалении переводов: {e}")
    
    def clear_history(self):
        """Очистка всей истории переводов"""
        try:
            # Удаление всех записей из базы данных
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM translations")
            conn.commit()
            conn.close()
            
            # Обновление таблицы
            self.load_history()
        except Exception as e:
            print(f"Ошибка при очистке истории: {e}") 