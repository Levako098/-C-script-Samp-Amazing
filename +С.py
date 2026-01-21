import keyboard
import time
from pynput.mouse import Button, Controller
import ctypes
import sys
import tkinter as tk
from screeninfo import get_monitors

mouse = Controller()

KEYBINDS = {
    "activate": "insert",
    "toggle": "alt",
    "forward": "w",
    "crouch": "c",
    "exit": "delete",
    "aim_toggle": "home"
}

DELAYS = {
    "right_click_hold": 0.1,
    "left_click_delay": 0.02,
    "left_click_hold": 0.05,
    "crouch_delay": 0.02,
    "sequence_delay": 0.08,
}

active = False
running = True
debounce_time = 0.3
last_activation = 0
aim_dot_visible = False
aim_dot_last_toggle = 0
aim_dot_window = None

def create_aim_dot():
    global aim_dot_window
    
    try:
        for monitor in get_monitors():
            screen_width = monitor.width
            screen_height = monitor.height
            break
    except:
        screen_width = 1920
        screen_height = 1080
    
    center_x = screen_width // 2
    center_y = screen_height // 2
    
    aim_dot_window = tk.Tk()
    aim_dot_window.overrideredirect(True)
    aim_dot_window.attributes('-topmost', True)
    aim_dot_window.attributes('-transparentcolor', 'black')
    aim_dot_window.configure(bg='black')
    
    size = 20
    pos_x = center_x - (size // 2)
    pos_y = center_y - (size // 2)
    
    aim_dot_window.geometry(f"{size}x{size}+{pos_x}+{pos_y}")
    
    canvas = tk.Canvas(aim_dot_window, width=size, height=size, bg='black', highlightthickness=0)
    canvas.pack()
    
    canvas.create_oval(5, 5, 15, 15, fill='red', outline='red', width=2)
    
    aim_dot_window.withdraw()
    return aim_dot_window

def toggle_aim_dot():
    global aim_dot_visible, aim_dot_window
    
    if aim_dot_window is None:
        aim_dot_window = create_aim_dot()
    
    if aim_dot_visible:
        aim_dot_window.withdraw()
        aim_dot_visible = False
        print("Aim dot hidden")
    else:
        aim_dot_window.deiconify()
        aim_dot_visible = True
        print("Aim dot shown")

def press_key_safely(key, duration=0.01):
    try:
        keyboard.press(key)
        time.sleep(duration)
        keyboard.release(key)
    except:
        keyboard.release(key)

def perform_shot():
    try:
        mouse.press(Button.right)
        keyboard.press(KEYBINDS["forward"])
        time.sleep(DELAYS["right_click_hold"])
        
        time.sleep(DELAYS["left_click_delay"])
        mouse.press(Button.left)
        time.sleep(DELAYS["left_click_hold"])
        mouse.release(Button.left)
        
        mouse.release(Button.right)
        keyboard.release(KEYBINDS["forward"])
        
        time.sleep(DELAYS["crouch_delay"])
        press_key_safely(KEYBINDS["crouch"], 0.02)
        
        time.sleep(DELAYS["sequence_delay"])
        return True
    except:
        release_all()
        return False

def release_all():
    try:
        mouse.release(Button.left)
        mouse.release(Button.right)
        keyboard.release(KEYBINDS["forward"])
        keyboard.release(KEYBINDS["crouch"])
    except:
        pass

def main():
    global active, running, last_activation, aim_dot_last_toggle
    print("Insert - on/off")
    print("Alt - shoot (hold)")
    print("Home - show/hide aim dot")
    try:
        while running:
            current_time = time.time()
            
            if keyboard.is_pressed(KEYBINDS["exit"]):
                print("Exiting...")
                running = False
                break
            
            if keyboard.is_pressed(KEYBINDS["activate"]):
                if current_time - last_activation > debounce_time:
                    active = not active
                    status = "ACTIVE" if active else "INACTIVE"
                    print(f"Script {status}")
                    last_activation = current_time
                    time.sleep(0.2)
            
            if keyboard.is_pressed(KEYBINDS["aim_toggle"]):
                if current_time - aim_dot_last_toggle > debounce_time:
                    toggle_aim_dot()
                    aim_dot_last_toggle = current_time
                    time.sleep(0.2)
            
            if active and keyboard.is_pressed(KEYBINDS["toggle"]):
                perform_shot()
                time.sleep(0.001)
            else:
                time.sleep(0.01)
            
            if aim_dot_window:
                aim_dot_window.update()
                
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        release_all()
        if aim_dot_window:
            aim_dot_window.destroy()
        print("Exit.")

if __name__ == "__main__":
    try:
        import screeninfo
    except ImportError:
        print("Installing screeninfo library...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "screeninfo"])
        import screeninfo
    
    main()