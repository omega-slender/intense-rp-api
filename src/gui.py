import threading, webbrowser, api, re, os, sys
import utils.config_manager as config_manager
import customtkinter as ctk

root = None
version = 2.4

console_window = None
console_textbox = None
textbox = None

manager = None
icon_path = None

config = {
    "browser": "Chrome",
    "model": "DeepSeek",
    "show_ip": False,
    "show_console": False,
    "models": {
        "deepseek": {
            "email": "",
            "password": "",
            "auto_login": False,
            "text_file": False,
            "deepthink": False,
            "search": False
        }
    }
}

class ConsoleRedirector:
    def __init__(self, callback):
        self.callback = callback

    def write(self, text):
        if text:
            try:
                self.callback(text)
            except Exception:
                pass

    def flush(self):
        pass

def load_files():
    global icon_path, manager, config
    
    script_path = os.path.dirname(os.path.realpath(__file__))
    
    if os.path.isfile(script_path):
        icon_base = os.path.dirname(script_path)
        base_path = os.path.dirname(os.path.dirname(script_path))
    else:
        icon_base = script_path
        base_path = script_path

    possible_icon_path = os.path.join(icon_base, "icon.ico")
    icon_path = possible_icon_path if os.path.isfile(possible_icon_path) else None
    save_path = os.path.join(base_path, "save")

    manager = config_manager.EncryptedConfigManager(save_path)
    config = manager.load_config(config)
    
def create_console_window():
    global console_window, console_textbox
    console_window = ctk.CTkToplevel()
    console_window.title("Console")
    console_window.geometry("600x300")
    console_window.minsize(200, 200)
    console_window.withdraw()
    console_window.protocol("WM_DELETE_WINDOW", lambda: None)
    
    if icon_path:
        console_window.after(200, lambda: console_window.iconbitmap(icon_path))
    
    console_textbox = ctk.CTkTextbox(
        console_window,
        state="disabled",
        font=("Arial", 16),
        wrap="none",
        border_width=0,
        corner_radius=0,
        fg_color="black",
        text_color="white"
    )
    console_textbox.pack(expand=True, fill="both")

def toggle_console_window(show):
    try:
        global root, console_window        
        if not root or not console_window:
            return
        
        is_visible = console_window.winfo_viewable() == 1
        if show == is_visible:
            return
        
        if show:
            console_window.update_idletasks()
            console_window.deiconify()
            console_window.lift()
            console_window.attributes("-topmost", False)

            root.update_idletasks()
            x = root.winfo_x() + (root.winfo_width() // 2) - (600 // 2)
            y = root.winfo_y() + (root.winfo_height() // 2) - (300 // 2)
            console_window.geometry(f"600x300+{x}+{y}")
            print("Show console window.")
        else:
            console_window.withdraw()
            print("Hide console window.")
    except Exception as e:
        print(f"Error toggling console window: {e}")

def console_add(text):
    try:
        global console_textbox
        if not console_textbox:
            return
        
        console_textbox.configure(state="normal")
        console_textbox.insert("end", text)
        console_textbox.configure(state="disabled")
        console_textbox.see("end")
    except Exception:
        pass

def textbox_add(widget, text):
    try:
        if not widget:
            return
        
        print(text)
        pattern = r'\[color:(\w+)\]'
        parts = re.split(pattern, text)
        current_tag = "white"
        
        widget.configure(state="normal")
        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    widget.insert("end", part, current_tag)
            else:
                current_tag = part
        
        widget.insert("end", "\n")
        widget.configure(state="disabled")
        widget.see("end")
    except Exception as e:
        print(f"Error adding text to textbox: {e}")

def textbox_clear(widget):
    try:
        if not widget:
            return
        
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.configure(state="disabled")
    except Exception as e:
        print(f"Error clearing textbox: {e}")

def start_services():
    try:
        textbox_clear(textbox)
        textbox_add(textbox, "[color:green]Please wait...")
        
        api.assign_config(config)
        threading.Thread(target=api.run_services, daemon=True).start()
    except Exception as e:
        textbox_clear(textbox)
        textbox_add(textbox, "[color:red]Selenium failed to start.")
        print(f"Error starting services: {e}")

def open_config_window():
    try:
        config_window = ctk.CTkToplevel(root)
        config_window.title("Settings")
        config_window.transient(root)
        config_window.grab_set()
        config_window.focus_force()
        config_window.lift()

        if icon_path:
            config_window.after(200, lambda: config_window.iconbitmap(icon_path))

        root.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() // 2) - (400 // 2)
        y = root.winfo_y() + (root.winfo_height() // 2) - (470 // 2)
        config_window.geometry(f"400x470+{x}+{y}")
        config_window.minsize(400, 470)

        for i in range(12):
            config_window.grid_rowconfigure(i, weight=1)
        
        config_window.grid_columnconfigure(0, weight=1)
        config_window.grid_columnconfigure(1, weight=1)
        
        d_settings_label = ctk.CTkLabel(config_window, text="DeepSeek Settings", font=("Arial", 14, "bold"))
        d_settings_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        d_email_label = ctk.CTkLabel(config_window, text="Email:")
        d_email_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        d_email_entry = ctk.CTkEntry(config_window, width=250)
        d_email_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        d_email_entry.insert(0, config["models"]["deepseek"]["email"])

        d_pass_label = ctk.CTkLabel(config_window, text="Password:")
        d_pass_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        d_pass_frame = ctk.CTkFrame(config_window, fg_color="transparent")
        d_pass_frame.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        d_pass_frame.grid_columnconfigure(0, weight=1)

        d_pass_entry = ctk.CTkEntry(d_pass_frame, show="*")
        d_pass_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        d_pass_entry.insert(0, config["models"]["deepseek"]["password"])

        def toggle_password_visibility():
            if d_pass_entry.cget("show") == "*":
                d_pass_entry.configure(show="")
                d_toggle_button.configure(text="Hide")
            else:
                d_pass_entry.configure(show="*")
                d_toggle_button.configure(text="Show")

        d_toggle_button = ctk.CTkButton(d_pass_frame, text="Show", width=60, command=toggle_password_visibility)
        d_toggle_button.grid(row=0, column=1, sticky="e")

        d_auto_login_label = ctk.CTkLabel(config_window, text="Auto Login:")
        d_auto_login_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        d_auto_login_var = ctk.BooleanVar(value=config["models"]["deepseek"]["auto_login"])
        d_auto_login_switch = ctk.CTkSwitch(config_window, variable=d_auto_login_var, text="")
        d_auto_login_switch.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        d_text_file_label = ctk.CTkLabel(config_window, text="Text file:")
        d_text_file_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        d_text_file_var = ctk.BooleanVar(value=config["models"]["deepseek"]["text_file"])
        d_text_file_switch = ctk.CTkSwitch(config_window, variable=d_text_file_var, text="")
        d_text_file_switch.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        d_deepthink_label = ctk.CTkLabel(config_window, text="DeepThink:")
        d_deepthink_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        d_deepthink_var = ctk.BooleanVar(value=config["models"]["deepseek"]["deepthink"])
        d_deepthink_switch = ctk.CTkSwitch(config_window, variable=d_deepthink_var, text="")
        d_deepthink_switch.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        d_search_label = ctk.CTkLabel(config_window, text="Search:")
        d_search_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        d_search_var = ctk.BooleanVar(value=config["models"]["deepseek"]["search"])
        d_search_switch = ctk.CTkSwitch(config_window, variable=d_search_var, text="")
        d_search_switch.grid(row=6, column=1, padx=10, pady=5, sticky="w")

        advanced_label = ctk.CTkLabel(config_window, text="Advanced Settings", font=("Arial", 14, "bold"))
        advanced_label.grid(row=7, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        browser_label = ctk.CTkLabel(config_window, text="Browser:")
        browser_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
        browser_options = ["Chrome", "Firefox", "Edge", "Safari"]
        browser_var = ctk.StringVar(value=config["browser"])
        browser_menu = ctk.CTkOptionMenu(config_window, variable=browser_var, values=browser_options)
        browser_menu.grid(row=8, column=1, padx=10, pady=5, sticky="ew")

        show_ip_label = ctk.CTkLabel(config_window, text="Show IP:")
        show_ip_label.grid(row=9, column=0, padx=10, pady=5, sticky="w")
        show_ip_var = ctk.BooleanVar(value=config["show_ip"])
        show_ip_switch = ctk.CTkSwitch(config_window, variable=show_ip_var, text="")
        show_ip_switch.grid(row=9, column=1, padx=10, pady=5, sticky="w")

        show_console_label = ctk.CTkLabel(config_window, text="Show Console:")
        show_console_label.grid(row=10, column=0, padx=10, pady=5, sticky="w")
        show_console_var = ctk.BooleanVar(value=config["show_console"])
        show_console_switch = ctk.CTkSwitch(config_window, variable=show_console_var, text="")
        show_console_switch.grid(row=10, column=1, padx=10, pady=5, sticky="w")

        button_frame = ctk.CTkFrame(config_window, fg_color="transparent")
        button_frame.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        save_button = ctk.CTkButton(
            button_frame, text="Save",
            command=lambda: save_config(
                config_window,
                browser_var,
                show_ip_var,
                show_console_var,
                d_email_entry,
                d_pass_entry,
                d_auto_login_var,
                d_text_file_var,
                d_deepthink_var,
                d_search_var
            )
        )
        save_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=config_window.destroy)
        cancel_button.grid(row=0, column=1, padx=5, sticky="ew")

        print("Settings window created.")
    except Exception as e:
        print(f"Error opening config window: {e}")

def save_config(
        config_window,
        browser_var,
        show_ip_var,
        show_console_var,
        d_email_entry,
        d_pass_entry,
        d_auto_login_var,
        d_text_file_var,
        d_deepthink_var,
        d_search_var
    ):
    try:
        config["browser"] = browser_var.get()
        config["show_ip"] = show_ip_var.get()
        config["show_console"] = show_console_var.get()

        config["models"]["deepseek"]["email"] = d_email_entry.get()
        config["models"]["deepseek"]["password"] = d_pass_entry.get()
        config["models"]["deepseek"]["auto_login"] = d_auto_login_var.get()
        config["models"]["deepseek"]["text_file"] = d_text_file_var.get()
        config["models"]["deepseek"]["deepthink"] = d_deepthink_var.get()
        config["models"]["deepseek"]["search"] = d_search_var.get()
        
        manager.save_config(config)
        api.assign_config(config)
        
        if console_window:
            toggle_console_window(config["show_console"])

        print("Saved config.")
        config_window.destroy()
    except Exception as e:
        print(f"Error saving config: {e}")

def open_credits():
    try:
        print("Link opened.")
        webbrowser.open("https://linktr.ee/omega_slender")
    except Exception as e:
        print(f"Error opening credits: {e}")

def create_gui():
    try:
        global root, textbox, console_window, icon_path, version
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        load_files()
        
        root = ctk.CTk()
        root.title(f"INTENSE RP API V{version}")

        if icon_path:
            root.iconbitmap(default=icon_path)
        
        x = (root.winfo_screenwidth() - 400) // 2
        y = (root.winfo_screenheight() - 500) // 2
        root.geometry(f"400x500+{x}+{y}")
        root.minsize(200, 250)
        
        def on_closing():
            api.close_selenium()

            if root:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(root, text=f"INTENSE RP API V{version}", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        textbox = ctk.CTkTextbox(root, state="disabled", font=("Arial", 16), wrap="none")
        textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        color_map = {
            "red": "red",
            "green": "#13ff00",
            "yellow": "yellow",
            "blue": "blue",
            "cyan": "cyan",
            "white": "white",
            "purple": "#e400ff",
            "orange": "orange",
            "pink": "pink"
        }
        
        for tag, color in color_map.items():
            textbox.tag_config(tag, foreground=color)

        api.assign_textbox(textbox)

        start_button = ctk.CTkButton(root, text="Start", command=start_services)
        start_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        config_button = ctk.CTkButton(root, text="Settings", command=open_config_window)
        config_button.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        credits_button = ctk.CTkButton(root, text="Credits", command=open_credits)
        credits_button.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")

        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            create_console_window()
            sys.stdout = ConsoleRedirector(console_add)
            sys.stderr = ConsoleRedirector(console_add)
        except Exception as e:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            print(f"Falling back to default console: {e}")

        if console_window and config["show_console"]:
            root.after(100, lambda: toggle_console_window(True))
            print("Console window created.")
        
        print("Main window created.")
        root.mainloop()
    except Exception as e:
        print(f"Error creating GUI: {e}")