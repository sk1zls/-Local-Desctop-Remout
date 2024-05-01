import os
import socket
import threading
import subprocess
from flask import Flask, render_template, request
import pyautogui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog
from PyQt5.uic import loadUi
from PyQt5 import QtGui
import win32api
import win32con
import time
app = Flask(__name__)

# Flask routes
@app.route('/')
def index():
    return render_template('web.html')

@app.route('/send_keys', methods=['POST'])
def send_keys():
    data = request.get_json()
    keys = data.get('keys')

    if keys in ['Key1', 'Key2', 'Key3', 'Key4', 'Key5', 'Key6', 'Key7', 'Key8', 'Key9']:
        pyautogui.press(keys.lower())
        return 'Keys sent successfully'

    return 'Invalid keys'

@app.route('/command/<command>')
def handle_command(command):
    if command in ['play', 'pause', 'next', 'prev', 'volup', 'voldown'] or command.startswith('custom'):
        process_command(command)
        return 'Command received and processed', 200
    elif command.startswith('Key'):
        key_number = command[3:]
        return handle_key_press(key_number)
    else:
        return 'Unknown command', 400

@app.route('/key/<key>', methods=['POST'])
def handle_key_press(key):
    try:
        key_number = int(key[3:])  # Extract the key number from the key (e.g., 'Key1' -> '1')
        
        if key_number in range(1, 10):
            key_sequence = read_key_sequence_from_file(key_number)
            if key_sequence:
                trigger_key_press(key_sequence)
                return f'Key press sent for {key}', 200
            else:
                return f'Key sequence for {key} not found', 404
        else:
            return 'Invalid key number. Key number should be between 1 and 9.', 400
    except ValueError:
        return 'Invalid key number. Key number should be an integer.', 400

def get_virtual_key_code(key):
    return win32api.MapVirtualKey(key, 0)

def get_special_key_virtual_code(key):
    special_keys = {
        'LSHIFT': 0xA0,
        'RSHIFT': 0xA1,
        'LCTRL': 0xA2,
        'RCTRL': 0xA3,
        'LALT': 0xA4,
        'RALT': 0xA5,
        'BACKSLASH': 0xDC,
        'SPACE': 0x20,
        # Add more special keys as needed
    }
    return special_keys.get(key, 0)



# Flask server setup and run
def run_flask():
    ip = socket.gethostbyname(socket.gethostname())
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host=ip, port=port)

# Read key sequence from file
def read_key_sequence_from_file(key_number):
    # Read the key sequence for the specified key number from the file
    file_path = "C:/Web/Key/combo.txt"
    key_sequence = ''

    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(': ')
                if len(parts) == 2 and parts[0] == f'key{key_number}':
                    key_sequence = parts[1].strip()  # Убедитесь, что удалили лишние пробелы в последовательности
                    break
    except FileNotFoundError:
        print(f"File {file_path} not found.")

    return key_sequence

def trigger_key_press(key_sequence):
    special_keys = {
    'CTRL': win32con.VK_CONTROL,
    'SHIFT': win32con.VK_SHIFT,
    'ALT': win32con.VK_MENU,
    'SPACE': win32con.VK_SPACE,
    'BACKSLASH': ord('\\'),
    'CLOSE_BRACKET': ord(']'),
    'A': ord('A'), 'B': ord('B'), 'C': ord('C'), 'D': ord('D'), 'E': ord('E'),
    'F': ord('F'), 'G': ord('G'), 'H': ord('H'), 'I': ord('I'), 'J': ord('J'),
    'K': ord('K'), 'L': ord('L'), 'M': ord('M'), 'N': ord('N'), 'O': ord('O'),
    'P': ord('P'), 'Q': ord('Q'), 'R': ord('R'), 'S': ord('S'), 'T': ord('T'),
    'U': ord('U'), 'V': ord('V'), 'W': ord('W'), 'X': ord('X'), 'Y': ord('Y'),
    'Z': ord('Z'),
    'Й': 0xA2, 'Ц': 0xA3, 'У': 0xA4, 'К': 0xA5, 'Е': 0xB3, 'Н': 0xA6,
    'Г': 0xA7, 'Ш': 0xA8, 'Щ': 0xA9, 'З': 0xAA, 'Х': 0xAB, 'Ъ': 0xAC,
    'Ф': 0xAD, 'Ы': 0xAE, 'В': 0xAF, 'А': 0xB0, 'П': 0xB1, 'Р': 0xB2,
    'О': 0xB4, 'Л': 0xB5, 'Д': 0xB6, 'Ж': 0xB7, 'Э': 0xB8, 'Я': 0xB9,
    'Ч': 0xBA, 'С': 0xBB, 'М': 0xBC, 'И': 0xBD, 'Т': 0xBE, 'Ь': 0xBF,
    'Б': 0xC0, 'Ю': 0xC1
}
    keys = key_sequence.split('+')
    
    for key in keys:
        if key.upper() in special_keys:
            win32api.keybd_event(special_keys[key.upper()], 0, 0, 0)
        else:
            # Press the regular key
            win32api.keybd_event(get_virtual_key_code(ord(key)), 0, 0, 0)
    
    time.sleep(0.1)  # Adding a short delay between key presses
    
    for key in keys:
        if key.upper() in special_keys:
            win32api.keybd_event(special_keys[key.upper()], 0, win32con.KEYEVENTF_KEYUP, 0)
        else:
            # Release the regular key
            win32api.keybd_event(get_virtual_key_code(ord(key)), 0, win32con.KEYEVENTF_KEYUP, 0)
    
    return

# Class for main application window
class MyMainWindow(QMainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        loadUi('C:/Web/ui.ui', self)
        self.setWindowTitle('My Application')

        # Connect buttons to functions
        for i in range(1, 10):
            push_button_name = f"pushButton_{i}"
            line_edit_name = f"lineEdit_{i}"
            push_button = getattr(self, push_button_name)
            line_edit = getattr(self, line_edit_name)
            
            push_button.clicked.connect(lambda _, le=line_edit: self.open_file_dialog(le))

        self.Save_changes.clicked.connect(self.on_save_clicked)
        self.Save_changes.clicked.connect(self.save_key_combinations)
        self.load_saved_data()
        self.load_key_combinations()
        self.on_save_clicked()
        self.Ip_text.setReadOnly(True)
        self.Port_text.setReadOnly(True)
        self.Web_text.setReadOnly(True)
        
        ip = socket.gethostbyname(socket.gethostname())
        self.Ip_text.setText(ip)
        
        port = int(os.getenv('FLASK_PORT', 5000))
        self.Port_text.setText(str(port))
        
        url = f"http://{ip}:{port}"
        self.Web_text.setText(url)

    # Save custom values to file
    def on_save_clicked(self):
        save_path = "C:/Web/Key/Key.txt"
        with open(save_path, 'w') as file:
            for i in range(1, 10):
                line_edit_name = f"lineEdit_{i}"
                line_edit = getattr(self, line_edit_name)
                file.write(f"custom{i}: {line_edit.text()}\n")
        print("Data saved successfully.")
        
        self.load_saved_data()  # Reload data after saving

    def load_saved_data(self):
        save_path = "C:/Web/Key/Key.txt"
        if os.path.exists(save_path):
            with open(save_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    parts = line.strip().split(": ")
                    if len(parts) == 2:
                        custom_number, custom_value = parts
                        line_edit_name = f"lineEdit_{custom_number.strip('custom')}"
                        if hasattr(self, line_edit_name):
                            line_edit = getattr(self, line_edit_name)
                            line_edit.setText(custom_value.strip())
                    else:
                        print(f"Ignoring line: {line} - Incorrect format")
            print("Data loaded successfully.")
        else:
            print(f"File {save_path} not found.")

    # Load key combinations from file
    def load_key_combinations(self):
        file_path = "C:/Web/Key/combo.txt"
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    parts = line.strip().split(': ')
                    if len(parts) == 2:
                        key_sequence_edit_name = f"keySequenceEdit_{i + 1}"
                        key_sequence_edit = getattr(self, key_sequence_edit_name)
                        key_sequence = parts[1]
                        key_sequence_edit.setKeySequence(QtGui.QKeySequence(key_sequence))
                    else:
                        print(f"Ignoring line: {line} - Incorrect format")
                print("Key combinations loaded successfully from combo.txt.")
        except FileNotFoundError:
            print("File combo.txt not found. No key combinations loaded.")

    # Save key combinations to file
    def save_key_combinations(self):
        save_path = "C:/Web/Key/combo.txt"
        with open(save_path, 'w') as file:
            for i in range(1, 10):
                key_sequence_edit_name = f"keySequenceEdit_{i}"
                key_sequence_edit = getattr(self, key_sequence_edit_name)
                file.write(f"key{i}: {key_sequence_edit.keySequence().toString()}\n")
        print("Key combinations saved successfully to combo.txt.")

    # Open file dialog for selecting files
    def open_file_dialog(self, line_edit):
        file_dialog = QFileDialog.getOpenFileName(self, 'Select File', '', 'All Files (*);;Python Files (*.py);;Text Files (*.txt)')
        file_path = file_dialog[0]
        if file_path:
            line_edit.setText(file_path)

# Class for editing key settings
class EditKey(QDialog):
    def __init__(self, key_name):
        super(EditKey, self).__init__()
        self.key_name = key_name
        loadUi('C:/Web/EditKey.ui', self)
        self.setWindowTitle(f'Edit Key {self.key_name}')

        self.Save_button.clicked.connect(self.accept)
        self.Clance_button.clicked.connect(self.reject)

# Process different commands
def process_command(command):
    if command == 'play':
        pyautogui.press('playpause')
    elif command == 'pause':
        pyautogui.press('playpause')
    elif command == 'next':
        pyautogui.press('nexttrack')
    elif command == 'prev':
        pyautogui.press('prevtrack')
    elif command == 'volup':
        pyautogui.press('volumeup')
    elif command == 'voldown':
        pyautogui.press('volumedown')
    elif command.startswith('custom'):
        try:
            custom_number = command.split('custom')[1].strip()  # Extract the custom number
            key = f'custom{custom_number}'
            program_path = read_custom_command_from_file(key)
            if program_path:
                subprocess.Popen(program_path, shell=True)
                print(f"Opening program: {program_path}")
            else:
                print(f"Program path for {key} not found in the file.")
        except Exception as e:
            print(f"Error opening program: {e}")
    elif command.startswith('Key'):
        key_number = command[3:]
        key_sequence = read_key_sequence_from_file(int(key_number))
        if key_sequence:
            trigger_key_press(key_sequence)
            print(f"Key {key_number} sequence triggered: {key_sequence}")
        else:
            print(f"Key sequence for Key {key_number} not found.")
    else:
        print("Unknown command")

# Read custom program path from file
def read_custom_command_from_file(key):
    file_path = "C:/Web/Key/Key.txt"

    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(": ")
                if len(parts) == 2:
                    if parts[0] == key:
                        return parts[1].strip()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    
    return None

if __name__ == '__main__':
    os.environ['FLASK_PORT'] = '5000'

    app_thread = threading.Thread(target=run_flask)
    app_thread.start()

    app = QApplication([])
    window = MyMainWindow()
    window.show()
    app.exec_()
    