"""
Модуль для распознавания текста из изображений
"""

import os
import sys
import pytesseract
import tempfile
from PIL import Image, ImageEnhance, ImageFilter

class OCREngine:
    """Класс для распознавания текста с помощью OCR"""
    
    def __init__(self, tesseract_path=""):
        """
        Инициализация OCR движка
        
        Args:
            tesseract_path: путь к исполняемому файлу Tesseract OCR
        """
        # Установка пути к Tesseract, если он указан
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Проверка работоспособности Tesseract
        self.is_tesseract_available = self._check_tesseract()
        
        # Поддерживаемые языки
        self.supported_languages = {
            "en": "eng",  # Английский
            "ru": "rus",  # Русский
            "ja": "jpn"   # Японский
        }
    
    def _check_tesseract(self):
        """
        Проверка доступности Tesseract OCR
        
        Returns:
            bool: True, если Tesseract доступен
        """
        try:
            # Проверка версии Tesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            print(f"Ошибка при проверке Tesseract OCR: {e}")
            return False
    
    def preprocess_image(self, image_path):
        """
        Предварительная обработка изображения для улучшения OCR
        
        Args:
            image_path: путь к исходному изображению
        
        Returns:
            PIL.Image: обработанное изображение
        """
        try:
            # Открытие изображения
            image = Image.open(image_path)
            
            # Базовое улучшение четкости
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Увеличение резкости
            image = image.filter(ImageFilter.SHARPEN)
            
            return image
        except Exception as e:
            print(f"Ошибка при обработке изображения: {e}")
            return None
    
    def recognize_text(self, image_path, language="en"):
        """
        Распознавание текста из изображения
        
        Args:
            image_path: путь к изображению
            language: язык распознаваемого текста (en, ru, ja)
        
        Returns:
            str: распознанный текст
        """
        if not self.is_tesseract_available:
            return "Ошибка: Tesseract OCR не доступен. Проверьте, установлен ли Tesseract и указан ли корректный путь."
        
        try:
            # Предварительная обработка изображения
            image = self.preprocess_image(image_path)
            if image is None:
                return "Ошибка: не удалось обработать изображение."
            
            # Получение кода языка для Tesseract
            tesseract_lang = self.supported_languages.get(language, "eng")
            
            # Распознавание текста с использованием Tesseract
            text = pytesseract.image_to_string(image, lang=tesseract_lang)
            
            # Очистка текста от лишних символов
            text = text.strip()
            
            return text if text else "Текст не обнаружен"
        except Exception as e:
            return f"Ошибка OCR: {str(e)}"
    
    def recognize_text_from_area(self, image_path, x1, y1, x2, y2, language="en"):
        """
        Распознавание текста из определенной области изображения
        
        Args:
            image_path: путь к изображению
            x1, y1: координаты верхнего левого угла
            x2, y2: координаты правого нижнего угла
            language: язык распознаваемого текста
        
        Returns:
            str: распознанный текст
        """
        if not self.is_tesseract_available:
            return "Ошибка: Tesseract OCR не доступен. Проверьте, установлен ли Tesseract и указан ли корректный путь."
        
        try:
            # Открытие изображения
            image = Image.open(image_path)
            
            # Вырезание указанной области
            area = image.crop((x1, y1, x2, y2))
            
            # Увеличение контрастности области
            enhancer = ImageEnhance.Contrast(area)
            area = enhancer.enhance(1.5)
            
            # Увеличение резкости
            area = area.filter(ImageFilter.SHARPEN)
            
            # Получение кода языка для Tesseract
            tesseract_lang = self.supported_languages.get(language, "eng")
            
            # Распознавание текста
            text = pytesseract.image_to_string(area, lang=tesseract_lang)
            
            # Очистка текста
            text = text.strip()
            
            return text if text else "Текст не обнаружен"
        except Exception as e:
            return f"Ошибка OCR при анализе области: {str(e)}"
    
    def detect_language(self, image_path):
        """
        Определение языка текста на изображении
        
        Args:
            image_path: путь к изображению
        
        Returns:
            str: код языка (en, ru, ja или none, если не удалось определить)
        """
        if not self.is_tesseract_available:
            print("Ошибка: Tesseract OCR не доступен")
            return "none"
        
        try:
            # Предварительная обработка изображения
            image = self.preprocess_image(image_path)
            if image is None:
                return "none"
            
            # Пробуем распознать текст на разных языках и оцениваем результаты
            results = {}
            for lang_code, tesseract_code in self.supported_languages.items():
                try:
                    # Распознавание с указанием языка
                    text = pytesseract.image_to_string(image, lang=tesseract_code)
                    
                    # Подсчет количества символов
                    text_len = len(text.strip())
                    
                    # Сохранение результата
                    results[lang_code] = text_len
                except:
                    results[lang_code] = 0
            
            # Определение языка с наибольшим количеством символов
            if not results:
                return "none"
            
            max_lang = max(results, key=results.get)
            return max_lang if results[max_lang] > 0 else "none"
        except Exception as e:
            print(f"Ошибка при определении языка: {e}")
            return "none" 