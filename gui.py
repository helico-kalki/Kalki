import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtCore import QSize
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont, ImageGrab, ImageQt, ImagePalette, ImageSequence, ImageMath, ImageOps, ImageChops, ImageStat


app = QApplication(sys.argv)
#app.setStyle("Fusion")

window = QMainWindow()
window.setGeometry(0, 0, 1000, 1000)
window.setWindowTitle("Kalki")
window.setWindowIcon(QIcon("colored_textures/logo.png"))

w_palette = window.palette()
w_palette.setColor(QPalette.ColorRole.Window, QColor("lightgray"))
window.setPalette(w_palette)
window.setAutoFillBackground(True)

top_toolbar = QToolBar()
top_toolbar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
top_toolbar.setStyleSheet("QToolBar { border: none; background: transparent; }")

new_action = QAction(QIcon("colored_textures/new.png"), "New Project / Clear Canvas", window)
new_action.triggered.connect(lambda: clear_canvas())

import_action = QAction(QIcon("colored_textures/import.png"), "Import Project", window)
import_action.triggered.connect(lambda: open_file_dialog(window))

export_action = QAction(QIcon("colored_textures/export.png"), "Export Project", window)
export_action.triggered.connect(lambda: save_file_dialog(window))

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

        self.pen_color = QColor("black")
        self.pen_width = 2
        self.pen_cap = Qt.PenCapStyle.RoundCap
        self.pen_join = Qt.PenJoinStyle.RoundJoin

        self.undo_stack = []
        self.redo_stack = []

        self.shape_mode = None  
        self.shape_start = None
        self.shape_end = None

        self.eyedropper_mode = False

        self.selection_mode = None  # "rect", "ellipse", "lasso"
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
        self.move_scaling = None  # "tl" or "br"
        self.move_rotating = False
        self.move_last_pos = None
        self.move_original_pixmap = None
        self.move_original_rect = None
        self.move_scale_x = 1.0
        self.move_scale_y = 1.0

        self.text_mode = False
        self.text_options = {
            "font": QFont("Lexend Deca", 32),
            "color": QColor("black"),
            "bold": False,
            "italic": False,
            "underline": False,
            "strikeout": False,
            "size": 32,
            "text": ""
        }

        self.setAttribute(Qt.WidgetAttribute.WA_TabletTracking, True)

    def set_text_mode(self, active: bool):
        self.text_mode = active

    def set_text_options(self, options: dict):
        self.text_options.update(options)

    def set_selection_mode(self, mode):
    # Auswahl nur löschen, wenn Modus "ellipse" oder "lasso" ist oder Modus None (clear)
        if mode in ("ellipse", "lasso", None):
            self.selection_active = False
            self.selection_rect = None
            self.selection_path = None
            self.selection_pixmap = None
            self.moving_selection = False
            self.selection_offset = QPoint(0, 0)
            self.selection_start = None
    # Modus setzen, Auswahl bleibt sonst erhalten
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
            # Prüfe auf Skalierpunkte
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
        # Nur neue Auswahl starten, wenn Auswahlmodus aktiv ist UND keine Auswahl existiert ODER Auswahl gerade aktiv ist
        if self.selection_mode and (not self.selection_rect and not self.selection_path or self.selection_active):
            self.selection_active = True
            self.selection_start = self.get_scaled_mouse_pos(event)
            if self.selection_mode == "lasso":
                self.selection_path = QPainterPath()
                self.selection_path.moveTo(self.selection_start)
            return
        # Wenn Auswahl existiert, nicht überschreiben!
        # ...restlicher Code wie gehabt...
        if self.moving_selection and self.selection_pixmap:
            self.selection_start = self.get_scaled_mouse_pos(event)
            return
        if self.eyedropper_mode:
            pos = self.get_scaled_mouse_pos(event)
            if 0 <= pos.x() < self.image.width() and 0 <= pos.y() < self.image.height():
                color = self.image.toImage().pixelColor(pos)
                self.set_pen_color(color)
            self.eyedropper_mode = False  # Nur einmal ausführen
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
                # Skalierung berechnen
                if self.move_scaling == "tl":
                    new_rect = QRect(pos, self.move_rect.bottomRight())
                else:
                    new_rect = QRect(self.move_rect.topLeft(), pos)
                new_rect = new_rect.normalized()
                self.move_rect = new_rect

                # Berechne Skalierungsfaktor relativ zur Originalgröße
                orig_size = self.move_original_rect.size()
                new_size = self.move_rect.size()
                if orig_size.width() > 0 and orig_size.height() > 0:
                    scale_x = new_size.width() / orig_size.width()
                    scale_y = new_size.height() / orig_size.height()
                    # Optional: proportional skalieren
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
        # ...restlicher Code...
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
        # --- Nur innerhalb der Auswahl Formen zeichnen ---
        if self.shape_mode and self.shape_start and self.shape_end:
            # Prüfe beide Endpunkte
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
            # Sonst: Form NICHT zeichnen!
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
        # Zeichne das Bild auf das Canvas
        scaled = self.image.scaled(
            self.image.size() * self.zoom_level,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        painter.drawPixmap(self.pan_offset, scaled)

        # --- Auswahl anzeigen, wenn NICHT im Move-Modus ---
        if not self.move_mode:
            pen = QPen(QColor("red"), 2, Qt.PenStyle.DashLine)
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

        # --- Move-Modus anzeigen ---
        if self.move_mode and self.move_rect and self.move_pixmap:
            painter.save()
            center = self.move_rect.center() * self.zoom_level + self.pan_offset + self.move_offset * self.zoom_level
            painter.translate(center)
            painter.rotate(self.move_rotation)
            painter.scale(self.move_scale_x, self.move_scale_y)
            painter.translate(-self.move_original_pixmap.width() / 2, -self.move_original_pixmap.height() / 2)
            painter.drawPixmap(0, 0, self.move_original_pixmap)
            painter.restore()
    # Rand und Punkte wie gehabt...
            # Rand
            pen = QPen(QColor("green"), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            rect = QRect(
                self.move_rect.topLeft() * self.zoom_level + self.pan_offset + self.move_offset * self.zoom_level,
                self.move_rect.bottomRight() * self.zoom_level + self.pan_offset + self.move_offset * self.zoom_level
            )
            painter.drawRect(rect)
            # Skalierpunkte
            painter.setBrush(QColor("white"))
            painter.setPen(QPen(QColor("green"), 2))
            painter.drawEllipse(rect.topLeft(), 8, 8)
            painter.drawEllipse(rect.bottomRight(), 8, 8)
            # Rotationspunkt
            painter.setBrush(QColor("green"))
            painter.drawEllipse(rect.center(), 8, 8)

        super().paintEvent(event)
    
    def copy_selection(self):
        clipboard = QApplication.clipboard()
        # Wenn keine Auswahl existiert, kopiere das gesamte Bild
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
    # Nur in Auswahl zeichnen
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
        # QPixmap -> PIL.Image
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())  # <--- Änderung hier!
        pil_img = Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)
        # Blur mit Pillow
        blurred = pil_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        # PIL.Image -> QPixmap
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
        # Übernehme die transformierte Auswahl ins Bild
        if self.move_mode and self.move_pixmap and self.move_rect:
            painter = QPainter(self.image)
            painter.save()
            # Zielrechteck berechnen
            target_rect = QRect(
                self.move_rect.topLeft() + self.move_offset,
                QSize(
                    int(self.move_original_pixmap.width() * self.move_scale_x),
                    int(self.move_original_pixmap.height() * self.move_scale_y)
                )
            )
            # Transformation für Rotation und Skalierung
            transform = QTransform()
            center = target_rect.center()
            transform.translate(center.x(), center.y())
            transform.rotate(self.move_rotation)
            transform.translate(-center.x(), -center.y())
            painter.setTransform(transform)
            painter.drawPixmap(target_rect, self.move_original_pixmap)
            painter.restore()
        # Move-Modus zurücksetzen
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
        # Farben invertieren
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


canvas = Canvas()
canvas.setStyleSheet("background-color: lightgray;")
canvas.setFixedSize(900, 900)
canvas_and_toolbar = QVBoxLayout()
canvas_and_toolbar.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignCenter)


undo_action = QAction(QIcon("colored_textures/undo.png"), "Undo", window)
undo_action.triggered.connect(canvas.undo)
undo_action.setShortcut("Ctrl+Z")

redo_action = QAction(QIcon("colored_textures/redo.png"), "Redo", window)
redo_action.triggered.connect(canvas.redo)
redo_action.setShortcut("Ctrl+Y")

zoom_in = QAction(QIcon("colored_textures/zoom_in.png"), "Zoom In", window)
zoom_in.triggered.connect(canvas.zoom_in)
zoom_out = QAction(QIcon("colored_textures/zoom_out.png"), "Zoom Out", window)
zoom_out.triggered.connect(canvas.zoom_out)

copy_selection = QAction(QIcon("colored_textures/copy.png"), "Copy", window)
copy_selection.triggered.connect(canvas.copy_selection)
copy_selection.setShortcut("Ctrl+C")

paste_selection = QAction(QIcon("colored_textures/paste.png"), "Paste", window)
paste_selection.triggered.connect(canvas.paste_selection)
paste_selection.setShortcut("Ctrl+V")

effects_action = QAction(window)
effects_action.setIcon(QIcon("colored_textures/effect_1.png"))
effects_action.setText("Effects")
effects_menu = QMenu()

ca_action = QAction(QIcon("colored_textures/ca.png"), "Combined Adjustments", window)
ca_action.triggered.connect(lambda: open_combined_adjustments(canvas))

blur_action = QAction(QIcon("colored_textures/blur.png"), "Gaussian Blur", window)
blur_action.triggered.connect(lambda: open_blur_options())

contour_action = QAction(QIcon("colored_textures/contour.png"), "Contour", window)
contour_action.triggered.connect(canvas.apply_contour)

detail_action = QAction(QIcon("colored_textures/detail.png"), "Detail", window)
detail_action.triggered.connect(canvas.apply_detail)

emboss_action = QAction(QIcon("colored_textures/emboss.png"), "Emboss", window)
emboss_action.triggered.connect(canvas.apply_emboss)

edge_enhance_action = QAction(QIcon("colored_textures/edge_enhance.png"), "Edge Enhance", window)
edge_enhance_action.triggered.connect(canvas.apply_find_edges)

smooth_action = QAction(QIcon("colored_textures/smooth.png"), "Smooth", window)
smooth_action.triggered.connect(canvas.apply_smooth)

smooth_more_action = QAction(QIcon("colored_textures/smooth_more.png"), "Smooth More", window)
smooth_more_action.triggered.connect(canvas.apply_smooth_more)

unsharp_mask_action = QAction(QIcon("colored_textures/unsharp_mask.png"), "Unsharp Mask", window)
unsharp_mask_action.triggered.connect(lambda: open_unsharp_mask_options())

find_edges_action = QAction(QIcon("colored_textures/find_edges.png"), "Find Edges", window)
find_edges_action.triggered.connect(canvas.apply_find_edges)

sharpen_action = QAction(QIcon("colored_textures/sharpen.png"), "Sharpen", window)
sharpen_action.triggered.connect(canvas.apply_sharpen)

invert_action = QAction(QIcon("colored_textures/invert.png"), "Invert Colors", window)
invert_action.triggered.connect(canvas.invert_colors)

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

rselect_button = QToolButton()
rselect_button.setIcon(QIcon("colored_textures/rectangular_selection.png"))
rselect_button.setIconSize(QSize(45,45))
rselect_button.setStyleSheet("border: none; background: transparent;")
rselect_button.setCheckable(True)
rselect_button.clicked.connect(lambda: canvas.set_selection_mode("rect"))


cselect_button = QToolButton()
cselect_button.setIcon(QIcon("colored_textures/circular_selection.png"))
cselect_button.setIconSize(QSize(45,45))
cselect_button.setStyleSheet("border: none; background: transparent;")
cselect_button.setCheckable(True)
cselect_button.clicked.connect(lambda: canvas.set_selection_mode("ellipse"))

lselect_button = QToolButton()
lselect_button.setIcon(QIcon("colored_textures/lasso_selection.png"))
lselect_button.setIconSize(QSize(45,45))
lselect_button.setStyleSheet("border: none; background: transparent;")
lselect_button.setCheckable(True)
lselect_button.clicked.connect(lambda: canvas.set_selection_mode("lasso"))

clear_button = QToolButton()
clear_button.setIcon(QIcon("colored_textures/clear_selection.png"))
clear_button.setIconSize(QSize(45,45))
clear_button.setStyleSheet("border: none; background: transparent;")
clear_button.clicked.connect(lambda: canvas.set_selection_mode(None))
bottom_layout.addWidget(clear_button)


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

rectangle = QAction(QIcon("colored_textures/rectangle.png"), " Rectangle", window)
rectangle.setCheckable(True)
rectangle.triggered.connect(lambda checked: canvas.set_shape_mode("rect") if checked else canvas.set_shape_mode(None))

ellipse = QAction(QIcon("colored_textures/ellipse.png"), " Ellipse", window)
ellipse.setCheckable(True)
ellipse.triggered.connect(lambda checked: canvas.set_shape_mode("ellipse") if checked else canvas.set_shape_mode(None))

triangle = QAction(QIcon("colored_textures/triangle.png"), " Triangle", window)
triangle.setCheckable(True)
triangle.triggered.connect(lambda checked: canvas.set_shape_mode("triangle") if checked else canvas.set_shape_mode(None))

lines = QAction(QIcon("colored_textures/lines.png"), " Lines", window)
lines.setCheckable(True)
lines.triggered.connect(lambda checked: canvas.set_shape_mode("line") if checked else canvas.set_shape_mode(None))

disableshape = QAction(QIcon("colored_textures/disableshape.png"), " Disable", window)
disableshape.setCheckable(True)
disableshape.triggered.connect(lambda checked: canvas.set_shape_mode(None) if checked else canvas.set_shape_mode(None))

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
#shapes_menu.setWindowFlags(shapes_menu.windowFlags() | Qt.WindowType.NoDropShadowWindowHint)

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
bottom_layout.addWidget(text_button)

pen_button = QToolButton()
pen_button.setIcon(QIcon("colored_textures/pen.png"))
pen_button.setIconSize(QSize(45,45))
pen_button.setStyleSheet("border: none; background: transparent;")
pen_button.setCheckable(False)
def activate_pen_tool():
    canvas.set_pen_color(QColor("black"))
    canvas.set_pen_width(2)
    canvas.set_pen_cap_style(Qt.PenCapStyle.RoundCap),
    canvas.set_pen_join_style(Qt.PenJoinStyle.RoundJoin)
    canvas.brush_active = False
    canvas.drawing = False
pen_button.clicked.connect(activate_pen_tool)          
pen_button.clicked.connect(lambda: [
    width_slider.setValue(2),
    width_text.setText("2")
])

marker_button = QToolButton()
marker_button.setIcon(QIcon("colored_textures/marker.png"))
marker_button.setIconSize(QSize(45,45))
marker_button.setStyleSheet("border: none; background: transparent;")
marker_button.setCheckable(False)
def use_marker_tool():
    canvas.set_pen_color(QColor(255, 255, 0, 100))
    canvas.set_pen_width(20)
    canvas.set_pen_cap_style(Qt.PenCapStyle.FlatCap),
    canvas.set_pen_join_style(Qt.PenJoinStyle.MiterJoin)
    canvas.brush_active = False
marker_button.clicked.connect(use_marker_tool)
marker_button.clicked.connect(lambda: [
    width_slider.setValue(20),
    width_text.setText("20")
])

brush_button = QToolButton()
brush_button.setIcon(QIcon("colored_textures/brush.png"))
brush_button.setIconSize(QSize(45,45))
brush_button.setStyleSheet("border: none; background: transparent;")
brush_button.setCheckable(False)
def use_brush_tool():
        canvas.set_pen_color(QColor("#55aaff"))
        canvas.set_pen_width(10)
        canvas.set_pen_cap_style(Qt.PenCapStyle.RoundCap)
        canvas.set_pen_join_style(Qt.PenJoinStyle.RoundJoin)
        canvas.brush_active = True
brush_button.clicked.connect(use_brush_tool)
brush_button.clicked.connect(lambda: [
    width_slider.setValue(10),
    width_text.setText("10")
])

erase_button = QToolButton()
erase_button.setIcon(QIcon("colored_textures/eraser.png"))
erase_button.setIconSize(QSize(45,45))
erase_button.setStyleSheet("border: none;; background: transparent;")
erase_button.setCheckable(True)
def use_erase_tool():
    canvas.set_pen_color(QColor("white"))
    canvas.set_pen_width(30)
    canvas.set_pen_cap_style(Qt.PenCapStyle.RoundCap),
    canvas.set_pen_join_style(Qt.PenJoinStyle.RoundJoin)
erase_button.clicked.connect(use_erase_tool)
erase_button.clicked.connect(lambda: [
    width_slider.setValue(30),
    width_text.setText("30")
])



width_text = QLineEdit()
width_text.setText("5")
width_text.setFixedSize(35,35)
width_text.setStyleSheet("border: transparent; background: transparent;")
width_text.setFont(QFont("Lexend Deca", 15))
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
width_slider.setValue(5)
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

color_picker = QToolButton()
color_picker.setIcon(QIcon("colored_textures/color_picker.png"))
color_picker.setIconSize(QSize(45,45))
color_picker.setStyleSheet("border: none; background: transparent;")
color_picker.setCheckable(True)
color_picker.clicked.connect(lambda checked: canvas.set_eyedropper_mode(True) if checked else canvas.set_eyedropper_mode(False))

color_button = QToolButton()
color_button.setIcon(QIcon("colored_textures/colorwheel.png"))
color_button.setIconSize(QSize(45,45))
color_button.setStyleSheet("border: none; background: transparent;")
color_button.clicked.connect(lambda: open_color_picker())

spacer0 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer1 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer2 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer3 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer4 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer5 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
spacer6 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

bottom_layout.addSpacerItem(spacer0)
bottom_layout.addWidget(move_button)
bottom_layout.addWidget(rselect_button)
bottom_layout.addWidget(cselect_button)
bottom_layout.addWidget(lselect_button)
bottom_layout.addWidget(clear_button)
bottom_layout.addSpacerItem(spacer1)
bottom_layout.addWidget(shapes)
bottom_layout.addWidget(text_button)
bottom_layout.addSpacerItem(spacer2)
bottom_layout.addWidget(pen_button)
bottom_layout.addWidget(marker_button)
bottom_layout.addWidget(brush_button)
bottom_layout.addWidget(erase_button)
bottom_layout.addSpacerItem(spacer3)
bottom_layout.addWidget(width_slider)
bottom_layout.addWidget(width_text)
bottom_layout.addSpacerItem(spacer4)
bottom_layout.addWidget(color_picker)
bottom_layout.addWidget(color_button)
bottom_layout.addSpacerItem(spacer5)
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
    try:
        canvas.image.fill(Qt.GlobalColor.white)  
        canvas.update()                          
        print("Canvas cleared")
    except Exception as e:
        print(f"Error while clearing canvas: {e}")

def open_color_picker():
    options = QColorDialog.ColorDialogOption.ShowAlphaChannel
    color = QColorDialog.getColor(canvas.pen_color, window, "Pick Color", options)
    if color.isValid():
        canvas.set_pen_color(color)

def open_blur_options():

    blur_options = QDialog(window)
    blur_options.setWindowTitle("Blur Options")
    layout = QHBoxLayout()
    blur_options.setLayout(layout)

    blur_slider = QSlider(Qt.Orientation.Horizontal)
    blur_slider.setRange(1, 35)
    blur_slider.setValue(5)

    blur_text = QLineEdit()
    blur_text.setText("5")
    blur_text.setFixedSize(30,20)
    blur_text.setValidator(QIntValidator(1, 150))

    blur_slider.setFixedSize(100,20)
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
    blur_confirm.clicked.connect(lambda: canvas.apply_blur(int(blur_text.text())))

    layout.addWidget(blur_slider)
    layout.addWidget(blur_text)
    layout.addWidget(blur_confirm)
    
    blur_options.exec()

def open_unsharp_mask_options():
    dialog = QDialog(window)
    dialog.setWindowTitle("Unsharp Mask Options")
    layout = QVBoxLayout(dialog)

    # Radius
    radius_layout = QHBoxLayout()
    radius_label = QLabel("Radius:")
    radius_slider = QSlider(Qt.Orientation.Horizontal)
    radius_slider.setRange(1, 10)
    radius_slider.setValue(2)
    radius_text = QLineEdit("2")
    radius_text.setFixedWidth(40)
    radius_text.setValidator(QIntValidator(1, 10))
    radius_layout.addWidget(radius_label)
    radius_layout.addWidget(radius_slider)
    radius_layout.addWidget(radius_text)
    layout.addLayout(radius_layout)

    # Percent
    percent_layout = QHBoxLayout()
    percent_label = QLabel("Percent:")
    percent_slider = QSlider(Qt.Orientation.Horizontal)
    percent_slider.setRange(50, 500)
    percent_slider.setValue(150)
    percent_text = QLineEdit("150")
    percent_text.setFixedWidth(50)
    percent_text.setValidator(QIntValidator(50, 500))
    percent_layout.addWidget(percent_label)
    percent_layout.addWidget(percent_slider)
    percent_layout.addWidget(percent_text)
    layout.addLayout(percent_layout)

    # Threshold
    threshold_layout = QHBoxLayout()
    threshold_label = QLabel("Threshold:")
    threshold_slider = QSlider(Qt.Orientation.Horizontal)
    threshold_slider.setRange(0, 255)
    threshold_slider.setValue(3)
    threshold_text = QLineEdit("3")
    threshold_text.setFixedWidth(40)
    threshold_text.setValidator(QIntValidator(0, 255))
    threshold_layout.addWidget(threshold_label)
    threshold_layout.addWidget(threshold_slider)
    threshold_layout.addWidget(threshold_text)
    layout.addLayout(threshold_layout)

    # Synchronisation Slider <-> Text
    radius_slider.valueChanged.connect(lambda v: radius_text.setText(str(v)))
    percent_slider.valueChanged.connect(lambda v: percent_text.setText(str(v)))
    threshold_slider.valueChanged.connect(lambda v: threshold_text.setText(str(v)))
    radius_text.textChanged.connect(lambda t: radius_slider.setValue(int(t) if t.isdigit() else 2))
    percent_text.textChanged.connect(lambda t: percent_slider.setValue(int(t) if t.isdigit() else 150))
    threshold_text.textChanged.connect(lambda t: threshold_slider.setValue(int(t) if t.isdigit() else 3))

    # Confirm Button
    confirm_btn = QPushButton("Confirm")
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
    layout = QVBoxLayout(dialog)

    # Text-Eingabe
    text_edit = QLineEdit(canvas.text_options["text"])
    layout.addWidget(QLabel("Text:"))
    layout.addWidget(text_edit)

    # Font-Auswahl
    font_combo = QFontComboBox()
    font_combo.setCurrentFont(canvas.text_options["font"])
    layout.addWidget(QLabel("Font:"))
    layout.addWidget(font_combo)

    # Größe
    size_slider = QSlider(Qt.Orientation.Horizontal)
    size_slider.setRange(8, 128)
    size_slider.setValue(canvas.text_options["size"])
    size_text = QLineEdit(str(canvas.text_options["size"]))
    size_text.setFixedWidth(40)
    size_text.setValidator(QIntValidator(8, 128))
    size_layout = QHBoxLayout()
    size_layout.addWidget(QLabel("Size:"))
    size_layout.addWidget(size_slider)
    size_layout.addWidget(size_text)
    layout.addLayout(size_layout)

    # Farbe
    color_btn = QPushButton("Pick Color")
    color_preview = QLabel()
    color_preview.setFixedSize(30, 30)
    color_preview.setStyleSheet(f"background: {canvas.text_options['color'].name()}; border: 1px solid #333;")
    def pick_color():
        color = QColorDialog.getColor(canvas.text_options["color"], window)
        if color.isValid():
            color_preview.setStyleSheet(f"background: {color.name()}; border: 1px solid #333;")
            color_btn.setProperty("picked_color", color)
    color_btn.clicked.connect(pick_color)
    color_layout = QHBoxLayout()
    color_layout.addWidget(color_btn)
    color_layout.addWidget(color_preview)
    layout.addLayout(color_layout)

    # Style-Checkboxen
    bold_cb = QCheckBox("Bold")
    bold_cb.setChecked(canvas.text_options["bold"])
    italic_cb = QCheckBox("Italic")
    italic_cb.setChecked(canvas.text_options["italic"])
    underline_cb = QCheckBox("Underline")
    underline_cb.setChecked(canvas.text_options["underline"])
    strike_cb = QCheckBox("Strikeout")
    strike_cb.setChecked(canvas.text_options["strikeout"])
    style_layout = QHBoxLayout()
    style_layout.addWidget(bold_cb)
    style_layout.addWidget(italic_cb)
    style_layout.addWidget(underline_cb)
    style_layout.addWidget(strike_cb)
    layout.addLayout(style_layout)

    # Synchronisation Slider <-> Text
    size_slider.valueChanged.connect(lambda v: size_text.setText(str(v)))
    size_text.textChanged.connect(lambda t: size_slider.setValue(int(t) if t.isdigit() else 32))

    # Confirm Button
    confirm_btn = QPushButton("Confirm")
    def apply_text_options():
        options = {
            "text": text_edit.text(),
            "font": font_combo.currentFont(),
            "size": int(size_text.text()),
            "color": color_btn.property("picked_color") if color_btn.property("picked_color") else canvas.text_options["color"],
            "bold": bold_cb.isChecked(),
            "italic": italic_cb.isChecked(),
            "underline": underline_cb.isChecked(),
            "strikeout": strike_cb.isChecked()
        }
        canvas.set_text_options(options)
        dialog.accept()
    confirm_btn.clicked.connect(apply_text_options)
    layout.addWidget(confirm_btn)

    dialog.exec()

def open_combined_adjustments(canvas):

    dialog = QDialog()
    dialog.setWindowTitle("Combined Adjustments")
    dialog.setWindowIcon(QIcon("colored_textures/logo.png"))
    dialog.setFixedSize(300, 360)

    layout = QVBoxLayout()
    sliders = {}

    # Utility: Slider + Label horizontal
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
        value_label.setFont(QFont("Lexend Deca", 15))
        value_label.textChanged.connect(lambda text: slider.setValue(int(text)) if text.isdigit() else None)

        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
        line.addWidget(label)
        line.addWidget(slider)
        line.addWidget(value_label)
        layout.addLayout(line)
        sliders[name] = slider

        label.setFont(QFont("Lexend Deca", 15))

    # Filterregler
    make_slider("R ", -100, 100)
    make_slider("B ", -100, 100)
    make_slider("Y ", -100, 100)  # simuliert +Rot +Grün

    # Visuelle Anpassungen
    make_slider("S ", -100, 100)
    make_slider("B ", -100, 100)
    make_slider("C ", -100, 100)

    

    # Bestätigen
    confirm = QPushButton("Confirm")
    layout.addWidget(confirm)
    dialog.setLayout(layout)

    # Logik zum Anwenden der Effekte

    def apply_adjustments():
            # Konvertiere QPixmap → PIL.Image
        pil_image = ImageQt.fromqpixmap(canvas.image)

        # Farbfilter (Rot, Blau, Gelb) – optional, manuell
        r_shift = sliders["R "].value()
        b_shift = sliders["B "].value()
        y_shift = sliders["Y "].value()

        

        # Farbverschiebung manuell anwenden
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

        # Sättigung
        saturation_factor = 1 + sliders["S "].value() / 100.0
        pil_image = ImageEnhance.Color(pil_image).enhance(saturation_factor)

        # Helligkeit
        brightness_factor = 1 + sliders["B "].value() / 100.0
        pil_image = ImageEnhance.Brightness(pil_image).enhance(brightness_factor)

        # Kontrast
        contrast_factor = 1 + sliders["C "].value() / 100.0
        pil_image = ImageEnhance.Contrast(pil_image).enhance(contrast_factor)

        # Zurück zu QPixmap
        qt_image = ImageQt.toqpixmap(pil_image)
        canvas.image = qt_image
        canvas.update()
        dialog.accept()

    confirm.clicked.connect(apply_adjustments)
    dialog.exec()

window.show()
sys.exit(app.exec())