from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QDialog, QButtonGroup, QCheckBox
from PyQt6.QtGui import QIcon
from config import CONFIRM_BUTTON_STYLE

class CanvasResizeDialog(QDialog):
    def __init__(self, current_width, current_height):
        super().__init__()
        self.setWindowTitle("Resize Canvas")
        self.setWindowIcon(QIcon("colored_textures/resize_canvas.png"))
        self.setFixedSize(280, 200)

        self.current_width = current_width
        self.current_height = current_height

        layout = QVBoxLayout()
        layout2 = QVBoxLayout()

        self.mode_group = QButtonGroup(self)
        mode_layout = QHBoxLayout()
        wlayout = QHBoxLayout()
        hlayout = QHBoxLayout()
        
        self.keep_ratio_checkbox = QCheckBox("Keep Ratio")
        self.keep_ratio_checkbox.setStyleSheet("font-family: 'Lexend Deca'; font-size: 15px;")
        self.keep_ratio_checkbox.setChecked(True)
        mode_layout.addWidget(self.keep_ratio_checkbox)

        self.width_input = QLineEdit(str(current_width))
        self.width_input.setStyleSheet("border: transparent; background: white; border-radius: 5px; height: 50px; font-family: 'Lexend Deca'; font-size: 20px;")
        self.width_input.textChanged.connect(self.update_hlabel)
        wlabel = QLabel("Width ")
        wlabel.setStyleSheet("font-family: 'Lexend Deca'; font-size: 17px;")
        wlayout.addWidget(wlabel)
        wlayout.addWidget(self.width_input)

        self.height_input = QLineEdit(str(current_height))
        self.height_input.setStyleSheet("border: transparent; background: white; border-radius: 5px; height: 50px; font-family: 'Lexend Deca'; font-size: 20px;")
        self.height_input.textChanged.connect(self.update_wlabel)
        hlabel = QLabel("Height ")
        hlabel.setStyleSheet("font-family: 'Lexend Deca'; font-size: 17px;")
        hlayout.addWidget(hlabel)
        hlayout.addWidget(self.height_input)

        self.w_init = self.width_input.text()
        self.h_init = self.height_input.text()

        button_layout = QHBoxLayout()
        confirm = QPushButton("Confirm")
        confirm.setStyleSheet(CONFIRM_BUTTON_STYLE)
        confirm.clicked.connect(self.accept)
        button_layout.addWidget(confirm)
        layout.addLayout(mode_layout)
        layout2.addLayout(wlayout)
        layout2.addLayout(hlayout)
        layout.addLayout(layout2)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def update_hlabel(self):
        if self.keep_ratio_checkbox.isChecked():
            self.height_input.setText(str(float(self.width_input.text()) * (float(self.w_init) / float(self.h_init))))

    def update_wlabel(self):
        if self.keep_ratio_checkbox.isChecked() and self.height_input.text() != "":
            self.width_input.setText(str(float(self.height_input.text()) * (float(self.h_init) / float(self.w_init))))

    def get_values(self):
        try:
            w = float(self.width_input.text())
            h = float(self.height_input.text())
            return int(w), int(h)
        except ValueError:
            return self.current_width, self.current_height
