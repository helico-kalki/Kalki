from PyQt6.QtWidgets import QFrame, QApplication
from PyQt6.QtGui import (
    QPixmap, QFont, QColor, QPainterPath, QPen, QWheelEvent, QLinearGradient, QTabletEvent, 
    QMouseEvent, QPaintEvent, QPainter, QTransform, QImage
)
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QPoint, QLineF, QRectF, QPointF, QRect, QEvent, QSizeF
from PIL import Image, ImageFilter
from config import *
from canvas_resize_dialog import CanvasResizeDialog

class Canvas(QFrame):
    brush_active_changed = pyqtSignal(bool)
    pen_style_changed = pyqtSignal()
    pen_color_changed = pyqtSignal(QColor)
    def __init__(self):
        super().__init__()

        self.image = QPixmap(CANVSIZE[0], CANVSIZE[1])
        self.image.fill(CANVCOLOR)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.drawing = False
        self.last_point = QPoint()
        self.current_tool = "draw"
        self.history = []
        self.history_index = -1
        self.save_state()
        self.selection_start = None
        self.selecting = False
        self.selection_finished = False
        self.blur_radius = 5

        self.pan_active = False
        self.pan_offset = QPoint(0, 0)
        self.pan_start = QPoint()

        self.zoom_level = 1.0

        self.pen_color = QColor(PENCOLOR)
        self.pen_width = PENWIDTH
        self.pen_cap = PENCAP
        self.pen_join = PENJOIN
        self.pen_style = PENSTYLE
        self.brush_active = False

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

    def _qimage_to_pil(self, qimg):
        qimg = qimg.convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(qimg.sizeInBytes())
        return Image.frombuffer("RGBA", (width, height), bytes(ptr), "raw", "RGBA", 0, 1)

    def _pil_to_qpixmap(self, pil_img):
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimg)

    def save_state(self):
        self.history = self.history[:self.history_index + 1]
        self.history.append(self.image.copy())
        self.history_index += 1

    def set_brush_active(self, active: bool):
        self.brush_active = active
        self.brush_active_changed.emit(active)  

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
        self.pen_color_changed.emit(color)

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

    def set_dash_pattern(self, pattern: list[float]):
        self.dash_pattern = pattern

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
                pen = QPen(self.pen_color, self.pen_width, self.pen_style, self.pen_cap, self.pen_join)
                if self.pen_style == Qt.PenStyle.CustomDashLine:
                    pen.setDashPattern(self.dash_pattern)
                    pen.setDashOffset(20)
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
#            if event.button() == Qt.MouseButton.MiddleButton:
#                self.setCursor(Qt.CursorShape.ClosedHandCursor)
#            else:
#                self.setCursor(Qt.CursorShape.ArrowCursor)

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
                pen = QPen(self.pen_color, self.pen_width, self.pen_style, self.pen_cap, self.pen_join)
                if self.pen_style == Qt.PenStyle.CustomDashLine:
                    pen.setDashPattern(self.dash_pattern)
                    pen.setDashOffset(20)
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
            Qt.TransformationMode.FastTransformation
        )
        painter.drawPixmap(self.pan_offset, scaled)


        if not self.move_mode:
            pen = QPen(QColor(SELCOLOR), SELWIDTH, SELSTYLE)
            painter.setPen(pen)
            if self.selection_mode == "rect" and self.selection_rect:
                rect = QRect(
                    self.selection_rect.topLeft() * self.zoom_level + self.pan_offset,
                    self.selection_rect.bottomRight() * self.zoom_level + self.pan_offset
                )
                painter.drawRect(rect)
            elif self.selection_mode == "ellipse" and self.selection_rect:
                rect = QRectF(
                    QPointF(self.selection_rect.topLeft()) * self.zoom_level + QPointF(self.pan_offset),
                    QPointF(self.selection_rect.bottomRight()) * self.zoom_level + QPointF(self.pan_offset)
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

            pen = QPen(QColor(SELCOLOR), SELWIDTH, SELSTYLE)
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

    def cut_selection(self):
            self.copy_selection()
            painter = QPainter(self.image)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            if self.selection_mode == "rect" and self.selection_rect:
                painter.fillRect(self.selection_rect, Qt.GlobalColor.transparent)
            elif self.selection_mode == "ellipse" and self.selection_rect:
                path = QPainterPath()
                path.addEllipse(QRectF(self.selection_rect))
                painter.fillPath(path, Qt.GlobalColor.transparent)
            elif self.selection_mode == "lasso" and self.selection_path:
                painter.fillPath(self.selection_path, Qt.GlobalColor.transparent)
            painter.end()
            self.clear_selection()
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
        self.pen_style_changed.emit()

    def set_pen_join_style(self, join_style: Qt.PenJoinStyle):
        self.pen_join = join_style
        self.pen_style_changed.emit()

    def set_pen_line_style(self, line_style: Qt.PenStyle):
        self.pen_line = line_style

    def set_pixmap(self, pixmap: QPixmap):
        self.image = pixmap
        self.update()

    def set_blur_radius(self, radius):
        self.blur_radius = radius
    
    def remove_blur(self):
        self.setGraphicsEffect(None)

    def apply_gradient(self, color1=QColor("white"), color2=QColor("blue")):
        painter = QPainter(self.image)
        gradient = QLinearGradient(0, 0, self.image.width(), 0)
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)

        if hasattr(self, "selection_rect") and self.selection_rect is not None:
            if self.selection_mode == "rect":
                painter.fillRect(self.selection_rect, gradient)
            elif self.selection_mode == "ellipse":
                path = QPainterPath()
                rectf = QRectF(self.selection_rect) if isinstance(self.selection_rect, QRect) else self.selection_rect
                path.addEllipse(rectf)
                painter.fillPath(path, gradient)
        else:
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
                    pen = QPen(self.pen_color, dynamic_width, self.pen_style, self.pen_cap, self.pen_join)
                    if self.pen_style == Qt.PenStyle.CustomDashLine:
                        pen.setDashPattern(self.dash_pattern)
                        pen.setDashOffset(20)
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

    def fill_selection(self, color: QColor):
        painter = QPainter(self.image)

        if hasattr(self, "selection_rect") and self.selection_rect is not None:
            if self.selection_mode == "rect":
                painter.fillRect(self.selection_rect, color)
            elif self.selection_mode == "ellipse":
                path = QPainterPath()
                path.addEllipse(QRectF(self.selection_rect))
                painter.fillPath(path, color)
        else:
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

    def _apply_filter_to_selection(self, filter_func):
        if not self.selection_rect:
            self.undo_stack.append(self.image.copy())
            pil_img = self._qimage_to_pil(self.image.toImage())
            processed_img = filter_func(pil_img)
            self.image = QPixmap.fromImage(processed_img.toqimage())
            self.update()
            return

        self.undo_stack.append(self.image.copy())
        
        q_img = self.image.toImage().copy(self.selection_rect)
        
        pil_img = self._qimage_to_pil(q_img)
        
        processed_pil_img = filter_func(pil_img)
        
        processed_q_img = processed_pil_img.toqimage()

        painter = QPainter(self.image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.drawImage(self.selection_rect.topLeft(), processed_q_img)
        painter.end()
        
        self.update()

    def apply_contour(self):
        self._apply_filter_to_selection(lambda img: img.filter(ImageFilter.CONTOUR))

    def apply_detail(self):
        self._apply_filter_to_selection(lambda img: img.filter(ImageFilter.DETAIL))

    def apply_blur(self, radius):
        qimg = self.image.toImage()
        pil_img = self._qimage_to_pil(qimg)
        blurred = pil_img.filter(ImageFilter.GaussianBlur(radius=radius))
        self.image = self._pil_to_qpixmap(blurred)
        self.update()

    def apply_emboss(self):
        qimg = self.image.toImage()
        pil_img = self._qimage_to_pil(qimg)
        filtered = pil_img.filter(ImageFilter.EMBOSS)
        self.image = self._pil_to_qpixmap(filtered)
        self.update()

    def apply_detail(self):
        qimg = self.image.toImage()
        pil_img = self._qimage_to_pil(qimg)
        filtered = pil_img.filter(ImageFilter.DETAIL)
        self.image = self._pil_to_qpixmap(filtered)
        self.update()

    def apply_edge_enhance(self):
        self._apply_filter_to_selection(lambda img: img.filter(ImageFilter.EDGE_ENHANCE))

    def apply_find_edges(self):
        self._apply_filter_to_selection(lambda img: img.filter(ImageFilter.FIND_EDGES))

    def apply_sharpen(self):
        qimg = self.image.toImage()
        pil_img = self._qimage_to_pil(qimg)
        filtered = pil_img.filter(ImageFilter.SHARPEN)
        self.image = self._pil_to_qpixmap(filtered)
        self.update()

    def apply_smooth(self):
        self._apply_filter_to_selection(lambda img: img.filter(ImageFilter.SMOOTH))

    def apply_smooth_more(self):
        self._apply_filter_to_selection(lambda img: img.filter(ImageFilter.SMOOTH_MORE))

    def apply_unsharp_mask(self, radius=2, percent=150, threshold=3):
        self._apply_filter_to_selection(lambda img: img.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold)))

    def invert_colors(self):
        from PIL import ImageOps
        def invert_filter(img):
            if img.mode == 'RGBA':
                r, g, b, a = img.split()
                rgb_img = Image.merge('RGB', (r, g, b))
                inverted_rgb = ImageOps.invert(rgb_img)
                return Image.merge('RGBA', (*inverted_rgb.split(), a))
            else:
                return ImageOps.invert(img)
        self._apply_filter_to_selection(invert_filter)

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
        if not self.selection_rect or self.selection_rect.isNull():
            return  

        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_RGBA8888)

        crop_rect = self.selection_rect.intersected(qimg.rect())  
        cropped = qimg.copy(crop_rect)

        self.image = QPixmap.fromImage(cropped)
        self.selection_rect = None  
        self.update()

    def resize_canvas(self):
        dialog = CanvasResizeDialog(self.image.width(), self.image.height())
        if dialog.exec():
            new_width, new_height = dialog.get_values()
            new_size = QSize(new_width, new_height)

            new_pixmap = QPixmap(new_size)
            new_pixmap.fill(Qt.GlobalColor.white)

            painter = QPainter(new_pixmap)
            scaled_old = self.image.scaled(new_size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled_old)
            painter.end()

            self.image = new_pixmap
            self.update()