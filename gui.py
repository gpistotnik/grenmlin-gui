import sys
import math

# For plotting:
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import networkx as nx

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction,
    QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem,
    QMessageBox, QInputDialog, QGraphicsItem
)
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPolygonF
)
from PyQt5.QtCore import (
    Qt, QRectF, QPointF
)

# ---------------------------------------------------
# 1) A minimal GRN class with networkx + matplotlib
# ---------------------------------------------------
class MyGRN:
    """
    Mock Gene Regulatory Network that we can plot with networkx.
    We'll store a DiGraph of nodes & edges.
    - Input nodes are labeled node_type="input"
    - Output nodes: node_type="output"
    - Others: node_type="normal"
    - Edge data: we just store them in Nx as (u->v).
    """

    def __init__(self):
        self.G = nx.DiGraph()

    def add_input_species(self, name: str):
        self.G.add_node(name, node_type="input")

    def add_species(self, name: str, degrade_rate: float):
        self.G.add_node(name, node_type="output", degrade=degrade_rate)

    def add_edge(self, source_name: str, target_name: str, reg_type=0, kd=1.0, n=1.0):
        """
        reg_type: 1 => activating (blue), -1 => repressing (red), 0 => unknown (orange)
        kd, n: for demonstration
        """
        self.G.add_edge(source_name, target_name, regType=reg_type, kd=kd, n=n)

    def plot_network(self):
        if self.G.number_of_nodes() == 0:
            QMessageBox.warning(None, "Plot Error", "No nodes in the GRN!")
            return

        pos = nx.spring_layout(self.G)

        # Partition nodes:
        input_nodes = [n for n,d in self.G.nodes(data=True) if d.get("node_type") == "input"]
        output_nodes = [n for n,d in self.G.nodes(data=True) if d.get("node_type") == "output"]
        normal_nodes = [n for n in self.G.nodes if n not in input_nodes and n not in output_nodes]

        nx.draw_networkx_nodes(self.G, pos, nodelist=input_nodes, node_color="green")
        nx.draw_networkx_nodes(self.G, pos, nodelist=output_nodes, node_color="purple")
        nx.draw_networkx_nodes(self.G, pos, nodelist=normal_nodes, node_color="gray")

        # Edges
        colors = []
        for (u,v,data) in self.G.edges(data=True):
            rt = data.get("regType", 0)
            if rt == 1:
                colors.append("blue")
            elif rt == -1:
                colors.append("red")
            else:
                colors.append("orange")
        nx.draw_networkx_edges(self.G, pos, edge_color=colors, arrows=True)

        nx.draw_networkx_labels(self.G, pos, font_color="white")

        plt.title("GRN Plot")
        plt.axis("off")
        plt.show()


# ---------------------------------------------------
# 2) NodeItem: a circle in the scene
# ---------------------------------------------------
class NodeItem(QGraphicsEllipseItem):
    """
    A simple node that can be 'input', 'output', or 'normal'.
    We'll store data in node_data = {'label':..., 'node_type':...}
    
    Double-click the node to rename it.
    
    Note the use of 'ItemSendsGeometryChanges' and 'itemChange()' so the edges
    can update their positions when this node moves.
    """

    def __init__(self, x, y, diameter=50, node_data=None):
        super().__init__(0, 0, diameter, diameter)
        self.setPos(x, y)

        # Make it selectable, movable, and geometry-change aware
        self.setFlags(
            self.ItemIsSelectable |
            self.ItemIsMovable |
            self.ItemSendsGeometryChanges
        )

        if node_data is None:
            node_data = {"label": "Node", "node_type": "normal"}
        self.node_data = node_data

        self.edges = []
        self.diameter = diameter
        self.font = QFont("Consolas", 10)

        # Color based on node_type
        node_type = self.node_data.get("node_type", "normal")
        if node_type == "input":
            self.setBrush(QBrush(QColor("#006600")))  # green
        elif node_type == "output":
            self.setBrush(QBrush(QColor("#660066")))  # purple
        else:
            self.setBrush(QBrush(QColor("#444444")))  # normal -> dark gray

        self.setPen(QPen(Qt.black, 1))

    def boundingRect(self):
        return QRectF(0, 0, self.diameter, self.diameter)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        # Draw label
        label = self.node_data.get("label", "Node")
        painter.setFont(self.font)
        painter.setPen(Qt.white)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, label)

    def add_edge(self, edge):
        if edge not in self.edges:
            self.edges.append(edge)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def itemChange(self, change, value):
        """
        Called whenever the node's position (or other states) changes.
        We only care about position changes so we can update connected edges.
        """
        if change == QGraphicsItem.ItemPositionChange:
            for edge in self.edges:
                edge.update_positions()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        """
        Double-click a node to rename it.
        """
        current_label = self.node_data.get("label", "")
        new_label, ok = QInputDialog.getText(
            None, "Edit Node Name",
            "Node Name:",
            text=current_label
        )
        if ok and new_label.strip():
            self.node_data["label"] = new_label.strip()
            self.update()
        super().mouseDoubleClickEvent(event)


# ---------------------------------------------------
# 3) EdgeItem: a line with arrow
# ---------------------------------------------------
class EdgeItem(QGraphicsLineItem):
    """
    Directed edge from source_node -> target_node.
    We'll store minimal data in edge_data if needed.
    
    Double-click to edit the edge data: 'type', 'Kd', 'n'.
    """

    def __init__(self, source_node, target_node=None):
        super().__init__()
        self.source_node = source_node
        self.target_node = target_node

        # Default edge data:
        #   type: 1 => activation, -1 => repression, 0 => unknown
        #   Kd, n: example param values
        self.edge_data = {
            "type": 0,
            "Kd": 1.0,
            "n": 1.0
        }

        # Styling
        self.pen_inactive = QPen(QColor("gray"), 2)
        self.pen_active = QPen(QColor("cyan"), 2)
        self.setPen(self.pen_inactive)
        self.setFlags(self.ItemIsSelectable)

        # Register with source
        self.source_node.add_edge(self)
        if self.target_node:
            self.target_node.add_edge(self)

        self.update_positions()

    def set_target_node(self, node):
        # Remove from old if needed
        if self.target_node is not None:
            self.target_node.remove_edge(self)
        self.target_node = node
        self.target_node.add_edge(self)
        self.update_positions()

    def update_positions(self):
        """
        Recompute the line endpoints based on the source/target node centers.
        """
        if not self.source_node:
            return
        sx = self.source_node.x() + self.source_node.diameter / 2
        sy = self.source_node.y() + self.source_node.diameter / 2

        if self.target_node:
            tx = self.target_node.x() + self.target_node.diameter / 2
            ty = self.target_node.y() + self.target_node.diameter / 2
        else:
            tx, ty = sx, sy

        self.setLine(sx, sy, tx, ty)

    def paint(self, painter, option, widget=None):
        # Highlight if selected
        if self.isSelected():
            painter.setPen(self.pen_active)
        else:
            painter.setPen(self.pen_inactive)

        line = self.line()
        painter.drawLine(line)

        # Draw arrow if we have a target
        if self.target_node:
            angle = math.atan2(line.dy(), line.dx())
            arrow_size = 12

            ex, ey = line.x2(), line.y2()
            arrow_angle = math.radians(30)

            p1 = QPointF(
                ex - arrow_size * math.cos(angle - arrow_angle),
                ey - arrow_size * math.sin(angle - arrow_angle)
            )
            p2 = QPointF(
                ex - arrow_size * math.cos(angle + arrow_angle),
                ey - arrow_size * math.sin(angle + arrow_angle)
            )
            polygon = QPolygonF([QPointF(ex, ey), p1, p2])
            painter.drawPolygon(polygon)

        super().paint(painter, option, widget)

    def mouseDoubleClickEvent(self, event):
        """
        Double-click an edge to edit its data: type, Kd, n.
        """
        # Edit 'type'
        current_type = self.edge_data.get("type", 0)
        new_type, ok = QInputDialog.getInt(None, "Edit Edge Type",
                                           "Type (-1, 0, or 1):",
                                           value=current_type)
        if ok:
            self.edge_data["type"] = new_type

        # Edit 'Kd'
        current_kd = self.edge_data.get("Kd", 1.0)
        new_kd, ok = QInputDialog.getDouble(None, "Edit Edge Kd",
                                            "Kd value:",
                                            value=current_kd)
        if ok:
            self.edge_data["Kd"] = new_kd

        # Edit 'n'
        current_n = self.edge_data.get("n", 1.0)
        new_n, ok = QInputDialog.getDouble(None, "Edit Edge n",
                                           "Hill coefficient n:",
                                           value=current_n)
        if ok:
            self.edge_data["n"] = new_n

        super().mouseDoubleClickEvent(event)


# ---------------------------------------------------
# 4) GraphScene: with "edge mode" + pinning
# ---------------------------------------------------
class GraphScene(QGraphicsScene):
    """
    Edge creation mode:
      - click on a node => start edge
      - drag => line follows mouse
      - if mouse is near a node, "pin" to that node
      - release => if pinned to a different node, finalize edge
                   else remove the temporary edge
    """

    SNAP_DISTANCE = 40  # how close we must be to "pin" a node

    def __init__(self, parent=None):
        super().__init__(parent)
        self.edge_mode = False
        self.temp_edge = None
        self.source_node = None

        self.pinned_node = None  # the node currently pinned (hover target)

    def set_edge_mode(self, enabled: bool):
        self.edge_mode = enabled
        # if turning off, cancel any partial edge
        if not enabled:
            if self.temp_edge:
                self.removeItem(self.temp_edge)
                self.temp_edge = None
            self.source_node = None
            self.clear_pinned_node()

    def clear_pinned_node(self):
        """Remove any highlight from the currently pinned node."""
        if self.pinned_node:
            self.pinned_node.setPen(QPen(Qt.black, 1))
        self.pinned_node = None

    def find_nearest_node(self, pos: QPointF):
        """
        Search all NodeItem in the scene. 
        Return the node whose center is within SNAP_DISTANCE, else None.
        """
        closest_node = None
        closest_dist = self.SNAP_DISTANCE
        for item in self.items():
            if isinstance(item, NodeItem):
                # center of item
                cx = item.x() + item.diameter/2
                cy = item.y() + item.diameter/2
                dx = pos.x() - cx
                dy = pos.y() - cy
                dist = math.hypot(dx, dy)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_node = item
        return closest_node

    def mousePressEvent(self, event):
        if self.edge_mode:
            # check if we clicked on a NodeItem
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, NodeItem):
                self.source_node = item
                # create a temporary edge
                self.temp_edge = EdgeItem(self.source_node)
                self.addItem(self.temp_edge)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.edge_mode and self.temp_edge and self.source_node:
            # 1) see if we are near a node => pinned
            nearest = self.find_nearest_node(event.scenePos())
            if nearest and nearest is not self.source_node:
                # pin to nearest
                self.handle_pinned_node(nearest)
                # update temp_edge line so it ends at pinned node center
                nx = nearest.x() + nearest.diameter/2
                ny = nearest.y() + nearest.diameter/2
                sx = self.source_node.x() + self.source_node.diameter/2
                sy = self.source_node.y() + self.source_node.diameter/2
                self.temp_edge.setLine(sx, sy, nx, ny)
            else:
                # no pinned node => unpin
                self.clear_pinned_node()
                # just draw line to mouse
                sx = self.source_node.x() + self.source_node.diameter/2
                sy = self.source_node.y() + self.source_node.diameter/2
                mx, my = event.scenePos().x(), event.scenePos().y()
                self.temp_edge.setLine(sx, sy, mx, my)

            event.accept()
            return
        super().mouseMoveEvent(event)

    def handle_pinned_node(self, node: NodeItem):
        """Highlight the pinned node if it's different from the current pinned_node."""
        if node == self.pinned_node:
            return
        self.clear_pinned_node()
        self.pinned_node = node
        self.pinned_node.setPen(QPen(QColor("cyan"), 2))

    def mouseReleaseEvent(self, event):
        if self.edge_mode and self.temp_edge and self.source_node:
            # finalize if pinned_node is valid and not the same as source
            if self.pinned_node and (self.pinned_node is not self.source_node):
                self.temp_edge.set_target_node(self.pinned_node)
            else:
                # not pinned => remove
                self.removeItem(self.temp_edge)
            # reset
            self.temp_edge = None
            self.source_node = None
            self.clear_pinned_node()
            event.accept()
            return
        super().mouseReleaseEvent(event)


# ---------------------------------------------------
# 5) MainWindow with a toolbar for edge mode, etc.
# ---------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NPMP Grenmlin GUI")

        # a) Scene & View
        self.scene = GraphScene()
        self.scene.setSceneRect(0, 0, 1200, 800)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.view)

        # Node Counters
        self.input_counter = 1
        self.output_counter = 1
        self.input_position = [50, 50]
        self.output_position = [300, 50]
        self.node_spacing = 60

        # b) Toolbar
        self.toolbar = QToolBar("Tools")
        self.addToolBar(self.toolbar)

        # Edge Mode toggle
        self.act_edge_mode = QAction("Edge Mode", self)
        self.act_edge_mode.setCheckable(True)
        self.act_edge_mode.toggled.connect(self.on_edge_mode_toggled)
        self.toolbar.addAction(self.act_edge_mode)

        # Add Input Node
        self.act_add_input = QAction("Add Input Node", self)
        self.act_add_input.triggered.connect(self.add_input_node)
        self.toolbar.addAction(self.act_add_input)

        # Add Output Node
        self.act_add_output = QAction("Add Output Node", self)
        self.act_add_output.triggered.connect(self.add_output_node)
        self.toolbar.addAction(self.act_add_output)

        # Delete Node
        self.act_delete_node = QAction("Delete Selected Node", self)
        self.act_delete_node.triggered.connect(self.delete_selected_node)
        self.toolbar.addAction(self.act_delete_node)

        # Delete Edge
        self.act_delete_edge = QAction("Delete Selected Edge", self)
        self.act_delete_edge.triggered.connect(self.delete_selected_edge)
        self.toolbar.addAction(self.act_delete_edge)

        # Plot GRN
        self.act_plot = QAction("Plot GRN", self)
        self.act_plot.triggered.connect(self.plot_grn)
        self.toolbar.addAction(self.act_plot)

    def on_edge_mode_toggled(self, checked: bool):
        self.scene.set_edge_mode(checked)

    # --- Node creation helpers ---
    def add_input_node(self):
        node_data = {"label": f"I{self.input_counter}", "node_type": "input"}
        node = NodeItem(self.input_position[0], self.input_position[1], diameter=50, node_data=node_data)
        self.scene.addItem(node)
        self.input_counter += 1
        self.input_position[1] += self.node_spacing

    def add_output_node(self):
        node_data = {"label": f"O{self.output_counter}", "node_type": "output"}
        node = NodeItem(self.output_position[0], self.output_position[1], diameter=50, node_data=node_data)
        self.scene.addItem(node)
        self.output_counter += 1
        self.output_position[1] += self.node_spacing

    def delete_selected_node(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, NodeItem):
                # Remove connected edges
                for edge in item.edges[:]:
                    self.scene.removeItem(edge)
                self.scene.removeItem(item)

    def delete_selected_edge(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, EdgeItem):
                self.scene.removeItem(item)

    # --- Build a MyGRN and plot ---
    def plot_grn(self):
        my_grn = MyGRN()
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                label = item.node_data.get("label", "???")
                node_type = item.node_data.get("node_type", "normal")
                if node_type == "input":
                    my_grn.add_input_species(label)
                elif node_type == "output":
                    my_grn.add_species(label, degrade_rate=0.1)
                else:
                    my_grn.add_species(label, degrade_rate=0.05)

        for item in self.scene.items():
            if isinstance(item, EdgeItem):
                src_label = item.source_node.node_data.get("label", "???")
                tgt_label = item.target_node.node_data.get("label", "???")
                reg_type = item.edge_data.get("type", 0)
                kd = item.edge_data.get("Kd", 1.0)
                n = item.edge_data.get("n", 1.0)
                my_grn.add_edge(src_label, tgt_label, reg_type, kd, n)

        # Use simple node labels
        pos = nx.spring_layout(my_grn.G)
        labels = {node: node for node in my_grn.G.nodes}
        nx.draw_networkx_labels(my_grn.G, pos, labels=labels, font_size=10, font_color='white')

        my_grn.plot_network()







def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
