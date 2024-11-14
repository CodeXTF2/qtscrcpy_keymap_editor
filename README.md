
# KeyMap Editor for QtScrcpy


KeyMap Editor is a Python-based tool designed to help generate and edit keymaps for [QtScrcpy](https://github.com/barry-ran/QtScrcpy), a popular GUI tool for Android screen mirroring. The editor provides a simple GUI to load, modify, and save keymap files in JSON format. The tool allows users to visually map keyboard inputs to touch controls on a ~~1920x1080~~ (**Support adaptive background image scaling**) canvas and includes the option to import background images to assist with key alignment.

## Features

- **Drag-and-Drop Editing**: Drag existing key bindings on the canvas to reposition them as needed.
- **Modify Key Bindings**: Right-click on a key to modify its assigned keyboard shortcut, including steering wheel controls (WASD).
- **Add New Key Bindings**: Right-click on an empty area of the canvas to add new key bindings.
- **Steering Wheel (WASD) Support**: Special handling for WASD steering wheel controls with customizable directional keys.
- **Background Image Support**: Load a background image to assist in precise keymap alignment for better integration with mirrored Android screens.
- **JSON KeyMap Support**: Load and save keymap configurations in JSON format that are compatible with QtScrcpy.

## Prerequisites

- **Python 3.x**
- Required Python libraries:
  - `tkinter` (included with most Python installations)
  - `Pillow` (for handling images)

You can install `Pillow` by running:
```bash
pip install Pillow
```

## Usage

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd keymap-editor-qtscrcpy
   ```

2. Install the required dependencies:
   ```bash
   pip install Pillow
   ```

3. Run the editor:
   ```bash
   python keymap_editor.py
   ```

4. Load an existing keymap JSON file, or start creating a new one by right-clicking on the canvas to add new keys.

5. Optionally, load a background image to help with key alignment using the **File > Open Background Image** option.

6. Once your keymap is complete, save it in JSON format via **File > Save KeyMap**.

### Controls

- **Right-click on a key**: Modify or delete the key.
- **Right-click on empty space**: Add a new key binding.
- **Drag**: Move a key to reposition it on the canvas.

## Key Mapping Types

- **KMT_CLICK**: Ordinary click mapping. Simulates touch when a keyboard key is pressed.
- **KMT_STEER_WHEEL**: Steering wheel controls (WASD). Supports left, right, up, and down directional keys for movement.

