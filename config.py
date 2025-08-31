from PyQt6.QtCore import Qt
# ✨ - * + KALKI CONFIG + * - ✨

# 🧩 SHORTCUTS
#--------------------------------

# 🦺 Toolbar

CLEAR_CANV="Ctrl+N"
IMP="Ctrl+O"
EXP="Ctrl+S"
UNDO="Ctrl+Z"
REDO="Ctrl+Y"
COPY="Ctrl+C"
PASTE="Ctrl+V"
ZOOM_IN="Ctrl++"
ZOOM_OUT="Ctrl+-"
RESIZE="Ctrl+R"
CROPTOSEL="Ctrl+Shift+X"
ROTATE90_CW="Ctrl+H"
ROTATE90_CCW="Ctrl+G"
MIRROR_H="Ctrl+Shift+H"
MIRROR_V="Ctrl+Shift+V"
DARKMODE_SHORTCUT="Ctrl+D"


# 🎆 Effects

CA="Ctrl+Shift+C"
TEMPERATURE="Ctrl+Shift+T"
GB="Ctrl+Shift+B"
SMOOTH="Ctrl+Shift+W"
SMOOTHMORE="Ctrl+Alt+W"
UNSHARP="Ctrl+Shift+U"
SHARPEN="Ctrl+Shift+Q"
CONTOUR="Ctrl+ALt+C"
FINDEDGES="Ctrl+Shift+E"
EDGEENHANCE="Ctrl+Alt+E"
EMBOSS="Ctrl+Shift+R"
DETAIL="Ctrl+Shift+D"
INVERT="Ctrl+Shift+I"


# 🥏 Taskbar

RSEL="S"
CSEL="Ctrl+E"
LSEL="Ctrl+L"
DELSEL="Del"
MOVE="M"

RECT="R"
ELLIPSE="E"
TRIANGLE="Ctrl+T"
LINES="L"
DISABLESHAPE="Ctrl+Del"
TEXT="T"

DRAW="D"
PEN="P"
MARKER="Ctrl+P"
BRUSH="B"
ERASER="X"

COLORPICKER="K"
COLOR="C"
COLORWHEEL="W"
BUCKET="F"
GRADIENT="G"

# 🔮 DEFAULT VALUES
#-------------------------------

# 🧧 Window
WINTITLE="Kalki"
WINSIZE=(0, 0, 1920, 1080)
WINICON="colored_textures/logo.png"
WINCOLOR="lightgray"
WARNBFCLOSE=True
STDSTYLE = "border: transparent; background: transparent;"
CONFIRM_BUTTON_STYLE = "border: transparent; background: #00B512; height: 30px; border-radius: 15px; font-family: 'Lexend Deca'; font-size: 17px; color: white;"
CANCEL_BUTTON_STYLE = "border: transparent; background: #E12C29; height: 30px; border-radius: 15px; font-family: 'Lexend Deca'; font-size: 17px; color: white;"
TOOL_BUTTON_STYLE = """
    QToolButton { 
        border: none; 
        background: transparent; } 
    QToolButton::menu-indicator {
        image: none;
        width: 0px;
        height: 0px;
    }
"""

# 🌙 Darkmode / Lightmode
DARKCOLOR = "#1c1c28"
DARKCOLOR2 = "#646478"
LIGHTCOLOR = "#d3d3d3"
DARK_MENU_STYLE = """
    QMenu { background-color: #1c1c28; border: 1px solid white;
            font-family: 'Lexend Deca'; font-size: 17px; color: white;
        }
    QMenu::item {
        padding: 4px 12px 4px 24px;
        height: 20px; 
        }
    QMenu::item:selected { background-color: #646478; color: white; }
    QMenu::icon { width: 35px; height: 35px; margin-right: 8px; margin-left: 16px; }
    QMenu::separator { height: 1px; background-color: #d3d3d3; margin: 5px 0; }
    QMenu::item:disabled { color: gray; }
    QMenu::item:checked { background-color: #909090; }
"""
LIGHT_MENU_STYLE = """
    QMenu { background-color: #d3d3d3;
            font-family: 'Lexend Deca'; font-size: 17px;
        }
    QMenu::item {
        padding: 4px 12px 4px 24px;
        height: 20px; 
        }
    QMenu::item:selected { background-color: #d3d3d3; }
    QMenu::icon { width: 35px; height: 35px; margin-right: 8px; margin-left: 16px; }
    QMenu::separator { height: 1px; background-color: #d3d3d3; margin: 5px 0; }
    QMenu::item:disabled { color: gray; }
    QMenu::item:checked { background-color: #909090; }
"""
DARK_SLIDER_STYLE = """
    QSlider::groove:horizontal { 
        background: #646478; 
        height: 25px; 
        border-radius: 5px; 
    }
    QSlider::handle:horizontal { 
        background: white; 
        width: 15px; 
        height: 35px; 
        border-radius: 5px; 
    }
"""
LIGHT_SLIDER_STYLE = """
    QSlider::groove:horizontal { 
        background: white; 
        height: 25px; 
        border-radius: 5px; 
    }
    QSlider::handle:horizontal { 
        background: #5b5b5b; 
        width: 15px; 
        height: 35px; 
        border-radius: 5px; 
    }
"""
DARK_SLIDER_STYLE2 = """
    QSlider::groove:horizontal { background: #646478; height: 25px; border-radius: 5px; }
    QSlider::handle:horizontal { background: white; width: 15px; height: 35px; border-radius: 5px; }
"""
LIGHT_SLIDER_STYLE2 = """
    QSlider::groove:horizontal { background: white; height: 25px; border-radius: 5px; }
    QSlider::handle:horizontal { background: #5b5b5b; width: 15px; height: 35px; border-radius: 5px; }
"""
DARK_TOOL_BUTTON_STYLE = """
    QToolButton {
        background: transparent;
        border: transparent;
        border-radius: 5px;
        min-width: 30px;
        min-height: 30px;
    }
    QToolButton:checked {
        background: #646478;
        color: black;
        border: transparent;
    }
"""
LIGHT_TOOL_BUTTON_STYLE = """
    QToolButton {
        background: transparent;
        border: transparent;
        border-radius: 5px;
        min-width: 30px;
        min-height: 30px;
    }
    QToolButton:checked {
        background: white;
        color: black;
        border: transparent;
    }
"""
LIGHT_TEXT_TOOL_BUTTON_STYLE = """
    QToolButton {
        background: #d3d3d3;
        color: black;
        border: transparent;
    }
    QToolButton:checked {
        background: white;
        border: transparent;
        border-radius: 5px;
        min-width: 30px;
        min-height: 30px;
    }
"""
DARK_TEXT_TOOL_BUTTON_STYLE = """
    QToolButton {
        background: #1c1c28;
        color: white;
        border: transparent;
    }
    QToolButton:checked {
        background: #646478;
        border: transparent;
        border-radius: 5px;
        min-width: 30px;
        min-height: 30px;
    }
"""
DARK_FONT_COMBO_STYLE = """
    QFontComboBox {
        background: #646478;
        border: transparent;
        border-radius: 5px;
        font-size: 15px;
        font-family: 'Lexend Deca';
        height: 20px;
        color: white;
    }
    QFontComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 50px;
        border-radius 5px;
        background: white;
    }
"""
LIGHT_FONT_COMBO_STYLE = """
    QFontComboBox {
        background: white;
        border: transparent;
        border-radius: 5px;
        font-size: 15px;
        font-family: 'Lexend Deca';
        height: 20px;
    }
    QFontComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 50px;
        border-radius 5px;
        background: transparent;
    }
"""
DARK_WIDGET_STYLE = """
    QWidget {
        background-color: #1c1c28;
        color: white;
    }
    QLabel {
        color: white;
        font-family: 'Lexend Deca';
    }
    QLineEdit {
        background: #646478;
        border: 1px solid white;
        border-radius: 5px;
        color: white;
        font-family: 'Lexend Deca';
    }
"""
LIGHT_WIDGET_STYLE = """
    QWidget {
        background-color: #d3d3d3;
        color: black;
    }
    QLabel {
        color: black;
        font-family: 'Lexend Deca';
    }
    QLineEdit {
        background: white;
        border: 1px solid black;
        border-radius: 5px;
        color: black;
        font-family: 'Lexend Deca';
    }
"""
DARK_COLOR_WIDGET_STYLE = """
    QWidget {
        background-color: #1c1c28;
        color: white;
    }
    QLabel {
        color: white;
        font-family: 'Lexend Deca';
    }
    QSlider::groove:horizontal {
        background: #646478;
        height: 25px;
        border-radius: 5px;
    }
    QSlider::handle:horizontal {
        background: white;
        width: 15px;
        height: 35px;
        border-radius: 5px;
    }
    QLineEdit {
        background: #646478;
        border: 1px solid white;
        border-radius: 5px;
        color: #646478;
        font-family: 'Lexend Deca';
    }
    QPushButton {
        background: #646478;
        border: 1px solid white;
        border-radius: 5px;
        color: white;
        font-family: 'Lexend Deca';
    }
    QPushButton:hover {
        background: #7a7a8a;
    }
"""
LIGHT_COLOR_WIDGET_STYLE = """
    QWidget {
        background-color: #d3d3d3;
        color: black;
    }
    QLabel {
        color: black;
        font-family: 'Lexend Deca';
    }
    QSlider::groove:horizontal {
        background: white;
        height: 25px;
        border-radius: 5px;
    }
    QSlider::handle:horizontal {
        background: #5b5b5b;
        width: 15px;
        height: 35px;
        border-radius: 5px;
    }
    QLineEdit {
        background: white;
        border: 1px solid black;
        border-radius: 5px;
        color: black;
        font-family: 'Lexend Deca';
    }
    QPushButton {
        background: white;
        border: 1px solid black;
        border-radius: 5px;
        color: black;
        font-family: 'Lexend Deca';
    }
    QPushButton:hover {
        background: #f0f0f0;
    }
"""
DARK_DIALOG_STYLE = """
    QWidget {
        background-color: #1c1c28;
        color: white;
    }
    QLabel {
        color: white;
        font-family: 'Lexend Deca';
    }
    QSlider::groove:horizontal {
        background: #646478;
        height: 25px;
        border-radius: 5px;
    }
    QSlider::handle:horizontal {
        background: white;
        width: 15px;
        height: 35px;
        border-radius: 5px;
    }
    QLineEdit {
        background: #646478;
        border: 1px solid white;
        border-radius: 5px;
        color: white;
        font-family: 'Lexend Deca';
    }
"""
LIGHT_DIALOG_STYLE = """
    QWidget {
        background-color: #d3d3d3;
        color: black;
    }
    QLabel {
        color: black;
        font-family: 'Lexend Deca';
    }
    QSlider::groove:horizontal {
        background: white;
        height: 25px;
        border-radius: 5px;
    }
    QSlider::handle:horizontal {
        background: #5b5b5b;
        width: 15px;
        height: 35px;
        border-radius: 5px;
    }
    QLineEdit {
        background: white;
        border: 1px solid black;
        border-radius: 5px;
        color: black;
        font-family: 'Lexend Deca';
    }
"""
DARK_COLOR_DIALOG_STYLE = """
    QDialog { 
        background-color: #1c1c28;
        font-family: 'Lexend Deca'; font-size: 17px; color: white;
    }
"""
LIGHT_COLOR_DIALOG_STYLE = """
    QDialog {
        background-color: #d3d3d3;
        font-family: 'Lexend Deca'; font-size: 17px; color: black;
    }
"""
# 🔲 Canvas
CANVSIZE=(1920,1080)
CANVCOLOR=Qt.GlobalColor.white
WARNBFCLEAR=True

# 📆 Font
FONT="Lexend Deca" # won't change the font in menus (sadly)

# 🎹 Default Text Settings
TEXTSIZE=32
TEXTCOLOR="black"
TEXTRANGE=(8,128)
TEXT_BOLD=False
TEXT_ITALIC=False
TEXT_UNDERLINE=False
TEXT_STRIKEOUT=False

# 🧿 Selection
SELCOLOR="#00C0FD"
SELWIDTH=2
SELVCOLOR="#001121"
SELVSIZE=5
SELVWIDTH=8
SELSTYLE=Qt.PenStyle.DashLine

# Drawing
DWIDTHRANGE=(1,150)
# ⚫ Pen
PENCOLOR="black"
PENWIDTH=2
PENCAP=Qt.PenCapStyle.RoundCap
PENJOIN=Qt.PenJoinStyle.RoundJoin
PENSTYLE=Qt.PenStyle.SolidLine
# 🟨 Marker
MARKERCOLOR=(255,255,0,100)
MARKERWIDTH=20
MARKERCAP=Qt.PenCapStyle.FlatCap
MARKERJOIN=Qt.PenJoinStyle.MiterJoin
# 💙 Brush
BRUSHCOLOR="#55aaff"
BRUSHWIDTH=10
BRUSHCAP=Qt.PenCapStyle.RoundCap
BRUSHJOIN=Qt.PenJoinStyle.RoundJoin
# ⚪ Eraser
ERASERCOLOR="white"
ERASERWIDTH=30
ERASERCAP=Qt.PenCapStyle.RoundCap
ERASERJOIN=Qt.PenJoinStyle.RoundJoin

# 🎨 Colors

P1 = (0, 0, 0) # black
P2 = (32, 32, 32) # dark gray
P3 = (64, 64, 64) # gray
P4 = (128, 128, 128) # light gray
P5 = (200, 200, 200) # very light gray
P6 = (255, 255, 255) # white
P7 = (255, 0, 0) # red
P8 = (255, 80, 0) # dark orange
P9 = (255, 165, 0) # orange
P10 = (255, 255, 0) # yellow
P11 = (205, 255, 0) # yellow green
P12 = (0, 255, 0) # vibrant green
P13 = (0, 255, 175) # mint
P14 = (0, 255, 255) # turquoise
P15 = (85, 170, 255) # light blue (is also the brush color)
P16 = (0, 48, 255) # blue
P17 = (90, 0, 255) # purple
P18 = (160, 0, 255) # dark_magenta
P19 = (255, 0, 255) # magenta
P20 = (255, 0, 128) # red pink
P21 = (100, 0, 0) # dark red
P22 = (150, 80, 0) # gold
P23 = (0, 150, 150) # toxic green
P24 = (0, 128, 0) # green
P25 = (0, 128, 80) # cyan
P26 = (0, 90, 128) # jeans blue
P27 = (0, 0, 128) # dark blue
P28 = (30, 128, 0) # dark purple
P29 = (110, 0, 110) # dark pink
P30 = (255, 128, 128) # pastelle red
P31 = (255, 180, 110) # pastelle orange
P32 = (255, 210, 90) # pastelle yellow
P33 = (220, 225, 128) # pastelle yellow green
P34 = (160, 255, 128) # pastelle green
P35 = (150, 255, 255) # pastelle blue
P36 = (128, 150, 255) # lavendar
P37 = (210, 128, 255) # pastelle pink
P38 = (255, 128, 240) # rosé pink
P39 = (255, 128, 180) # pastelle red pink
P40 = (255, 210, 170) # light skin color
P41 = (128, 70, 35) # latino skin color
P42 = (50, 30, 20) # dark desaturated brown





