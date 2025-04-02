"""
Модуль для работы с окнами операционной системы
"""

import os
import sys
import platform

# Обнаружение операционной системы
OS_TYPE = platform.system()

if OS_TYPE == 'Windows':
    try:
        import win32gui
        import win32process
        import win32con
        import ctypes
        import psutil
    except ImportError:
        print("Для работы с окнами на Windows необходимо установить библиотеки pywin32 и psutil.")
        print("Выполните команду: pip install pywin32 psutil")
elif OS_TYPE == 'Linux':
    try:
        import Xlib
        import Xlib.display
    except ImportError:
        print("Для работы с окнами на Linux необходимо установить библиотеку python-xlib.")
        print("Выполните команду: pip install python-xlib")
elif OS_TYPE == 'Darwin':  # MacOS
    try:
        import AppKit
    except ImportError:
        print("Для работы с окнами на MacOS необходимо установить библиотеку pyobjc.")
        print("Выполните команду: pip install pyobjc")

class WindowManager:
    """Класс для работы с окнами операционной системы"""
    
    def __init__(self):
        """Инициализация менеджера окон"""
        self.windows = []
        self.window_handles = {}
    
    def get_window_list(self):
        """
        Получение списка всех окон в системе
        
        Returns:
            list: список кортежей (имя_окна, хендл_окна)
        """
        self.windows = []
        self.window_handles = {}
        
        if OS_TYPE == 'Windows':
            # На Windows используем win32gui для получения всех окон
            def enum_windows_callback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    # Фильтрация служебных и пустых окон
                    if window_text and len(window_text) > 1 and window_text != "Program Manager" and window_text != "Рабочий стол":
                        # Добавляем окно в список
                        self.windows.append(window_text)
                        self.window_handles[window_text] = hwnd
                return True
            
            # Перечисление всех окон
            win32gui.EnumWindows(enum_windows_callback, [])
            
        elif OS_TYPE == 'Linux':
            # На Linux используем Xlib для получения окон
            try:
                display = Xlib.display.Display()
                root = display.screen().root
                
                window_ids = root.get_full_property(
                    display.intern_atom('_NET_CLIENT_LIST'),
                    Xlib.X.AnyPropertyType
                ).value
                
                for window_id in window_ids:
                    window = display.create_resource_object('window', window_id)
                    name = window.get_wm_name()
                    if name:
                        self.windows.append(name)
                        self.window_handles[name] = window_id
            except Exception as e:
                print(f"Ошибка при получении списка окон в Linux: {e}")
                
        elif OS_TYPE == 'Darwin':  # MacOS
            # На MacOS используем AppKit
            try:
                app = AppKit.NSWorkspace.sharedWorkspace()
                running_apps = app.runningApplications()
                for app in running_apps:
                    app_name = app.localizedName()
                    if app_name:
                        self.windows.append(app_name)
                        self.window_handles[app_name] = app
            except Exception as e:
                print(f"Ошибка при получении списка окон в MacOS: {e}")
        
        return self.windows
    
    def capture_window(self, window_name):
        """
        Захват указанного окна
        
        Args:
            window_name: имя окна для захвата
        
        Returns:
            tuple: (x, y, width, height) координаты и размеры окна или None в случае ошибки
        """
        if window_name not in self.window_handles:
            return None
        
        if OS_TYPE == 'Windows':
            hwnd = self.window_handles[window_name]
            try:
                # Получение размеров и позиции окна
                rect = win32gui.GetWindowRect(hwnd)
                x, y, right, bottom = rect
                return (x, y, right - x, bottom - y)
            except Exception as e:
                print(f"Ошибка при получении размеров окна: {e}")
                return None
                
        elif OS_TYPE == 'Linux':
            window_id = self.window_handles[window_name]
            try:
                display = Xlib.display.Display()
                window = display.create_resource_object('window', window_id)
                geometry = window.get_geometry()
                x, y = geometry.x, geometry.y
                width, height = geometry.width, geometry.height
                return (x, y, width, height)
            except Exception as e:
                print(f"Ошибка при получении размеров окна: {e}")
                return None
                
        elif OS_TYPE == 'Darwin':  # MacOS
            # На MacOS получение размеров окна может быть сложнее
            # и требовать дополнительных библиотек
            print("Захват окна на MacOS пока не реализован")
            return None
        
        return None
    
    def bring_window_to_front(self, window_name):
        """
        Вывод окна на передний план
        
        Args:
            window_name: имя окна
            
        Returns:
            bool: True в случае успеха, False в случае ошибки
        """
        if window_name not in self.window_handles:
            return False
        
        if OS_TYPE == 'Windows':
            hwnd = self.window_handles[window_name]
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                return True
            except Exception as e:
                print(f"Ошибка при выводе окна на передний план: {e}")
                return False
                
        elif OS_TYPE == 'Linux':
            # На Linux это может потребовать дополнительных библиотек
            # и зависит от оконного менеджера
            print("Вывод окна на передний план на Linux пока не реализован")
            return False
            
        elif OS_TYPE == 'Darwin':  # MacOS
            app = self.window_handles[window_name]
            try:
                app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
                return True
            except Exception as e:
                print(f"Ошибка при выводе окна на передний план: {e}")
                return False
        
        return False 