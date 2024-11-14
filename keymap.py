import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import json


class KeyMapEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KeyMap Editor")
        # Default value
        self.width = 1920
        self.height = 1080
        self.scale = 1
        self.geometry(f"{self.width}x{self.height}")

        # Canvas to display the keymap
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="white")
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

        # Store loaded keymap and key widgets
        self.keymap = None
        self.key_widgets = []
        self.selected_key = None
        self.background_image = None

        # Menu for loading/saving JSON and background image
        menu = tk.Menu(self)
        self.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open KeyMap", command=self.load_keymap)
        file_menu.add_command(label="Save KeyMap", command=self.save_keymap)
        file_menu.add_command(
            label="Open Background Image", command=self.load_background_image
        )

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind(
            "<Button-3>", self.on_right_click
        )  # Right-click event for menu

    def load_keymap(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:  # Support UTF8
                self.keymap = json.load(file)
                if (
                    "height" in self.keymap
                    and "width" in self.keymap
                    and self.keymap["height"] > 0
                    and self.keymap["width"] > 0
                ):
                    self.height = self.keymap["height"]
                    self.width = self.keymap["width"]
                    self.geometry(f"{self.width}x{self.height}")
                    self.canvas.config(width=self.width, height=self.height)
                self.render_keymap()

    def save_keymap(self):
        if self.keymap:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json", filetypes=[("JSON files", "*.json")]
            )
            if file_path:
                self.keymap["height"] = self.height
                self.keymap["width"] = self.width
                with open(file_path, "w", encoding="utf-8") as file:  # Support UTF8
                    json.dump(
                        self.keymap, file, indent=4, ensure_ascii=False
                    )  # ensure_ascii Prevent Chinese escape
                messagebox.showinfo("KeyMap Editor", "Keymap saved successfully!")
        else:
            messagebox.showwarning("KeyMap Editor", "No keymap to save!")

    def load_background_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )
        if file_path:
            img = Image.open(file_path)

            # Obtain the original size of the image
            img_width, img_height = img.size
            # Calculate scaling ratio
            scale_width = self.winfo_width() / img_width
            scale_height = self.winfo_height() / img_height
            self.scale = min(scale_width, scale_height)
            # Apply proportional scaling
            self.width = int(img_width * self.scale)
            self.height = int(img_height * self.scale)
            self.geometry(f"{self.width}x{self.height}")
            self.canvas.config(width=self.width, height=self.height)
            img = img.resize((self.width, self.height), Image.LANCZOS)

            self.background_image = ImageTk.PhotoImage(img)
            self.render_keymap()  # Re-render to apply background image

    def render_keymap(self):
        self.canvas.delete("all")  # Clear previous canvas

        # Draw the background image if it exists
        if self.background_image:
            self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)

        self.key_widgets = []

        if self.keymap:
            for keymap_node in self.keymap["keyMapNodes"]:
                if keymap_node["type"] == "KMT_STEER_WHEEL":
                    self.render_steer_wheel(keymap_node)
                elif "pos" in keymap_node:  # Check if 'pos' exists for normal keymaps
                    self.render_key(keymap_node)

    def render_key(self, keymap_node):
        x = keymap_node["pos"]["x"] * self.width
        y = keymap_node["pos"]["y"] * self.height

        # Create the key rectangle
        widget = self.canvas.create_rectangle(
            x - 20, y - 20, x + 20, y + 20, fill="blue"
        )

        # Create white background text for 2px border (multiple white texts around the black text)
        key_label = keymap_node.get("key", keymap_node.get("comment", "Unknown Key"))

        outline_ids = [
            self.canvas.create_text(
                x - 1, y - 25 - 1, text=key_label, font=("Arial", 10), fill="white"
            ),  # Top-left
            self.canvas.create_text(
                x + 1, y - 25 - 1, text=key_label, font=("Arial", 10), fill="white"
            ),  # Top-right
            self.canvas.create_text(
                x - 1, y - 25 + 1, text=key_label, font=("Arial", 10), fill="white"
            ),  # Bottom-left
            self.canvas.create_text(
                x + 1, y - 25 + 1, text=key_label, font=("Arial", 10), fill="white"
            ),  # Bottom-right
        ]

        # Create the main black text in front
        text_id_black = self.canvas.create_text(
            x, y - 25, text=key_label, font=("Arial", 10), fill="black"
        )

        self.key_widgets.append(
            (widget, keymap_node, text_id_black, outline_ids, 0)
        )  # Store widget, black text, and outlines

    def render_steer_wheel(self, keymap_node):
        # Handle the special case for KMT_STEER_WHEEL (WASD control)
        x = keymap_node["centerPos"]["x"] * self.width
        y = keymap_node["centerPos"]["y"] * self.height
        widget = self.canvas.create_oval(
            x - 50, y - 50, x + 50, y + 50, outline="green", width=2
        )
        text_id = self.canvas.create_text(
            x, y - 70, text="Steer Wheel (WASD)", font=("Arial", 10), fill="black"
        )
        self.key_widgets.append(
            (widget, keymap_node, text_id, [], 50)
        )  # Include oval radius for later use

    def on_click(self, event):
        # Check if a key was clicked
        for widget, keymap_node, text_id, outline_ids, radius in self.key_widgets:
            coords = self.canvas.coords(widget)
            if (
                coords
                and coords[0] <= event.x <= coords[2]
                and coords[1] <= event.y <= coords[3]
            ):
                self.selected_key = (widget, keymap_node, text_id, outline_ids, radius)
                break

    def on_drag(self, event):
        if self.selected_key:
            widget, keymap_node, text_id_black, outline_ids, radius = self.selected_key

            if keymap_node["type"] == "KMT_STEER_WHEEL":
                # Move the steering wheel and its label
                self.canvas.coords(
                    widget,
                    event.x - radius,
                    event.y - radius,
                    event.x + radius,
                    event.y + radius,
                )
                self.canvas.coords(text_id_black, event.x, event.y - 70)

                # Update the keymap's centerPos
                keymap_node["centerPos"]["x"] = event.x / self.width
                keymap_node["centerPos"]["y"] = event.y / self.height
            else:
                # Move the key and its text outline
                self.canvas.coords(
                    widget, event.x - 20, event.y - 20, event.x + 20, event.y + 20
                )
                self.canvas.coords(text_id_black, event.x, event.y - 25)
                # Move the white outline around the black text
                self.canvas.coords(
                    outline_ids[0], event.x - 1, event.y - 25 - 1
                )  # Top-left
                self.canvas.coords(
                    outline_ids[1], event.x + 1, event.y - 25 - 1
                )  # Top-right
                self.canvas.coords(
                    outline_ids[2], event.x - 1, event.y - 25 + 1
                )  # Bottom-left
                self.canvas.coords(
                    outline_ids[3], event.x + 1, event.y - 25 + 1
                )  # Bottom-right

                # Update the keymap's pos
                keymap_node["pos"]["x"] = event.x / self.width
                keymap_node["pos"]["y"] = event.y / self.height

    def on_right_click(self, event):
        clicked_widget = None

        # Check if a key was right-clicked
        for widget, keymap_node, text_id, *_ in self.key_widgets:
            coords = self.canvas.coords(widget)
            if (
                coords
                and coords[0] <= event.x <= coords[2]
                and coords[1] <= event.y <= coords[3]
            ):
                clicked_widget = (widget, keymap_node, text_id)
                break

        if clicked_widget:
            # Show options to modify or delete the key
            self.show_modify_delete_menu(clicked_widget)
        else:
            # Add new key binding
            self.add_key(event.x, event.y)

    def show_modify_delete_menu(self, clicked_widget):
        widget, keymap_node, text_id = clicked_widget

        # Create a popup dialog for modify/delete
        dialog = tk.Toplevel(self)
        dialog.title("Modify or Delete Key")

        # Make sure the dialog stays on top and grabs focus
        dialog.transient(self)  # Make it a child of the main window
        dialog.grab_set()  # Block interaction with other windows until dialog is closed
        dialog.focus()  # Focus on the dialog

        if keymap_node["type"] == "KMT_STEER_WHEEL":
            # Add input fields for directional keys
            tk.Label(dialog, text="Left Key:").pack(pady=5)
            left_key_entry = tk.Entry(dialog)
            left_key_entry.insert(0, keymap_node.get("leftKey", "Key_A"))
            left_key_entry.pack()

            tk.Label(dialog, text="Right Key:").pack(pady=5)
            right_key_entry = tk.Entry(dialog)
            right_key_entry.insert(0, keymap_node.get("rightKey", "Key_D"))
            right_key_entry.pack()

            tk.Label(dialog, text="Up Key:").pack(pady=5)
            up_key_entry = tk.Entry(dialog)
            up_key_entry.insert(0, keymap_node.get("upKey", "Key_W"))
            up_key_entry.pack()

            tk.Label(dialog, text="Down Key:").pack(pady=5)
            down_key_entry = tk.Entry(dialog)
            down_key_entry.insert(0, keymap_node.get("downKey", "Key_S"))
            down_key_entry.pack()

            def modify_steer_wheel_keys():
                keymap_node["leftKey"] = left_key_entry.get()
                keymap_node["rightKey"] = right_key_entry.get()
                keymap_node["upKey"] = up_key_entry.get()
                keymap_node["downKey"] = down_key_entry.get()
                dialog.destroy()

            modify_button = tk.Button(
                dialog, text="Modify Keys", command=modify_steer_wheel_keys, width=20
            )
            modify_button.pack(pady=5)
        else:
            # Modify Key Button
            def modify_key():
                new_key = simpledialog.askstring(
                    "Change Key Binding", "Enter new key:", parent=self
                )  # parent Specify the parent window to prevent pop ups from being overwritten
                if new_key:
                    keymap_node["key"] = new_key
                    self.canvas.itemconfig(text_id, text=new_key)
                dialog.destroy()

            modify_button = tk.Button(
                dialog, text="Modify Key", command=modify_key, width=20
            )
            modify_button.pack(pady=5)

        # Delete Key Button
        def delete_key():
            self.keymap["keyMapNodes"].remove(keymap_node)
            self.key_widgets = [
                w for w in self.key_widgets if w[1] != keymap_node
            ]  # Remove from key_widgets
            self.canvas.delete(widget)
            self.canvas.delete(text_id)
            dialog.destroy()

        delete_button = tk.Button(
            dialog, text="Delete Key", command=delete_key, width=20
        )
        delete_button.pack(pady=5)

        # Wait for the user to close the dialog
        dialog.wait_window(dialog)

    def add_key(self, x, y):
        # Create a popup window for key type selection
        key_type = self.ask_key_type()

        if not key_type:
            return

        if key_type == "KMT_STEER_WHEEL":
            # Use default values for steer wheel
            new_key = {
                "comment": "wasd",
                "type": "KMT_STEER_WHEEL",
                "centerPos": {"x": x / self.width, "y": y / self.height},
                "leftOffset": 0.2,
                "rightOffset": 0.2,
                "upOffset": 0.3,
                "downOffset": 0.2,
                "leftKey": "Key_A",
                "rightKey": "Key_D",
                "upKey": "Key_W",
                "downKey": "Key_S",
            }
        else:
            # Ask for key value for other types
            key_value = simpledialog.askstring(
                "Add Key Binding", "Enter key (e.g., Key_W):", parent=self
            )  # parent Specify the parent window to prevent pop ups from being overwritten
            if not key_value:
                return

            new_key = {
                "comment": key_value,
                "type": key_type,
                "pos": {"x": x / self.width, "y": y / self.height},
                "key": key_value,
            }

        if not self.keymap:
            self.keymap = {"keyMapNodes": []}

        # Append new key to keymap
        self.keymap["keyMapNodes"].append(new_key)

        # Render the newly added key directly
        if key_type == "KMT_STEER_WHEEL":
            self.render_steer_wheel(new_key)  # Render the new steer wheel
        else:
            self.render_key(new_key)  # Render the new normal key

    def ask_key_type(self):
        # Create a dialog to ask for the key type
        dialog = tk.Toplevel(self)
        dialog.title("Select Key Type")

        # Make sure the dialog stays on top and grabs focus
        dialog.transient(self)  # Make it a child of the main window
        dialog.grab_set()  # Block interaction with other windows until dialog is closed
        dialog.focus()  # Focus on the dialog

        key_type_var = tk.StringVar(value=None)

        def select_kmt_click():
            key_type_var.set("KMT_CLICK")
            dialog.destroy()

        def select_kmt_steer_wheel():
            key_type_var.set("KMT_STEER_WHEEL")
            dialog.destroy()

        # Buttons to select key type
        label = tk.Label(dialog, text="Select Key Type:", font=("Arial", 12))
        label.pack(pady=10)

        button_click = tk.Button(
            dialog, text="KMT_CLICK", command=select_kmt_click, width=20
        )
        button_click.pack(pady=5)

        button_steer_wheel = tk.Button(
            dialog, text="KMT_STEER_WHEEL", command=select_kmt_steer_wheel, width=20
        )
        button_steer_wheel.pack(pady=5)

        # Wait for the user to close the dialog
        dialog.wait_window(dialog)

        return key_type_var.get()


if __name__ == "__main__":
    app = KeyMapEditor()
    app.mainloop()
