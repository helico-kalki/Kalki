import sys
from PyQt6.QtWidgets import (
    QColorDialog, QCheckBox, QButtonGroup, QWidgetAction, QSpacerItem, QSizePolicy, QFontComboBox, QFrame,
    QSlider, QMenu, QToolBar, QToolButton, QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit, QDialog, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QIcon, QColor, QFont, QPalette, QAction, QIntValidator, QActionGroup, QPixmap, QMouseEvent
from PyQt6.QtCore import QSize, Qt
from PIL import ImageFilter, ImageEnhance, ImageQt
from config import *
from canvas import Canvas
from color_picker_widget import ColorPickerWidget

app = QApplication(sys.argv)

class MainWindow(QMainWindow):
    def closeEvent(self, event):
        if WARNBFCLOSE==True:
            reply = QMessageBox.warning(
                self,
                "Proceed to close Kalki",
                "Your canvas will be lost, if not saved. Do you want to proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            elif reply == QMessageBox.StandardButton.Save:
                save_file_dialog(window)
        else:
            event.accept()
    


window = MainWindow()
window.setGeometry(*WINSIZE)
window.setWindowTitle(WINTITLE)
window.setWindowIcon(QIcon(WINICON))
dark_mode = False

w_palette = window.palette()
w_palette.setColor(QPalette.ColorRole.Window, QColor(WINCOLOR))
window.setPalette(w_palette)
window.setAutoFillBackground(True)

top_toolbar = QToolBar()
top_toolbar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
top_toolbar.setStyleSheet("""
    QToolBar { 
        border: none; background: transparent; 
    }
    QToolBar QToolButton:checked {
        background-color: transparent;
        border: none;
    }
    QToolBar QToolButton:hover {
        background-color: transparent;
    }
    QToolBar QToolButton:pressed {
        background-color: transparent;
    }
""")
top_toolbar.setCursor(Qt.CursorShape.PointingHandCursor)

new_action = QAction(QIcon("colored_textures/new.png"), "New Project / Clear Canvas", window)
new_action.triggered.connect(lambda: clear_canvas())
new_action.setShortcut(CLEAR_CANV)

import_action = QAction(QIcon("colored_textures/import.png"), "Import Project", window)
import_action.triggered.connect(lambda: open_file_dialog(window))
import_action.setShortcut(IMP)

export_action = QAction(QIcon("colored_textures/export.png"), "Export Project", window)
export_action.triggered.connect(lambda: save_file_dialog(window))
export_action.setShortcut(EXP)

window.addToolBar(Qt.ToolBarArea.TopToolBarArea, top_toolbar)

central_widget = QWidget()
central_layout = QVBoxLayout()
central_widget.setLayout(central_layout)
window.setCentralWidget(central_widget)

canvas = Canvas()
canvas.setStyleSheet(f"background-color: {LIGHTCOLOR}")
canvas.setFixedSize(1900, 900)

resize_canvas_action = QAction(QIcon("colored_textures/resize_canvas.png"), "Resize Canvas", window)
resize_canvas_action.triggered.connect(canvas.resize_canvas)
resize_canvas_action.setShortcut(RESIZE)

undo_action = QAction(QIcon("colored_textures/undo.png"), "Undo", window)
undo_action.triggered.connect(canvas.undo)
undo_action.setShortcut(UNDO)

redo_action = QAction(QIcon("colored_textures/redo.png"), "Redo", window)
redo_action.triggered.connect(canvas.redo)
redo_action.setShortcut(REDO)

zoom_in = QAction(QIcon("colored_textures/zoom_in.png"), "Zoom In", window)
zoom_in.triggered.connect(lambda: canvas.zoom_in_at_point())
zoom_in.setShortcut(ZOOM_IN)

zoom_out = QAction(QIcon("colored_textures/zoom_out.png"), "Zoom Out", window)
zoom_out.triggered.connect(lambda: canvas.zoom_out_at_point())
zoom_out.setShortcut(ZOOM_OUT)

copy_selection = QAction(QIcon("colored_textures/copy.png"), "Copy", window)
copy_selection.triggered.connect(canvas.copy_selection)
copy_selection.setShortcut(COPY)

paste_selection = QAction(QIcon("colored_textures/paste.png"), "Paste", window)
paste_selection.triggered.connect(canvas.paste_selection)
paste_selection.setShortcut(PASTE)

rotate_90_cw_action = QAction(QIcon("colored_textures/rotate_90_cw.png"), "Rotate 90 degrees clockwise", window)
rotate_90_cw_action.triggered.connect(canvas.rotate_90_cw)
rotate_90_cw_action.setShortcut(ROTATE90_CW)

rotate_90_ccw_action = QAction(QIcon("colored_textures/rotate_90_ccw.png"), "Rotate 90 degrees counterclockwise", window)
rotate_90_ccw_action.triggered.connect(canvas.rotate_90_ccw)
rotate_90_ccw_action.setShortcut(ROTATE90_CCW)

mirror_horizontal_action = QAction(QIcon("colored_textures/mirror_horizontal.png"), "Mirror horizontally", window)
mirror_horizontal_action.triggered.connect(canvas.mirror_horizontal)
mirror_horizontal_action.setShortcut(MIRROR_H)

mirror_vertical_action = QAction(QIcon("colored_textures/mirror_vertical.png"), "Mirror vertically", window)
mirror_vertical_action.triggered.connect(canvas.mirror_vertical)
mirror_vertical_action.setShortcut(MIRROR_V)

crop_selection_action = QAction(QIcon("colored_textures/crop_selection.png"), "Crop Image to Selection", window)
crop_selection_action.triggered.connect(canvas.crop_to_selection)
crop_selection_action.setShortcut(CROPTOSEL)

effects_action = QAction(window)
effects_action.setIcon(QIcon("colored_textures/effects.png"))
effects_action.setText("Effects")
effects_menu = QMenu()

ca_action = QAction(QIcon("colored_textures/ca.png"), "Combined Adjustments", window)
ca_action.triggered.connect(lambda: open_combined_adjustments(canvas))
ca_action.setShortcut(CA)

blur_action = QAction(QIcon("colored_textures/blur.png"), "Gaussian Blur", window)
blur_action.triggered.connect(lambda: open_blur_options())
blur_action.setShortcut(GB)

contour_action = QAction(QIcon("colored_textures/contour.png"), "Contour", window)
contour_action.triggered.connect(canvas.apply_contour)
contour_action.setShortcut(CONTOUR)

detail_action = QAction(QIcon("colored_textures/detail.png"), "Detail", window)
detail_action.triggered.connect(canvas.apply_detail)
detail_action.setShortcut(DETAIL)

emboss_action = QAction(QIcon("colored_textures/emboss.png"), "Emboss", window)
emboss_action.triggered.connect(canvas.apply_emboss)
emboss_action.setShortcut(EMBOSS)

edge_enhance_action = QAction(QIcon("colored_textures/edge_enhance.png"), "Edge Enhance", window)
edge_enhance_action.triggered.connect(canvas.apply_find_edges)
edge_enhance_action.setShortcut(EDGEENHANCE)

smooth_action = QAction(QIcon("colored_textures/smooth.png"), "Smooth", window)
smooth_action.triggered.connect(canvas.apply_smooth)
smooth_action.setShortcut(SMOOTH)

smooth_more_action = QAction(QIcon("colored_textures/smooth_more.png"), "Smooth More", window)
smooth_more_action.triggered.connect(canvas.apply_smooth_more)
smooth_more_action.setShortcut(SMOOTHMORE)

unsharp_mask_action = QAction(QIcon("colored_textures/unsharp_mask.png"), "Unsharp Mask", window)
unsharp_mask_action.triggered.connect(lambda: open_unsharp_mask_options())
unsharp_mask_action.setShortcut(UNSHARP)

find_edges_action = QAction(QIcon("colored_textures/find_edges.png"), "Find Edges", window)
find_edges_action.triggered.connect(canvas.apply_find_edges)
find_edges_action.setShortcut(FINDEDGES)

sharpen_action = QAction(QIcon("colored_textures/sharpen.png"), "Sharpen", window)
sharpen_action.triggered.connect(canvas.apply_sharpen)
sharpen_action.setShortcut(SHARPEN)

invert_action = QAction(QIcon("colored_textures/invert.png"), "Invert Colors", window)
invert_action.triggered.connect(canvas.invert_colors)
invert_action.setShortcut(INVERT)

temperature_action = QAction(QIcon("colored_textures/temperature.png"), "Temperature", window)
temperature_action.triggered.connect(lambda: open_temperature_options(canvas))
temperature_action.setShortcut(TEMPERATURE)

effects_action.setMenu(effects_menu)
effects_menu.setStyleSheet(LIGHT_MENU_STYLE)
effects_menu.addAction(ca_action)
effects_menu.addAction(temperature_action)
effects_menu.addAction(blur_action)
effects_menu.addAction(smooth_action)
effects_menu.addAction(smooth_more_action)
effects_menu.addAction(unsharp_mask_action)
effects_menu.addAction(sharpen_action)
effects_menu.addAction(contour_action)
effects_menu.addAction(find_edges_action)
effects_menu.addAction(edge_enhance_action)
effects_menu.addAction(emboss_action)
effects_menu.addAction(detail_action)
effects_menu.addAction(invert_action)

dark_mode_action = QAction(QIcon("dark_textures/dark_mode.png"), "Dark Mode / Light Mode", window)
dark_mode_action.setCheckable(True)
def toggle_dark_mode_handler(checked):
    global dark_mode
    toggle_dark_mode(checked)
    dark_mode = checked
    dark_mode_action.setIcon(
        QIcon("colored_textures/light_mode.png") if checked else QIcon("dark_textures/dark_mode.png")
    )
dark_mode_action.triggered.connect(toggle_dark_mode_handler)
dark_mode_action.setShortcut(DARKMODE_SHORTCUT)

top_toolbar.addAction(new_action)
top_toolbar.addAction(import_action)
top_toolbar.addAction(export_action)
top_toolbar.addAction(undo_action)
top_toolbar.addAction(redo_action)
top_toolbar.addAction(copy_selection)
top_toolbar.addAction(paste_selection)
top_toolbar.addAction(zoom_in)
top_toolbar.addAction(zoom_out)
top_toolbar.addAction(resize_canvas_action)
top_toolbar.addAction(crop_selection_action)
top_toolbar.addAction(rotate_90_cw_action)
top_toolbar.addAction(rotate_90_ccw_action)
top_toolbar.addAction(mirror_horizontal_action)
top_toolbar.addAction(mirror_vertical_action)
top_toolbar.addAction(effects_action)
top_toolbar.addAction(dark_mode_action)

bottom_toolbar = QFrame()
bottom_toolbar.setStyleSheet("background-color: #ffffff; border-radius: 50px;")
bottom_toolbar.setFixedHeight(100)
bottom_layout = QHBoxLayout()
bottom_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
bottom_toolbar.setLayout(bottom_layout)

move_button = QToolButton()
move_button.setIcon(QIcon("colored_textures/move.png"))
move_button.setIconSize(QSize(45,45))
move_button.setStyleSheet("border: none; background: transparent;")
move_button.setCursor(Qt.CursorShape.PointingHandCursor)
move_button.setCheckable(True)
def on_move_button_toggled(checked):
    if checked:
        canvas.enable_move_selection()
    else:
        canvas.disable_move_mode()
move_button.clicked.connect(on_move_button_toggled)
move_button.setShortcut(MOVE)

selection_button = QToolButton()
selection_button.setIcon(QIcon("colored_textures/selection.png"))
selection_button.setIconSize(QSize(45,45))
selection_button.setCursor(Qt.CursorShape.PointingHandCursor)
selection_button.setStyleSheet(TOOL_BUTTON_STYLE)
selection_button.setCheckable(False)
selection_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)  
selection_menu = QMenu()
selection_button.setMenu(selection_menu)
selection_menu.setStyleSheet(LIGHT_MENU_STYLE)
selection_group = QActionGroup(window)
selection_group.setExclusive(True)

def update_selection_mode(mode):
    canvas.set_selection_mode(mode)
    if mode == "rect":
        selection_button.setIcon(QIcon("colored_textures/rectangular_selection.png"))
    elif mode == "ellipse":
        selection_button.setIcon(QIcon("colored_textures/circular_selection.png"))
    elif mode == "lasso":
        selection_button.setIcon(QIcon("colored_textures/lasso_selection.png"))
    elif mode is None:
        selection_button.setIcon(QIcon("colored_textures/selection.png"))

rselect_button = QAction(QIcon("colored_textures/rectangular_selection.png"), " Rectangular", window)
rselect_button.setCheckable(True)
rselect_button.triggered.connect(lambda checked: update_selection_mode("rect") if checked else update_selection_mode(None))
rselect_button.setShortcut(RSEL)

cselect_button = QAction(QIcon("colored_textures/circular_selection.png"), " Circular", window)
cselect_button.setCheckable(True)
cselect_button.triggered.connect(lambda checked: update_selection_mode("ellipse") if checked else update_selection_mode(None))
cselect_button.setShortcut(CSEL)

lselect_button = QAction(QIcon("colored_textures/lasso_selection.png"), " Lasso", window)
lselect_button.setCheckable(True)
lselect_button.triggered.connect(lambda checked: update_selection_mode("lasso") if checked else update_selection_mode(None))
lselect_button.setShortcut(LSEL)

clearsel_button = QAction(QIcon("colored_textures/clear_selection.png"), " Clear Selection", window)
clearsel_button.setCheckable(False)
clearsel_button.triggered.connect(lambda: update_selection_mode(None))
clearsel_button.setShortcut(DELSEL)

selection_group.addAction(rselect_button)
selection_group.addAction(cselect_button)
selection_group.addAction(lselect_button)
selection_group.addAction(clearsel_button)

selection_menu.addAction(rselect_button)
selection_menu.addAction(cselect_button)
selection_menu.addAction(lselect_button)
selection_menu.addAction(clearsel_button)

shapes = QToolButton(window)
shapes.setIcon(QIcon("colored_textures/shapes.png"))
shapes.setIconSize(QSize(45,45))
shapes.setCursor(Qt.CursorShape.PointingHandCursor)
shapes.setStyleSheet(TOOL_BUTTON_STYLE)
shapes.setCheckable(False)
shapes_menu = QMenu()
shapes.setMenu(shapes_menu)
shapes.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)  
shapes_group = QActionGroup(window)
shapes_group.setExclusive(True)

def update_shape_mode(mode):
        canvas.set_shape_mode(mode)
        if mode == "rect":
            shapes.setIcon(QIcon("colored_textures/rectangle.png"))
        elif mode == "ellipse":
            shapes.setIcon(QIcon("colored_textures/ellipse.png"))
        elif mode == "triangle":
            shapes.setIcon(QIcon("colored_textures/triangle.png"))
        elif mode == "line":
            shapes.setIcon(QIcon("colored_textures/lines.png"))
        elif mode is None:
            shapes.setIcon(QIcon("colored_textures/shapes.png"))

rectangle = QAction(QIcon("colored_textures/rectangle.png"), " Rectangle", window)
rectangle.setCheckable(True)
rectangle.triggered.connect(lambda checked: update_shape_mode("rect") if checked else update_shape_mode(None))
rectangle.setShortcut(RECT)

ellipse = QAction(QIcon("colored_textures/ellipse.png"), " Ellipse", window)
ellipse.setCheckable(True)
ellipse.triggered.connect(lambda checked: update_shape_mode("ellipse") if checked else update_shape_mode(None))
ellipse.setShortcut(ELLIPSE)

triangle = QAction(QIcon("colored_textures/triangle.png"), " Triangle", window)
triangle.setCheckable(True)
triangle.triggered.connect(lambda checked: update_shape_mode("triangle") if checked else update_shape_mode(None))
triangle.setShortcut(TRIANGLE)

lines = QAction(QIcon("colored_textures/lines.png"), " Lines", window)
lines.setCheckable(True)
lines.triggered.connect(lambda checked: update_shape_mode("line") if checked else update_shape_mode(None))
lines.setShortcut(LINES)

disableshape = QAction(QIcon("colored_textures/disableshape.png"), " Disable", window)
disableshape.setCheckable(True)
disableshape.triggered.connect(lambda checked: update_shape_mode(None) if checked else update_shape_mode(None))
disableshape.setShortcut(DISABLESHAPE)

shapes_group.addAction(rectangle)
shapes_group.addAction(triangle)
shapes_group.addAction(ellipse)
shapes_group.addAction(lines)
shapes_group.addAction(disableshape)

shapes_menu.setStyleSheet(LIGHT_MENU_STYLE)


shapes_menu.addAction(rectangle)
shapes_menu.addAction(triangle)
shapes_menu.addAction(ellipse)
shapes_menu.addAction(lines)
shapes_menu.addAction(disableshape)

t_menu = QMenu()
t_menu.setStyleSheet(LIGHT_MENU_STYLE)

t_button = QToolButton()
t_button.setIcon(QIcon("colored_textures/text.png"))
t_button.setIconSize(QSize(45,45))
t_button.setCursor(Qt.CursorShape.PointingHandCursor)
t_button.setStyleSheet(TOOL_BUTTON_STYLE)
t_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
t_button.setShortcut(TEXT)

t_widget = QWidget()
t_luni = QHBoxLayout(t_widget)
t_ldef = QVBoxLayout()
t_lmain = QVBoxLayout()
t_luni.addLayout(t_ldef)
t_luni.addLayout(t_lmain)
t_lopt = QHBoxLayout()
t_lsize = QHBoxLayout()

t_pre0 = QToolButton()
t_pre0.setText("L")
t_pre0.setStyleSheet("border: transparent; background: white; border-radius: 5px; font-family: 'Lexend Deca'; font-size: 25px; height: 35px; width: 35px")
t_pre1 = QToolButton()
t_pre1.setText("I")
t_pre1.setStyleSheet("border: transparent; background: white; border-radius: 5px; font-family: 'Inter Medium'; font-size: 20px; height: 35px; width: 35px")
t_pre2 = QToolButton()
t_pre2.setText("k")
t_pre2.setStyleSheet("border: transparent; background: white; border-radius: 5px; font-family: 'Wurper Regular'; font-size: 20px; color: red; height: 35px; width: 35px")
t_pre3 = QToolButton()
t_pre3.setText("C")
t_pre3.setStyleSheet("border: transparent; background: white; border-radius: 5px; font-family: 'Consolas'; font-size: 20px; height: 35px; width: 35px")
t_ldef.addWidget(t_pre0)
t_ldef.addWidget(t_pre1)
t_ldef.addWidget(t_pre2)
t_ldef.addWidget(t_pre3)

t_text = QLineEdit(canvas.text_options["text"])
t_text.setStyleSheet("border: transparent; background: white; border-radius: 5px; height: 50px; font-family: 'Lexend Deca'; font-size: 15px;")
t_lmain.addWidget(t_text)

t_font = QFontComboBox()
t_font.setCurrentFont(canvas.text_options["font"])
t_font.setStyleSheet(LIGHT_FONT_COMBO_STYLE)
t_lmain.addWidget(t_font)

t_slider = QSlider(Qt.Orientation.Horizontal)
t_slider.setRange(*TEXTRANGE)
t_slider.setValue(canvas.text_options["size"])
t_slider.setStyleSheet(LIGHT_SLIDER_STYLE2)
t_size = QLineEdit(str(canvas.text_options["size"]))
t_size.setStyleSheet("border: transparent; background: transparent; font-family: 'Lexend Deca'; font-size: 15px;")
t_size.setFixedWidth(40)
t_size.setValidator(QIntValidator(*TEXTRANGE))
t_slider.valueChanged.connect(lambda v: t_size.setText(str(v)))
t_size.textChanged.connect(lambda t: t_slider.setValue(int(t) if t.isdigit() else 32))
t_lsize.addWidget(t_slider)
t_lsize.addWidget(t_size)


t_bold = QToolButton()
t_bold.setText("B")
t_bold.setCheckable(True)
t_bold.setFont(QFont(FONT, 20))
t_bold.setStyleSheet(LIGHT_TEXT_TOOL_BUTTON_STYLE)
t_bold.setChecked(canvas.text_options["bold"])

t_italic = QToolButton()
t_italic.setText("I")
t_italic.setCheckable(True)
t_italic.setFont(QFont(FONT, 20))
t_italic.setStyleSheet(LIGHT_TEXT_TOOL_BUTTON_STYLE)
t_italic.setChecked(canvas.text_options["italic"])

t_underline = QToolButton()
t_underline.setText("U")
t_underline.setCheckable(True)
t_underline.setFont(QFont(FONT, 20))
t_underline.setStyleSheet(LIGHT_TEXT_TOOL_BUTTON_STYLE)
t_underline.setChecked(canvas.text_options["underline"])

t_strike = QToolButton()
t_strike.setText("S")
t_strike.setCheckable(True)
t_strike.setFont(QFont(FONT, 20))
t_strike.setStyleSheet(LIGHT_TEXT_TOOL_BUTTON_STYLE)
t_strike.setChecked(canvas.text_options["strikeout"])

t_color = QPushButton()
t_color.setFixedSize(30, 30)
t_color.setStyleSheet(f"background: {canvas.text_options['color'].name()}; border: 2px solid black; border-radius: 15px;")
def pick_text_color():
    dialog = QDialog(window)
    dialog.setWindowTitle("Text Color Picker")
    if dark_mode == True:
        dialog.setWindowIcon(QIcon("dark_textures/colorwheel.png"))
    else:
        dialog.setWindowIcon(QIcon("colored_textures/colorwheel.png"))
    dialog.setFixedSize(550, 320)
    if dark_mode == True:
        dialog.setStyleSheet(DARK_COLOR_DIALOG_STYLE)
    else:
        dialog.setStyleSheet(LIGHT_COLOR_DIALOG_STYLE)
    layout = QVBoxLayout(dialog)

    color_picker_widget = ColorPickerWidget(canvas)
    color_picker_widget.colorChanged.connect(canvas.set_pen_color)
    color_picker_widget.set_color(canvas.text_options["color"])
    if dark_mode == True:
        color_picker_widget.setStyleSheet(DARK_COLOR_WIDGET_STYLE)
    else:
        color_picker_widget.setStyleSheet(LIGHT_COLOR_WIDGET_STYLE)
    layout.addWidget(color_picker_widget)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    ok_button.setStyleSheet(CONFIRM_BUTTON_STYLE)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(CANCEL_BUTTON_STYLE)
    
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    layout.addLayout(button_layout)

    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        selected_color = color_picker_widget.color
        if dark_mode == True:
            t_color.setStyleSheet(f"background: {selected_color.name()}; border: 2px solid white; border-radius: 15px;")
        else:
            t_color.setStyleSheet(f"background: {selected_color.name()}; border: 2px solid black; border-radius: 15px;")
        t_color.setProperty("picked_color", selected_color)
        canvas.set_pen_color(selected_color)
t_color.clicked.connect(pick_text_color)

def update_text_color_from_pen(color: QColor):
    t_color.setStyleSheet(f"background: {color.name()}; border: 2px solid black; border-radius: 15px;")
    t_color.setProperty("picked_color", color)
    canvas.text_options["color"] = color

canvas.pen_color_changed.connect(update_text_color_from_pen)

t_lopt.addWidget(t_bold)
t_lopt.addWidget(t_italic)
t_lopt.addWidget(t_underline)
t_lopt.addWidget(t_strike)
t_lopt.addWidget(t_color)

t_apply = QPushButton("Apply")
t_apply.setStyleSheet(CONFIRM_BUTTON_STYLE)
def apply_text_options():
    options = {
        "text": t_text.text(),
        "font": t_font.currentFont(),
        "size": int(t_size.text()),
        "color": t_color.property("picked_color") if t_color.property("picked_color") else canvas.text_options["color"],
        "bold": t_bold.isChecked(),
        "italic": t_italic.isChecked(),
        "underline": t_underline.isChecked(),
        "strikeout": t_strike.isChecked()
    }
    canvas.set_text_options(options)
t_apply.clicked.connect(apply_text_options)
t_apply.clicked.connect(lambda: canvas.set_text_mode(True))

t_lmain.addLayout(t_lsize)
t_lmain.addLayout(t_lopt)
t_lmain.addWidget(t_apply)
t_action = QWidgetAction(t_menu)
t_action.setDefaultWidget(t_widget)
t_menu.addAction(t_action)
t_button.setMenu(t_menu)

d_menu = QMenu()
d_menu.setStyleSheet(LIGHT_MENU_STYLE)

d_button= QToolButton()
d_button.setIcon(QIcon("colored_textures/draw.png"))
d_button.setIconSize(QSize(45,45))
d_button.setCursor(Qt.CursorShape.PointingHandCursor)
d_button.setStyleSheet(TOOL_BUTTON_STYLE)
d_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
d_button.setShortcut(DRAW)

d_widget = QWidget()
d_uni_layout = QHBoxLayout(d_widget)
d_main_layout = QVBoxLayout()
d_def_layout = QVBoxLayout()
d_slider_layout = QHBoxLayout()
d_opt_layout = QHBoxLayout()
d_opt2_layout = QHBoxLayout()
spacer1 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
d_uni_layout.addLayout(d_def_layout)
d_uni_layout.addSpacerItem(spacer1)
d_uni_layout.addLayout(d_main_layout)

d_pen = QToolButton()
d_pen.setIcon(QIcon("colored_textures/pen.png"))
d_pen.setIconSize(QSize(35,35))
d_pen.setStyleSheet(STDSTYLE)
d_pen.setCheckable(False)
def activate_pen_tool():
    canvas.set_pen_color(QColor(PENCOLOR))
    canvas.set_pen_width(PENWIDTH)
    canvas.set_pen_line_style(PENSTYLE),
    canvas.set_pen_cap_style(PENCAP),
    canvas.set_pen_join_style(PENJOIN)
    canvas.set_brush_active(False)
    canvas.drawing = False
d_pen.clicked.connect(activate_pen_tool)          
d_pen.clicked.connect(lambda: [
    d_width_slider.setValue(PENWIDTH),
    d_width_text.setText(str(PENWIDTH))
])
d_pen.setShortcut(PEN)
d_def_layout.addWidget(d_pen)

d_marker = QToolButton()
d_marker.setIcon(QIcon("colored_textures/marker.png"))
d_marker.setIconSize(QSize(35,35))
d_marker.setStyleSheet(STDSTYLE)
d_marker.setCheckable(False)
def use_marker_tool():
    canvas.set_pen_color(QColor(*MARKERCOLOR))
    canvas.set_pen_width(MARKERWIDTH)
    canvas.set_pen_cap_style(MARKERCAP),
    canvas.set_pen_join_style(MARKERJOIN)
    canvas.set_brush_active(False)
d_marker.clicked.connect(use_marker_tool)
d_marker.clicked.connect(lambda: [
    d_width_slider.setValue(MARKERWIDTH),
    d_width_text.setText(str(MARKERWIDTH))
])
d_marker.setShortcut(MARKER)
d_def_layout.addWidget(d_marker)

d_brush = QToolButton()
d_brush.setIcon(QIcon("colored_textures/brush.png"))
d_brush.setIconSize(QSize(35,35))
d_brush.setStyleSheet(STDSTYLE)
d_brush.setCheckable(False)
def use_brush_tool():
        canvas.set_pen_color(QColor(BRUSHCOLOR))
        canvas.set_pen_width(BRUSHWIDTH)
        canvas.set_pen_cap_style(BRUSHCAP)
        canvas.set_pen_join_style(BRUSHJOIN)
        canvas.set_brush_active(True)
d_brush.clicked.connect(use_brush_tool)
d_brush.clicked.connect(lambda: [
    d_width_slider.setValue(BRUSHWIDTH),
    d_width_text.setText(str(BRUSHWIDTH))
])
d_brush.setShortcut(BRUSH)
d_def_layout.addWidget(d_brush)

d_eraser = QToolButton()
d_eraser.setIcon(QIcon("colored_textures/eraser.png"))
d_eraser.setIconSize(QSize(35,35))
d_eraser.setStyleSheet(STDSTYLE)
d_eraser.setCheckable(True)
def use_erase_tool():
    canvas.set_pen_color(QColor(ERASERCOLOR))
    canvas.set_pen_width(ERASERWIDTH)
    canvas.set_pen_cap_style(ERASERCAP),
    canvas.set_pen_join_style(ERASERJOIN)
d_eraser.clicked.connect(use_erase_tool)
d_eraser.clicked.connect(lambda: [
    d_width_slider.setValue(ERASERWIDTH),
    d_width_text.setText(str(ERASERWIDTH))
])
d_eraser.setShortcut(ERASER)
d_def_layout.addWidget(d_eraser)

d_width_text = QLineEdit()
d_width_text.setText(str(PENWIDTH))
d_width_text.setFixedSize(35,35)
d_width_text.setStyleSheet(STDSTYLE)
d_width_text.setFont(QFont(FONT, 15))
d_width_text.setValidator(QIntValidator(*DWIDTHRANGE))
def update_draw_width_from_text(text):
    if not text.isdigit():
        return  
    value = int(text)
    canvas.set_pen_width(value)
    d_width_slider.setValue(value)
d_width_text.textChanged.connect(update_draw_width_from_text)
d_slider_layout.addWidget(d_width_text)

d_width_slider = QSlider(Qt.Orientation.Horizontal)
d_width_slider.setRange(*DWIDTHRANGE)
d_width_slider.setValue(PENWIDTH)
d_width_slider.setStyleSheet(LIGHT_SLIDER_STYLE2)
d_width_slider.setSliderDown(True)
d_width_slider.valueChanged.connect(lambda value: [
    canvas.set_pen_width(value),
    d_width_text.setText(str(value))
    ])
d_slider_layout.addWidget(d_width_slider)

d_color = QPushButton()
d_color.setFixedSize(175, 30)
d_color.setStyleSheet(f"background: {canvas.pen_color.name()}; border: transparent; border-radius: 15px;")
def pick_color():
    dialog = QDialog(window)
    dialog.setWindowTitle("Color Picker")
    dialog.setFixedSize(550, 320)
    dialog.setWindowIcon(QIcon("colored_textures/colorwheel.png"))
    if dark_mode == True:
        dialog.setStyleSheet(DARK_COLOR_DIALOG_STYLE)
    else:
        dialog.setStyleSheet(LIGHT_COLOR_DIALOG_STYLE)
    
    layout = QVBoxLayout(dialog)

    color_picker_widget = ColorPickerWidget(canvas)
    color_picker_widget.set_color(canvas.pen_color)
    color_picker_widget.colorChanged.connect(canvas.set_pen_color)
    if dark_mode == True:
        color_picker_widget.setStyleSheet(DARK_COLOR_WIDGET_STYLE)
    else:
        color_picker_widget.setStyleSheet(LIGHT_COLOR_WIDGET_STYLE)
    layout.addWidget(color_picker_widget)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    ok_button.setStyleSheet(CONFIRM_BUTTON_STYLE)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(CANCEL_BUTTON_STYLE)
    
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    layout.addLayout(button_layout)

    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        selected_color = color_picker_widget.color
        if dark_mode == True:
            d_color.setStyleSheet(f"background: {selected_color.name()}; border: 2px solid white; border-radius: 15px;")
        else:
            d_color.setStyleSheet(f"background: {selected_color.name()}; border: 2px solid black; border-radius: 15px;")
        d_color.setProperty("picked_color", selected_color)
        canvas.set_pen_color(selected_color)
d_color.clicked.connect(pick_color)

def update_color_buttons(color: QColor):
    if dark_mode == True:
        t_color.setStyleSheet(f"background: {color.name()}; border: 2px solid white; border-radius: 15px;")
    else:
        t_color.setStyleSheet(f"background: {color.name()}; border: 2px solid black; border-radius: 15px;")
    if dark_mode == True:
        d_color.setStyleSheet(f"background: {color.name()}; border: 2px solid white; border-radius: 15px;")
    else:
        d_color.setStyleSheet(f"background: {color.name()}; border: 2px solid black; border-radius: 15px;")
    if dark_mode == True:
        color_wheel.setStyleSheet(f"""
            background: {color.name()}; 
            border: 2px solid white; 
            border-radius: 22px;
            QToolButton::menu-indicator {{
                image: none;
                width: 0px;
                height: 0px;
            }}
        """)
    else:
        color_wheel.setStyleSheet(f"""
            background: {color.name()}; 
            border: 2px solid black; 
            border-radius: 22px;
            QToolButton::menu-indicator {{
                image: none;
                width: 0px;
                height: 0px;
            }}
        """)
canvas.pen_color_changed.connect(update_color_buttons)

d_round = QToolButton()
d_round.setIcon(QIcon("colored_textures/round.png"))
d_round.setIconSize(QSize(35,35))
d_round.setCheckable(True)
d_round.setChecked(True)
d_round.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
d_round.toggled.connect(lambda checked: [
    canvas.set_pen_cap_style(Qt.PenCapStyle.RoundCap) if checked else None,
    canvas.set_pen_join_style(Qt.PenJoinStyle.RoundJoin) if checked else None
])
d_opt_layout.addWidget(d_round)

def update_d_style():
    is_round = (
        canvas.pen_cap == Qt.PenCapStyle.RoundCap and
        canvas.pen_join == Qt.PenJoinStyle.RoundJoin
    )
    is_flat = (
        canvas.pen_cap == Qt.PenCapStyle.FlatCap and
        canvas.pen_join == Qt.PenJoinStyle.MiterJoin
    )
    d_round.setChecked(is_round)
    d_flat.setChecked(is_flat)
canvas.pen_style_changed.connect(update_d_style)

d_flat = QToolButton()
d_flat.setIcon(QIcon("colored_textures/flat.png"))
d_flat.setIconSize(QSize(35,35))
d_flat.setCheckable(True)
d_flat.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
d_flat.toggled.connect(lambda checked: [
    canvas.set_pen_cap_style(Qt.PenCapStyle.FlatCap) if checked else canvas.set_pen_cap_style(Qt.PenCapStyle.RoundCap),
    canvas.set_pen_join_style(Qt.PenJoinStyle.MiterJoin) if checked else canvas.set_pen_join_style(Qt.PenJoinStyle.RoundJoin)
])
d_opt_layout.addWidget(d_flat)


d_dynamic = QToolButton()
d_dynamic.setIcon(QIcon("colored_textures/dynamic.png"))
d_dynamic.setIconSize(QSize(35,35))
d_dynamic.setCheckable(True)
d_dynamic.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
d_dynamic.setChecked(canvas.brush_active)
d_dynamic.toggled.connect(lambda checked: canvas.set_brush_active(checked))

def update_brush_button(active: bool):
    d_dynamic.setChecked(active)
canvas.brush_active_changed.connect(update_brush_button)
d_opt_layout.addWidget(d_dynamic)

d_cj_group = QButtonGroup(d_menu)
d_cj_group.setExclusive(True)
d_cj_group.addButton(d_round)
d_cj_group.addButton(d_flat)
d_cj_group.addButton(d_dynamic)

'''
d_solid = QToolButton()
d_solid.setIcon(QIcon("colored_textures/solid.png"))
d_solid.setIconSize(QSize(35,35))
d_solid.setCheckable(True)
d_solid.setChecked(True)
d_solid.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
d_solid.toggled.connect(lambda checked: canvas.set_pen_line_style(Qt.PenStyle.SolidLine) if checked else None)
d_opt2_layout.addWidget(d_solid)

d_dash = QToolButton()
d_dash.setIcon(QIcon("colored_textures/dash.png"))
d_dash.setIconSize(QSize(35,35))
d_dash.setCheckable(True)
d_dash.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
d_dash.toggled.connect(lambda checked: (
    canvas.set_pen_line_style(Qt.PenStyle.CustomDashLine) if checked else canvas.set_pen_line_style(Qt.PenStyle.SolidLine),
    canvas.set_dash_pattern([1, 1, 1, 1]) if checked else canvas.set_dash_pattern([])
))
d_opt2_layout.addWidget(d_dash)

d_dot = QToolButton()
d_dot.setIcon(QIcon("colored_textures/dot.png"))
d_dot.setIconSize(QSize(35,35))
d_dot.setCheckable(True)
d_dot.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
d_dot.toggled.connect(lambda checked: canvas.set_pen_line_style(Qt.PenStyle.DotLine) if checked else canvas.set_pen_line_style(Qt.PenStyle.SolidLine))
d_opt2_layout.addWidget(d_dot)
'''
d_main_layout.addWidget(d_color)
d_main_layout.addLayout(d_slider_layout)
d_main_layout.addLayout(d_opt_layout)
#d_main_layout.addLayout(d_opt2_layout)

d_style_group = QButtonGroup(d_menu)
d_style_group.setExclusive(True)
#d_style_group.addButton(d_solid)
#d_style_group.addButton(d_dash)
#d_style_group.addButton(d_dot)

d_action = QWidgetAction(d_menu)
d_action.setDefaultWidget(d_widget)
d_menu.addAction(d_action)
d_button.setMenu(d_menu)

color_bucket = QToolButton()
color_bucket.setIcon(QIcon("colored_textures/bucket.png"))
color_bucket.setIconSize(QSize(45,45))
color_bucket.setCursor(Qt.CursorShape.PointingHandCursor)
color_bucket.setStyleSheet(STDSTYLE)
color_bucket.clicked.connect(lambda: [
    canvas.fill_selection(canvas.pen_color)
])
color_bucket.setShortcut(BUCKET)

gradient = QToolButton()
gradient.setIcon(QIcon("colored_textures/gradient.png"))
gradient.setIconSize(QSize(45,45))
gradient.setCursor(Qt.CursorShape.PointingHandCursor)
gradient.setStyleSheet(STDSTYLE)
def use_gradient():
    dialog1 = QDialog(window)
    dialog1.setWindowTitle("Pick Color 1 (Left)")
    dialog1.setFixedSize(550, 320)
    if dark_mode == True:
        dialog1.setWindowIcon(QIcon("dark_textures/colorwheel.png"))
    else:
        dialog1.setWindowIcon(QIcon("colored_textures/colorwheel.png"))
    if dark_mode == True:
        dialog1.setStyleSheet(DARK_COLOR_DIALOG_STYLE)
    else:
        dialog1.setStyleSheet(LIGHT_COLOR_DIALOG_STYLE)
    
    layout1 = QVBoxLayout(dialog1)

    color_picker_widget1 = ColorPickerWidget(canvas)
    color_picker_widget1.set_color(canvas.pen_color)
    if dark_mode == True:
        color_picker_widget1.setStyleSheet(DARK_COLOR_WIDGET_STYLE)
    else:
        color_picker_widget1.setStyleSheet(LIGHT_COLOR_WIDGET_STYLE)
    layout1.addWidget(color_picker_widget1)

    button_layout1 = QHBoxLayout()
    ok_button1 = QPushButton("OK")
    ok_button1.setStyleSheet(CONFIRM_BUTTON_STYLE)
    cancel_button1 = QPushButton("Cancel")
    cancel_button1.setStyleSheet(CANCEL_BUTTON_STYLE)
    
    button_layout1.addWidget(ok_button1)
    button_layout1.addWidget(cancel_button1)
    layout1.addLayout(button_layout1)

    ok_button1.clicked.connect(dialog1.accept)
    cancel_button1.clicked.connect(dialog1.reject)

    if dialog1.exec() != QDialog.DialogCode.Accepted:
        return
    
    color1 = color_picker_widget1.color

    dialog2 = QDialog(window)
    dialog2.setWindowTitle("Pick Color 2 (Right)")
    dialog2.setFixedSize(550, 320)
    if dark_mode == True:
        dialog2.setWindowIcon(QIcon("dark_textures/colorwheel.png"))
    else:
        dialog2.setWindowIcon(QIcon("colored_textures/colorwheel.png"))
    if dark_mode == True:
        dialog2.setStyleSheet(DARK_COLOR_DIALOG_STYLE)
    else:
        dialog2.setStyleSheet(LIGHT_COLOR_DIALOG_STYLE)
    
    layout2 = QVBoxLayout(dialog2)

    color_picker_widget2 = ColorPickerWidget(canvas)
    color_picker_widget2.set_color(canvas.pen_color)
    if dark_mode == True:
        color_picker_widget2.setStyleSheet(DARK_COLOR_WIDGET_STYLE)
    else:
        color_picker_widget2.setStyleSheet(LIGHT_COLOR_WIDGET_STYLE)
    layout2.addWidget(color_picker_widget2)

    button_layout2 = QHBoxLayout()
    ok_button2 = QPushButton("OK")
    ok_button2.setStyleSheet(CONFIRM_BUTTON_STYLE)
    cancel_button2 = QPushButton("Cancel")
    cancel_button2.setStyleSheet(CANCEL_BUTTON_STYLE)
    button_layout2.addWidget(ok_button2)
    button_layout2.addWidget(cancel_button2)
    layout2.addLayout(button_layout2)

    ok_button2.clicked.connect(dialog2.accept)
    cancel_button2.clicked.connect(dialog2.reject)

    if dialog2.exec() == QDialog.DialogCode.Accepted:
        color2 = color_picker_widget2.color
        canvas.apply_gradient(color1, color2)
gradient.clicked.connect(use_gradient)
gradient.setShortcut(GRADIENT)

color_wheel = QToolButton()
color_wheel.setFixedSize(45, 45)
color_wheel.setCursor(Qt.CursorShape.PointingHandCursor)
if dark_mode == True:
        color_wheel.setStyleSheet(f"""
            background: {canvas.pen_color.name()}; 
            border: 2px solid white; 
            border-radius: 22px;
            QToolButton::menu-indicator {{
                image: none;
                width: 0px;
                height: 0px;
            }}
        """)
else:
    color_wheel.setStyleSheet(f"""
        background: {canvas.pen_color.name()}; 
        border: 2px solid black;  
        border-radius: 22px;
        QToolButton::menu-indicator {{
            image: none;
            width: 0px;
            height: 0px;
        }}
    """)
color_wheel.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
color_wheel.setShortcut(DRAW)

color_menu = QMenu()
color_menu.setStyleSheet(LIGHT_MENU_STYLE)

color_widget = ColorPickerWidget(canvas)
color_widget.colorChanged.connect(canvas.set_pen_color)
canvas.pen_color_changed.connect(color_widget.set_color)

color_action = QWidgetAction(color_menu)
color_action.setDefaultWidget(color_widget)
color_menu.addAction(color_action)
color_wheel.setMenu(color_menu)

spacer0 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer2 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer4 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer6 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

bottom_layout.addSpacerItem(spacer0)
bottom_layout.addWidget(selection_button)
bottom_layout.addWidget(move_button)
bottom_layout.addSpacerItem(spacer2)
bottom_layout.addWidget(d_button)
bottom_layout.addWidget(shapes)
bottom_layout.addWidget(t_button)
bottom_layout.addSpacerItem(spacer4)
bottom_layout.addWidget(color_bucket)
bottom_layout.addWidget(gradient)
bottom_layout.addWidget(color_wheel)
bottom_layout.addSpacerItem(spacer6)

canvas_and_toolbar = QVBoxLayout()
canvas_and_toolbar.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignCenter)
canvas_and_toolbar.addWidget(bottom_toolbar)
central_layout.addLayout(canvas_and_toolbar)
        
def open_file_dialog(window):
    file_path, _ = QFileDialog.getOpenFileName(window, "Open File", "", "All Files (*)")
    if file_path:
        pixmap = QPixmap(file_path)
        canvas.set_pixmap(pixmap)
        print(file_path)

def save_file_dialog(window):
    file_path, _ = QFileDialog.getSaveFileName(
        window,
        "Save File",
        "",
        "PNG (*.png);;JPEG (*.jpg);;All Files (*)"
    )
    if file_path:
        try:
            if canvas.image and not canvas.image.isNull():
                canvas.image.save(file_path)
                print(f"Saved under: {file_path}")
            else:
                print("No Image there to save")
        except Exception as e:
            print(f"Error while saving: {e}")

def clear_canvas():
    if WARNBFCLEAR==True:
        reply = QMessageBox.warning(
            window, 
            "Clear canvas",
            "Your canvas is about to be cleared. Do you want to proceed?",
            QMessageBox.StandardButton.Yes| QMessageBox.StandardButton.Save
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                canvas.image.fill(Qt.GlobalColor.white)
                canvas.update()
            except Exception as e:
                print(f"Error while clearing canvas: {e}")
        elif reply == QMessageBox.StandardButton.Save:
            save_file_dialog(window)
    else:
        try:
            canvas.image.fill(Qt.GlobalColor.white)
            canvas.update()
        except Exception as e:
            print(f"Error while clearing canvas: {e}")

def open_blur_options():
    blur_options = QDialog(window)
    blur_options.setWindowTitle("Blur Options")
    if dark_mode == True:
        blur_options.setWindowIcon(QIcon("dark_textures/blur.png"))
    else:
        blur_options.setWindowIcon(QIcon("colored_textures/blur.png"))
    layout = QVBoxLayout()
    blur_options.setLayout(layout)
    if dark_mode == True:
        blur_options.setStyleSheet(DARK_DIALOG_STYLE)
    else:
        blur_options.setStyleSheet(LIGHT_DIALOG_STYLE)

    blur_slider = QSlider(Qt.Orientation.Horizontal)
    blur_slider.setRange(1, 35)
    blur_slider.setValue(5)

    blur_text = QLineEdit()
    blur_text.setText("5")
    blur_text.setStyleSheet("border: transparent; background: transparent; font-family: 'Lexend Deca'; font-size: 15px;")
    blur_text.setFixedSize(30,20)
    blur_text.setValidator(QIntValidator(1, 150))

    blur_slider.setFixedSize(100,20)
    blur_slider.setStyleSheet(LIGHT_SLIDER_STYLE2)
    blur_slider.valueChanged.connect(lambda value: blur_text.setText(str(value)))

    
    def update_value_from_text(text):
        if not text.isdigit():
            return  
        value = int(text)
        blur_slider.setValue(value)

    blur_text.textChanged.connect(update_value_from_text)

    blur_confirm = QPushButton("Confirm")
    blur_confirm.setStyleSheet(CONFIRM_BUTTON_STYLE)
    blur_confirm.clicked.connect(lambda: (canvas.apply_blur(blur_slider.value()), blur_options.accept()))
    layout2 = QHBoxLayout()
    layout2.addWidget(blur_slider)
    layout2.addWidget(blur_text)
    
    layout.addLayout(layout2)
    layout.addWidget(blur_confirm)
    
    blur_options.exec()

def open_unsharp_mask_options():
    dialog = QDialog(window)
    dialog.setWindowTitle("Unsharp Mask Options")
    if dark_mode == True:
        dialog.setWindowIcon(QIcon("dark_textures/unsharp_mask.png"))
    else:
        dialog.setWindowIcon(QIcon("colored_textures/unsharp_mask.png"))
    layout = QVBoxLayout(dialog)
    if dark_mode == True:
        dialog.setStyleSheet(DARK_DIALOG_STYLE)
    else:
        dialog.setStyleSheet(LIGHT_DIALOG_STYLE)

    radius_layout = QHBoxLayout()
    radius_label = QLabel("R")
    radius_label.setFont(QFont(FONT, 15))
    radius_slider = QSlider(Qt.Orientation.Horizontal)
    radius_slider.setRange(1, 10)
    radius_slider.setValue(2)
    radius_slider.setStyleSheet(LIGHT_SLIDER_STYLE2)
    radius_text = QLineEdit("2")
    radius_text.setFont(QFont(FONT, 15))
    radius_text.setStyleSheet("border: transparent; background: transparent;")
    radius_text.setFixedWidth(40)
    radius_text.setValidator(QIntValidator(1, 10))
    radius_layout.addWidget(radius_label)
    radius_layout.addWidget(radius_slider)
    radius_layout.addWidget(radius_text)
    layout.addLayout(radius_layout)


    percent_layout = QHBoxLayout()
    percent_label = QLabel("%")
    percent_label.setFont(QFont(FONT, 15))
    percent_slider = QSlider(Qt.Orientation.Horizontal)
    percent_slider.setRange(50, 500)
    percent_slider.setValue(150)
    percent_slider.setStyleSheet(LIGHT_SLIDER_STYLE2)
    percent_text = QLineEdit("150")
    percent_text.setFont(QFont(FONT, 15))
    percent_text.setStyleSheet("border: transparent; background: transparent;")
    percent_text.setFixedWidth(50)
    percent_text.setValidator(QIntValidator(50, 500))
    percent_layout.addWidget(percent_label)
    percent_layout.addWidget(percent_slider)
    percent_layout.addWidget(percent_text)
    layout.addLayout(percent_layout)

    threshold_layout = QHBoxLayout()
    threshold_label = QLabel("T")
    threshold_label.setFont(QFont(FONT, 15))
    threshold_slider = QSlider(Qt.Orientation.Horizontal)
    threshold_slider.setRange(0, 255)
    threshold_slider.setValue(3)
    threshold_slider.setStyleSheet(LIGHT_SLIDER_STYLE2)
    threshold_text = QLineEdit("3")
    threshold_text.setFont(QFont(FONT, 15))
    threshold_text.setStyleSheet(STDSTYLE)
    threshold_text.setFixedWidth(40)
    threshold_text.setValidator(QIntValidator(0, 255))
    threshold_layout.addWidget(threshold_label)
    threshold_layout.addWidget(threshold_slider)
    threshold_layout.addWidget(threshold_text)
    layout.addLayout(threshold_layout)

    radius_slider.valueChanged.connect(lambda v: radius_text.setText(str(v)))
    percent_slider.valueChanged.connect(lambda v: percent_text.setText(str(v)))
    threshold_slider.valueChanged.connect(lambda v: threshold_text.setText(str(v)))
    radius_text.textChanged.connect(lambda t: radius_slider.setValue(int(t) if t.isdigit() else 2))
    percent_text.textChanged.connect(lambda t: percent_slider.setValue(int(t) if t.isdigit() else 150))
    threshold_text.textChanged.connect(lambda t: threshold_slider.setValue(int(t) if t.isdigit() else 3))

    info = QLabel()
    info.setText("R = Radius / % = Percent / T = Threshold")
    info.setFont(QFont(FONT, 9))
    layout.addWidget(info)

    confirm_btn = QPushButton("Confirm")
    confirm_btn.setStyleSheet(CONFIRM_BUTTON_STYLE)
    def apply_unsharp():
        radius = int(radius_text.text())
        percent = int(percent_text.text())
        threshold = int(threshold_text.text())
        canvas.apply_unsharp_mask(radius=radius, percent=percent, threshold=threshold)
        dialog.accept()
    confirm_btn.clicked.connect(apply_unsharp)
    layout.addWidget(confirm_btn)

    
    dialog.exec()

def open_combined_adjustments(canvas):

    dialog = QDialog()
    dialog.setWindowTitle("Combined Adjustments")
    if dark_mode == True:
        dialog.setWindowIcon(QIcon("dark_textures/ca.png"))
    else:
        dialog.setWindowIcon(QIcon("colored_textures/ca.png"))
    dialog.setFixedSize(300, 360)
    if dark_mode == True:
        dialog.setStyleSheet(DARK_DIALOG_STYLE)
    else:
        dialog.setStyleSheet(LIGHT_DIALOG_STYLE)

    layout = QVBoxLayout()
    sliders = {}

    def make_slider(name, min_val, max_val, default=0):
        line = QHBoxLayout()
        label = QLabel(name)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.setStyleSheet(LIGHT_SLIDER_STYLE2)
        value_label = QLineEdit(str(default))
        value_label.setFixedSize(35,35)
        value_label.setStyleSheet("border: transparent; background: transparent;")
        value_label.setFont(QFont(FONT, 15))
        value_label.textChanged.connect(lambda text: slider.setValue(int(text)) if text.isdigit() else None)

        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
        line.addWidget(label)
        line.addWidget(slider)
        line.addWidget(value_label)
        layout.addLayout(line)
        sliders[name] = slider

        label.setFont(QFont(FONT, 15))

    make_slider("R ", -100, 100)
    make_slider("B ", -100, 100)
    make_slider("Y ", -100, 100)
    make_slider("S ", -100, 100)
    make_slider("B ", -100, 100)
    make_slider("C ", -100, 100)

    confirm = QPushButton("Confirm")
    confirm.setStyleSheet(CONFIRM_BUTTON_STYLE)
    info = QLabel()
    info.setText("R = Red / G = Green / Y = Yellow")
    info.setFont(QFont(FONT, 9))
    info2 = QLabel()
    info2.setText("S = Saturation / B = Brightness / C = Contrast")
    info2.setFont(QFont(FONT, 9))
    layout.addWidget(info)
    layout.addWidget(info2)
    layout.addWidget(confirm)
    dialog.setLayout(layout)

    def apply_adjustments():

        pil_image = ImageQt.fromqpixmap(canvas.image)

        r_shift = sliders["R "].value()
        b_shift = sliders["B "].value()
        y_shift = sliders["Y "].value()

        pixels = pil_image.load()
        for x in range(pil_image.width):
            for y in range(pil_image.height):
                r, g, b = pixels[x, y][:3]
                r += r_shift + y_shift
                g += y_shift
                b += b_shift
                pixels[x, y] = (
                    max(0, min(r, 255)),
                    max(0, min(g, 255)),
                    max(0, min(b, 255))
                )

        saturation_factor = 1 + sliders["S "].value() / 100.0
        pil_image = ImageEnhance.Color(pil_image).enhance(saturation_factor)

        brightness_factor = 1 + sliders["B "].value() / 100.0
        pil_image = ImageEnhance.Brightness(pil_image).enhance(brightness_factor)

        contrast_factor = 1 + sliders["C "].value() / 100.0
        pil_image = ImageEnhance.Contrast(pil_image).enhance(contrast_factor)

        qt_image = ImageQt.toqpixmap(pil_image)
        canvas.image = qt_image
        canvas.update()
        dialog.accept()

    confirm.clicked.connect(apply_adjustments)
    dialog.exec()

def open_temperature_options(canvas):

    dialog = QDialog()
    dialog.setWindowTitle("Temperature / Tint")
    if dark_mode == True:
        dialog.setWindowIcon(QIcon("dark_textures/temperature.png"))
    else:
        dialog.setWindowIcon(QIcon("colored_textures/temperature.png"))
    dialog.setFixedSize(300, 120)
    if dark_mode == True:
        dialog.setStyleSheet(DARK_DIALOG_STYLE)
    else:
        dialog.setStyleSheet(LIGHT_DIALOG_STYLE)

    layout = QVBoxLayout()

    temp_label = QLabel("Temp.")
    temp_label.setFont(QFont(FONT, 15))
    
    lslider_temp = QHBoxLayout()
    slider_temp = QSlider(Qt.Orientation.Horizontal)
    slider_temp.setRange(-99, 99)
    slider_temp.setValue(0)
    slider_temp.setFixedSize(150,20)
    
    value_label_temp = QLineEdit(str(0))
    value_label_temp.setFixedSize(30,20)
    value_label_temp.setStyleSheet(STDSTYLE)
    value_label_temp.setFont(QFont(FONT, 15))
    value_label_temp.textChanged.connect(lambda text: slider_temp.setValue(int(text)) if text.isdigit() or (text.startswith('-') and text[1:].isdigit()) else None)
    slider_temp.valueChanged.connect(lambda v: value_label_temp.setText(str(v)))

    lslider_temp.addWidget(temp_label)
    lslider_temp.addWidget(slider_temp)
    lslider_temp.addWidget(value_label_temp)
    layout.addLayout(lslider_temp)

    tint_label = QLabel("Tint")
    tint_label.setFont(QFont(FONT, 15))

    lslider_tint = QHBoxLayout()
    slider_tint = QSlider(Qt.Orientation.Horizontal)
    slider_tint.setRange(-99, 99)
    slider_tint.setValue(0)
    slider_tint.setFixedSize(150,20)

    value_label_tint = QLineEdit(str(0))
    value_label_tint.setFixedSize(30,20)
    value_label_tint.setStyleSheet(STDSTYLE)
    value_label_tint.setFont(QFont(FONT, 15))
    value_label_tint.textChanged.connect(lambda text: slider_tint.setValue(int(text)) if text.isdigit() or (text.startswith('-') and text[1:].isdigit()) else None)
    slider_tint.valueChanged.connect(lambda v: value_label_tint.setText(str(v)))
    
    lslider_tint.addWidget(tint_label)
    lslider_tint.addWidget(slider_tint)
    lslider_tint.addWidget(value_label_tint)
    layout.addLayout(lslider_tint)


    confirm = QPushButton("Confirm")
    confirm.setStyleSheet(CONFIRM_BUTTON_STYLE)
    layout.addWidget(confirm)
    dialog.setLayout(layout)

    def apply_adjustments():

        pil_image = ImageQt.fromqpixmap(canvas.image)

        temperature = slider_temp.value()
        tint = slider_tint.value()

        pixels = pil_image.load()
        for x in range(pil_image.width):
            for y in range(pil_image.height):
                r, g, b = pixels[x, y][:3]

                new_r = r + temperature
                new_b = b - temperature

                new_g = g + tint

                pixels[x, y] = (
                    max(0, min(new_r, 255)),
                    max(0, min(new_g, 255)),
                    max(0, min(new_b, 255))
                )

        qt_image = ImageQt.toqpixmap(pil_image)
        canvas.image = qt_image
        canvas.update()
        dialog.accept()

    confirm.clicked.connect(apply_adjustments)
    dialog.exec()

def toggle_dark_mode(enabled: bool):
    if enabled:
        dark_mode = True
        dark_palette = window.palette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(DARKCOLOR))
        window.setPalette(dark_palette)
        window.setAutoFillBackground(True)

        new_action.setIcon(QIcon("dark_textures/new.png"))
        import_action.setIcon(QIcon("dark_textures/import.png"))
        export_action.setIcon(QIcon("dark_textures/export.png"))
        undo_action.setIcon(QIcon("dark_textures/undo.png"))
        redo_action.setIcon(QIcon("dark_textures/redo.png"))
        copy_selection.setIcon(QIcon("dark_textures/copy.png"))
        paste_selection.setIcon(QIcon("dark_textures/paste.png"))
        zoom_in.setIcon(QIcon("dark_textures/zoom_in.png"))
        zoom_out.setIcon(QIcon("dark_textures/zoom_out.png"))
        resize_canvas_action.setIcon(QIcon("dark_textures/resize_canvas.png"))
        crop_selection_action.setIcon(QIcon("dark_textures/crop_selection.png"))
        rotate_90_cw_action.setIcon(QIcon("dark_textures/rotate_90_cw.png"))
        rotate_90_ccw_action.setIcon(QIcon("dark_textures/rotate_90_ccw.png"))
        mirror_horizontal_action.setIcon(QIcon("dark_textures/mirror_horizontal.png"))
        mirror_vertical_action.setIcon(QIcon("dark_textures/mirror_vertical.png"))

        effects_action.setIcon(QIcon("dark_textures/effects.png"))
        effects_menu.setStyleSheet(DARK_MENU_STYLE)
        ca_action.setIcon(QIcon("dark_textures/ca.png"))
        temperature_action.setIcon(QIcon("dark_textures/temperature.png"))
        blur_action.setIcon(QIcon("dark_textures/blur.png"))
        smooth_action.setIcon(QIcon("dark_textures/smooth.png"))
        smooth_more_action.setIcon(QIcon("dark_textures/smooth_more.png"))
        unsharp_mask_action.setIcon(QIcon("dark_textures/unsharp_mask.png"))
        sharpen_action.setIcon(QIcon("dark_textures/sharpen.png"))
        contour_action.setIcon(QIcon("dark_textures/contour.png"))
        find_edges_action.setIcon(QIcon("dark_textures/find_edges.png"))
        edge_enhance_action.setIcon(QIcon("dark_textures/edge_enhance.png"))
        emboss_action.setIcon(QIcon("dark_textures/emboss.png"))
        detail_action.setIcon(QIcon("dark_textures/detail.png"))
        invert_action.setIcon(QIcon("dark_textures/invert.png"))

        bottom_toolbar.setStyleSheet(f"background-color: {DARKCOLOR2}; border-radius: 50px;")
        move_button.setIcon(QIcon("dark_textures/move.png"))

        selection_menu.setStyleSheet(DARK_MENU_STYLE)
        selection_button.setIcon(QIcon("dark_textures/selection.png"))
        rselect_button.setIcon(QIcon("dark_textures/rectangular_selection.png"))
        cselect_button.setIcon(QIcon("dark_textures/circular_selection.png"))
        lselect_button.setIcon(QIcon("dark_textures/lasso_selection.png"))
        clearsel_button.setIcon(QIcon("dark_textures/clear_selection.png"))

        shapes_menu.setStyleSheet(DARK_MENU_STYLE)
        shapes.setIcon(QIcon("dark_textures/shapes.png"))
        rectangle.setIcon(QIcon("dark_textures/rectangle.png"))
        triangle.setIcon(QIcon("dark_textures/triangle.png"))
        ellipse.setIcon(QIcon("dark_textures/ellipse.png"))
        lines.setIcon(QIcon("dark_textures/lines.png"))
        disableshape.setIcon(QIcon("dark_textures/disableshape.png"))

        d_menu.setStyleSheet(DARK_MENU_STYLE)
        d_button.setIcon(QIcon("dark_textures/draw.png"))
        d_pen.setIcon(QIcon("dark_textures/pen.png"))
        d_marker.setIcon(QIcon("dark_textures/marker.png"))
        d_eraser.setIcon(QIcon("dark_textures/eraser.png"))
        d_color.setStyleSheet(f"background: {canvas.pen_color.name()}; border: 2px solid white; border-radius: 15px;")
        d_width_text.setStyleSheet("border: transparent; background: transparent; color: white;")
        d_width_slider.setStyleSheet(DARK_SLIDER_STYLE2)
        d_brush.setIcon(QIcon("dark_textures/brush.png"))
        d_round.setIcon(QIcon("dark_textures/round.png"))
        d_round.setStyleSheet(DARK_TOOL_BUTTON_STYLE)
        d_flat.setIcon(QIcon("dark_textures/flat.png"))
        d_flat.setStyleSheet(DARK_TOOL_BUTTON_STYLE)
        d_dynamic.setIcon(QIcon("dark_textures/dynamic.png"))
        d_dynamic.setStyleSheet(DARK_TOOL_BUTTON_STYLE)
        '''
        d_solid.setIcon(QIcon("dark_textures/solid.png"))
        d_solid.setStyleSheet(DARK_TOOL_BUTTON_STYLE)
        d_dash.setIcon(QIcon("dark_textures/dash.png"))
        d_dash.setStyleSheet(DARK_TOOL_BUTTON_STYLE)
        d_dot.setIcon(QIcon("dark_textures/dot.png"))
        d_dot.setStyleSheet(DARK_TOOL_BUTTON_STYLE)
        '''

        t_menu.setStyleSheet(DARK_MENU_STYLE)
        t_button.setIcon(QIcon("dark_textures/text.png"))
        t_text.setStyleSheet("border: transparent; background: #646478; border-radius: 5px; height: 50px; font-family: 'Lexend Deca'; font-size: 15px; color: white;")
        t_font.setStyleSheet(DARK_FONT_COMBO_STYLE)
        t_slider.setStyleSheet(DARK_SLIDER_STYLE2)
        t_size.setStyleSheet("border: transparent; background: transparent; font-family: 'Lexend Deca'; font-size: 15px; color: white;")
        t_bold.setStyleSheet(DARK_TEXT_TOOL_BUTTON_STYLE)
        t_italic.setStyleSheet(DARK_TEXT_TOOL_BUTTON_STYLE)
        t_underline.setStyleSheet(DARK_TEXT_TOOL_BUTTON_STYLE)
        t_strike.setStyleSheet(DARK_TEXT_TOOL_BUTTON_STYLE)
        t_color.setStyleSheet(f"background: {canvas.text_options['color'].name()}; border: 2px solid white; border-radius: 15px;")
        
        color_bucket.setIcon(QIcon("dark_textures/bucket.png"))
        gradient.setIcon(QIcon("dark_textures/gradient.png"))
        color_menu.setStyleSheet(DARK_MENU_STYLE)
        color_widget.setStyleSheet(DARK_COLOR_WIDGET_STYLE)

        canvas.setStyleSheet("background-color: #1c1c28;")

    else:
        dark_mode = False
        window.setPalette(w_palette)

        new_action.setIcon(QIcon("colored_textures/new.png"))
        import_action.setIcon(QIcon("colored_textures/import.png"))
        export_action.setIcon(QIcon("colored_textures/export.png"))
        undo_action.setIcon(QIcon("colored_textures/undo.png"))
        redo_action.setIcon(QIcon("colored_textures/redo.png"))
        copy_selection.setIcon(QIcon("colored_textures/copy.png"))
        paste_selection.setIcon(QIcon("colored_textures/paste.png"))
        zoom_in.setIcon(QIcon("colored_textures/zoom_in.png"))
        zoom_out.setIcon(QIcon("colored_textures/zoom_out.png"))
        resize_canvas_action.setIcon(QIcon("colored_textures/resize_canvas.png"))
        crop_selection_action.setIcon(QIcon("colored_textures/crop_selection.png"))
        rotate_90_cw_action.setIcon(QIcon("colored_textures/rotate_90_cw.png"))
        rotate_90_ccw_action.setIcon(QIcon("colored_textures/rotate_90_ccw.png"))
        mirror_horizontal_action.setIcon(QIcon("colored_textures/mirror_horizontal.png"))
        mirror_vertical_action.setIcon(QIcon("colored_textures/mirror_vertical.png"))

        effects_action.setIcon(QIcon("colored_textures/effects.png"))
        effects_menu.setStyleSheet(LIGHT_MENU_STYLE)
        ca_action.setIcon(QIcon("colored_textures/ca.png"))
        temperature_action.setIcon(QIcon("colored_textures/temperature.png"))
        blur_action.setIcon(QIcon("colored_textures/blur.png"))
        smooth_action.setIcon(QIcon("colored_textures/smooth.png"))
        smooth_more_action.setIcon(QIcon("colored_textures/smooth_more.png"))
        unsharp_mask_action.setIcon(QIcon("colored_textures/unsharp_mask.png"))
        sharpen_action.setIcon(QIcon("colored_textures/sharpen.png"))
        contour_action.setIcon(QIcon("colored_textures/contour.png"))
        find_edges_action.setIcon(QIcon("colored_textures/find_edges.png"))
        edge_enhance_action.setIcon(QIcon("colored_textures/edge_enhance.png"))
        emboss_action.setIcon(QIcon("colored_textures/emboss.png"))
        detail_action.setIcon(QIcon("colored_textures/detail.png"))
        invert_action.setIcon(QIcon("colored_textures/invert.png"))

        bottom_toolbar.setStyleSheet(f"background-color: #ffffff; border-radius: 50px;")
        move_button.setIcon(QIcon("colored_textures/move.png"))

        selection_menu.setStyleSheet(LIGHT_MENU_STYLE)
        selection_button.setIcon(QIcon("colored_textures/selection.png"))
        rselect_button.setIcon(QIcon("colored_textures/rectangular_selection.png"))
        cselect_button.setIcon(QIcon("colored_textures/circular_selection.png"))
        lselect_button.setIcon(QIcon("colored_textures/lasso_selection.png"))
        clearsel_button.setIcon(QIcon("colored_textures/clear_selection.png"))

        shapes_menu.setStyleSheet(LIGHT_MENU_STYLE)
        shapes.setIcon(QIcon("colored_textures/shapes.png"))
        rectangle.setIcon(QIcon("colored_textures/rectangle.png"))
        triangle.setIcon(QIcon("colored_textures/triangle.png"))
        ellipse.setIcon(QIcon("colored_textures/ellipse.png"))
        lines.setIcon(QIcon("colored_textures/lines.png"))
        disableshape.setIcon(QIcon("colored_textures/disableshape.png"))

        d_menu.setStyleSheet(LIGHT_MENU_STYLE)
        d_button.setIcon(QIcon("colored_textures/draw.png"))
        d_pen.setIcon(QIcon("colored_textures/pen.png"))
        d_marker.setIcon(QIcon("colored_textures/marker.png"))
        d_brush.setIcon(QIcon("colored_textures/brush.png"))
        d_eraser.setIcon(QIcon("colored_textures/eraser.png"))
        d_color.setStyleSheet(f"background: {canvas.pen_color.name()}; border: 2px solid black; border-radius: 15px;")
        d_width_text.setStyleSheet(STDSTYLE)
        d_width_slider.setStyleSheet(LIGHT_SLIDER_STYLE2)
        d_round.setIcon(QIcon("colored_textures/round.png"))
        d_round.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
        d_flat.setIcon(QIcon("colored_textures/flat.png"))
        d_flat.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
        d_dynamic.setIcon(QIcon("colored_textures/dynamic.png"))
        d_dynamic.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
        '''
        d_solid.setIcon(QIcon("colored_textures/solid.png"))
        d_solid.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
        d_dash.setIcon(QIcon("colored_textures/dash.png"))
        d_dash.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
        d_dot.setIcon(QIcon("colored_textures/dot.png"))
        d_dot.setStyleSheet(LIGHT_TOOL_BUTTON_STYLE)
        '''

        t_menu.setStyleSheet(LIGHT_MENU_STYLE)
        t_button.setIcon(QIcon("colored_textures/text.png"))
        t_text.setStyleSheet("border: transparent; background: white; border-radius: 5px; height: 50px; font-family: 'Lexend Deca'; font-size: 15px;")
        t_font.setStyleSheet(LIGHT_FONT_COMBO_STYLE)
        t_slider.setStyleSheet(LIGHT_SLIDER_STYLE2)
        t_size.setStyleSheet("border: transparent; background: transparent; font-family: 'Lexend Deca'; font-size: 15px;")
        t_bold.setStyleSheet(LIGHT_TEXT_TOOL_BUTTON_STYLE)
        t_italic.setStyleSheet(LIGHT_TEXT_TOOL_BUTTON_STYLE)
        t_underline.setStyleSheet(LIGHT_TEXT_TOOL_BUTTON_STYLE)
        t_strike.setStyleSheet(LIGHT_TEXT_TOOL_BUTTON_STYLE)
        t_color.setStyleSheet(f"background: {canvas.text_options['color'].name()}; border: 2px solid black; border-radius: 15px;")
        color_bucket.setIcon(QIcon("colored_textures/bucket.png"))
        gradient.setIcon(QIcon("colored_textures/gradient.png"))
        color_menu.setStyleSheet(LIGHT_MENU_STYLE)
        color_widget.setStyleSheet(LIGHT_COLOR_WIDGET_STYLE)
        canvas.setStyleSheet(f"background-color: {LIGHTCOLOR};")

window.show()
sys.exit(app.exec())