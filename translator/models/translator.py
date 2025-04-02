"""
Модуль для перевода текста с использованием различных API провайдеров (OpenAI, DeepSeek и т.д.)
"""

import json
import sqlite3
import time
import os
import requests
from openai import OpenAI
from datetime import datetime

class LLMTranslator:
    """Класс для перевода текста с помощью больших языковых моделей (LLM)"""
    
    def __init__(self, db_path='translations.db'):
        """
        Инициализация переводчика
        
        Args:
            db_path: путь к базе данных для кэширования переводов
        """
        self.db_path = db_path
        self._init_db()
        self.default_provider = 'openai'
        self.openai_api_key = None
        self.openai_base_url = "https://api.openai.com/v1"
        self.deepseek_api_key = None
        self.deepseek_base_url = "https://api.aiguoguo199.com/v1"
        
    def _init_db(self):
        """Инициализация базы данных для кэширования"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
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
        
    def set_api_key(self, provider, api_key, base_url=None):
        """
        Установка API ключа для конкретного провайдера
        
        Args:
            provider: имя провайдера ('openai', 'deepseek')
            api_key: API ключ
            base_url: базовый URL для API (опционально)
        """
        if provider == 'openai':
            self.openai_api_key = api_key
            if base_url:
                self.openai_base_url = base_url
        elif provider == 'deepseek':
            self.deepseek_api_key = api_key
            if base_url:
                self.deepseek_base_url = base_url
        else:
            raise ValueError(f"Неизвестный провайдер: {provider}")
            
    def set_default_provider(self, provider):
        """
        Установка провайдера по умолчанию
        
        Args:
            provider: имя провайдера ('openai', 'deepseek')
        """
        if provider not in ['openai', 'deepseek']:
            raise ValueError(f"Неизвестный провайдер: {provider}")
        self.default_provider = provider
        
    def _get_cached_translation(self, source_text, source_lang, target_lang, provider):
        """
        Получение перевода из кэша
        
        Args:
            source_text: исходный текст
            source_lang: язык исходного текста
            target_lang: целевой язык
            provider: провайдер
            
        Returns:
            str: переведенный текст или None, если кэш не найден
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT target_text FROM translations WHERE source_text=? AND source_lang=? AND target_lang=? AND provider=?",
            (source_text, source_lang, target_lang, provider)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        return None
        
    def _cache_translation(self, source_text, target_text, source_lang, target_lang, provider):
        """
        Сохранение перевода в кэш
        
        Args:
            source_text: исходный текст
            target_text: переведенный текст
            source_lang: язык исходного текста
            target_lang: целевой язык
            provider: провайдер
        """
        current_time = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO translations (source_text, target_text, source_lang, target_lang, provider, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (source_text, target_text, source_lang, target_lang, provider, current_time)
        )
        conn.commit()
        conn.close()
        
    def translate_with_openai(self, text, source_lang, target_lang):
        """
        Перевод текста с помощью OpenAI API
        
        Args:
            text: исходный текст
            source_lang: язык исходного текста ('en', 'ja', 'ru')
            target_lang: целевой язык ('en', 'ja', 'ru')
            
        Returns:
            str: переведенный текст
        """
        if not self.openai_api_key:
            raise ValueError("API ключ OpenAI не установлен")
            
        # Проверка кэша
        cached = self._get_cached_translation(text, source_lang, target_lang, 'openai')
        if cached:
            return cached
            
        # Формирование промпта для перевода
        client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_base_url
        )
        
        # Подготовка правильного наименования языков
        lang_names = {
            'en': 'English',
            'ru': 'Russian',
            'ja': 'Japanese'
        }
        
        source_lang_name = lang_names.get(source_lang, source_lang)
        target_lang_name = lang_names.get(target_lang, target_lang)
        
        # Создание промпта
        prompt = f"""You are a professional translator. 
Translate the following text from {source_lang_name} to {target_lang_name}, preserving the meaning, tone, and style. 
Respond only with the translated text, without any additional commentary or explanations.

Text: {text}"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",  # Можно использовать другую модель, например "gpt-3.5-turbo"
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Низкая температура для более строгого перевода
                max_tokens=2048
            )
            
            # Получение текста ответа
            translated_text = response.choices[0].message.content.strip()
            
            # Кэширование результата
            self._cache_translation(text, translated_text, source_lang, target_lang, 'openai')
            
            return translated_text
        except Exception as e:
            print(f"Ошибка при переводе через OpenAI: {e}")
            return f"Ошибка перевода: {e}"
            
    def translate_with_deepseek(self, text, source_lang, target_lang):
        """
        Перевод текста с помощью DeepSeek API
        
        Args:
            text: исходный текст
            source_lang: язык исходного текста ('en', 'ja', 'ru')
            target_lang: целевой язык ('en', 'ja', 'ru')
            
        Returns:
            str: переведенный текст
        """
        if not self.deepseek_api_key:
            raise ValueError("API ключ DeepSeek не установлен")
            
        # Проверка кэша
        cached = self._get_cached_translation(text, source_lang, target_lang, 'deepseek')
        if cached:
            return cached
            
        # Формирование промпта для перевода
        client = OpenAI(
            api_key=self.deepseek_api_key,
            base_url=self.deepseek_base_url
        )
        
        # Подготовка правильного наименования языков
        lang_names = {
            'en': 'English',
            'ru': 'Russian',
            'ja': 'Japanese'
        }
        
        source_lang_name = lang_names.get(source_lang, source_lang)
        target_lang_name = lang_names.get(target_lang, target_lang)
        
        # Создание промпта
        prompt = f"""You are a professional translator. 
Translate the following text from {source_lang_name} to {target_lang_name}, preserving the meaning, tone, and style. 
Respond only with the translated text, without any additional commentary or explanations.

Text: {text}"""
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",  # Модель DeepSeek
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2048
            )
            
            # Получение текста ответа
            translated_text = response.choices[0].message.content.strip()
            
            # Кэширование результата
            self._cache_translation(text, translated_text, source_lang, target_lang, 'deepseek')
            
            return translated_text
        except Exception as e:
            print(f"Ошибка при переводе через DeepSeek: {e}")
            return f"Ошибка перевода: {e}"
    
    def translate(self, text, source_lang, target_lang, provider=None):
        """
        Перевод текста с использованием указанного провайдера
        
        Args:
            text: исходный текст
            source_lang: язык исходного текста ('en', 'ja', 'ru')
            target_lang: целевой язык ('en', 'ja', 'ru')
            provider: провайдер перевода (если None, используется провайдер по умолчанию)
            
        Returns:
            str: переведенный текст
        """
        if not provider:
            provider = self.default_provider
            
        if provider == 'openai':
            return self.translate_with_openai(text, source_lang, target_lang)
        elif provider == 'deepseek':
            return self.translate_with_deepseek(text, source_lang, target_lang)
        else:
            raise ValueError(f"Неизвестный провайдер: {provider}")
            
    def get_translation_history(self, limit=50):
        """
        Получение истории переводов
        
        Args:
            limit: максимальное количество записей
            
        Returns:
            list: список словарей с данными о переводах
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM translations ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        results = cursor.fetchall()
        conn.close()
        
        # Преобразование результатов в список словарей
        history = []
        for row in results:
            history.append({
                'id': row['id'],
                'source_text': row['source_text'],
                'target_text': row['target_text'],
                'source_lang': row['source_lang'],
                'target_lang': row['target_lang'],
                'provider': row['provider'],
                'timestamp': row['timestamp']
            })
            
        return history
        
    def clear_history(self):
        """Очистка истории переводов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM translations")
        conn.commit()
        conn.close() 