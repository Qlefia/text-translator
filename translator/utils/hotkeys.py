"""
Модуль для работы с глобальными горячими клавишами
"""

import os
import sys
import platform
import threading

# Обнаружение операционной системы
OS_TYPE = platform.system()

if OS_TYPE == 'Windows':
    try:
        import keyboard
    except ImportError:
        print("Для работы с горячими клавишами на Windows необходимо установить библиотеку keyboard.")
        print("Выполните команду: pip install keyboard")
elif OS_TYPE == 'Linux':
    try:
        import keyboard
    except ImportError:
        print("Для работы с горячими клавишами на Linux необходимо установить библиотеку keyboard.")
        print("Выполните команду: pip install keyboard")
elif OS_TYPE == 'Darwin':  # MacOS
    try:
        import keyboard
    except ImportError:
        print("Для работы с горячими клавишами на MacOS необходимо установить библиотеку keyboard.")
        print("Выполните команду: pip install keyboard")

class HotkeyManager:
    """Класс для работы с глобальными горячими клавишами"""
    
    def __init__(self):
        """Инициализация менеджера горячих клавиш"""
        self.registered_hotkeys = {}
        self.running = True
        self.is_initialized = False
        
        # Проверка наличия необходимых библиотек
        try:
            import keyboard
            self.is_initialized = True
        except ImportError:
            self.is_initialized = False
            print("Ошибка инициализации менеджера горячих клавиш. Библиотека keyboard не установлена.")
    
    def register_hotkey(self, hotkey, callback):
        """
        Регистрация горячей клавиши
        
        Args:
            hotkey: строка с комбинацией клавиш (например, 'alt+shift+c')
            callback: функция, которая будет вызвана при нажатии комбинации
            
        Returns:
            bool: True в случае успеха, False в случае ошибки
        """
        if not self.is_initialized:
            print("Менеджер горячих клавиш не инициализирован.")
            return False
        
        try:
            # Проверка, не зарегистрирована ли уже такая комбинация
            if hotkey in self.registered_hotkeys:
                print(f"Горячая клавиша {hotkey} уже зарегистрирована.")
                return False
            
            # Регистрация горячей клавиши
            keyboard.add_hotkey(hotkey.lower(), callback)
            self.registered_hotkeys[hotkey] = callback
            print(f"Зарегистрирована горячая клавиша: {hotkey}")
            return True
        except Exception as e:
            print(f"Ошибка при регистрации горячей клавиши {hotkey}: {e}")
            return False
    
    def unregister_hotkey(self, hotkey):
        """
        Отмена регистрации горячей клавиши
        
        Args:
            hotkey: строка с комбинацией клавиш
            
        Returns:
            bool: True в случае успеха, False в случае ошибки
        """
        if not self.is_initialized:
            print("Менеджер горячих клавиш не инициализирован.")
            return False
        
        try:
            if hotkey in self.registered_hotkeys:
                keyboard.remove_hotkey(hotkey.lower())
                del self.registered_hotkeys[hotkey]
                print(f"Отменена регистрация горячей клавиши: {hotkey}")
                return True
            else:
                print(f"Горячая клавиша {hotkey} не зарегистрирована.")
                return False
        except Exception as e:
            print(f"Ошибка при отмене регистрации горячей клавиши {hotkey}: {e}")
            return False
    
    def unregister_all_hotkeys(self):
        """
        Отмена регистрации всех горячих клавиш
        
        Returns:
            bool: True в случае успеха, False в случае ошибки
        """
        if not self.is_initialized:
            print("Менеджер горячих клавиш не инициализирован.")
            return False
        
        try:
            # Отмена регистрации всех горячих клавиш
            for hotkey in list(self.registered_hotkeys.keys()):
                keyboard.remove_hotkey(hotkey.lower())
                del self.registered_hotkeys[hotkey]
            
            return True
        except Exception as e:
            print(f"Ошибка при отмене регистрации всех горячих клавиш: {e}")
            return False
    
    def start_listening(self):
        """
        Запуск прослушивания горячих клавиш
        
        Returns:
            bool: True в случае успеха, False в случае ошибки
        """
        if not self.is_initialized:
            print("Менеджер горячих клавиш не инициализирован.")
            return False
        
        try:
            # Запуск прослушивания в отдельном потоке
            self.running = True
            
            # Создание и запуск потока для прослушивания
            listener_thread = threading.Thread(target=self._listener_thread)
            listener_thread.daemon = True
            listener_thread.start()
            
            return True
        except Exception as e:
            print(f"Ошибка при запуске прослушивания горячих клавиш: {e}")
            return False
    
    def stop_listening(self):
        """
        Остановка прослушивания горячих клавиш
        
        Returns:
            bool: True в случае успеха, False в случае ошибки
        """
        if not self.is_initialized:
            print("Менеджер горячих клавиш не инициализирован.")
            return False
        
        try:
            self.running = False
            return True
        except Exception as e:
            print(f"Ошибка при остановке прослушивания горячих клавиш: {e}")
            return False
    
    def _listener_thread(self):
        """Поток для прослушивания горячих клавиш"""
        try:
            # Запуск прослушивания
            keyboard.wait()
        except Exception as e:
            print(f"Ошибка в потоке прослушивания горячих клавиш: {e}") 