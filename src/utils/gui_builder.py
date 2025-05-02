from typing import Optional, List, Callable
import customtkinter as ctk
import re

# =============================================================================================================================
# Rows and Columns Utils
# =============================================================================================================================

def _set_row_grid(obj: ctk.CTkBaseClass, row: int) -> None:
    obj.grid_rowconfigure(row, weight=1)

# =============================================================================================================================
# Widget Utils
# =============================================================================================================================

def _save_widget(obj: ctk.CTkBaseClass, widget_id: str, widget: ctk.CTkBaseClass) -> None:
    if not hasattr(obj, "_widgets"):
        obj._widgets = {}
    obj._widgets[widget_id] = widget

def _get_widget(obj: ctk.CTkBaseClass, widget_id: str) -> Optional[ctk.CTkBaseClass]:
    return getattr(obj, "_widgets", {}).get(widget_id)

def _get_widget_value(obj: ctk.CTkBaseClass, widget_id: str) -> Optional[str]:
    widget = getattr(obj, "_widgets", {}).get(widget_id)
    return widget.get() if widget and hasattr(widget, "get") else None

# =============================================================================================================================
# Frame Utils
# =============================================================================================================================

def _save_frame(obj: ctk.CTkBaseClass, frame_id: str, frame: ctk.CTkFrame) -> None:
    if not hasattr(obj, "_frames"):
        obj._frames = {}
    obj._frames[frame_id] = frame

def _get_frame(obj: ctk.CTkBaseClass, frame_id: str) -> Optional[ctk.CTkFrame]:
    return getattr(obj, "_frames", {}).get(frame_id)

# =============================================================================================================================
# Parent Window Utils
# =============================================================================================================================

def _create_parent_window(
    parent: ctk.CTkToplevel,
    visible: bool,
    title: str,
    width: int,
    height: int,
    min_width: Optional[int] = None,
    min_height: Optional[int] = None,
    icon: Optional[str] = None
) -> None:
    parent.title(title)
    
    if visible:
        parent.geometry(f"{width}x{height}")
        if min_width or min_height:
            parent.minsize(min_width or 0, min_height or 0)
        if icon:
            try:
                parent.after(200, lambda: parent.iconbitmap(icon))
            except Exception:
                pass
    else:
        parent.withdraw()

def _center_parent_window(parent: ctk.CTkToplevel, root: ctk.CTk, width: Optional[int] = None, height: Optional[int] = None) -> None:
    root.update_idletasks()
    parent.update_idletasks()
    
    width = width or parent.winfo_width()
    height = height or parent.winfo_height()
    x = root.winfo_x() + (root.winfo_width() - width) // 2
    y = root.winfo_y() + (root.winfo_height() - height) // 2
    parent.geometry(f"{width}x{height}+{x}+{y}")

# =============================================================================================================================
# Textbox Widget
# =============================================================================================================================

class CustomTextbox(ctk.CTkTextbox):
    def _ensure_max_lines(self, max_lines: int = 500) -> None:
        self.update_idletasks()
        total_lines = int(self.index("end-1c").split('.')[0])
        if total_lines > max_lines:
            self.delete("1.0", f"{total_lines - max_lines + 1}.0")

    def add_colors(self) -> None:
        self._color_map = {
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
        for tag, color in self._color_map.items():
            self.tag_config(tag, foreground=color)
    
    def clear(self) -> None:
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")

    def colored_add(self, text: str) -> None:
        print(text)
        
        pattern = r'\[color:(\w+)\]'
        parts = re.split(pattern, text)
        current_tag = "white"

        self.configure(state="normal")
        self._ensure_max_lines()

        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    self.insert("end", part, current_tag)
            else:
                tag = part.lower()
                current_tag = tag if hasattr(self, "_color_map") and tag in self._color_map else "white"

        self.insert("end", "\n")
        self.configure(state="disabled")
        self.see("end")

    def add(self, text: str) -> None:
        self.configure(state="normal")
        self._ensure_max_lines()
        self.insert("end", text)
        self.configure(state="disabled")
        self.see("end")

# =============================================================================================================================
# Root Window
# =============================================================================================================================

def apply_appearance() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

class RootWindow(ctk.CTk):
    def create(
        self,
        title: str,
        width: int,
        height: int,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        icon: Optional[str] = None
    ) -> None:
        self._last_title = title
        self._last_width = width
        self._last_height = height
        self._last_min_width = min_width
        self._last_min_height = min_height
        self._last_icon = icon

        self.title(title)
        self.geometry(f"{width}x{height}")
        if min_width or min_height:
            self.minsize(min_width or 0, min_height or 0)
        
        if icon:
            try:
                self.iconbitmap(icon)
            except Exception:
                pass
    
    def center(self) -> None:
        self.update_idletasks()

        width = self._last_width or self.winfo_width()
        height = self._last_height or self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")

    def get_widget(self, id: str) -> Optional[ctk.CTkBaseClass]:
        return _get_widget(self, id)

    def get_widget_value(self, id: str) -> Optional[str]:
        return _get_widget_value(self, id)

    def create_title(self, id: str, text: str, row: int = 0, column: int = 0, row_grid: bool = False) -> ctk.CTkLabel:
        label = ctk.CTkLabel(self, text=text, font=("Arial", 18, "bold"))
        label.grid(row=row, column=column, padx=10, pady=(10, 0), sticky="nsew")

        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, label)
        return label
    
    def create_textbox(self, id: str, row: int = 0, column: int = 0, row_grid: bool = False, bg_color: Optional[str]= None) -> CustomTextbox:
        textbox = CustomTextbox(self, state="disabled", font=("Arial", 16), wrap="none", fg_color=bg_color)
        textbox.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, textbox)
        return textbox

    def create_button(self, id: str, text: str, command: Optional[Callable] = None, row: int = 0, column: int = 0, row_grid: bool = False) -> ctk.CTkButton:
        button = ctk.CTkButton(self, text=text, command=command)
        button.grid(row=row, column=column, padx=10, pady=(0, 10), sticky="ew")

        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, button)
        return button

# =============================================================================================================================
# Config Window
# =============================================================================================================================

class ConfigFrame(ctk.CTkFrame):
    def get_widget(self, id: str) -> Optional[ctk.CTkBaseClass]:
        return _get_widget(self, id)
    
    def get_widget_value(self, id: str) -> Optional[str]:
        return _get_widget_value(self, id)
    
    def create_title(self, id: str, text: str, row: int = 0, row_grid: bool = False) -> ctk.CTkLabel:
        label = ctk.CTkLabel(self, text=text, font=("Arial", 14, "bold"))
        label.grid(row=row, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, label)
        return label

    def create_entry(self, id: str, label_text: str, default_value: str, row: int = 0, row_grid: bool = False) -> ctk.CTkEntry:
        ctk.CTkLabel(self, text=label_text).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        entry = ctk.CTkEntry(self, width=250, border_color="gray")
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        entry.insert(0, default_value)

        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, entry)
        return entry

    def create_password(self, id: str, label_text: str, default_value: str, row: int = 0, row_grid: bool = False) -> ctk.CTkEntry:
        ctk.CTkLabel(self, text=label_text).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(frame, show="*", border_color="gray")
        entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        entry.insert(0, default_value)

        def toggle():
            show_state = entry.cget("show")
            entry.configure(show="" if show_state == "*" else "*")
            toggle_btn.configure(text="Show" if show_state == "*" else "Hide")

        toggle_btn = ctk.CTkButton(frame, text="Show", width=60, command=toggle)
        toggle_btn.grid(row=0, column=1, sticky="e")

        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, entry)
        return entry

    def create_switch(self, id: str, label_text: str, default_value: bool, command: Callable[[bool], None] = None, row: int = 0, row_grid: bool = False) -> ctk.CTkSwitch:
        ctk.CTkLabel(self, text=label_text).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        var = ctk.BooleanVar(value=default_value)
        switch = ctk.CTkSwitch(self, variable=var, text="")
        switch.grid(row=row, column=1, padx=10, pady=5, sticky="w")

        if command:
            switch.configure(command=lambda: command(var.get()))

        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, switch)
        return switch

    def create_option_menu(self, id: str, label_text: str, default_value: str, options: List[str], row: int = 0, row_grid: bool = False) -> ctk.CTkOptionMenu:
        ctk.CTkLabel(self, text=label_text).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        var = ctk.StringVar(value=default_value)
        menu = ctk.CTkOptionMenu(self, variable=var, values=options)
        menu.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, menu)
        return menu
    
    def create_button(self, id: str, text: str, command: Optional[Callable] = None, row: int = 0, column: int = 0, row_grid: bool = False) -> ctk.CTkButton:        
        button = ctk.CTkButton(self, text=text, command=command)
        button.grid(row=row, column=column, padx=3, sticky="ew")

        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, button)
        return button

class ConfigWindow(ctk.CTkToplevel):
    def create(
        self,
        visible: bool,
        title: str,
        width: int,
        height: int,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        icon: Optional[str] = None
    ) -> None:
        self._last_title = title
        self._last_width = width
        self._last_height = height
        self._last_min_width = min_width
        self._last_min_height = min_height
        self._last_icon = icon

        _create_parent_window(self, visible, title, width, height, min_width, min_height, icon)
    
    def center(self, root: ctk.CTk) -> None:
        return _center_parent_window(self, root, self._last_width, self._last_height)
    
    def get_widget(self, id: str) -> Optional[ctk.CTkBaseClass]:
        return _get_widget(self, id)

    def get_widget_value(self, id: str) -> Optional[str]:
        return _get_widget_value(self, id)
    
    def get_frame(self, id: str) -> Optional[ctk.CTkFrame]:
        return _get_frame(self, id)
    
    def create_section_frame(
        self,
        id: str = None,
        padding: int = 10,
        top_padding: int = 0,
        bottom_padding: int = 10,
        bg_color: Optional[str] = None,
        row: int = 0,
        column: int = 0,
        row_grid: bool = False
    ) -> ConfigFrame:
        frame = ConfigFrame(self, fg_color=bg_color)
        frame.grid(
            row=row,
            column=column,
            columnspan=2,
            padx=padding,
            pady=(top_padding, bottom_padding),
            sticky="nsew"
        )

        if row_grid:
            _set_row_grid(self, row)

        _save_frame(self, id, frame)
        return frame

# =============================================================================================================================
# Console Window
# =============================================================================================================================

class ConsoleWindow(ctk.CTkToplevel):
    def create(
        self,
        visible: bool,
        title: str,
        width: int,
        height: int,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        icon: Optional[str] = None
    ) -> None:
        self._last_title = title
        self._last_width = width
        self._last_height = height
        self._last_min_width = min_width
        self._last_min_height = min_height
        self._last_icon = icon
        
        _create_parent_window(self, visible, title, width, height, min_width, min_height, icon)
    
    def center(self, root: ctk.CTk) -> None:
        return _center_parent_window(self, root, self._last_width, self._last_height)
    
    def get_widget(self, id: str) -> Optional[ctk.CTkBaseClass]:
        return _get_widget(self, id)

    def get_widget_value(self, id: str) -> Optional[str]:
        return _get_widget_value(self, id)
    
    def show(self, show: bool, root: ctk.CTk, center: bool) -> None:
        if (self.winfo_viewable() == 1) == show:
            return
        
        if show:
            self.deiconify()
            self.lift()
            self.geometry(f"{self._last_width}x{self._last_height}")
            self.minsize(self._last_min_width, self._last_min_height)

            if self._last_icon:
                self.after(200, lambda: self.iconbitmap(self._last_icon))

            if center:
                return _center_parent_window(self, root, self._last_width, self._last_height)
        else:
            self.withdraw()
    
    def create_textbox(self, id: str) -> CustomTextbox:
        textbox = CustomTextbox(
            self,
            state="disabled",
            font=("Arial", 16),
            wrap="none",
            border_width=0,
            corner_radius=0,
            fg_color="black",
            text_color="white"
        )
        textbox.pack(expand=True, fill="both")
        _save_widget(self, id, textbox)
        return textbox

class UpdateWindow(ctk.CTkToplevel):
    def create(
        self,
        visible: bool,
        title: str,
        width: int,
        height: int,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        icon: Optional[str] = None
    ) -> None:
        self._last_title = title
        self._last_width = width
        self._last_height = height
        self._last_min_width = min_width
        self._last_min_height = min_height
        self._last_icon = icon
        
        _create_parent_window(self, visible, title, width, height, min_width, min_height, icon)
    
    def center(self, root: ctk.CTk) -> None:
        return _center_parent_window(self, root, self._last_width, self._last_height)
    
    def get_widget(self, id: str) -> Optional[ctk.CTkBaseClass]:
        return _get_widget(self, id)

    def get_widget_value(self, id: str) -> Optional[str]:
        return _get_widget_value(self, id)
    
    def create_title(self, id: str, text: str, row: int = 0, column: int = 0, row_grid: bool = False) -> ctk.CTkLabel:
        label = ctk.CTkLabel(self, text=text, font=("Arial", 14, "bold"))
        label.grid(row=row, column=column, padx=10, pady=(10, 10), sticky="nsew")
    
        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, label)
        return label
    
    def create_button(self, id: str, text: str, command: Optional[Callable] = None, row: int = 0, column: int = 0, row_grid: bool = False) -> ctk.CTkButton:
        button = ctk.CTkButton(self, text=text, command=command)
        button.grid(row=row, column=column, padx=10, pady=(0, 10), sticky="ew")

        if row_grid:
            _set_row_grid(self, row)

        _save_widget(self, id, button)
        return button