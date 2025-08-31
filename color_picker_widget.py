from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QToolButton, QGridLayout, QSlider, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QColor, QIcon, QIntValidator
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from config import *

class ColorPickerWidget(QWidget):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, canvas, initial_color=QColor(0, 0, 0), parent=None):
        super().__init__(parent)
        self.color = initial_color
        self.updating = False

        self.h_label = self._create_label("Hue")
        self.h_slider = self._create_slider(self.color.hue(), 359)
        self.h_value = self._create_value_label(0, 359)
        self.s_label = self._create_label("Sat.")
        self.s_slider = self._create_slider(self.color.saturation(), 100)
        self.s_value = self._create_value_label(0, 100)
        self.v_label = self._create_label("Value")
        self.v_slider = self._create_slider(self.color.value(), 100)
        self.v_value = self._create_value_label(0, 100)
        self.r_label = self._create_label("Red")
        self.r_slider = self._create_slider(self.color.red())
        self.r_value = self._create_value_label(0, 255)
        self.g_label = self._create_label("Green")
        self.g_slider = self._create_slider(self.color.green())
        self.g_value = self._create_value_label(0, 255)
        self.b_label = self._create_label("Blue")
        self.b_slider = self._create_slider(self.color.blue())
        self.b_value = self._create_value_label(0, 255)
        self.a_label = self._create_label("Alpha")
        self.a_slider = self._create_slider(self.color.alpha())
        self.a_value = self._create_value_label(255, 255)

        self.p1 = self._create_preset(QColor(*P1))
        self.p2 = self._create_preset(QColor(*P2))
        self.p3 = self._create_preset(QColor(*P3))
        self.p4 = self._create_preset(QColor(*P4))
        self.p5 = self._create_preset(QColor(*P5))
        self.p6 = self._create_preset(QColor(*P6))
        self.p7 = self._create_preset(QColor(*P7))
        self.p8 = self._create_preset(QColor(*P8))
        self.p9 = self._create_preset(QColor(*P9))
        self.p10 = self._create_preset(QColor(*P10))
        self.p11 = self._create_preset(QColor(*P11))
        self.p12 = self._create_preset(QColor(*P12))
        self.p13 = self._create_preset(QColor(*P13))
        self.p14 = self._create_preset(QColor(*P14))
        self.p15 = self._create_preset(QColor(*P15))
        self.p16 = self._create_preset(QColor(*P16))
        self.p17 = self._create_preset(QColor(*P17))
        self.p18 = self._create_preset(QColor(*P18))
        self.p19 = self._create_preset(QColor(*P19))
        self.p20 = self._create_preset(QColor(*P20))
        self.p21 = self._create_preset(QColor(*P21))
        self.p22 = self._create_preset(QColor(*P22))
        self.p23 = self._create_preset(QColor(*P23))
        self.p24 = self._create_preset(QColor(*P24))
        self.p25 = self._create_preset(QColor(*P25))
        self.p26 = self._create_preset(QColor(*P26))
        self.p27 = self._create_preset(QColor(*P27))
        self.p28 = self._create_preset(QColor(*P28))
        self.p29 = self._create_preset(QColor(*P29))
        self.p30 = self._create_preset(QColor(*P30))
        self.p31 = self._create_preset(QColor(*P31))
        self.p32 = self._create_preset(QColor(*P32))
        self.p33 = self._create_preset(QColor(*P33))
        self.p34 = self._create_preset(QColor(*P34))
        self.p35 = self._create_preset(QColor(*P35))
        self.p36 = self._create_preset(QColor(*P36))
        self.p37 = self._create_preset(QColor(*P37))
        self.p38 = self._create_preset(QColor(*P38))
        self.p39 = self._create_preset(QColor(*P39))
        self.p40 = self._create_preset(QColor(*P40))
        self.p41 = self._create_preset(QColor(*P41))
        self.p42 = self._create_preset(QColor(*P42))

        self.preview = QLabel()
        self.preview.setFixedSize(100, 100)
        self.preview.setStyleSheet(f"background-color: {self.color.name()}; border: 2px solid white; border-radius: 15px;")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.hex_input = QLineEdit(self.color.name())
        self.hex_input.setStyleSheet("background: white; border: none; font-family: 'Lexend Deca'; font-size: 15px; text-align: center; border-radius: 5px;")
        self.hex_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hex_input.setFixedWidth(100)
        self.hex_input.setFixedHeight(25)
        self.hex_input.setMaxLength(7)
        self.hex_input.textChanged.connect(self._update_from_hex)

        self.eyedropper = QToolButton()
        self.eyedropper.setIcon(QIcon("dark_textures/color_picker.png"))
        self.eyedropper.setIconSize(QSize(30,30))
        self.eyedropper.setStyleSheet(STDSTYLE)
        self.eyedropper.setCheckable(True)
        self.eyedropper.clicked.connect(lambda checked: canvas.set_eyedropper_mode(True) if checked else canvas.set_eyedropper_mode(False))
        self.eyedropper.setShortcut(COLORPICKER)

        uni_layout = QHBoxLayout(self)
        uni_layout.setContentsMargins(10, 10, 10, 10)
        uni_layout.setSpacing(8)
        self.setLayout(uni_layout)

        prev_layout = QVBoxLayout(self)
        uni_layout.addLayout(prev_layout)
        prev_layout.addWidget(self.preview)
        prev_layout.addWidget(self.hex_input)
        prev_layout.addWidget(self.eyedropper)

        layout = QVBoxLayout(self)
        uni_layout.addLayout(layout)

        preset_layout = QGridLayout()
        preset_layout.setSpacing(0) 
        uni_layout.addLayout(preset_layout)

        h_layout = QHBoxLayout()
        s_layout = QHBoxLayout()
        v_layout = QHBoxLayout()
        r_layout = QHBoxLayout()
        g_layout = QHBoxLayout()
        b_layout = QHBoxLayout()
        a_layout = QHBoxLayout()
        
        h_layout.addWidget(self.h_label)
        h_layout.addWidget(self.h_slider)
        h_layout.addWidget(self.h_value)
        s_layout.addWidget(self.s_label)
        s_layout.addWidget(self.s_slider)
        s_layout.addWidget(self.s_value)
        v_layout.addWidget(self.v_label)
        v_layout.addWidget(self.v_slider)
        v_layout.addWidget(self.v_value)
        r_layout.addWidget(self.r_label)
        r_layout.addWidget(self.r_slider)
        r_layout.addWidget(self.r_value)
        g_layout.addWidget(self.g_label)
        g_layout.addWidget(self.g_slider)
        g_layout.addWidget(self.g_value)
        b_layout.addWidget(self.b_label)
        b_layout.addWidget(self.b_slider)
        b_layout.addWidget(self.b_value)
        a_layout.addWidget(self.a_label)
        a_layout.addWidget(self.a_slider)
        a_layout.addWidget(self.a_value)

        layout.addLayout(h_layout)
        layout.addLayout(s_layout)
        layout.addLayout(v_layout)
        layout.addLayout(r_layout)
        layout.addLayout(g_layout)
        layout.addLayout(b_layout)
        layout.addLayout(a_layout)

        preset_layout.addWidget(self.p1, 0, 0)
        preset_layout.addWidget(self.p2, 0, 1)
        preset_layout.addWidget(self.p3, 0, 2)
        preset_layout.addWidget(self.p4, 0, 3)
        preset_layout.addWidget(self.p5, 0, 4)
        preset_layout.addWidget(self.p6, 0, 5)
        preset_layout.addWidget(self.p7, 1, 0)
        preset_layout.addWidget(self.p8, 1, 1)
        preset_layout.addWidget(self.p9, 1, 2)
        preset_layout.addWidget(self.p10, 1, 3)
        preset_layout.addWidget(self.p11, 1, 4)
        preset_layout.addWidget(self.p12, 1, 5)
        preset_layout.addWidget(self.p13, 2, 0)
        preset_layout.addWidget(self.p14, 2, 1)
        preset_layout.addWidget(self.p15, 2, 2)
        preset_layout.addWidget(self.p16, 2, 3)
        preset_layout.addWidget(self.p17, 2, 4)
        preset_layout.addWidget(self.p18, 2, 5)
        preset_layout.addWidget(self.p19, 3, 0)
        preset_layout.addWidget(self.p20, 3, 1)
        preset_layout.addWidget(self.p21, 3, 2)
        preset_layout.addWidget(self.p22, 3, 3)
        preset_layout.addWidget(self.p23, 3, 4)
        preset_layout.addWidget(self.p24, 3, 5)
        preset_layout.addWidget(self.p25, 4, 0)
        preset_layout.addWidget(self.p26, 4, 1)
        preset_layout.addWidget(self.p27, 4, 2)
        preset_layout.addWidget(self.p28, 4, 3)
        preset_layout.addWidget(self.p29, 4, 4)
        preset_layout.addWidget(self.p30, 4, 5)
        preset_layout.addWidget(self.p31, 5, 0)
        preset_layout.addWidget(self.p32, 5, 1)
        preset_layout.addWidget(self.p33, 5, 2)
        preset_layout.addWidget(self.p34, 5, 3)
        preset_layout.addWidget(self.p35, 5, 4)
        preset_layout.addWidget(self.p36, 5, 5)
        preset_layout.addWidget(self.p37, 6, 0)
        preset_layout.addWidget(self.p38, 6, 1)
        preset_layout.addWidget(self.p39, 6, 2)
        preset_layout.addWidget(self.p40, 6, 3)
        preset_layout.addWidget(self.p41, 6, 4)
        preset_layout.addWidget(self.p42, 6, 5)

        
        self.h_slider.valueChanged.connect(self._update_color_from_hsv)
        self.s_slider.valueChanged.connect(self._update_color_from_hsv)
        self.v_slider.valueChanged.connect(self._update_color_from_hsv)

        self.r_slider.valueChanged.connect(self._update_color_from_rgb)
        self.g_slider.valueChanged.connect(self._update_color_from_rgb)
        self.b_slider.valueChanged.connect(self._update_color_from_rgb)
        self.a_slider.valueChanged.connect(self._update_color_from_rgb)

        self.h_value.textChanged.connect(self._update_from_hsv_text)
        self.s_value.textChanged.connect(self._update_from_hsv_text)
        self.v_value.textChanged.connect(self._update_from_hsv_text)
        self.r_value.textChanged.connect(self._update_from_rgb_text)
        self.g_value.textChanged.connect(self._update_from_rgb_text)
        self.b_value.textChanged.connect(self._update_from_rgb_text)
        self.a_value.textChanged.connect(self._update_from_rgb_text)

    def _create_label(self, text):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setFixedWidth(50)
        label.setFixedHeight(25)
        label.setStyleSheet("font-family: 'Lexend Deca'; font-size: 15px;")
        label.setContentsMargins(0, 0, 0, 0)
        return label
    
    def _create_slider(self, value=0, max_val=255):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setStyleSheet(LIGHT_SLIDER_STYLE2)
        slider.setRange(0, max_val)
        slider.setValue(value)
        return slider
    
    def _create_value_label(self, value=0, max_val=255):
        label = QLineEdit(str(value))
        label.setStyleSheet("background: transparent; border: none; font-family: 'Lexend Deca'; font-size: 15px;")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setFixedWidth(30)
        label.setFixedHeight(25)
        label.setContentsMargins(0, 0, 0, 0)
        label.setValidator(QIntValidator(0, max_val))
        return label
    
    def _create_preset(self, color):
        button = QPushButton()
        button.setStyleSheet(f"background-color: {color.name()}; border: none; border-radius: 5px;")
        button.setFixedSize(35, 35)
        button.clicked.connect(lambda: [ 
            self.set_color(color),
            self._update_preview()
            ])
        return button

    def _update_color_from_hsv(self):
        if self.updating:
            return
        self.updating = True

        h = self.h_slider.value()
        s = int(self.s_slider.value() / 100 * 255)
        v = int(self.v_slider.value() / 100 * 255)

        self.color.setHsv(
            h, s, v,
            self.a_slider.value()
        )

        self.h_value.setText(str(self.h_slider.value()))
        self.s_value.setText(str(self.s_slider.value()))
        self.v_value.setText(str(self.v_slider.value()))

        self.r_slider.setValue(self.color.red())
        self.g_slider.setValue(self.color.green())
        self.b_slider.setValue(self.color.blue())
        self.r_value.setText(str(self.color.red()))
        self.g_value.setText(str(self.color.green()))
        self.b_value.setText(str(self.color.blue()))

        self.hex_input.setText(self.color.name().upper())
        
        self.colorChanged.emit(self.color)
        self._update_preview()
        self.updating = False
    def _update_color_from_rgb(self):
        if self.updating:
            return
        self.updating = True

        self.color.setRed(self.r_slider.value())
        self.color.setGreen(self.g_slider.value())
        self.color.setBlue(self.b_slider.value())
        self.color.setAlpha(self.a_slider.value())

        self.r_value.setText(str(self.r_slider.value()))
        self.g_value.setText(str(self.g_slider.value()))
        self.b_value.setText(str(self.b_slider.value()))
        self.a_value.setText(str(self.a_slider.value()))

        self.h_slider.setValue(self.color.hue())
        self.s_slider.setValue(int(self.color.saturation() / 255 * 100))
        self.v_slider.setValue(int(self.color.value() / 255 * 100))
        self.h_value.setText(str(self.color.hue()))
        self.s_value.setText(str(int(self.color.saturation() / 255 * 100)))
        self.v_value.setText(str(int(self.color.value() / 255 * 100)))

        self.hex_input.setText(self.color.name().upper())

        self.colorChanged.emit(self.color)
        self._update_preview()
        self.updating = False

    def _update_from_rgb_text(self):
        if self.updating:
            return
        self.updating = True
        
        try:
            r_val = max(0, min(255, int(self.r_value.text()) if self.r_value.text().isdigit() else 0))
            g_val = max(0, min(255, int(self.g_value.text()) if self.g_value.text().isdigit() else 0))
            b_val = max(0, min(255, int(self.b_value.text()) if self.b_value.text().isdigit() else 0))
            a_val = max(0, min(255, int(self.a_value.text()) if self.a_value.text().isdigit() else 255))

            self.r_slider.setValue(r_val)
            self.g_slider.setValue(g_val)
            self.b_slider.setValue(b_val)
            self.a_slider.setValue(a_val)

            self.color.setRed(r_val)
            self.color.setGreen(g_val)
            self.color.setBlue(b_val)
            self.color.setAlpha(a_val)

            self.h_slider.setValue(self.color.hue())
            self.s_slider.setValue(int(self.color.saturation() / 255 * 100))
            self.v_slider.setValue(int(self.color.value() / 255 * 100))
            self.h_value.setText(str(self.color.hue()))
            self.s_value.setText(str(int(self.color.saturation() / 255 * 100)))
            self.v_value.setText(str(int(self.color.value() / 255 * 100)))

            self.hex_input.setText(self.color.name().upper())

            self.colorChanged.emit(self.color)
            self._update_preview()
        except (ValueError, AttributeError):
            pass
        finally:
            self.updating = False

    def _update_from_hsv_text(self):
        if self.updating:
            return
        self.updating = True
        
        try:
            h_val = max(0, min(359, int(self.h_value.text()) if self.h_value.text().isdigit() else 0))
            s_val = max(0, min(100, int(self.s_value.text()) if self.s_value.text().isdigit() else 0))
            v_val = max(0, min(100, int(self.v_value.text()) if self.v_value.text().isdigit() else 0))

            self.h_slider.setValue(h_val)
            self.s_slider.setValue(s_val)
            self.v_slider.setValue(v_val)

            s_val_255 = int(s_val / 100 * 255)
            v_val_255 = int(v_val / 100 * 255)

            self.color.setHsv(h_val, s_val_255, v_val_255, self.a_slider.value())

            self.r_slider.setValue(self.color.red())
            self.g_slider.setValue(self.color.green())
            self.b_slider.setValue(self.color.blue())
            self.r_value.setText(str(self.color.red()))
            self.g_value.setText(str(self.color.green()))
            self.b_value.setText(str(self.color.blue()))

            self.hex_input.setText(self.color.name().upper())

            self.colorChanged.emit(self.color)
            self._update_preview()
        except (ValueError, AttributeError):
            pass
        finally:
            self.updating = False

    def _emit_color(self):
        self.colorChanged.emit(self.color)
        self.updating = True

        self.color.setRed(self.r_slider.value())
        self.color.setGreen(self.g_slider.value())
        self.color.setBlue(self.b_slider.value())
        self.color.setAlpha(self.a_slider.value())

        self.r_value.setText(str(self.r_slider.value()))
        self.g_value.setText(str(self.g_slider.value()))
        self.b_value.setText(str(self.b_slider.value()))
        self.a_value.setText(str(self.a_slider.value()))

        self.h_slider.setValue(self.color.hue())
        self.s_slider.setValue(self.color.saturation())
        self.v_slider.setValue(self.color.value())
        self.h_value.setText(str(self.color.hue()))
        self.s_value.setText(str(self.color.saturation()))
        self.v_value.setText(str(self.color.value()))

        self.colorChanged.emit(self.color)
        self._update_preview()
        self.updating = False

    def _update_from_hex(self):
        if self.updating:
            return
        
        hex_text = self.hex_input.text().strip()

        if not hex_text.startswith('#'):
            if len(hex_text) == 6 and all(c in '0123456789ABCDEFabcdef' for c in hex_text):
                hex_text = '#' + hex_text
            else:
                return
        
        if len(hex_text) != 7 or not all(c in '0123456789ABCDEFabcdef' for c in hex_text[1:]):
            return
        
        try:
            self.updating = True
            new_color = QColor(hex_text)
            if new_color.isValid():
                self.color = new_color

                self.r_slider.setValue(self.color.red())
                self.g_slider.setValue(self.color.green())
                self.b_slider.setValue(self.color.blue())
                self.h_slider.setValue(self.color.hue())
                self.s_slider.setValue(self.color.saturation())
                self.v_slider.setValue(self.color.value())

                self.r_value.setText(str(self.color.red()))
                self.g_value.setText(str(self.color.green()))
                self.b_value.setText(str(self.color.blue()))
                self.h_value.setText(str(self.color.hue()))
                self.s_value.setText(str(self.color.saturation()))
                self.v_value.setText(str(self.color.value()))

                self.colorChanged.emit(self.color)
                self._update_preview()
        except Exception:
            pass
        finally:
            self.updating = False
            self.h_slider.setValue(self.color.hue())
            self.s_slider.setValue(self.color.saturation())
            self.v_slider.setValue(self.color.value())

            self.r_value.setText(str(self.color.red()))
            self.g_value.setText(str(self.color.green()))
            self.b_value.setText(str(self.color.blue()))
            self.h_value.setText(str(self.color.hue()))
            self.s_value.setText(str(self.color.saturation()))
            self.v_value.setText(str(self.color.value()))

            self.colorChanged.emit(self.color)
            self._update_preview()

    def set_color(self, color):
        if self.updating:
            return
        self.updating = True
        
        self.color = QColor(color)

        self.r_slider.setValue(self.color.red())
        self.g_slider.setValue(self.color.green())
        self.b_slider.setValue(self.color.blue())
        self.a_slider.setValue(self.color.alpha())
        self.h_slider.setValue(self.color.hue())
        self.s_slider.setValue(self.color.saturation())
        self.v_slider.setValue(self.color.value())

        self.r_value.setText(str(self.color.red()))
        self.g_value.setText(str(self.color.green()))
        self.b_value.setText(str(self.color.blue()))
        self.a_value.setText(str(self.color.alpha()))
        self.h_value.setText(str(self.color.hue()))
        self.s_value.setText(str(self.color.saturation()))
        self.v_value.setText(str(self.color.value()))
        
        self._update_preview()
        self.updating = False

    def _update_preview(self):
        if hasattr(self, 'preview'):
            self.preview.setStyleSheet(f"background-color: {self.color.name()}; border: 2px solid white; border-radius: 15px;")

        if hasattr(self, 'hex_input') and not self.updating:
            self.hex_input.setText(self.color.name().upper())
'''
    def _update_from_hex(self):
        """Update color from hex input"""
        if self.updating:
            return
        
        hex_text = self.hex_input.text().strip()

        if not hex_text.startswith('#'):
            if len(hex_text) == 6 and all(c in '0123456789ABCDEFabcdef' for c in hex_text):
                hex_text = '#' + hex_text
            else:
                return
        
        if len(hex_text) != 7 or not all(c in '0123456789ABCDEFabcdef' for c in hex_text[1:]):
            return
        
        try:
            self.updating = True
            new_color = QColor(hex_text)
            if new_color.isValid():
                self.color = new_color

                self.r_slider.setValue(self.color.red())
                self.g_slider.setValue(self.color.green())
                self.b_slider.setValue(self.color.blue())
                self.h_slider.setValue(self.color.hue())
                self.s_slider.setValue(self.color.saturation())
                self.v_slider.setValue(self.color.value())

                self.r_value.setText(str(self.color.red()))
                self.g_value.setText(str(self.color.green()))
                self.b_value.setText(str(self.color.blue()))
                self.h_value.setText(str(self.color.hue()))
                self.s_value.setText(str(self.color.saturation()))
                self.v_value.setText(str(self.color.value()))

                self.colorChanged.emit(self.color)
                self._update_preview()
        except Exception:
            pass
        finally:
            self.updating = False
'''