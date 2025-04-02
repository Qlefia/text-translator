"""
Модуль для создания скриншотов
"""

import os
import sys
import time
import tempfile
import platform
from PIL import Image, ImageGrab

class ScreenCapture:
    """Класс для создания скриншотов"""
    
    def __init__(self):
        """Инициализация захватчика экрана"""
        # Создание временной директории для скриншотов
        self.temp_dir = tempfile.mkdtemp(prefix="translator_")
        self.screenshot_count = 0
        
        # Определение операционной системы
        self.os_type = platform.system()
        
        # Проверка и импорт дополнительных библиотек в зависимости от ОС
        if self.os_type == 'Windows':
            try:
                import win32gui
                import win32con
                import win32ui
                import win32api
                self.windows_modules_available = True
            except ImportError:
                self.windows_modules_available = False
                print("Для оптимального захвата окон на Windows установите библиотеку pywin32")
                print("pip install pywin32")
    
    def capture_fullscreen(self):
        """
        Создание скриншота всего экрана
        
        Returns:
            str: путь к файлу скриншота
        """
        # Генерация пути для сохранения скриншота
        self.screenshot_count += 1
        screenshot_path = os.path.join(
            self.temp_dir, 
            f"fullscreen_{int(time.time())}_{self.screenshot_count}.png"
        )
        
        # Захват экрана с помощью PIL
        try:
            screenshot = ImageGrab.grab()
            screenshot.save(screenshot_path)
            return screenshot_path
        except Exception as e:
            print(f"Ошибка при захвате экрана: {e}")
            # Возвращаем пустой путь в случае ошибки
            return ""
    
    def capture_area(self, x1, y1, x2, y2):
        """
        Создание скриншота указанной области экрана
        
        Args:
            x1: координата X левого верхнего угла
            y1: координата Y левого верхнего угла
            x2: координата X правого нижнего угла
            y2: координата Y правого нижнего угла
        
        Returns:
            str: путь к файлу скриншота
        """
        # Генерация пути для сохранения скриншота
        self.screenshot_count += 1
        screenshot_path = os.path.join(
            self.temp_dir, 
            f"area_{int(time.time())}_{self.screenshot_count}.png"
        )
        
        # Расчет размеров области
        width = x2 - x1
        height = y2 - y1
        
        # Проверка корректности параметров
        if width <= 0 or height <= 0:
            print("Некорректные размеры области для захвата")
            return ""
        
        # Захват указанной области экрана
        try:
            # Полный скриншот экрана
            full_screenshot = ImageGrab.grab()
            
            # Вырезание нужной области
            area_screenshot = full_screenshot.crop((x1, y1, x2, y2))
            area_screenshot.save(screenshot_path)
            
            return screenshot_path
        except Exception as e:
            print(f"Ошибка при захвате области экрана: {e}")
            return ""
    
    def capture_window(self, hwnd=None):
        """
        Создание скриншота указанного окна (только для Windows)
        
        Args:
            hwnd: хендл окна для захвата
        
        Returns:
            str: путь к файлу скриншота
        """
        # Проверка ОС и наличия необходимых модулей
        if self.os_type != 'Windows' or not self.windows_modules_available:
            print("Захват окна доступен только на Windows с установленным pywin32")
            return self.capture_fullscreen()
        
        # Генерация пути для сохранения скриншота
        self.screenshot_count += 1
        screenshot_path = os.path.join(
            self.temp_dir, 
            f"window_{int(time.time())}_{self.screenshot_count}.png"
        )
        
        try:
            import win32gui
            import win32con
            import win32ui
            import win32api
            
            # Если хендл не указан, используем окно на переднем плане
            if hwnd is None:
                hwnd = win32gui.GetForegroundWindow()
            
            # Получение размеров окна
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # Создание контекста устройства
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            # Создание битмапа
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)
            
            # Копирование изображения окна
            result = save_dc.BitBlt(
                (0, 0), (width, height), 
                mfc_dc, (0, 0), 
                win32con.SRCCOPY
            )
            
            # Конвертация в формат PIL
            bmpinfo = save_bitmap.GetInfo()
            bmpstr = save_bitmap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # Сохранение изображения
            img.save(screenshot_path)
            
            # Освобождение ресурсов
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            win32gui.DeleteObject(save_bitmap.GetHandle())
            
            return screenshot_path
        except Exception as e:
            print(f"Ошибка при захвате окна: {e}")
            # В случае ошибки пробуем захватить весь экран
            return self.capture_fullscreen()
    
    def cleanup(self):
        """Очистка временных файлов"""
        try:
            # Удаление всех файлов во временной директории
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            # Удаление временной директории
            os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"Ошибка при очистке временных файлов: {e}") 