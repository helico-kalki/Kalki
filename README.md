# Kalki Image Manipulation Program
<img width="100" height="100" alt="Kalki" src="https://github.com/user-attachments/assets/25a8c636-5a0c-4252-bb35-bf082ec20eeb" />

Kalki is a python-built, light image manipulation program aiming an intuitive design, rather than functionality.

This program is 90% AI - I am not good at coding and actually not even in ambition to change this.

The reason I wanted to create an image manipulation program was designing my own - all textures (and the layout) are by myself. In uploading this, I hope to see my vision take shape in the hands of the internet. This project also willingly does not have any copyright, you do not have to give me credit, just don't be evil making profit of something that's not supposed to do so.

## GUI
<img width="999" height="1052" alt="GUI" src="https://github.com/user-attachments/assets/b2004a39-97b7-4e79-98b1-c4e1800fd19e" />
As seen on the screenshot, the application consists of a top actionbar, the white canvas and the task/toolbar.

### Actionbar
- New (Clear Canvas)
- Import (Open File)
- Export Canvas (Save)
- Undo/Redo
- Copy/Paste
- Zoom In/Zoom Out
- Effects (12 Options)
### Taskbar
- Move Selection
- Rectangular Selection
- Circular Selection
- Lasso Selection (not working quite yet)
- Delete Selection
- Shapes (Rectangle, Triangle, Ellipse, Lines)/Shape Mode (no drawing to shape automation, just en/disabling drawing shapes)
- Text (Customization Window, then applying to the canvas by a click)
- Pen (Black, Width: 2)
- Marker (Yellow, Translucent, 20)
- Brush (Blue, 10, Graphics Tablet Compatibility)
- Eraser (White, 30)
- Pen Width Slider
- Pick Color
- Select Color
- Fill Canvas with selected Color
- Fill Canvas with two-color gradient (left to right)
### Other Functionality
- Pan with Middle Mouse Click
- Zoom with Ctrl and Mouse Scroll

## Installation
You'll need PyQt6 and Pillow.

Download the ZIP with the green Code button and get the Kalki-main folder out of the ZIP.

You'll most likely need to type this into the Terminal (Visual Studio Code):

- pip install pyqt6

- pip install pillow

If not working, try py -m pip install (...)

Of course, Python itself is required: https://www.python.org/downloads/

To start, just open the gui.py file.

Some text in the GUI is written with the non-standard font Lexend Deca: https://fonts.google.com/specimen/Lexend+Deca

## Further Ambition
The Selection tool is very limited, it's only possible to move the Selection and to only draw in the Selection. Moving a Circular Selection will turn it into a Rectangular Selection. The Color Bucket and the Gradient tool are of course meant to fill the selection, not simply the canvas. Also, in the colored_textures folder there's a texture for Magic Selection - just if someone wants to code it...

The Undo/Redo function is a picky one, while working perfectly when only drawing actions are undone, other actions make it undo way more than asked for.

I aim for an even more sharp design, but I'm limited by (my knowledge of) PyQt - although this is the best option by functionality. Especially opening the Text tool is something i'd have implemented into the main frame, not an external window.

To give you an idea of my ambition, my favorite design tool is paint.net (not a website), which is what I'm daily driving. Taking Kalki this far by functionality would be amazing.



