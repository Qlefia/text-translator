"""
Модуль для захвата экрана или окна
"""

import os
import tempfile
from datetime import datetime
import cv2
import numpy as np
from PIL import ImageGrab, Image
import mss
import mss.tools

class ScreenCapture:
    """Класс для захвата области экрана или окна"""
    
    def __init__(self):
        """Инициализация захвата экрана"""
        self.temp_dir = tempfile.gettempdir()
        
    def capture_area(self, x1, y1, x2, y2):
        """
        Захват выбранной области экрана
        
        Args:
            x1, y1: координаты верхнего левого угла
            x2, y2: координаты правого нижнего угла
            
        Returns:
            str: путь к файлу скриншота
        """
        # Убедимся, что x1 < x2 и y1 < y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
            
        with mss.mss() as sct:
            # Определение региона для захвата
            region = {
                'left': x1,
                'top': y1,
                'width': x2 - x1,
                'height': y2 - y1
            }
            
            # Захват экрана
            screenshot = sct.grab(region)
            
            # Сохранение во временный файл
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_path = os.path.join(self.temp_dir, f"screenshot_{timestamp}.png")
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=file_path)
            
            return file_path
    
    def capture_fullscreen(self):
        """
        Захват всего экрана
        
        Returns:
            str: путь к файлу скриншота
        """
        with mss.mss() as sct:
            # Захват экрана
            screenshot = sct.grab(sct.monitors[0])
            
            # Сохранение во временный файл
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_path = os.path.join(self.temp_dir, f"screenshot_{timestamp}.png")
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=file_path)
            
            return file_path
    
    def capture_window(self, window_handle):
        """
        Захват определенного окна
        
        Args:
            window_handle: хэндл окна для захвата
            
        Returns:
            str: путь к файлу скриншота
        """
        # Эта функция будет зависеть от платформы
        # Для Windows потребуется использовать win32gui
        # Для Linux и MacOS - другие библиотеки
        
        # Пока реализуем просто с помощью захвата всего экрана
        # В реальной реализации нужно будет доработать
        return self.capture_fullscreen()
    
    def process_image(self, image_path):
        """
        Обработка изображения для улучшения OCR
        
        Args:
            image_path: путь к файлу изображения
            
        Returns:
            str: путь к обработанному изображению
        """
        # Загрузка изображения
        img = cv2.imread(image_path)
        
        # Преобразование в оттенки серого
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Применение фильтра для повышения резкости
        sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpen = cv2.filter2D(gray, -1, sharpen_kernel)
        
        # Бинаризация (адаптивная пороговая обработка)
        thresh = cv2.adaptiveThreshold(
            sharpen, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Сохранение обработанного изображения
        processed_path = image_path.replace('.png', '_processed.png')
        cv2.imwrite(processed_path, thresh)
        
        return processed_path 