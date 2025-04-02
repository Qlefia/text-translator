"""
Модуль для оптического распознавания текста (OCR)
с использованием Tesseract OCR
"""

import os
import pytesseract
import cv2
import numpy as np
from PIL import Image
import platform

class OCREngine:
    """Класс для работы с OCR"""
    
    def __init__(self, tesseract_path=None):
        """
        Инициализация OCR движка
        
        Args:
            tesseract_path: путь к исполняемому файлу Tesseract (для Windows)
        """
        # Определение пути к Tesseract для разных ОС
        if platform.system() == 'Windows':
            # Типичный путь для Windows
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            else:
                # Путь по умолчанию
                default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                if os.path.exists(default_path):
                    pytesseract.pytesseract.tesseract_cmd = default_path
                else:
                    print("Предупреждение: Tesseract не найден по пути по умолчанию.")
                    print("Установите Tesseract или укажите путь вручную.")
    
    def recognize_text(self, image_path, lang='eng+jpn+rus'):
        """
        Распознавание текста из изображения
        
        Args:
            image_path: путь к файлу изображения
            lang: языки для распознавания (eng, jpn, rus)
            
        Returns:
            str: распознанный текст
        """
        try:
            # Загрузка изображения
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Не удалось загрузить изображение: {image_path}")
                
            # Преобразование в оттенки серого
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Применение различных методов улучшения изображения
            # Убираем шум
            denoise = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Адаптивная бинаризация для лучшего распознавания текста
            binary = cv2.adaptiveThreshold(
                denoise, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2)
            
            # Распознавание с помощью Tesseract
            text = pytesseract.image_to_string(binary, lang=lang)
            
            return text.strip()
        except Exception as e:
            print(f"Ошибка при распознавании текста: {e}")
            return ""
    
    def recognize_text_from_pil(self, pil_image, lang='eng+jpn+rus'):
        """
        Распознавание текста из объекта PIL.Image
        
        Args:
            pil_image: объект PIL.Image
            lang: языки для распознавания
            
        Returns:
            str: распознанный текст
        """
        try:
            # Преобразование в numpy array и затем в grayscale
            img = np.array(pil_image)
            if len(img.shape) == 3:  # если цветное изображение
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            else:
                gray = img
                
            # Применение улучшений
            denoise = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            binary = cv2.adaptiveThreshold(
                denoise, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2)
            
            # Распознавание
            text = pytesseract.image_to_string(binary, lang=lang)
            
            return text.strip()
        except Exception as e:
            print(f"Ошибка при распознавании текста: {e}")
            return ""
    
    def detect_language(self, image_path):
        """
        Определение языка текста на изображении
        
        Args:
            image_path: путь к файлу изображения
            
        Returns:
            str: код языка (eng, jpn, rus)
        """
        try:
            # Загрузка изображения
            img = cv2.imread(image_path)
            
            # Преобразование в оттенки серого
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Получение данных об языке
            lang_data = pytesseract.image_to_osd(gray)
            
            # Анализ данных
            if 'Script: Japanese' in lang_data:
                return 'jpn'
            elif 'Script: Latin' in lang_data:
                return 'eng'
            elif 'Script: Cyrillic' in lang_data:
                return 'rus'
            else:
                return 'eng'  # по умолчанию
        except Exception as e:
            print(f"Ошибка при определении языка: {e}")
            return 'eng'  # по умолчанию 