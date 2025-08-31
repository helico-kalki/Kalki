# <img width="100" height="100" alt="Kalki" src="https://github.com/user-attachments/assets/25a8c636-5a0c-4252-bb35-bf082ec20eeb" />   Kalki Image Manipulation Program

✅ **Kalki** is a powerful **image manipulation program** built in `Python`. It aims to have a **colorful and intuitive** design.

🤖 This program is 90% AI - I am **not good** at coding and actually not even in ambition to change this.

🎈 The reason I wanted to create an image manipulation program was **designing** my own - all textures (and the layout) are by myself. In uploading this, I hope to see my vision take shape in the hands of the internet. Due to risks with AI generated code and the PyQt6 license, this project is published under the GPL license, although I'd wish this to have no copyright at all.

## 📥 Installation
🔽 Download the **ZIP** with the green **Code** button and get the *Kalki-main* folder out of the **ZIP**.

You'll most likely need to type this into the `Terminal` (Visual Studio Code), as you need `PyQt6` and `Pillow`:

    pip install pyqt6

    pip install pillow

If not working, try:

    py -m pip install pyqt6

    py -m pip install pillow

▶ **To start, just open the gui.py file.**

The font used is `Lexend Deca`, you'll have to install it on your own: https://fonts.google.com/specimen/Lexend+Deca  
Of course, `Python` itself is required: https://www.python.org/downloads/

## 🖼 GUI
☀ Light Mode

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6d186ad4-1782-446e-9bf8-f1a2fe814fd3" />

🌙 Dark Mode

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/d76d4c37-6ed3-4491-a65f-08ead1dc761a" />

As seen on the screenshots, the application consists of a **top actionbar**, the **canvas** and the **task/toolbar**.

### 🦺 Actionbar
- *️⃣ New (Clear Canvas)
- 🔽 Import to Canvas (Open File)
- 🔼 Export Canvas (Save)
- ↪ Undo/Redo
- ⏩ Copy/Paste
- 🌌 Zoom In/Zoom Out
- 🌊 Resize Canvas (Canvas will be morphed)
- 💠 Crop Canvas to Selection
- 🔄 Rotate 90 degrees (counter)clockwise
- ⏸ Mirror vertically/horizontally
- ⭐ Effects (12 Options)
  
      - 🚦 Combined Adjustments (Red, Blue, Yellow, Saturation, Brightness, Contrast)
      - 🌡 Temperature / Tint (Light Blue - Orange and Magenta - Green Color Correction)
      - 💧 Gaussian Blur
      - 💧 Smooth
      - 💧 Smooth More
      - 🎭 Unsharp Mask
      - 🗻 Sharpen
      - 🚧 Contour
      - 🏁 Find Edges
      - 🚨 Edge Enhance
      - 🔑 Emboss
      - 👀 Detail
      - 💊 Invert Colors

- 🌙 Dark Mode/Light Mode

### 🥏 Taskbar
- 🧭 Selection (Rectangular, Circular, Lasso, Delete Selection)
- 🔆 Move/Scale Selection (must be clicked another time to submit new position/scale)
- 🔶 Shapes (Rectangle, Triangle, Ellipse, Lines, Disable Shape Mode)
- 🅰 Text (Customization Menu, then applying to the canvas by a click)
- 📝 Drawing

         - ✏ Pen (Black, Width: 2)
         - 🖍 Marker (Yellow, Translucent, 20)
         - 🖌 Brush (Blue, 10, Graphics Tablet Compatibility)
         - 🧹 Eraser (White, 30)

- ⏹ Fill Selection with selected Color
- ⏮ Fill Selection with two-color gradient (left to right)
- 🎨 Select Color (Opens Pick Color Menu)

### 🎀 Other Functionality
- 🏓 Pan with Middle Mouse Click
- 🖱 Zoom with Mouse Scroll
- 📮 Config File to Customize Kalki to your needs with Shortcuts for every feature and Default Values

## 📌 Ideas
- 🔲 Outline Tool
- 〽 Courves
- 🆎 Text Presets (implemented, not working as supposed to)
- ➗ Dash and Dot Line
- 💥 Filter to Selection working for Combined Adjustments and Temperature/Tint

## ♻ Changelog
08/31/25 | 1.7 | Finally fixed the **Lasso Selection** tool and **Apply Filter to Selection** (not working for Combined Adjustments and Temp/Tint). Also minor **performance optimization** and **Zoom is centered** to the Cursor. The canvas is **not anti-aliased** making pixelart viable.

08/31/25 | 1.6 | Added **Dark Mode**, **Temperature / Tint Effect** and a better file structure.

08/30/25 | 1.5 | Added a **custom Pick Color** menu/popup, with preview, hex code, eyedropper, hsv sliders, rgba sliders and presets.

08/28/25 | 1.4 | The text menu is not a **popup** anymore, but an **integrated menu**. Same goes for the **drawing tool**. Not yet working experiments on **text presets** and **dash/dot lines** are contained in this version. 

08/28/25 | 1.3 | Added **resizing canvas**, **fill selection (with gradient)** and a **warning message before closing Kalki**

08/27/25 | 1.2 | Added **configurable constants** (config.py file) and a **warning message before clearing canvas**

08/27/25 | 1.1 | Added **Mirror**, **Rotate** and **Crop to Selection** (also minor design changes)

08/26/25 | 1.0 | **Base** Version




