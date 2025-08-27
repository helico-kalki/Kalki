import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import QSize
from PIL import Image, ImageFilter, ImageEnhance, ImageQt
from config import *

app = QApplication(sys.argv)

window = QMainWindow()
window.setGeometry(*WINSIZE)
window.setWindowTitle(WINTITLE)
window.setWindowIcon(QIcon(WINICON))

w_palette = window.palette()
w_palette.setColor(QPalette.ColorRole.Window, QColor(WINCOLOR))
window.setPalette(w_palette)
window.setAutoFillBackground(True)

top_toolbar = QToolBar()
top_toolbar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
top_toolbar.setStyleSheet("QToolBar { border: none; background: transparent; }")

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


class Canvas(QFrame):
    def __init__(self):
        super().__init__()

        self.image = QPixmap(900, 900)
        self.image.fill(Qt.GlobalColor.white)

        self.drawing = False
        self.last_point = QPoint()
        self.pan_active = False
        self.pan_offset = QPoint(0, 0)
        self.pan_start = QPoint()

        self.zoom_level = 1.0

        self.pen_color = QColor(PENCOLOR)
        self.pen_width = PENWIDTH
        self.pen_cap = Qt.PenCapStyle.RoundCap
        self.pen_join = Qt.PenJoinStyle.RoundJoin

        self.undo_stack = []
        self.redo_stack = []

        self.shape_mode = None  
        self.shape_start = None
        self.shape_end = None

        self.eyedropper_mode = False

        self.selection_mode = None  
        self.selection_active = False
        self.selection_rect = None
        self.selection_path = None
        self.selection_pixmap = None
        self.moving_selection = False
        self.selection_offset = QPoint(0, 0)
        self.selection_start = None

        self.move_mode = False
        self.move_rect = None
        self.move_pixmap = None
        self.move_offset = QPoint(0, 0)
        self.move_scale = 1.0
        self.move_rotation = 0.0
        self.move_dragging = False
        self.move_scaling = None  
        self.move_rotating = False
        self.move_last_pos = None
        self.move_original_pixmap = None
        self.move_original_rect = None
        self.move_scale_x = 1.0
        self.move_scale_y = 1.0

        self.text_mode = False
        self.text_options = {
            "font": QFont(FONT, TEXTSIZE),
            "color": QColor(TEXTCOLOR),
            "bold": TEXT_BOLD,
            "italic": TEXT_ITALIC,
            "underline": TEXT_UNDERLINE,
            "strikeout": TEXT_STRIKEOUT,
            "size": TEXTSIZE,
            "text": ""
        }

        self.setAttribute(Qt.WidgetAttribute.WA_TabletTracking, True)

    def set_text_mode(self, active: bool):
        self.text_mode = active

    def set_text_options(self, options: dict):
        self.text_options.update(options)

    def set_selection_mode(self, mode):

        if mode in ("ellipse", "lasso", None):
            self.selection_active = False
            self.selection_rect = None
            self.selection_path = None
            self.selection_pixmap = None
            self.moving_selection = False
            self.selection_offset = QPoint(0, 0)
            self.selection_start = None

        self.selection_mode = mode
        self.update()

    def set_shape_mode(self, mode):
        self.shape_mode = mode

    def set_pen_color(self, color: QColor):
        self.pen_color = color

    def set_pen_width(self, width: int):
        self.pen_width = width

    def set_zoom_level(self, zoom: float):
        self.zoom_level = max(0.1, min(zoom, 5.0))
        self.update()

    def zoom_in(self):
        self.set_zoom_level(self.zoom_level * 1.1)

    def zoom_out(self):
        self.set_zoom_level(self.zoom_level / 1.1)

    def reset_view(self):
        self.zoom_level = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.update()

    def get_scaled_mouse_pos(self, event: QMouseEvent):
        raw = event.position().toPoint()
        return QPoint(
            int((raw.x() - self.pan_offset.x()) / self.zoom_level),
            int((raw.y() - self.pan_offset.y()) / self.zoom_level)
        )
    
    def set_eyedropper_mode(self, active: bool):
        self.eyedropper_mode = active

    def mousePressEvent(self, event: QMouseEvent):
        if self.text_mode:
            pos = self.get_scaled_mouse_pos(event)
            self.draw_text_at(pos)
            self.text_mode = False
            self.update()
            return
        pos = self.get_scaled_mouse_pos(event)
        if self.move_mode and self.move_rect:

            tl = self.move_rect.topLeft() + self.move_offset
            br = self.move_rect.bottomRight() + self.move_offset
            center = self.move_rect.center() + self.move_offset
            if (pos - tl).manhattanLength() < 15:
                self.move_scaling = "tl"
                self.move_last_pos = pos
                return
            elif (pos - br).manhattanLength() < 15:
                self.move_scaling = "br"
                self.move_last_pos = pos
                return
            elif (pos - center).manhattanLength() < 15:
                self.move_rotating = True
                self.move_last_pos = pos
                return
            elif self.move_rect.translated(self.move_offset).contains(pos):
                self.move_dragging = True
                self.move_last_pos = pos
                return

        if self.selection_mode and (not self.selection_rect and not self.selection_path or self.selection_active):
            self.selection_active = True
            self.selection_start = self.get_scaled_mouse_pos(event)
            if self.selection_mode == "lasso":
                self.selection_path = QPainterPath()
                self.selection_path.moveTo(self.selection_start)
            return

        if self.moving_selection and self.selection_pixmap:
            self.selection_start = self.get_scaled_mouse_pos(event)
            return
        if self.eyedropper_mode:
            pos = self.get_scaled_mouse_pos(event)
            if 0 <= pos.x() < self.image.width() and 0 <= pos.y() < self.image.height():
                color = self.image.toImage().pixelColor(pos)
                self.set_pen_color(color)
            self.eyedropper_mode = False  
            self.update()
            return
        if self.shape_mode:
            self.shape_start = self.get_scaled_mouse_pos(event)
            self.shape_end = self.shape_start
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = self.get_scaled_mouse_pos(event)
            self.undo_stack.append(self.image.copy())
            self.redo_stack.clear()
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.pan_active = True
            self.pan_start = event.position().toPoint()
                
    def mouseMoveEvent(self, event: QMouseEvent):
        pos = self.get_scaled_mouse_pos(event)
        if self.move_mode and self.move_rect:
            if self.move_scaling:

                if self.move_scaling == "tl":
                    new_rect = QRect(pos, self.move_rect.bottomRight())
                else:
                    new_rect = QRect(self.move_rect.topLeft(), pos)
                new_rect = new_rect.normalized()
                self.move_rect = new_rect

                orig_size = self.move_original_rect.size()
                new_size = self.move_rect.size()
                if orig_size.width() > 0 and orig_size.height() > 0:
                    scale_x = new_size.width() / orig_size.width()
                    scale_y = new_size.height() / orig_size.height()

                    self.move_scale_x = scale_x
                    self.move_scale_y = scale_y
                self.move_last_pos = pos
                self.update()
                return
            elif self.move_rotating:
                center = self.move_rect.center() + self.move_offset
                v1 = self.move_last_pos - center
                v2 = pos - center
                angle = QLineF(center, self.move_last_pos).angleTo(QLineF(center, pos))
                self.move_rotation += angle
                self.move_last_pos = pos
                self.update()
                return

        pos = self.get_scaled_mouse_pos(event)
        if self.move_mode and self.move_rect:
            if self.move_dragging:
                delta = pos - self.move_last_pos
                self.move_offset += delta
                self.move_last_pos = pos
                self.update()
                return
            elif self.move_scaling:
                if self.move_scaling == "tl":
                    new_rect = QRect(pos, self.move_rect.bottomRight())
                else:
                    new_rect = QRect(self.move_rect.topLeft(), pos)
                self.move_rect = new_rect.normalized()
                self.update()
                self.move_last_pos = pos
                return
            elif self.move_rotating:
                center = self.move_rect.center() + self.move_offset
                v1 = self.move_last_pos - center
                v2 = pos - center
                angle = QLineF(center, self.move_last_pos).angleTo(QLineF(center, pos))
                self.move_rotation += angle
                self.move_last_pos = pos
                self.update()
                return
        if self.selection_active and self.selection_mode:
            current = self.get_scaled_mouse_pos(event)
            if self.selection_mode == "rect" or self.selection_mode == "ellipse":
                self.selection_rect = QRect(self.selection_start, current)
            elif self.selection_mode == "lasso":
                self.selection_path.lineTo(current)
            self.update()
            return
        elif self.moving_selection and self.selection_pixmap:
            current = self.get_scaled_mouse_pos(event)
            delta = current - self.selection_start
            self.selection_offset += delta
            self.selection_start = current
            self.update()
            return
        if self.shape_mode and self.shape_start:
            self.shape_end = self.get_scaled_mouse_pos(event)
            self.update()
            return
        if self.drawing:
            current = self.get_scaled_mouse_pos(event)
            if self.can_draw_at(current):
                painter = QPainter(self.image)
                pen = QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine,
                        self.pen_cap, self.pen_join)
                painter.setPen(pen)
                painter.drawLine(self.last_point, current)
                self.last_point = current
                self.update()
            else:
                self.last_point = current
            return
        if self.pan_active:
            delta = event.position().toPoint() - self.pan_start
            self.pan_offset += delta
            self.pan_start = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.move_mode:
            self.move_dragging = False
            self.move_scaling = None
            self.move_rotating = False
            self.move_last_pos = None
            self.update()
            return
        if self.selection_active and self.selection_mode:
            self.selection_active = False
            self.update()
            return
        if self.moving_selection and self.selection_pixmap:
            self.moving_selection = False
            self.update()
            return

        if self.shape_mode and self.shape_start and self.shape_end:

            if self.can_draw_at(self.shape_start) and self.can_draw_at(self.shape_end):
                painter = QPainter(self.image)
                pen = QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine,
                        self.pen_cap, self.pen_join)
                painter.setPen(pen)
                rect = QRect(self.shape_start, self.shape_end)
                if self.shape_mode == "rect":
                    painter.drawRect(rect)
                elif self.shape_mode == "ellipse":
                    painter.drawEllipse(rect)
                elif self.shape_mode == "line":
                    painter.drawLine(self.shape_start, self.shape_end)
                elif self.shape_mode == "triangle":
                    p1 = QPoint(rect.center().x(), rect.top())
                    p2 = QPoint(rect.left(), rect.bottom())
                    p3 = QPoint(rect.right(), rect.bottom())
                    painter.drawPolygon(p1, p2, p3)

            self.shape_start = None
            self.shape_end = None
            self.update()
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.pan_active = False

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            self.update()
        else:
            event.ignore()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        scaled = self.image.scaled(
            self.image.size() * self.zoom_level,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        painter.drawPixmap(self.pan_offset, scaled)


        if not self.move_mode:
            pen = QPen(QColor(SELCOLOR), SELWIDTH, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            if self.selection_mode == "rect" and self.selection_rect:
                rect = QRect(
                    self.selection_rect.topLeft() * self.zoom_level + self.pan_offset,
                    self.selection_rect.bottomRight() * self.zoom_level + self.pan_offset
                )
                painter.drawRect(rect)
            elif self.selection_mode == "ellipse" and self.selection_rect:
                rect = QRect(
                    self.selection_rect.topLeft() * self.zoom_level + self.pan_offset,
                    self.selection_rect.bottomRight() * self.zoom_level + self.pan_offset
                )
                painter.drawEllipse(rect)
            elif self.selection_mode == "lasso" and self.selection_path:
                path = QPainterPath(self.selection_path)
                transform = QTransform()
                transform.translate(self.pan_offset.x(), self.pan_offset.y())
                transform.scale(self.zoom_level, self.zoom_level)
                painter.drawPath(path * transform)


        if self.move_mode and self.move_rect and self.move_pixmap:
            painter.save()
            center = self.move_rect.center() * self.zoom_level + self.pan_offset + self.move_offset * self.zoom_level
            painter.translate(center)
            painter.rotate(self.move_rotation)
            painter.scale(self.move_scale_x, self.move_scale_y)
            painter.translate(-self.move_original_pixmap.width() / 2, -self.move_original_pixmap.height() / 2)
            painter.drawPixmap(0, 0, self.move_original_pixmap)
            painter.restore()

            pen = QPen(QColor(SELCOLOR), SELWIDTH, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            rect = QRect(
                self.move_rect.topLeft() * self.zoom_level + self.pan_offset + self.move_offset * self.zoom_level,
                self.move_rect.bottomRight() * self.zoom_level + self.pan_offset + self.move_offset * self.zoom_level
            )
            painter.drawRect(rect)

            painter.setBrush(QColor("white"))
            painter.setPen(QPen(QColor(SELVCOLOR), SELVSIZE))
            painter.drawEllipse(rect.topLeft(), SELVWIDTH, SELVWIDTH)
            painter.drawEllipse(rect.bottomRight(), SELVWIDTH, SELVWIDTH)


        super().paintEvent(event)
    
    def copy_selection(self):
        clipboard = QApplication.clipboard()

        if not (self.selection_rect or self.selection_path):
            clipboard.setPixmap(self.image)
        elif self.selection_mode == "rect" and self.selection_rect:
            pixmap = self.image.copy(self.selection_rect)
            clipboard.setPixmap(pixmap)
        elif self.selection_mode == "ellipse" and self.selection_rect:
            mask = QPixmap(self.selection_rect.size())
            mask.fill(Qt.GlobalColor.transparent)
            mask_painter = QPainter(mask)
            mask_painter.setBrush(Qt.GlobalColor.white)
            mask_painter.setPen(Qt.PenStyle.NoPen)
            mask_painter.drawEllipse(QRect(QPoint(0,0), self.selection_rect.size()))
            mask_painter.end()
            temp = self.image.copy(self.selection_rect)
            temp.setMask(mask.createMaskFromColor(Qt.GlobalColor.transparent))
            clipboard.setPixmap(temp)
        elif self.selection_mode == "lasso" and self.selection_path:
            rect = self.selection_path.boundingRect().toRect()
            mask = QPixmap(rect.size())
            mask.fill(Qt.GlobalColor.transparent)
            mask_painter = QPainter(mask)
            mask_painter.setBrush(Qt.GlobalColor.white)
            mask_painter.setPen(Qt.PenStyle.NoPen)
            mask_painter.drawPath(self.selection_path.translated(-rect.topLeft()))
            mask_painter.end()
            temp = self.image.copy(rect)
            temp.setMask(mask.createMaskFromColor(Qt.GlobalColor.transparent))
            clipboard.setPixmap(temp)
        self.update()

    def paste_selection(self):
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()
        if not pixmap.isNull():
            pos = self.selection_rect.topLeft() if self.selection_rect else QPoint(0, 0)
            painter = QPainter(self.image)
            painter.drawPixmap(pos, pixmap)
            painter.end()
            self.update()
            self.move_mode = True
            self.move_pixmap = pixmap
            self.move_rect = QRect(pos, pixmap.size())
            self.move_offset = QPoint(0, 0)
            self.move_scale = 1.0
            self.move_rotation = 0.0
            self.move_original_pixmap = QPixmap(pixmap)
            self.move_original_rect = QRect(self.move_rect)

    def enable_move_selection(self):
        if self.selection_pixmap or self.selection_rect:
            self.move_mode = True
            if self.selection_pixmap:
                self.move_pixmap = self.selection_pixmap
                self.move_rect = QRect(self.selection_rect.topLeft(), self.selection_pixmap.size())
            elif self.selection_rect:
                self.move_pixmap = self.image.copy(self.selection_rect)
                self.move_rect = self.selection_rect
            self.move_offset = QPoint(0, 0)
            self.move_scale = 1.0
            self.move_rotation = 0.0
            self.move_original_pixmap = QPixmap(self.move_pixmap)
            self.move_original_rect = QRect(self.move_rect)
            self.update()

    def can_draw_at(self, pos: QPoint):

        if self.selection_mode == "rect" and self.selection_rect:
            return self.selection_rect.normalized().contains(pos)
        elif self.selection_mode == "ellipse" and self.selection_rect:
            rect = self.selection_rect.normalized()
            rx = rect.width() / 2
            ry = rect.height() / 2
            cx = rect.center().x()
            cy = rect.center().y()
            return ((pos.x()-cx)**2)/rx**2 + ((pos.y()-cy)**2)/ry**2 <= 1
        elif self.selection_mode == "lasso" and self.selection_path:
            return self.selection_path.contains(QPointF(pos))
        return True

    def set_pen_cap_style(self, cap_style: Qt.PenCapStyle):
        self.pen_cap = cap_style

    def set_pen_join_style(self, join_style: Qt.PenJoinStyle):
        self.pen_join = join_style

    def set_pixmap(self, pixmap: QPixmap):
        self.image = pixmap
        self.update()

    def set_blur_radius(self, radius):
        self.blur_radius = radius

    def apply_blur(self, blur_radius):

        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())  
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)

        blurred = pil_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        data = blurred.tobytes("raw", "RGBA")
        qimg_blur = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_blur)
        self.update()
            
    def remove_blur(self):
        self.setGraphicsEffect(None)

    def apply_gradient(self, color1=QColor("white"), color2=QColor("blue")):
        painter = QPainter(self.image)
        gradient = QLinearGradient(0, 0, self.image.width(), 0)
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)
        painter.fillRect(self.image.rect(), gradient)
        painter.end()
        self.update()

    def tabletEvent(self, event: QTabletEvent):
        if hasattr(self, "brush_active") and self.brush_active:
            pressure = event.pressure()
            dynamic_width = int(2 + pressure * 28)
            self.set_pen_width(dynamic_width)
            scaled_pos = QPoint( 
                int((event.position().x() - self.pan_offset.x()) / self.zoom_level),
                int((event.position().y() - self.pan_offset.y()) / self.zoom_level)
            )
            if event.type() == QEvent.Type.TabletPress:
                self.drawing = True
                self.last_point = scaled_pos
                event.accept()
            elif event.type() == QEvent.Type.TabletMove and self.drawing:
                if self.can_draw_at(scaled_pos):
                    painter = QPainter(self.image)
                    pen = QPen(self.pen_color, dynamic_width, Qt.PenStyle.SolidLine,
                            self.pen_cap, self.pen_join)
                    painter.setPen(pen)
                    painter.drawLine(self.last_point, scaled_pos)
                    self.last_point = scaled_pos
                    self.update()
                event.accept()
            elif event.type() == QEvent.Type.TabletRelease:
                self.drawing = False
                event.accept()
        else:
            event.ignore()

    def fill_background(self, color: QColor):
        painter = QPainter(self.image)
        painter.fillRect(self.image.rect(), color)
        painter.end()
        self.update()

    def disable_move_mode(self):

        if self.move_mode and self.move_pixmap and self.move_rect:
            painter = QPainter(self.image)
            painter.save()

            target_rect = QRect(
                self.move_rect.topLeft() + self.move_offset,
                QSize(
                    int(self.move_original_pixmap.width() * self.move_scale_x),
                    int(self.move_original_pixmap.height() * self.move_scale_y)
                )
            )

            transform = QTransform()
            center = target_rect.center()
            transform.translate(center.x(), center.y())
            transform.rotate(self.move_rotation)
            transform.translate(-center.x(), -center.y())
            painter.setTransform(transform)
            painter.drawPixmap(target_rect, self.move_original_pixmap)
            painter.restore()

        self.move_mode = False
        self.move_dragging = False
        self.move_scaling = None
        self.move_rotating = False
        self.move_last_pos = None
        self.move_pixmap = None
        self.move_rect = None
        self.move_offset = QPoint(0, 0)
        self.move_scale_x = 1.0
        self.move_scale_y = 1.0
        self.move_rotation = 0.0
        self.move_original_pixmap = None
        self.move_original_rect = None
        self.update()

    def apply_contour(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        filtered = pil_img.filter(ImageFilter.CONTOUR)
        data = filtered.tobytes("raw", "RGBA")
        qimg_filtered = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_filtered)
        self.update()

    def apply_detail(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        filtered = pil_img.filter(ImageFilter.DETAIL)
        data = filtered.tobytes("raw", "RGBA")
        qimg_filtered = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_filtered)
        self.update()


    def apply_emboss(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        filtered = pil_img.filter(ImageFilter.EMBOSS)
        data = filtered.tobytes("raw", "RGBA")
        qimg_filtered = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_filtered)
        self.update()

    def apply_find_edges(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        filtered = pil_img.filter(ImageFilter.FIND_EDGES)
        data = filtered.tobytes("raw", "RGBA")
        qimg_filtered = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_filtered)
        self.update()

    def apply_sharpen(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        filtered = pil_img.filter(ImageFilter.SHARPEN)
        data = filtered.tobytes("raw", "RGBA")
        qimg_filtered = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_filtered)
        self.update()

    def apply_smooth(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        filtered = pil_img.filter(ImageFilter.SMOOTH)
        data = filtered.tobytes("raw", "RGBA")
        qimg_filtered = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_filtered)
        self.update()

    def apply_smooth_more(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        filtered = pil_img.filter(ImageFilter.SMOOTH_MORE)
        data = filtered.tobytes("raw", "RGBA")
        qimg_filtered = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_filtered)
        self.update()

    def apply_unsharp_mask(self, radius=2, percent=150, threshold=3):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        filtered = pil_img.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
        data = filtered.tobytes("raw", "RGBA")
        qimg_filtered = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_filtered)
        self.update()

    def invert_colors(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        from PIL import ImageOps
        inverted = ImageOps.invert(pil_img.convert("RGB")).convert("RGBA")
        data = inverted.tobytes("raw", "RGBA")
        qimg_invert = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_invert)
        self.update()

    def draw_text_at(self, pos: QPoint):

        painter = QPainter(self.image)
        font = QFont(self.text_options["font"])
        font.setPointSize(self.text_options["size"])
        font.setBold(self.text_options["bold"])
        font.setItalic(self.text_options["italic"])
        font.setUnderline(self.text_options["underline"])
        font.setStrikeOut(self.text_options["strikeout"])
        painter.setFont(font)
        painter.setPen(QPen(self.text_options["color"]))
        painter.drawText(pos, self.text_options["text"])
        painter.end()

    def mirror_horizontal(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)

        mirrored = pil_img.transpose(Image.FLIP_LEFT_RIGHT)
        data = mirrored.tobytes("raw", "RGBA")
        qimg_mirrored = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_mirrored)
        self.update()

    def mirror_vertical(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)

        mirrored = pil_img.transpose(Image.FLIP_TOP_BOTTOM)
        data = mirrored.tobytes("raw", "RGBA")
        qimg_mirrored = QImage(data, width, height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_mirrored)
        self.update()

    def rotate_90_cw(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)

        rotated = pil_img.transpose(Image.ROTATE_270)
        data = rotated.tobytes("raw", "RGBA")
        qimg_rotated = QImage(data, rotated.width, rotated.height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_rotated)
        self.update()

    def rotate_90_ccw(self):
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)

        rotated = pil_img.transpose(Image.ROTATE_90)
        data = rotated.tobytes("raw", "RGBA")
        qimg_rotated = QImage(data, rotated.width, rotated.height, QImage.Format.Format_RGBA8888)
        self.image = QPixmap.fromImage(qimg_rotated)
        self.update()

    def crop_to_selection(self):
        # Stelle sicher, dass eine Auswahl existiert
        if not self.selection_rect or self.selection_rect.isNull():
            return  # Keine gültige Auswahl

        # Hole das aktuelle Bild als QImage
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)

        # Berechne den Ausschnitt basierend auf dem QRect
        crop_rect = self.selection_rect.intersected(qimg.rect())  # Begrenzung auf Bildgröße
        cropped = qimg.copy(crop_rect)

        # Konvertiere zurück zu QPixmap
        self.image = QPixmap.fromImage(cropped)
        self.selection_rect = None  # Auswahl zurücksetzen
        self.update()

canvas = Canvas()
canvas.setStyleSheet("background-color: lightgray;")
canvas.setFixedSize(900, 900)
canvas_and_toolbar = QVBoxLayout()
canvas_and_toolbar.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignCenter)

undo_action = QAction(QIcon("colored_textures/undo.png"), "Undo", window)
undo_action.triggered.connect(canvas.undo)
undo_action.setShortcut(UNDO)

redo_action = QAction(QIcon("colored_textures/redo.png"), "Redo", window)
redo_action.triggered.connect(canvas.redo)
redo_action.setShortcut(REDO)

zoom_in = QAction(QIcon("colored_textures/zoom_in.png"), "Zoom In", window)
zoom_in.triggered.connect(canvas.zoom_in)
zoom_in.setShortcut(ZOOM_IN)

zoom_out = QAction(QIcon("colored_textures/zoom_out.png"), "Zoom Out", window)
zoom_out.triggered.connect(canvas.zoom_out)
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
effects_action.setIcon(QIcon("colored_textures/effect_1.png"))
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

effects_action.setMenu(effects_menu)
effects_menu.setStyleSheet("""
        QMenu { background-color: #b5b5b5;
                font-family: 'Lexend Deca'; font-size: 17px;
            }
        QMenu::item {
            padding: 4px 12px 4px 24px; /* Platz für großes Icon links */
            height: 20px; 
            }
        QMenu::item:selected { background-color: #d3d3d3; }
        QMenu::icon { width: 35px; height: 35px; margin-right: 8px; margin-left: 16px; }
        QMenu::separator { height: 1px; background-color: #d3d3d3; margin: 5px 0; }
        QMenu::item:disabled { color: gray; }
        QMenu::item:checked { background-color: #909090; }
        """)
effects_menu.addAction(ca_action)
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

top_toolbar.addAction(new_action)
top_toolbar.addAction(import_action)
top_toolbar.addAction(export_action)
top_toolbar.addAction(undo_action)
top_toolbar.addAction(redo_action)
top_toolbar.addAction(copy_selection)
top_toolbar.addAction(paste_selection)
top_toolbar.addAction(zoom_in)
top_toolbar.addAction(zoom_out)
top_toolbar.addAction(rotate_90_cw_action)
top_toolbar.addAction(rotate_90_ccw_action)
top_toolbar.addAction(mirror_horizontal_action)
top_toolbar.addAction(mirror_vertical_action)
top_toolbar.addAction(crop_selection_action)
top_toolbar.addAction(effects_action)

bottom_toolbar = QFrame()
bottom_toolbar.setStyleSheet("background-color: lightgray;")
bottom_layout = QHBoxLayout()
bottom_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
bottom_toolbar.setLayout(bottom_layout)

move_button = QToolButton()
move_button.setIcon(QIcon("colored_textures/move.png"))
move_button.setIconSize(QSize(45,45))
move_button.setStyleSheet("border: none; background: transparent;")
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
selection_button.setStyleSheet("border: none; background: transparent;")
selection_button.setCheckable(False)
selection_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)  
selection_menu = QMenu()
selection_button.setMenu(selection_menu)
selection_menu.setStyleSheet("""
        QMenu { background-color: #b5b5b5;
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
        """)
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

selection_menu.addAction(rselect_button)
selection_menu.addAction(cselect_button)
selection_menu.addAction(lselect_button)
selection_menu.addAction(clearsel_button)

shapes = QToolButton(window)
shapes.setIcon(QIcon("colored_textures/shapes.png"))
shapes.setIconSize(QSize(45,45))
shapes.setStyleSheet("border: none; background: transparent;")
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

shapes_menu.setStyleSheet("""
        QMenu { background-color: #b5b5b5;
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
        """)


shapes_menu.addAction(rectangle)
shapes_menu.addAction(triangle)
shapes_menu.addAction(ellipse)
shapes_menu.addAction(lines)
shapes_menu.addAction(disableshape)

text_button = QToolButton()
text_button.setIcon(QIcon("colored_textures/text.png"))
text_button.setIconSize(QSize(45,45))
text_button.setStyleSheet("border: none; background: transparent;")
text_button.setCheckable(False)
def activate_text_tool():
    open_text_options_dialog()
    canvas.set_text_mode(True)
text_button.clicked.connect(activate_text_tool)
text_button.setShortcut("T")
bottom_layout.addWidget(text_button)

pen_button = QToolButton()
pen_button.setIcon(QIcon("colored_textures/pen.png"))
pen_button.setIconSize(QSize(45,45))
pen_button.setStyleSheet("border: none; background: transparent;")
pen_button.setCheckable(False)
def activate_pen_tool():
    canvas.set_pen_color(QColor(PENCOLOR))
    canvas.set_pen_width(PENWIDTH)
    canvas.set_pen_cap_style(Qt.PenCapStyle.RoundCap),
    canvas.set_pen_join_style(Qt.PenJoinStyle.RoundJoin)
    canvas.brush_active = False
    canvas.drawing = False
pen_button.clicked.connect(activate_pen_tool)          
pen_button.clicked.connect(lambda: [
    width_slider.setValue(PENWIDTH),
    width_text.setText(str(PENWIDTH))
])
pen_button.setShortcut(PEN)

marker_button = QToolButton()
marker_button.setIcon(QIcon("colored_textures/marker.png"))
marker_button.setIconSize(QSize(45,45))
marker_button.setStyleSheet("border: none; background: transparent;")
marker_button.setCheckable(False)
def use_marker_tool():
    canvas.set_pen_color(QColor(*MARKERCOLOR))
    canvas.set_pen_width(MARKERWIDTH)
    canvas.set_pen_cap_style(Qt.PenCapStyle.FlatCap),
    canvas.set_pen_join_style(Qt.PenJoinStyle.MiterJoin)
    canvas.brush_active = False
marker_button.clicked.connect(use_marker_tool)
marker_button.clicked.connect(lambda: [
    width_slider.setValue(MARKERWIDTH),
    width_text.setText(str(MARKERWIDTH))
])
marker_button.setShortcut(MARKER)

brush_button = QToolButton()
brush_button.setIcon(QIcon("colored_textures/brush.png"))
brush_button.setIconSize(QSize(45,45))
brush_button.setStyleSheet("border: none; background: transparent;")
brush_button.setCheckable(False)
def use_brush_tool():
        canvas.set_pen_color(QColor(BRUSHCOLOR))
        canvas.set_pen_width(BRUSHWIDTH)
        canvas.set_pen_cap_style(Qt.PenCapStyle.RoundCap)
        canvas.set_pen_join_style(Qt.PenJoinStyle.RoundJoin)
        canvas.brush_active = True
brush_button.clicked.connect(use_brush_tool)
brush_button.clicked.connect(lambda: [
    width_slider.setValue(BRUSHWIDTH),
    width_text.setText(str(BRUSHWIDTH))
])
brush_button.setShortcut(BRUSH)

erase_button = QToolButton()
erase_button.setIcon(QIcon("colored_textures/eraser.png"))
erase_button.setIconSize(QSize(45,45))
erase_button.setStyleSheet("border: none;; background: transparent;")
erase_button.setCheckable(True)
def use_erase_tool():
    canvas.set_pen_color(QColor(ERASERCOLOR))
    canvas.set_pen_width(ERASERWIDTH)
    canvas.set_pen_cap_style(Qt.PenCapStyle.RoundCap),
    canvas.set_pen_join_style(Qt.PenJoinStyle.RoundJoin)
erase_button.clicked.connect(use_erase_tool)
erase_button.clicked.connect(lambda: [
    width_slider.setValue(ERASERWIDTH),
    width_text.setText(str(ERASERWIDTH))
])
erase_button.setShortcut(ERASER)

width_text = QLineEdit()
width_text.setText("2")
width_text.setFixedSize(35,35)
width_text.setStyleSheet("border: transparent; background: transparent;")
width_text.setFont(QFont(FONT, 15))
width_text.setValidator(QIntValidator(1, 150))
def update_width_from_text(text):
    if not text.isdigit():
        return  
    value = int(text)
    canvas.set_pen_width(value)
    width_slider.setValue(value)
width_text.textChanged.connect(update_width_from_text)

width_slider = QSlider(Qt.Orientation.Horizontal)
width_slider.setRange(1, 150)
width_slider.setValue(2)
width_slider.setFixedSize(100,30)
width_slider.setStyleSheet("""
    QSlider::groove:horizontal { background: white; height: 25px; border-radius: 5px; }
    QSlider::handle:horizontal { background: #5b5b5b; width: 15px; height: 35px; border-radius: 5px; }
        """)
width_slider.setSliderDown(True)
width_slider.valueChanged.connect(lambda value: [
    canvas.set_pen_width(value),
    width_text.setText(str(value))
    ])

color_bucket = QToolButton()
color_bucket.setIcon(QIcon("colored_textures/bucket.png"))
color_bucket.setIconSize(QSize(45,45))
color_bucket.setStyleSheet("border: none; background: transparent;")
color_bucket.clicked.connect(lambda: [
    canvas.fill_background(canvas.pen_color)
])
color_bucket.setShortcut(BUCKET)

gradient = QToolButton()
gradient.setIcon(QIcon("colored_textures/gradient.png"))
gradient.setIconSize(QSize(45,45))
gradient.setStyleSheet("border: none; background: transparent;")
def use_gradient():
    options = QColorDialog.ColorDialogOption.ShowAlphaChannel
    color1 = QColorDialog.getColor(canvas.pen_color, window, "Pick Color 1 (Left)", options)
    color2 = QColorDialog.getColor(canvas.pen_color, window, "Pick Color 2 (Right)", options)
    if color1.isValid():
        canvas.apply_gradient(color1, color2)
gradient.clicked.connect(use_gradient)
gradient.setShortcut(GRADIENT)

color_picker = QToolButton()
color_picker.setIcon(QIcon("colored_textures/color_picker.png"))
color_picker.setIconSize(QSize(45,45))
color_picker.setStyleSheet("border: none; background: transparent;")
color_picker.setCheckable(True)
color_picker.clicked.connect(lambda checked: canvas.set_eyedropper_mode(True) if checked else canvas.set_eyedropper_mode(False))
color_picker.setShortcut(COLORPICKER)

color_button = QToolButton()
color_button.setIcon(QIcon("colored_textures/colorwheel.png"))
color_button.setIconSize(QSize(45,45))
color_button.setStyleSheet("border: none; background: transparent;")
color_button.clicked.connect(lambda: open_color_picker())
color_button.setShortcut(COLOR)

spacer0 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
#spacer1 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer2 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
#spacer3 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer4 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
#spacer5 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer6 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

bottom_layout.addSpacerItem(spacer0)
bottom_layout.addWidget(selection_button)
bottom_layout.addWidget(move_button)
bottom_layout.addWidget(shapes)
bottom_layout.addWidget(text_button)
bottom_layout.addSpacerItem(spacer2)
bottom_layout.addWidget(pen_button)
bottom_layout.addWidget(marker_button)
bottom_layout.addWidget(brush_button)
bottom_layout.addWidget(erase_button)
bottom_layout.addWidget(width_slider)
bottom_layout.addWidget(width_text)
bottom_layout.addSpacerItem(spacer4)
bottom_layout.addWidget(color_picker)
bottom_layout.addWidget(color_button)
bottom_layout.addWidget(color_bucket)
bottom_layout.addWidget(gradient)
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
    reply = QMessageBox.warning(
        window, 
        "Clear canvas",
        "Your canvas is about to be cleared. Do you want to proceed?",
        QMessageBox.StandardButton.Yes| QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel
    )
    if reply == QMessageBox.StandardButton.Yes:
        try:
            canvas.image.fill(Qt.GlobalColor.white)
            canvas.update()
        except Exception as e:
            print(f"Error while clearing canvas: {e}")
    elif reply == QMessageBox.StandardButton.Save:
        save_file_dialog(window)

def open_color_picker():
    options = QColorDialog.ColorDialogOption.ShowAlphaChannel
    color = QColorDialog.getColor(canvas.pen_color, window, "Pick Color", options)
    if color.isValid():
        canvas.set_pen_color(color)

def open_blur_options():
    blur_options = QDialog(window)
    blur_options.setWindowTitle("Blur Options")
    blur_options.setWindowIcon(QIcon("colored_textures/blur.png"))
    layout = QVBoxLayout()
    blur_options.setLayout(layout)

    blur_slider = QSlider(Qt.Orientation.Horizontal)
    blur_slider.setRange(1, 35)
    blur_slider.setValue(5)

    blur_text = QLineEdit()
    blur_text.setText("5")
    blur_text.setStyleSheet("border: transparent; background: transparent; font-family: 'Lexend Deca'; font-size: 15px;")
    blur_text.setFixedSize(30,20)
    blur_text.setValidator(QIntValidator(1, 150))

    blur_slider.setFixedSize(100,20)
    blur_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: white; height: 25px; border-radius: 5px; }
            QSlider::handle:horizontal { background: #5b5b5b; width: 15px; height: 35px; border-radius: 5px; }
        """)
    blur_slider.valueChanged.connect(lambda value: [
        canvas.set_blur_radius(value),
        blur_text.setText(str(value))
    ])

    
    def update_value_from_text(text):
        if not text.isdigit():
            return  
        value = int(text)
        canvas.set_blur_radius(value)
        blur_slider.setValue(int(text))
    blur_text.textChanged.connect(update_value_from_text)

    blur_confirm = QPushButton("Confirm")
    blur_confirm.setStyleSheet("border: transparent; background: #00B512; height: 30px; border-radius: 15px; font-family: 'Lexend Deca'; font-size: 17px; color: white;")
    blur_confirm.clicked.connect(lambda: canvas.apply_blur(int(blur_text.text())))
    layout2 = QHBoxLayout()
    layout2.addWidget(blur_slider)
    layout2.addWidget(blur_text)
    layout.addLayout(layout2)
    layout.addWidget(blur_confirm)
    
    
    blur_options.exec()

def open_unsharp_mask_options():
    dialog = QDialog(window)
    dialog.setWindowTitle("Unsharp Mask Options")
    dialog.setWindowIcon(QIcon("colored_textures/unsharp_mask.png"))
    layout = QVBoxLayout(dialog)


    radius_layout = QHBoxLayout()
    radius_label = QLabel("R")
    radius_label.setFont(QFont(FONT, 15))
    radius_slider = QSlider(Qt.Orientation.Horizontal)
    radius_slider.setRange(1, 10)
    radius_slider.setValue(2)
    radius_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: white; height: 25px; border-radius: 5px; }
            QSlider::handle:horizontal { background: #5b5b5b; width: 15px; height: 35px; border-radius: 5px; }
        """)
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
    percent_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: white; height: 25px; border-radius: 5px; }
            QSlider::handle:horizontal { background: #5b5b5b; width: 15px; height: 35px; border-radius: 5px; }
        """)
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
    threshold_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: white; height: 25px; border-radius: 5px; }
            QSlider::handle:horizontal { background: #5b5b5b; width: 15px; height: 35px; border-radius: 5px; }
        """)
    threshold_text = QLineEdit("3")
    threshold_text.setFont(QFont(FONT, 15))
    threshold_text.setStyleSheet("border: transparent; background: transparent;")
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
    confirm_btn.setStyleSheet("border: transparent; background: #00B512; height: 30px; border-radius: 15px; font-family: 'Lexend Deca'; font-size: 17px; color: white;")
    def apply_unsharp():
        radius = int(radius_text.text())
        percent = int(percent_text.text())
        threshold = int(threshold_text.text())
        canvas.apply_unsharp_mask(radius=radius, percent=percent, threshold=threshold)
        dialog.accept()
    confirm_btn.clicked.connect(apply_unsharp)
    layout.addWidget(confirm_btn)

    
    dialog.exec()

def open_text_options_dialog():

    dialog = QDialog(window)
    dialog.setWindowTitle("Text Options")
    dialog.setWindowIcon(QIcon("colored_textures/text.png"))
    layout = QVBoxLayout(dialog)

    text_edit = QLineEdit(canvas.text_options["text"])
    text_edit.setStyleSheet("border: transparent; background: white; border-radius: 5px; height: 50px; font-family: 'Lexend Deca'; font-size: 15px;")
    layout.addWidget(text_edit)

    font_combo = QFontComboBox()
    font_combo.setCurrentFont(canvas.text_options["font"])
    font_combo.setStyleSheet(("""
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
    """))
    layout.addWidget(font_combo)

    size_slider = QSlider(Qt.Orientation.Horizontal)
    size_slider.setRange(8, 128)
    size_slider.setValue(canvas.text_options["size"])
    size_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: white; height: 25px; border-radius: 5px; }
            QSlider::handle:horizontal { background: #5b5b5b; width: 15px; height: 35px; border-radius: 5px; }
        """)
    size_text = QLineEdit(str(canvas.text_options["size"]))
    size_text.setStyleSheet("border: transparent; background: transparent; font-family: 'Lexend Deca'; font-size: 15px;")
    size_text.setFixedWidth(40)
    size_text.setValidator(QIntValidator(8, 128))
    size_layout = QHBoxLayout()
    size_layout.addWidget(size_slider)
    size_layout.addWidget(size_text)
    layout.addLayout(size_layout)

    color_btn = QPushButton()
    color_btn.setFixedSize(30, 30)
    color_btn.setStyleSheet(f"background: {canvas.text_options['color'].name()}; border: transparent; border-radius: 15px;")
    def pick_color():
        color = QColorDialog.getColor(canvas.text_options["color"], window)
        if color.isValid():
            color_btn.setStyleSheet(f"background: {color.name()}; border: transparent; border-radius: 15px;")
            color_btn.setProperty("picked_color", color)
    color_btn.clicked.connect(pick_color)

    bold_btn = QToolButton()
    bold_btn.setText("B")
    bold_btn.setCheckable(True)
    bold_btn.setFont(QFont(FONT, 20))
    bold_btn.setStyleSheet(("""
            QToolButton {
                background: white;
                border: transparent;
                border-radius: 5px;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:checked {
                background: #d3d3d3;
                color: black;
                border: transparent;
            }
        """))
    bold_btn.setChecked(canvas.text_options["bold"])

    italic_btn = QToolButton()
    italic_btn.setText("I")
    italic_btn.setCheckable(True)
    italic_btn.setFont(QFont(FONT, 20))
    italic_btn.setStyleSheet(("""
            QToolButton {
                background: white;
                border: transparent;
                border-radius: 5px;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:checked {
                background: #d3d3d3;
                color: black;
                border: transparent;
            }
        """))
    italic_btn.setChecked(canvas.text_options["italic"])
    
    underline_btn = QToolButton()
    underline_btn.setText("U")
    underline_btn.setCheckable(True)
    underline_btn.setFont(QFont(FONT, 20))
    underline_btn.setStyleSheet(("""
            QToolButton {
                background: white;
                border: transparent;
                border-radius: 5px;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:checked {
                background: #d3d3d3;
                color: black;
                border: transparent;
            }
        """))
    underline_btn.setChecked(canvas.text_options["underline"])

    strike_btn = QToolButton()
    strike_btn.setText("S")
    strike_btn.setCheckable(True)
    strike_btn.setFont(QFont(FONT, 20))
    strike_btn.setStyleSheet(("""
            QToolButton {
                background: white;
                border: transparent;
                border-radius: 5px;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:checked {
                background: #d3d3d3;
                color: black;
                border: transparent;
            }
        """))
    strike_btn.setChecked(canvas.text_options["strikeout"])
    fontopt_layout = QHBoxLayout()
    fontopt_layout.addWidget(color_btn)
    fontopt_layout.addWidget(bold_btn)
    fontopt_layout.addWidget(italic_btn)
    fontopt_layout.addWidget(underline_btn)
    fontopt_layout.addWidget(strike_btn)
    layout.addLayout(fontopt_layout)

    size_slider.valueChanged.connect(lambda v: size_text.setText(str(v)))
    size_text.textChanged.connect(lambda t: size_slider.setValue(int(t) if t.isdigit() else 32))

    confirm_btn = QPushButton("Confirm")
    confirm_btn.setStyleSheet("border: transparent; background: #00B512; height: 30px; border-radius: 15px; font-family: 'Lexend Deca'; font-size: 17px; color: white;")
    def apply_text_options():
        options = {
            "text": text_edit.text(),
            "font": font_combo.currentFont(),
            "size": int(size_text.text()),
            "color": color_btn.property("picked_color") if color_btn.property("picked_color") else canvas.text_options["color"],
            "bold": bold_btn.isChecked(),
            "italic": italic_btn.isChecked(),
            "underline": underline_btn.isChecked(),
            "strikeout": strike_btn.isChecked()
        }
        canvas.set_text_options(options)
        dialog.accept()
    confirm_btn.clicked.connect(apply_text_options)
    layout.addWidget(confirm_btn)

    dialog.exec()

def open_combined_adjustments(canvas):

    dialog = QDialog()
    dialog.setWindowTitle("Combined Adjustments")
    dialog.setWindowIcon(QIcon("colored_textures/ca.png"))
    dialog.setFixedSize(300, 360)

    layout = QVBoxLayout()
    sliders = {}

    def make_slider(name, min_val, max_val, default=0):
        line = QHBoxLayout()
        label = QLabel(name)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.setStyleSheet("""
            QSlider::groove:horizontal { background: white; height: 25px; border-radius: 5px; }
            QSlider::handle:horizontal { background: #5b5b5b; width: 15px; height: 35px; border-radius: 5px; }
        """)
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
    confirm.setStyleSheet("border: transparent; background: #00B512; height: 30px; border-radius: 15px; font-family: 'Lexend Deca'; font-size: 17px; color: white;")
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

window.show()
sys.exit(app.exec())