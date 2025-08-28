# Kalki Image Manipulation Program

✅ **Kalki** is a lightweight **image manipulation program** built in `Python`. It aims to have a **colorful and intuitive** design.

🤖 This program is 90% AI - I am **not good** at coding and actually not even in ambition to change this.

🎈 The reason I wanted to create an image manipulation program was **designing** my own - all textures (and the layout) are by myself. In uploading this, I hope to see my vision take shape in the hands of the internet. This project also willingly **does not have any copyright**, you do not have to give me credit, just don't be evil making profit of something that's not supposed to do so.

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
<img width="1001" height="1049" alt="image" src="https://github.com/user-attachments/assets/51322db0-f13c-41e8-8886-68a0d2ee733b" />


As seen on the screenshot, the application consists of a **top actionbar**, the **white canvas** and the **task/toolbar**.

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

### 🥏 Taskbar
- 🧭 Selection (Rectangular, Circular, Lasso (not working), Delete Selection)
- 🔆 Move/Scale Selection (must be clicked another time to submit new position/scale)
- 🔶 Shapes (Rectangle, Triangle, Ellipse, Lines, Disable Shape Mode)
- 🅰 Text (Customization Window, then applying to the canvas by a click)
- ✏ Pen (Black, Width: 2)
- 🖍 Marker (Yellow, Translucent, 20)
- 🖌 Brush (Blue, 10, Graphics Tablet Compatibility)
- 🧹 Eraser (White, 30)
- ⏏ Pen Width Slider
- 🔬 Pick Color
- 🎨 Select Color
- ⏹ Fill Canvas with selected Color
- ⏮ Fill Canvas with two-color gradient (left to right)

### 🎀 Other Functionality
- 🏓 Pan with Middle Mouse Click
- 🖱 Zoom with Ctrl and Mouse Scroll
- 📮 Config File to Customize Kalki to your needs with Shortcuts for every feature and Default Values

## 📌 Ideas
- 🌙 Dark Mode
- 🔲 Outline Tool
- 〽 Courves
- 🌈 Custom Color Selection
- ❄ Color Temperature

## ♻ Changelog
08/28/25 | 1.3 | Added **resizing canvas**, **fill selection (with gradient)** and a **warning message before closing Kalki**

08/27/25 | 1.2 | Added **configurable constants** (config.py file) and a **warning message before clearing canvas**

08/27/25 | 1.1 | Added **Mirror**, **Rotate** and **Crop to Selection** (also minor design changes)

08/26/25 | 1.0 | **Base** Version

<img width="100" height="100" alt="Kalki" src="https://github.com/user-attachments/assets/25a8c636-5a0c-4252-bb35-bf082ec20eeb" />



