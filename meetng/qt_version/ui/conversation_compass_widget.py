"""
Conversation Compass Widget

This module provides a visual conversation tree with programmatic control capabilities.

Key programmatic features:
1. Tree Visibility Control:
   - Show/hide specific branches using show_branch()
   - Control how many levels of a branch are visible

2. Camera/View Control:
   - Focus on specific nodes using focus_on_node()
   - Programmatically center the view on important parts of the conversation

3. Layout Control:
   - Switch between layout types (hierarchical, radial) using change_layout()
   - Apply force-directed adjustments to prevent node overlap

Usage examples:
    # Focus on a specific node
    compass_widget.focus_on_node("decision_node_123")
    
    # Show only a specific branch with 2 levels of depth
    compass_widget.show_branch("objection_node_456", 2)
    
    # Change the layout type
    compass_widget.change_layout("radial")
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QSplitter, QFrame, QToolButton, QMenu, QScrollArea,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem,
    QGraphicsPathItem, QGraphicsItem, QDialog, QFormLayout, QLineEdit,
    QTextEdit, QDialogButtonBox, QComboBox, QGraphicsRectItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF, QSizeF, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QPainterPath, QPen, QBrush, QColor, QFont, QPainter
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from math import cos, sin, pi
import random

class ConversationCompassSetupDialog(QDialog):
    """Dialog for setting up a new conversation compass session"""
    
    def __init__(self, parent=None, langchain_service=None):
        super().__init__(parent)
        self.langchain_service = langchain_service
        
        self.setWindowTitle("New Conversation Compass")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Form layout for inputs
        form = QFormLayout()
        
        # Conversation type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Sales Conversation", 
            "Job Interview",
            "Customer Support",
            "Negotiation",
            "Team Meeting"
        ])
        form.addRow("Conversation Type:", self.type_combo)
        
        # Conversation title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter a title for this conversation")
        form.addRow("Title:", self.title_edit)
        
        # Conversation goal
        self.goal_edit = QTextEdit()
        self.goal_edit.setPlaceholderText("What is the goal of this conversation?")
        self.goal_edit.setMaximumHeight(80)
        form.addRow("Goal:", self.goal_edit)
        
        # Participants
        self.participants_edit = QLineEdit()
        self.participants_edit.setPlaceholderText("Enter participant names separated by commas")
        form.addRow("Participants:", self.participants_edit)
        
        layout.addLayout(form)
        
        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
    def get_setup_result(self):
        """Get the setup result as a dictionary"""
        # Parse participants (comma-separated)
        participants = [p.strip() for p in self.participants_edit.text().split(",") if p.strip()]
        
        return {
            "conversation_type": self.type_combo.currentText(),
            "title": self.title_edit.text().strip(),
            "goal": self.goal_edit.toPlainText().strip(),
            "participants": participants
        }

class TreeLayoutManager:
    """Manages different layout strategies for conversation trees"""
    
    def __init__(self, tree_view):
        self.tree_view = tree_view
        self.node_spacing_x = 180  # Horizontal spacing between siblings
        self.level_spacing_y = 120  # Vertical spacing between levels
        self.min_node_distance = 80  # Minimum distance between any two nodes
        self.layout_strategy = "hierarchical"  # Default layout strategy
        
    def layout_tree(self, root_id=None):
        """Layout the entire tree using the current strategy"""
        if not root_id:
            # Find root nodes (no parent)
            root_nodes = [node_id for node_id, node in self.tree_view.nodes.items() 
                         if not node.parent_id]
            if not root_nodes:
                return
            root_id = root_nodes[0]
            
        # Reset all node positions for a fresh layout
        self._reset_node_positions()
        
        # Apply the selected layout strategy
        if self.layout_strategy == "radial":
            self._apply_radial_layout(root_id)
        else:
            # Default hierarchical layout
            self._apply_hierarchical_layout(root_id)
        
        # Update all edges
        self.tree_view._update_all_edges()
        
        # Update scene rect to fit all nodes
        self.tree_view.scene.setSceneRect(self.tree_view.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50))
    
    def _apply_hierarchical_layout(self, root_id):
        """Apply the traditional hierarchical layout"""
        # Position the root node at the center top
        root_node = self.tree_view.nodes.get(root_id)
        if not root_node:
            return
            
        scene_rect = self.tree_view.scene.sceneRect()
        root_node.setPos((scene_rect.width() - root_node.rect().width()) / 2, 20)
        
        # Calculate subtree sizes first (bottom-up pass)
        subtree_sizes = self._calculate_subtree_sizes(root_id)
        
        # Position all nodes (top-down pass)
        self._position_subtree(root_id, 0, subtree_sizes)
    
    def _apply_radial_layout(self, root_id):
        """Apply a radial layout with root at center and children in concentric circles"""
        from math import cos, sin, pi
        
        # Get the root node
        root_node = self.tree_view.nodes.get(root_id)
        if not root_node:
            return
            
        # Get scene dimensions
        scene_rect = self.tree_view.scene.sceneRect()
        center_x = scene_rect.width() / 2
        center_y = scene_rect.height() / 2
        
        # Position root node at center
        root_node.setPos(
            center_x - root_node.rect().width() / 2,
            center_y - root_node.rect().height() / 2
        )
        
        # Calculate the maximum depth of the tree
        max_depth = self._calculate_max_depth(root_id)
        
        # Position all other nodes in concentric circles
        self._position_nodes_radial(root_id, center_x, center_y, 0, max_depth)
        
    def _reset_node_positions(self):
        """Reset all node positions"""
        for node in self.tree_view.nodes.values():
            # Don't actually move them yet, just reset internal positions
            node.setPos(0, 0)
    
    def _calculate_max_depth(self, node_id, current_depth=0):
        """Calculate the maximum depth of the tree from the given node"""
        node = self.tree_view.nodes.get(node_id)
        if not node or not node.children:
            return current_depth
            
        child_depths = [self._calculate_max_depth(child_id, current_depth + 1) 
                        for child_id in node.children]
        return max(child_depths) if child_depths else current_depth
    
    def _position_nodes_radial(self, node_id, center_x, center_y, depth, max_depth):
        """Position nodes in a radial layout with improved alignment
        
        Args:
            node_id: ID of the current node
            center_x, center_y: Center coordinates of the layout
            depth: Current depth level (0 for root)
            max_depth: Maximum depth of the tree
        """
        from math import cos, sin, pi
        
        node = self.tree_view.nodes.get(node_id)
        if not node:
            return
            
        # Skip root node (already positioned at center)
        if depth > 0:
            # Calculate radius for this level (increases with depth)
            # Use a non-linear scale to give more space to outer rings
            radius = 150 * (depth / max_depth) ** 0.8 if max_depth > 0 else 150
            
            # Get number of children for the parent
            parent = self.tree_view.nodes.get(node.parent_id)
            if not parent:
                return
                
            # Find position of this node among siblings
            siblings = parent.children
            position = siblings.index(node_id) if node_id in siblings else 0
            total_siblings = len(siblings)
            
            # Calculate angle based on position among siblings
            # Distribute nodes evenly around the circle
            angle_start = 0  # Start angle in radians
            angle_step = 2 * pi / total_siblings if total_siblings > 0 else 0
            
            # Ensure even distribution by using fixed angles
            # This creates a more balanced layout
            angle = angle_start + position * angle_step
            
            # Calculate position using polar coordinates
            x = center_x + radius * cos(angle)
            y = center_y + radius * sin(angle)
            
            # Adjust for node size
            x -= node.rect().width() / 2
            y -= node.rect().height() / 2
            
            # Set node position
            node.setPos(x, y)
        
        # Recursively position children
        for child_id in node.children:
            self._position_nodes_radial(child_id, center_x, center_y, depth + 1, max_depth)
            
    def _calculate_subtree_sizes(self, node_id):
        """Calculate the size requirements of each subtree
        
        Returns a dictionary mapping node_id to (width, height, num_leaves)
        """
        node = self.tree_view.nodes.get(node_id)
        if not node:
            return {}
            
        result = {}
        
        if not node.children:
            # Leaf node
            result[node_id] = (node.rect().width(), node.rect().height(), 1)
            return result
            
        # Calculate sizes for all children first
        child_sizes = {}
        total_width = 0
        max_height = 0
        total_leaves = 0
        
        for child_id in node.children:
            # Recursively calculate child subtree sizes
            subtree_sizes = self._calculate_subtree_sizes(child_id)
            child_sizes.update(subtree_sizes)
            
            if child_id in subtree_sizes:
                child_width, child_height, child_leaves = subtree_sizes[child_id]
                total_width += child_width
                max_height = max(max_height, child_height)
                total_leaves += child_leaves
                
        # Add spacing between children
        if len(node.children) > 1:
            total_width += self.node_spacing_x * (len(node.children) - 1)
            
        # Calculate this node's subtree size
        width = max(node.rect().width(), total_width)
        height = node.rect().height() + self.level_spacing_y + max_height
        
        result[node_id] = (width, height, total_leaves)
        result.update(child_sizes)
        
        return result
        
    def _position_subtree(self, node_id, level, subtree_sizes, x_offset=0):
        """Position a node and all its children recursively
        
        Args:
            node_id: ID of the node to position
            level: Current tree level (0 for root)
            subtree_sizes: Dictionary of subtree size requirements
            x_offset: Horizontal offset for this subtree
        
        Returns:
            The total width used by this subtree
        """
        node = self.tree_view.nodes.get(node_id)
        if not node:
            return 0
            
        # Position this node
        y_pos = level * self.level_spacing_y
        
        if level == 0:
            # Root node is already positioned
            node_width = node.rect().width()
        else:
            # Position based on parent and siblings
            node_width = node.rect().width()
            node.setPos(x_offset + (subtree_sizes[node_id][0] - node_width) / 2, y_pos)
            
        if not node.children:
            return subtree_sizes[node_id][0] if node_id in subtree_sizes else node_width
            
        # Position all children
        current_x = x_offset
        for child_id in node.children:
            if child_id in subtree_sizes:
                child_width = subtree_sizes[child_id][0]
                self._position_subtree(child_id, level + 1, subtree_sizes, current_x)
                current_x += child_width + self.node_spacing_x
                
        return subtree_sizes[node_id][0] if node_id in subtree_sizes else node_width
        
    def apply_force_directed_adjustments(self, iterations=10):
        """Apply force-directed layout adjustments to prevent node overlap"""
        if not self.tree_view.nodes:
            return
            
        # Parameters for force-directed layout
        repulsion = 5000  # Repulsion force between nodes
        attraction = 0.1  # Attraction force to ideal positions
        damping = 0.9     # Damping factor to prevent oscillation
        
        # Store original positions
        original_positions = {node_id: node.pos() for node_id, node in self.tree_view.nodes.items()}
        
        # Create a working copy of current positions
        positions = {node_id: QPointF(node.pos()) for node_id, node in self.tree_view.nodes.items()}
        
        # Calculate forces and update positions
        for _ in range(iterations):
            # Calculate repulsion forces between all pairs of nodes
            forces = {node_id: QPointF(0, 0) for node_id in self.tree_view.nodes}
            
            # Repulsion between nodes
            node_ids = list(self.tree_view.nodes.keys())
            for i, node_id1 in enumerate(node_ids):
                node1 = self.tree_view.nodes[node_id1]
                pos1 = positions[node_id1]
                
                for node_id2 in node_ids[i+1:]:
                    node2 = self.tree_view.nodes[node_id2]
                    pos2 = positions[node_id2]
                    
                    # Calculate distance and direction
                    dx = pos1.x() - pos2.x()
                    dy = pos1.y() - pos2.y()
                    distance_sq = dx*dx + dy*dy
                    
                    if distance_sq < 1:  # Avoid division by zero
                        dx = random.uniform(-1, 1)
                        dy = random.uniform(-1, 1)
                        distance_sq = dx*dx + dy*dy
                        
                    # Calculate repulsion force (inverse square law)
                    force = repulsion / distance_sq
                    
                    # Apply force in the direction of the vector between nodes
                    distance = (distance_sq) ** 0.5
                    fx = force * dx / distance
                    fy = force * dy / distance
                    
                    # Add to total forces
                    forces[node_id1] += QPointF(fx, fy)
                    forces[node_id2] += QPointF(-fx, -fy)
            
            # Attraction to original positions (maintain hierarchy)
            for node_id, pos in positions.items():
                orig_pos = original_positions[node_id]
                dx = orig_pos.x() - pos.x()
                dy = orig_pos.y() - pos.y()
                
                forces[node_id] += QPointF(dx * attraction, dy * attraction)
                
            # Update positions based on forces
            for node_id, force in forces.items():
                # Apply damping to the force
                force *= damping
                
                # Update position
                positions[node_id] += force
                
                # Ensure y-position maintains hierarchy (nodes stay at their level)
                positions[node_id].setY(original_positions[node_id].y())
                
        # Apply the final positions to the actual nodes
        for node_id, pos in positions.items():
            self.tree_view.nodes[node_id].setPos(pos)
            
        # Update all edges
        self.tree_view._update_all_edges()

class ConversationNode(QGraphicsRectItem):
    """A node in the conversation tree"""
    
    def __init__(self, x, y, width, height, text, node_type="statement", parent=None):
        super().__init__(0, 0, width, height, parent)
        self.setPos(x, y)
        self.setBrush(QBrush(self._get_color_for_type(node_type)))
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        # Disable node dragging to prevent users from moving nodes
        
        # Add text
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setPlainText(text)
        self.text_item.setTextWidth(width - 10)
        
        # Center text
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(
            (width - text_rect.width()) / 2,
            (height - text_rect.height()) / 2
        )
        
        # Set tooltip with full text for better readability on hover
        self.setToolTip(text)
        
        # Store metadata
        self.node_type = node_type
        self.node_id = None
        self.parent_id = None
        self.children = []
        self.speaker = ""
        self.content = text
        self.node_number = None  # Will be set when added to the tree
        
        # Collapsible state
        self.is_collapsed = False
        self.collapse_button = None
        self._create_collapse_button()
        
        # Navigation indicator
        self.nav_indicator = None
        
    def _create_collapse_button(self):
        """Create a collapse/expand button for this node"""
        # Disable collapse/expand functionality
        self.collapse_button = None
        self.collapse_text = None
        
    def update_collapse_button(self):
        """Update the collapse button state"""
        # Collapse functionality disabled
        pass
    
    def toggle_collapsed(self):
        """Toggle the collapsed state of this node"""
        # Collapse functionality disabled
        pass
        
    def contains_point(self, point):
        """Check if a point is inside this node"""
        # Check if point is in the main node
        node_rect = QRectF(
            self.pos().x(),
            self.pos().y(),
            self.rect().width(),
            self.rect().height()
        )
        if node_rect.contains(point):
            return "node"
            
        return None
        
    def _get_color_for_type(self, node_type):
        """Get color based on node type"""
        colors = {
            "statement": QColor(200, 230, 255),  # Light blue
            "question": QColor(255, 230, 200),   # Light orange
            "objection": QColor(255, 200, 200),  # Light red
            "decision": QColor(200, 255, 200),   # Light green
            "current": QColor(255, 255, 150),    # Light yellow
            "suggested": QColor(230, 255, 230),  # Pale green
            "actual": QColor(220, 240, 255)      # Pale blue
        }
        return colors.get(node_type, QColor(240, 240, 240))  # Default light gray
        
    def set_speaker(self, speaker):
        """Set the speaker for this node"""
        self.speaker = speaker
        self._update_text()
        
    def _update_text(self):
        """Update the displayed text with speaker if available"""
        # Truncate text if too long
        display_text = self.content
        if len(display_text) > 100:
            display_text = display_text[:97] + "..."
            
        # Add node number if available
        number_prefix = f"#{self.node_number}: " if self.node_number else ""
        
        if self.speaker:
            self.text_item.setHtml(f"<b>{number_prefix}{self.speaker}</b><br>{display_text}")
        else:
            self.text_item.setHtml(f"<b>{number_prefix}</b>{display_text}")
        
        # Recenter text
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(
            (self.rect().width() - text_rect.width()) / 2,
            (self.rect().height() - text_rect.height()) / 2
        )
        
        # Always set full text as tooltip
        full_text = f"{self.speaker}: {self.content}" if self.speaker else self.content
        self.setToolTip(full_text)
        
    def add_navigation_indicator(self, number):
        """Add a visual indicator showing this node can be navigated to by number
        
        Args:
            number: The number to display, or None to remove the indicator
        """
        # Remove existing indicator if any
        if hasattr(self, 'nav_indicator') and self.nav_indicator:
            self.scene().removeItem(self.nav_indicator)
            self.nav_indicator = None
            
        # If number is None, just remove the indicator
        if number is None:
            return
            
        # Create a circular indicator with number
        from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
        from PyQt6.QtCore import QRectF
        from PyQt6.QtGui import QBrush, QColor, QPen, QFont
        
        # Create circle
        self.nav_indicator = QGraphicsEllipseItem(0, 0, 24, 24, self)
        self.nav_indicator.setBrush(QBrush(QColor(0, 120, 215)))
        self.nav_indicator.setPen(QPen(QColor(255, 255, 255)))
        
        # Position at top-right corner
        self.nav_indicator.setPos(self.rect().width() - 30, -12)
        
        # Add number text
        text = QGraphicsTextItem(str(number), self.nav_indicator)
        text.setDefaultTextColor(QColor(255, 255, 255))
        text.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        # Center text in circle
        text_rect = text.boundingRect()
        text.setPos(
            (24 - text_rect.width()) / 2,
            (24 - text_rect.height()) / 2
        )

class TreeMinimap(QGraphicsView):
    """A minimap showing the entire tree with current viewport"""
    
    viewport_clicked = pyqtSignal(QPointF)  # Signal when minimap is clicked
    
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        self.setFixedSize(150, 150)
        self.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 5px;")
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create scene that mirrors the main scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Add viewport rectangle
        self.viewport_rect = QGraphicsRectItem(0, 0, 50, 50)
        self.viewport_rect.setPen(QPen(QColor(255, 0, 0)))
        self.viewport_rect.setBrush(QBrush(QColor(255, 0, 0, 30)))
        self.scene.addItem(self.viewport_rect)
        
    def update_minimap(self):
        """Update the minimap with current tree and viewport"""
        if not self.main_view:
            return
            
        # Clear existing items except viewport rect
        for item in self.scene.items():
            if item != self.viewport_rect:
                self.scene.removeItem(item)
        
        # Get main scene bounds
        main_bounds = self.main_view.scene.itemsBoundingRect()
        if main_bounds.isEmpty():
            return
            
        # Calculate scale factor to fit in minimap
        scale_x = self.width() / max(1, main_bounds.width())
        scale_y = self.height() / max(1, main_bounds.height())
        scale = min(scale_x, scale_y) * 0.9  # 90% to leave some margin
        
        # Add simplified versions of all nodes
        for node_id, node in self.main_view.nodes.items():
            if not node.isVisible():
                continue
                
            # Create mini node
            mini_node = QGraphicsRectItem(
                node.pos().x() * scale,
                node.pos().y() * scale,
                node.rect().width() * scale,
                node.rect().height() * scale
            )
            
            # Use same color as main node but slightly transparent
            color = node._get_color_for_type(node.node_type)
            mini_node.setBrush(QBrush(color))
            mini_node.setPen(QPen(Qt.GlobalColor.black, 0.5))
            
            # Highlight current node
            if node_id == self.main_view.current_node_id:
                mini_node.setPen(QPen(Qt.GlobalColor.red, 1))
                mini_node.setBrush(QBrush(QColor(255, 0, 0, 100)))
            
            self.scene.addItem(mini_node)
        
        # Add simplified edges
        for edge, src_id, dst_id in self.main_view.edges:
            if src_id in self.main_view.nodes and dst_id in self.main_view.nodes:
                src = self.main_view.nodes[src_id]
                dst = self.main_view.nodes[dst_id]
                
                if not src.isVisible() or not dst.isVisible():
                    continue
                    
                # Create path for edge
                path = QPainterPath()
                path.moveTo(
                    (src.pos().x() + src.rect().width()/2) * scale,
                    (src.pos().y() + src.rect().height()/2) * scale
                )
                path.lineTo(
                    (dst.pos().x() + dst.rect().width()/2) * scale,
                    (dst.pos().y() + dst.rect().height()/2) * scale
                )
                
                # Add path to scene
                edge_item = QGraphicsPathItem(path)
                edge_item.setPen(QPen(Qt.GlobalColor.darkGray, 0.5))
                self.scene.addItem(edge_item)
        
        # Update viewport rectangle
        visible_rect = self.main_view.mapToScene(self.main_view.viewport().rect()).boundingRect()
        self.viewport_rect.setRect(
            visible_rect.x() * scale,
            visible_rect.y() * scale,
            visible_rect.width() * scale,
            visible_rect.height() * scale
        )
        
        # Fit scene in view
        self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
    def mousePressEvent(self, event):
        """Handle mouse press to navigate in main view"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert click to scene coordinates
            scene_pos = self.mapToScene(event.pos())
            
            # Emit signal with the clicked position
            self.viewport_clicked.emit(scene_pos)
            
            event.accept()
        else:
            super().mousePressEvent(event)

class ConversationTreeView(QGraphicsView):
    """Custom view for displaying the conversation tree"""
    
    node_clicked = pyqtSignal(object)  # Signal when a node is clicked
    node_collapsed = pyqtSignal(str, bool)  # Signal when a node is collapsed/expanded (node_id, is_collapsed)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        # Set tooltip with usage instructions
        self.setToolTip(
            "Navigation Controls:\n"
            "- Click and drag to pan the view\n"
            "- Ctrl+Scroll to zoom in/out\n"
            "- Click on a node to select it\n"
            "- Click the +/- button on a node to expand/collapse its children"
        )
        
        # Create scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Initialize tree data
        self.nodes = {}
        self.current_node_id = None
        self.edges = []  # Store edges for updating
        self.collapsed_subtrees = set()  # Track collapsed subtrees
        
        # Create layout manager
        self.layout_manager = TreeLayoutManager(self)
        
        # Set up zoom
        self.zoom_factor = 1.15
        
        # Animation properties
        self.node_animations = {}
        self.edge_animations = {}
        
        # Create minimap
        self.minimap = TreeMinimap(self)
        self.minimap.viewport_clicked.connect(self._navigate_to_minimap_position)
        self.minimap.hide()  # Initially hidden, will be shown when tree has nodes
    
    def wheelEvent(self, event):
        """Handle zoom with mouse wheel"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom in/out with Ctrl+Wheel
            if event.angleDelta().y() > 0:
                self.scale(self.zoom_factor, self.zoom_factor)
            else:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
            event.accept()
        else:
            super().wheelEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Get scene position
            scene_pos = self.mapToScene(event.pos())
            
            # Check if we clicked on a node
            for node_id, node in self.nodes.items():
                hit_part = node.contains_point(scene_pos)
                if hit_part == "node":
                    self.node_clicked.emit(node)
                    return
                    
        # Allow panning with drag
        super().mousePressEvent(event)
    
    def clear_tree(self):
        """Clear the tree"""
        self.scene.clear()
        self.nodes = {}
        self.edges = []
        self.current_node_id = None
        self.collapsed_subtrees = set()
        self.node_animations = {}
        self.edge_animations = {}
    
    def set_current_node(self, node_id):
        """Set the current active node"""
        # Reset previous current node
        if self.current_node_id and self.current_node_id in self.nodes:
            prev_node = self.nodes[self.current_node_id]
            prev_node.setBrush(QBrush(prev_node._get_color_for_type(prev_node.node_type)))
            prev_node.setGraphicsEffect(None)
        
        # Reset all edge styles
        for edge, src, dst in self.edges:
            edge.setPen(QPen(Qt.GlobalColor.darkGray, 2))
        
        # Set new current node
        if node_id in self.nodes:
            self.current_node_id = node_id
            current_node = self.nodes[node_id]
            current_node.setBrush(QBrush(current_node._get_color_for_type("current")))
            
            # Add a subtle highlight effect
            from PyQt6.QtWidgets import QGraphicsDropShadowEffect
            from PyQt6.QtGui import QColor
            
            glow = QGraphicsDropShadowEffect()
            glow.setColor(QColor(255, 255, 0, 160))  # Yellow glow
            glow.setOffset(0, 0)
            glow.setBlurRadius(20)
            current_node.setGraphicsEffect(glow)
            
            # Ensure node is visible
            self.ensureVisible(current_node)
            
            # Make sure all parent nodes are expanded to show this node
            self._ensure_parents_expanded(node_id)
            
            # Highlight the path from root to this node
            self._highlight_path_to_node(node_id)
            
            # Update navigation indicators
            self.update_navigation_indicators()
            
            # Update minimap to reflect changes
            if hasattr(self, 'minimap'):
                self.minimap.update_minimap()
    
    def _highlight_path_to_node(self, node_id):
        """Highlight the path from root to the specified node"""
        # Build the path from node to root
        path = []
        current = node_id
        
        while current:
            path.insert(0, current)  # Add to beginning of path
            node = self.nodes.get(current)
            if not node or not node.parent_id:
                break
            current = node.parent_id
            
        # Highlight nodes and edges along the path
        for i, path_node_id in enumerate(path):
            if path_node_id not in self.nodes:
                continue
                
            node = self.nodes[path_node_id]
            
            # Skip the current node (already highlighted)
            if path_node_id == self.current_node_id:
                continue
                
            # Use a gradient from start to current
            progress = i / max(1, len(path) - 1)
            color = QColor(
                int(220 + 35 * progress),  # More red as we progress
                int(240 - 40 * progress),  # Less green as we progress
                255                         # Constant blue
            )
            
            # Apply a subtle highlight to path nodes
            node.setBrush(QBrush(color))
            
            # Highlight edges between path nodes
            if i > 0:
                prev_id = path[i-1]
                for edge, src, dst in self.edges:
                    if (src == prev_id and dst == path_node_id) or (src == path_node_id and dst == prev_id):
                        edge.setPen(QPen(QColor(0, 120, 215), 3))
    
    def _ensure_parents_expanded(self, node_id):
        """Make sure all parent nodes are expanded to show this node"""
        node = self.nodes.get(node_id)
        if not node or not node.parent_id:
            return
            
        # Check if parent is collapsed
        parent = self.nodes.get(node.parent_id)
        if parent and parent.is_collapsed:
            # Expand parent
            parent.is_collapsed = False
            parent.update_collapse_button()
            self.node_collapsed.emit(parent.node_id, False)
            
            # Update visibility
            self._update_subtree_visibility(parent.node_id, True)
            
        # Recursively check parent's parents
        self._ensure_parents_expanded(node.parent_id)
    
    def add_node(self, node_id, parent_id, text, node_type="statement", x=0, y=0, speaker=""):
        """Add a node to the tree"""
        # Create node with wider rectangle
        width = 200  # Increased from 150
        height = 80  # Increased from 60
        node = ConversationNode(x, y, width, height, text, node_type)
        node.node_id = node_id
        node.parent_id = parent_id
        node.node_number = len(self.nodes) + 1  # Assign sequential number
        if speaker:
            node.set_speaker(speaker)
        
        # Add to scene
        self.scene.addItem(node)
        self.nodes[node_id] = node
        
        # Connect to parent if exists
        if parent_id and parent_id in self.nodes:
            parent = self.nodes[parent_id]
            parent.children.append(node_id)
            parent.update_collapse_button()
            
            # Draw connection line
            path = QPainterPath()
            path.moveTo(parent.pos() + QPointF(parent.rect().width()/2, parent.rect().height()))
            path.lineTo(node.pos() + QPointF(node.rect().width()/2, 0))
            
            line = QGraphicsPathItem(path)
            line.setPen(QPen(Qt.GlobalColor.darkGray, 2))
            self.scene.addItem(line)
            self.edges.append((line, parent.node_id, node.node_id))
            
            # Check if parent is collapsed
            if parent.is_collapsed:
                node.setVisible(False)
        
        # Animate the new node
        self._animate_new_node(node)
        
        return node
    
    def _animate_new_node(self, node):
        """Animate a new node appearing"""
        try:
            # Save original position
            original_pos = node.pos()
            
            # Start from slightly above
            node.setPos(original_pos.x(), original_pos.y() - 20)
            
            # Create position animation
            pos_anim = QPropertyAnimation(node, b"pos")
            pos_anim.setDuration(500)
            pos_anim.setStartValue(node.pos())
            pos_anim.setEndValue(original_pos)
            pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Start animation
            pos_anim.start()
            
            # Store animation to prevent garbage collection
            self.node_animations[node.node_id] = pos_anim
        except Exception as e:
            print(f"Animation error: {str(e)}")
            # Just set the final position without animation
            node.setPos(original_pos)
    
    def layout_tree(self):
        """Layout the tree using the layout manager"""
        try:
            # Use the layout manager to position all nodes
            self.layout_manager.layout_tree()
            
            # Apply force-directed adjustments to prevent overlap
            self.layout_manager.apply_force_directed_adjustments()
            
            # Update scene rect to fit all nodes
            self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50))
            
            # Center view on current node if one is selected
            if self.current_node_id and self.current_node_id in self.nodes:
                self.centerOn(self.nodes[self.current_node_id])
                
            # Update minimap
            if len(self.nodes) > 0:
                self.minimap.update_minimap()
                self.minimap.show()
            else:
                self.minimap.hide()
                
        except Exception as e:
            print(f"Error in layout_tree: {str(e)}")
            
    def _navigate_to_minimap_position(self, scene_pos):
        """Navigate to the position clicked on the minimap"""
        # Calculate the scale factor between minimap and main view
        minimap_bounds = self.minimap.scene.itemsBoundingRect()
        main_bounds = self.scene.itemsBoundingRect()
        
        if minimap_bounds.isEmpty() or main_bounds.isEmpty():
            return
            
        scale_x = main_bounds.width() / max(1, minimap_bounds.width())
        scale_y = main_bounds.height() / max(1, minimap_bounds.height())
        
        # Calculate target position in main scene
        target_x = scene_pos.x() * scale_x
        target_y = scene_pos.y() * scale_y
        
        # Center view on this position
        self.centerOn(target_x, target_y)
        
        # Update minimap
        self.minimap.update_minimap()
    
    def _update_subtree_visibility(self, node_id, visible):
        """Update visibility of a subtree
        
        Args:
            node_id: ID of the root of the subtree
            visible: Whether the subtree should be visible
        """
        node = self.nodes.get(node_id)
        if not node:
            return
            
        # Update children recursively
        for child_id in node.children:
            child = self.nodes.get(child_id)
            if child:
                child.setVisible(visible)
                
                # Only recurse if this child is expanded
                if not child.is_collapsed:
                    self._update_subtree_visibility(child_id, visible)
    
    def _update_all_edges(self):
        """Update all edge connections after nodes have moved"""
        for edge, parent_id, child_id in self.edges:
            if parent_id in self.nodes and child_id in self.nodes:
                parent = self.nodes[parent_id]
                child = self.nodes[child_id]
                
                # Only update if both nodes are visible
                if parent.isVisible() and child.isVisible():
                    # Update path with a curved line
                    path = QPainterPath()
                    
                    # Start and end points - connect at bottom center of parent and top center of child
                    start_x = parent.pos().x() + parent.rect().width()/2
                    start_y = parent.pos().y() + parent.rect().height()
                    end_x = child.pos().x() + child.rect().width()/2
                    end_y = child.pos().y()
                    
                    # Control points for curve
                    ctrl1_x = start_x
                    ctrl1_y = start_y + (end_y - start_y) / 3
                    ctrl2_x = end_x
                    ctrl2_y = end_y - (end_y - start_y) / 3
                    
                    # Create curved path
                    path.moveTo(start_x, start_y)
                    path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, end_x, end_y)
                    
                    # Update edge
                    edge.setPath(path)
                    edge.setVisible(True)
                else:
                    edge.setVisible(False)
    
    def focus_on_branch(self, root_node_id):
        """Programmatically focus on a specific branch
        
        This method allows developers to programmatically focus the view on a specific
        node and its branch. It will:
        1. Set the specified node as the current node (highlighting it)
        2. Center the view on this node
        3. Update the minimap to reflect the new focus
        
        Usage example:
            tree_view.focus_on_branch("node_123")
        
        Args:
            root_node_id: ID of the node to focus on
        """
        # Find the node
        if root_node_id not in self.nodes:
            return
            
        # Set current node
        self.set_current_node(root_node_id)
        
        # Center view on this node
        self.centerOn(self.nodes[root_node_id])
        
        # Update navigation indicators
        self.update_navigation_indicators()
        
        # Update minimap
        self.minimap.update_minimap()
        
    def update_navigation_indicators(self):
        """Update navigation indicators on nodes"""
        # Clear all existing indicators
        for node in self.nodes.values():
            if hasattr(node, 'add_navigation_indicator'):
                node.add_navigation_indicator(None)
        
        # Add indicators to children of current node
        if self.current_node_id and self.current_node_id in self.nodes:
            current_node = self.nodes[self.current_node_id]
            for i, child_id in enumerate(current_node.children):
                if child_id in self.nodes:
                    child = self.nodes[child_id]
                    if hasattr(child, 'add_navigation_indicator'):
                        child.add_navigation_indicator(i + 1)
    
    def show_only_branch(self, root_node_id, levels=2):
        """Show only a specific branch up to specified levels
        
        This method allows developers to programmatically control which parts of the tree
        are visible. It will:
        1. Hide all nodes in the tree
        2. Show only the specified node and its descendants up to the specified number of levels
        3. Update the edge connections
        4. Update the minimap
        
        Usage example:
            # Show node_123 and its children and grandchildren
            tree_view.show_only_branch("node_123", 2)
            
            # Show just node_123 and its immediate children
            tree_view.show_only_branch("node_123", 1)
        
        Args:
            root_node_id: ID of the root node of the branch to show
            levels: Number of levels to show (0 = just the root node)
        """
        # Reset visibility of all nodes
        for node in self.nodes.values():
            node.setVisible(False)
            
        # Show the specified branch
        self._show_branch_recursive(root_node_id, 0, levels)
        
        # Update edges
        self._update_all_edges()
        
        # Update minimap
        self.minimap.update_minimap()
    
    def _show_branch_recursive(self, node_id, current_level, max_levels):
        """Recursively show nodes in a branch
        
        Helper method for show_only_branch that recursively shows nodes
        up to the specified maximum level.
        
        Args:
            node_id: ID of the current node
            current_level: Current depth level (0 for root)
            max_levels: Maximum depth to show
        """
        if node_id not in self.nodes or current_level > max_levels:
            return
            
        # Show this node
        self.nodes[node_id].setVisible(True)
        
        # Show children if not at max level
        if current_level < max_levels:
            for child_id in self.nodes[node_id].children:
                self._show_branch_recursive(child_id, current_level + 1, max_levels)

class SuggestedResponseWidget(QFrame):
    """Widget for displaying suggested responses"""
    
    response_selected = pyqtSignal(str, str)  # speaker, content
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Suggested Responses")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        # Responses container
        self.responses_layout = QVBoxLayout()
        layout.addLayout(self.responses_layout)
        
        # Add some placeholder responses
        self.clear_responses()
    
    def add_response(self, speaker, text, confidence=0.0):
        """Add a suggested response"""
        response_frame = QFrame()
        response_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        response_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self._get_confidence_color(confidence)};
                border-radius: 5px;
                padding: 5px;
            }}
        """)
        
        response_layout = QVBoxLayout(response_frame)
        response_layout.setContentsMargins(5, 5, 5, 5)
        
        # Speaker label
        speaker_label = QLabel(f"<b>{speaker}</b>")
        speaker_label.setToolTip(f"Speaker: {speaker}")
        response_layout.addWidget(speaker_label)
        
        # Response text
        response_label = QLabel(text)
        response_label.setWordWrap(True)
        response_label.setToolTip(text)  # Show full text on hover
        response_layout.addWidget(response_label)
        
        # Confidence indicator
        confidence_label = QLabel(f"Confidence: {int(confidence * 100)}%")
        confidence_label.setStyleSheet("color: #666; font-size: 10px;")
        response_layout.addWidget(confidence_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        use_btn = QPushButton("Use")
        use_btn.setMaximumWidth(60)
        use_btn.setToolTip("Use this response in the conversation")
        use_btn.clicked.connect(lambda: self.response_selected.emit(speaker, text))
        
        copy_btn = QPushButton("Copy")
        copy_btn.setMaximumWidth(60)
        copy_btn.setToolTip("Copy this response to clipboard")
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(text))
        
        button_layout.addWidget(use_btn)
        button_layout.addWidget(copy_btn)
        button_layout.addStretch()
        
        response_layout.addLayout(button_layout)
        
        self.responses_layout.addWidget(response_frame)
    
    def clear_responses(self):
        """Clear all responses"""
        # Remove all widgets from layout
        while self.responses_layout.count():
            item = self.responses_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add empty state
        empty_label = QLabel("No suggested responses yet")
        empty_label.setStyleSheet("color: #999; font-style: italic;")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.responses_layout.addWidget(empty_label)
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        
        # Show feedback when text is copied
        from PyQt6.QtWidgets import QToolTip
        from PyQt6.QtGui import QCursor
        QToolTip.showText(QCursor.pos(), "Copied to clipboard!", None, 2000)
    
    def _get_confidence_color(self, confidence):
        """Get background color based on confidence level"""
        if confidence >= 0.8:
            return "#E8F5E9"  # Light green
        elif confidence >= 0.5:
            return "#FFF8E1"  # Light yellow
        else:
            return "#FFF3E0"  # Light orange
            
    def set_suggestions(self, suggestions):
        """Set suggestions from a list of ConversationNode objects
        
        Args:
            suggestions: List of ConversationNode objects
        """
        self.clear_responses()
        
        if not suggestions:
            return
            
        # Add each suggestion with decreasing confidence
        base_confidence = 0.85
        for i, node in enumerate(suggestions):
            confidence = max(0.5, base_confidence - (i * 0.1))
            self.add_response(node.speaker, node.content, confidence)

class ConversationCompassWidget(QWidget):
    """Main widget for the Conversation Compass feature"""
    
    def __init__(self, parent=None, langchain_service=None):
        super().__init__(parent)
        self.langchain_service = langchain_service
        self.current_session = None
        self.tree_service = None
        
        self.init_ui()
        
        # Set default layout strategy
        self.current_layout = "hierarchical"
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        # New session button
        self.new_session_btn = QPushButton("New Conversation")
        self.new_session_btn.setToolTip("Start a new conversation compass session")
        self.new_session_btn.clicked.connect(self.start_new_session)
        header_layout.addWidget(self.new_session_btn)
        
        # Session info
        self.session_info = QLabel("No active session")
        header_layout.addWidget(self.session_info, 1)
        
        # Mode indicator will be added dynamically when session starts
        
        # Layout selection
        layout_label = QLabel("Layout:")
        header_layout.addWidget(layout_label)
        
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Hierarchical", "Radial"])
        self.layout_combo.setCurrentText("Hierarchical")
        self.layout_combo.currentTextChanged.connect(self.change_layout)
        self.layout_combo.setToolTip("Change the tree layout style")
        header_layout.addWidget(self.layout_combo)
        
        # Control buttons
        self.refresh_btn = QToolButton()
        self.refresh_btn.setText("⟳")
        self.refresh_btn.setToolTip("Refresh tree visualization")
        self.refresh_btn.clicked.connect(self.refresh_tree)
        header_layout.addWidget(self.refresh_btn)
        
        self.options_btn = QToolButton()
        self.options_btn.setText("⋮")
        self.options_btn.setToolTip("Additional options and actions")
        self.options_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        options_menu = QMenu(self)
        reset_action = options_menu.addAction("Reset View", self.reset_view)
        reset_action.setToolTip("Reset the tree view to default zoom and position")
        
        options_menu.addSeparator()
        
        save_action = options_menu.addAction("Save Tree...", self.save_conversation_tree)
        save_action.setToolTip("Save the current conversation tree to a file")
        
        load_action = options_menu.addAction("Load Tree...", self.load_conversation_tree)
        load_action.setToolTip("Load a conversation tree from a file")
        
        options_menu.addSeparator()
        
        export_action = options_menu.addAction("Export Tree", self.export_tree)
        export_action.setToolTip("Export the conversation tree in a different format")
        
        settings_action = options_menu.addAction("Settings", self.show_settings)
        settings_action.setToolTip("Configure conversation compass settings")
        self.options_btn.setMenu(options_menu)
        
        header_layout.addWidget(self.options_btn)
        
        layout.addLayout(header_layout)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tree view container (to allow for minimap overlay)
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tree view on the left
        self.tree_view = ConversationTreeView()
        self.tree_view.node_clicked.connect(self.on_node_clicked)
        self.tree_view.node_collapsed.connect(self._on_node_collapsed)
        tree_layout.addWidget(self.tree_view)
        
        # Position minimap in the corner of the tree view
        self.tree_view.minimap.setParent(self.tree_view)
        self.tree_view.minimap.move(10, 10)
        self.tree_view.minimap.raise_()
        
        splitter.addWidget(tree_container)
        
        # Right panel with suggested responses
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Current position
        self.position_label = QLabel("Current Position: Not started")
        right_layout.addWidget(self.position_label)
        
        # Status label for feedback
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        right_layout.addWidget(self.status_label)
        
        # Suggested responses
        self.responses_widget = SuggestedResponseWidget()
        self.responses_widget.response_selected.connect(self.on_response_selected)
        right_layout.addWidget(self.responses_widget)
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLabel("What would you say next?")
        input_layout.addWidget(self.input_field)
        
        self.generate_btn = QPushButton("Generate Options")
        self.generate_btn.setToolTip("Generate new conversation options based on current position")
        self.generate_btn.clicked.connect(self.generate_options)
        input_layout.addWidget(self.generate_btn)
        
        right_layout.addLayout(input_layout)
        
        splitter.addWidget(right_panel)
        
        # Set initial sizes (60% tree, 40% responses)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
        
        # Empty state
        self.empty_label = QLabel("Start a new conversation to begin")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("font-size: 16px; color: #999; margin: 20px;")
        layout.addWidget(self.empty_label)
        
        # Initially hide the splitter until a session is started
        splitter.setVisible(False)
    
    def _initialize_tree_service(self):
        """Initialize the conversation tree service"""
        # Import here to avoid circular imports
        from qt_version.services.conversation_tree_service import ConversationTreeService
        
        try:
            self.tree_service = ConversationTreeService(self.langchain_service)
            
            # Connect signals
            self.tree_service.tree_updated.connect(self._on_tree_updated)
            self.tree_service.node_added.connect(self._on_node_added)
            self.tree_service.suggestions_ready.connect(self._on_suggestions_ready)
            self.tree_service.error_occurred.connect(self._on_error)
            if hasattr(self.tree_service, 'current_position_changed'):
                self.tree_service.current_position_changed.connect(self._on_position_changed)
                
            print("Tree service initialized successfully")
        except Exception as e:
            print(f"Error initializing tree service: {str(e)}")
            if hasattr(self, 'error_occurred'):
                self.error_occurred.emit(f"Error initializing tree service: {str(e)}")
            else:
                self._show_status_message(f"Error initializing tree service: {str(e)}", "error")
            raise  # Re-raise to be caught by the caller
    
    def start_new_session(self):
        """Start a new conversation compass session"""
        try:
            print("Starting new conversation compass session")
            dialog = ConversationCompassSetupDialog(self, self.langchain_service)
            if dialog.exec():
                # Get setup result
                self.current_session = dialog.get_setup_result()
                print(f"Session setup completed: {self.current_session}")
                
                # Get the selected mode
                self.active_mode = self.current_session.get('mode', 0)
                mode_names = ["Tracking", "Guidance", "Preparation", "Analysis"]
                mode_name = mode_names[self.active_mode]
                
                # Update UI
                self.session_info.setText(f"Session: {self.current_session['conversation_type']} ({mode_name} Mode)")
                
                # Add mode indicator
                if not hasattr(self, 'mode_indicator'):
                    self.mode_indicator = QLabel()
                    self.mode_indicator.setStyleSheet("""
                        padding: 3px 8px;
                        border-radius: 10px;
                        font-weight: bold;
                        color: white;
                    """)
                    header_layout = self.findChild(QHBoxLayout)
                    if header_layout:
                        header_layout.insertWidget(2, self.mode_indicator)
                
                # Set mode indicator style based on mode
                mode_colors = ["#4CAF50", "#2196F3", "#9C27B0", "#FF9800"]  # Green, Blue, Purple, Orange
                self.mode_indicator.setText(mode_name)
                self.mode_indicator.setStyleSheet(f"""
                    background-color: {mode_colors[self.active_mode]};
                    padding: 3px 8px;
                    border-radius: 10px;
                    font-weight: bold;
                    color: white;
                """)
                
                # Show content and hide empty state
                self.findChild(QSplitter).setVisible(True)
                self.empty_label.setVisible(False)
                
                # Initialize tree service
                if not self.tree_service:
                    print("Initializing tree service")
                    try:
                        self._initialize_tree_service()
                    except Exception as e:
                        print(f"Error initializing tree service: {str(e)}")
                        self._show_status_message(f"Error initializing tree service: {str(e)}", "error")
                        return
                        
                # Create new conversation in tree service
                if self.tree_service:
                    context = {
                        "title": self.current_session.get("title", "Untitled"),
                        "description": "",
                        "participants": self.current_session.get("participants", []),
                        "goals": [self.current_session.get("goal", "")],
                        "settings": {
                            "type": self.current_session.get("conversation_type", "")
                        },
                        "conversation_type": self.current_session.get("conversation_type", ""),
                        "goal": self.current_session.get("goal", ""),
                        "additional_context": self.current_session.get("additional_context", ""),
                        "mode": self.active_mode  # Use the selected mode
                    }
                    
                    print(f"Creating new conversation with context: {context}")
                    try:
                        success = self.tree_service.create_new_conversation(context)
                        if success:
                            self.position_label.setText("Current Position: Starting the conversation")
                            print("Conversation created successfully")
                            
                            # For Guidance and Preparation modes, pre-generate initial suggestions
                            if self.active_mode in [1, 2]:  # Guidance or Preparation
                                self._show_status_message("Generating initial conversation paths...", "info")
                                self._generate_suggestions_for_current_node()
                                
                                # For Preparation mode, generate more extensive paths
                                if self.active_mode == 2:
                                    self._generate_deeper_conversation_paths()
                        else:
                            self.position_label.setText("Failed to create conversation")
                            print("Failed to create conversation")
                    except Exception as e:
                        print(f"Error creating conversation: {str(e)}")
                        self._show_status_message(f"Error creating conversation: {str(e)}", "error")
                else:
                    # Fallback to static initialization if tree service fails
                    print("Tree service not available, using fallback initialization")
                    self.initialize_tree()
        except Exception as e:
            print(f"Error in start_new_session: {str(e)}")
            self._show_status_message(f"Error starting session: {str(e)}", "error")
    
    def initialize_tree(self):
        """Initialize the conversation tree based on current session (fallback method)"""
        # Clear existing tree
        self.tree_view.clear_tree()
        
        # Create root node
        root = self.tree_view.add_node(
            "root", 
            None, 
            f"Start: {self.current_session['goal']}", 
            "statement",
            0, 0
        )
        
        # Add initial branches based on session type
        if self.current_session['conversation_type'] == "Sales Conversation":
            self.tree_view.add_node(
                "intro", 
                "root", 
                "Introduction and rapport building", 
                "statement",
                -200, 100
            )
            self.tree_view.add_node(
                "needs", 
                "root", 
                "Discover needs and pain points", 
                "question",
                0, 100
            )
            self.tree_view.add_node(
                "present", 
                "root", 
                "Present solution", 
                "statement",
                200, 100
            )
            
            # Add some child nodes
            self.tree_view.add_node(
                "objection1", 
                "present", 
                "Price objection", 
                "objection",
                100, 200
            )
            self.tree_view.add_node(
                "decision", 
                "present", 
                "Decision point", 
                "decision",
                300, 200
            )
        
        # Layout the tree
        self.tree_view.layout_tree()
        
        # Set current node
        self.tree_view.set_current_node("root")
        self.position_label.setText("Current Position: Starting the conversation")
        
        # Generate initial responses
        self.generate_initial_responses()
    
    def generate_initial_responses(self):
        """Generate initial suggested responses (fallback method)"""
        self.responses_widget.clear_responses()
        
        # In a real implementation, these would come from the LLM
        if self.current_session['conversation_type'] == "Sales Conversation":
            self.responses_widget.add_response(
                "Sales Rep",
                "Hi there! I noticed you've been looking at our product. What specific challenges are you trying to solve?",
                0.85
            )
            self.responses_widget.add_response(
                "Sales Rep",
                "Thanks for your interest in our solution. Before we dive in, could you tell me a bit about your current situation?",
                0.75
            )
            self.responses_widget.add_response(
                "Sales Rep",
                "I'd love to understand what brought you here today. What's the main problem you're hoping to address?",
                0.65
            )
    
    def on_node_clicked(self, node):
        """Handle node click in the tree view"""
        # Update current position
        self.tree_view.set_current_node(node.node_id)
        
        # Get node text
        if hasattr(node, 'speaker') and node.speaker:
            position_text = f"{node.speaker}: {node.content}"
        else:
            position_text = node.text_item.toPlainText()
            
        self.position_label.setText(f"Current Position: {position_text[:50]}...")
        
        # Provide visual feedback for node selection
        self._show_status_message(f"Selected: {position_text[:30]}...", "info")
        
        # If using tree service, update current node
        if self.tree_service:
            # Update current node in tree service
            pass
        else:
            # Fallback to static responses
            self.responses_widget.clear_responses()
            
            # In a real implementation, these would be generated dynamically
            if node.node_type == "question":
                self.responses_widget.add_response(
                    "Customer",
                    "That's an interesting question. Let me address that...",
                    0.8
                )
                self.responses_widget.add_response(
                    "Customer",
                    "I'm glad you asked. Here's my perspective...",
                    0.7
                )
            elif node.node_type == "objection":
                self.responses_widget.add_response(
                    "Sales Rep",
                    "I understand your concern. Let me clarify...",
                    0.9
                )
                self.responses_widget.add_response(
                    "Sales Rep",
                    "That's a valid point. Here's how we can address it...",
                    0.85
                )
    
    def on_response_selected(self, speaker, text):
        """Handle when a suggested response is selected"""
        # If using tree service, add the utterance
        if self.tree_service:
            node_id = self.tree_service.add_utterance(text, speaker)
            if node_id:
                self.position_label.setText(f"Added: {speaker}: {text[:30]}...")
                # Update tree view to reflect the new node
                self.tree_view.set_current_node(node_id)
                
                # Show visual feedback
                self._show_status_message(f"Added response from {speaker}", "success")
                
                # For Guidance mode, generate new suggestions after selecting a response
                if hasattr(self, 'active_mode') and self.active_mode == 1:  # Guidance mode
                    self._generate_suggestions_for_current_node()
        else:
            # Fallback behavior
            self.position_label.setText(f"Selected: {speaker}: {text[:30]}...")
            self._show_status_message("Response selected (tree service not available)", "warning")
    
    def generate_options(self):
        """Generate new conversation options"""
        # Show loading state
        self._show_status_message("Generating new options...", "info")
        
        # If using tree service, generate new suggestions
        if self.tree_service:
            self._generate_suggestions_for_current_node()
        else:
            # Fallback behavior
            self.responses_widget.clear_responses()
            self.responses_widget.add_response(
                "Customer",
                "Here's a dynamically generated response based on the current conversation state.",
                0.7
            )
            self.responses_widget.add_response(
                "Sales Rep",
                "This is another possible response that takes a different approach.",
                0.6
            )
            self._show_status_message("Generated options (using fallback mode)", "warning")
    
    def refresh_tree(self):
        """Refresh the conversation tree"""
        # In a real implementation, this would update the tree based on new data
        # For now, just re-layout the tree
        self._show_status_message("Refreshing tree visualization...", "info")
        self.tree_view.layout_tree()
        self._show_status_message("Tree visualization refreshed", "success")
        
    def change_layout(self, layout_name):
        """Change the tree layout strategy"""
        layout_name = layout_name.lower()
        if hasattr(self, 'tree_view') and self.tree_view:
            if layout_name == "radial":
                self.tree_view.layout_manager.layout_strategy = "radial"
            else:
                self.tree_view.layout_manager.layout_strategy = "hierarchical"
                
            # Apply the new layout
            self._show_status_message(f"Changing to {layout_name} layout...", "info")
            self.tree_view.layout_tree()
            self._show_status_message(f"{layout_name.capitalize()} layout applied", "success")
    
    def reset_view(self):
        """Reset the tree view to default zoom and position"""
        self._show_status_message("Resetting view...", "info")
        self.tree_view.resetTransform()
        self.tree_view.centerOn(0, 0)
        self._show_status_message("View reset to default", "success")
    
    def save_conversation_tree(self):
        """Save the current conversation tree to a file"""
        if not self.tree_service or not hasattr(self.tree_service, 'save_tree'):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Save Failed", "Tree service not initialized or doesn't support saving")
            self._show_status_message("Save failed: Tree service not available", "error")
            return
            
        # Get file path from user
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Conversation Tree",
            "",
            "Conversation Tree Files (*.ctree);;JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return  # User cancelled
            
        # Show saving status
        self._show_status_message(f"Saving tree to {file_path}...", "info")
            
        # Save the tree
        try:
            success = self.tree_service.save_tree(file_path)
            if success:
                self.position_label.setText(f"Tree saved to {file_path}")
                self._show_status_message("Tree saved successfully", "success")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Save Failed", "Failed to save conversation tree")
                self._show_status_message("Failed to save tree", "error")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error saving tree: {str(e)}")
            self._show_status_message(f"Error saving tree: {str(e)}", "error")

    def load_conversation_tree(self):
        """Load a conversation tree from a file"""
        if not self.tree_service or not hasattr(self.tree_service, 'load_tree'):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Load Failed", "Tree service not initialized or doesn't support loading")
            self._show_status_message("Load failed: Tree service not available", "error")
            return
            
        # Get file path from user
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Conversation Tree",
            "",
            "Conversation Tree Files (*.ctree);;JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return  # User cancelled
            
        # Show loading status
        self._show_status_message(f"Loading tree from {file_path}...", "info")
            
        # Load the tree
        try:
            success = self.tree_service.load_tree(file_path)
            if success:
                self.position_label.setText(f"Tree loaded from {file_path}")
                self._update_visualization()
                self._show_status_message("Tree loaded successfully", "success")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Load Failed", "Failed to load conversation tree")
                self._show_status_message("Failed to load tree", "error")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error loading tree: {str(e)}")
            self._show_status_message(f"Error loading tree: {str(e)}", "error")
            
    def export_tree(self):
        """Export the conversation tree"""
        # If using tree service, use its export functionality
        if self.tree_service:
            from PyQt6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Conversation Tree", "", "JSON Files (*.json)"
            )
            if file_path:
                self._show_status_message(f"Exporting tree to {file_path}...", "info")
                success = self.tree_service.save_tree(file_path)
                if success:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Export Successful", 
                                          f"Conversation tree exported to {file_path}")
                    self._show_status_message("Tree exported successfully", "success")
                else:
                    self._show_status_message("Failed to export tree", "error")
        else:
            # Fallback message
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Export Tree", "Tree export not implemented yet")
            self._show_status_message("Tree export not implemented yet", "warning")
    
    def show_settings(self):
        """Show settings dialog"""
        # This would show a settings dialog
        # For now, just show a message
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet")
        self._show_status_message("Settings dialog not implemented yet", "info")
        
    def _on_tree_updated(self):
        """Handle tree updated signal"""
        # Update visualization
        self._update_visualization()
        
    def _on_node_added(self, node_id):
        """Handle node added signal"""
        # Update status
        if self.tree_service:
            node = self.tree_service.get_node(node_id)
            if node:
                self.position_label.setText(f"Added: {node.speaker}: {node.content[:30]}...")
                
                # For Guidance mode, generate new suggestions based on this node
                if hasattr(self, 'active_mode') and self.active_mode == 1:  # Guidance mode
                    self._generate_suggestions_for_current_node()
        
    def _on_suggestions_ready(self, suggestions):
        """Handle suggestions ready signal"""
        # Update suggestions panel
        self.responses_widget.set_suggestions(suggestions)
        
    def _on_error(self, error_message):
        """Handle error signal"""
        # Update status
        self.position_label.setText(f"Error: {error_message}")
        
    def _on_position_changed(self, node_id):
        """Handle when the current position changes in the conversation tree"""
        if self.tree_service:
            node = self.tree_service.get_node(node_id)
            if node:
                # Update position label
                if hasattr(node, 'speaker') and node.speaker:
                    position_text = f"{node.speaker}: {node.content}"
                else:
                    position_text = node.content
                    
                self.position_label.setText(f"Current Position: {position_text[:50]}...")
                
                # Update tree view
                self.tree_view.set_current_node(node_id)
        
    def _update_visualization(self):
        """Update the tree visualization"""
        if not self.tree_service:
            return
            
        # Clear existing visualization
        self.tree_view.clear_tree()
        
        # Add all nodes to the visualization
        for node_id, node in self.tree_service.nodes.items():
            self.tree_view.add_node(
                node_id=node_id,
                parent_id=node.parent_id,
                text=node.content,
                node_type=node.node_type,
                speaker=node.speaker
            )
            
        # Layout the tree with the improved algorithm
        self.tree_view.layout_tree()
        
        # Set current node
        if self.tree_service.current_node_id:
            self.tree_view.set_current_node(self.tree_service.current_node_id)
            
    def _generate_suggestions_for_current_node(self):
        """Generate suggestions for the current node based on active mode"""
        if not self.tree_service or not self.tree_service.current_node_id:
            return
            
        # Show loading state
        self._show_status_message("Generating conversation options...", "info")
        
        # Call the tree service method
        if hasattr(self.tree_service, '_generate_suggestions_for_current_node'):
            self.tree_service._generate_suggestions_for_current_node()
        else:
            print("Tree service doesn't have _generate_suggestions_for_current_node method")
            
    def _generate_deeper_conversation_paths(self):
        """Generate deeper conversation paths for Preparation mode"""
        if not self.tree_service or not self.tree_service.current_node_id:
            return
            
        # Only for Preparation mode
        if not hasattr(self, 'active_mode') or self.active_mode != 2:
            return
            
        # Show loading state
        self._show_status_message("Generating deeper conversation paths...", "info")
        
        # Get current node
        current_node = self.tree_service.get_node(self.tree_service.current_node_id)
        if not current_node:
            return
            
        # Generate suggestions for each child node
        for child_id in current_node.children:
            # Temporarily set current node to child
            original_node_id = self.tree_service.current_node_id
            self.tree_service.set_current_node(child_id)
            
            # Generate suggestions for this child
            if hasattr(self.tree_service, '_generate_suggestions_for_current_node'):
                self.tree_service._generate_suggestions_for_current_node()
                
            # Restore original current node
            self.tree_service.set_current_node(original_node_id)
            
        # Update visualization
        self._update_visualization()
        
        # Show completion message
        self._show_status_message("Deeper conversation paths generated", "success")
            
    def _on_node_collapsed(self, node_id, is_collapsed):
        """Handle when a node is collapsed or expanded"""
        # Update the tree layout
        self.tree_view.layout_tree()
        
        # Update status
        node = self.tree_service.get_node(node_id) if self.tree_service else None
        if node:
            action = "collapsed" if is_collapsed else "expanded"
            self.position_label.setText(f"Node {action}: {node.content[:30]}...")
            self._show_status_message(f"Node {action}", "info")
            
        # Update navigation options
        self.update_navigation_options()
            
    def _show_status_message(self, message, message_type="info"):
        """Show a status message with visual feedback
        
        Args:
            message: The message to display
            message_type: The type of message (info, success, warning, error)
        """
        # Update status label with message
        self.status_label = getattr(self, 'status_label', None)
        if self.status_label:
            self.status_label.setText(message)
            
            # Set color based on message type
            if message_type == "success":
                self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")  # Green
            elif message_type == "warning":
                self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")  # Orange
            elif message_type == "error":
                self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")  # Red
            else:  # info
                self.status_label.setStyleSheet("color: #2196F3; font-weight: bold;")  # Blue
                
        # Create a temporary floating notification for important messages
        if message_type in ["success", "error", "warning"]:
            from PyQt6.QtWidgets import QLabel
            from PyQt6.QtCore import Qt, QTimer
            
            notification = QLabel(message, self)
            
            # Style based on message type
            if message_type == "success":
                bg_color = "#E8F5E9"
                border_color = "#4CAF50"
                text_color = "#2E7D32"
            elif message_type == "warning":
                bg_color = "#FFF3E0"
                border_color = "#FF9800"
                text_color = "#E65100"
            elif message_type == "error":
                bg_color = "#FFEBEE"
                border_color = "#F44336"
                text_color = "#C62828"
            else:  # info
                bg_color = "#E3F2FD"
                border_color = "#2196F3"
                text_color = "#0D47A1"
                
            notification.setStyleSheet(f"""
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            """)
            
            notification.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
            notification.adjustSize()
            
            # Position at the bottom of the widget
            x = (self.width() - notification.width()) // 2
            y = self.height() - notification.height() - 20
            notification.move(x, y)
            
            notification.show()
            
            # Auto-hide after 2 seconds
            QTimer.singleShot(2000, notification.deleteLater)
                
    def focus_on_node(self, node_id):
        """Focus the tree view on a specific node
        
        This is a public method that allows other components to programmatically
        focus the conversation tree on a specific node. It will:
        1. Center the view on the specified node
        2. Highlight the node as the current node
        3. Show a status message
        
        Usage example:
            # Focus on a specific node when a keyword is detected in the transcript
            compass_widget.focus_on_node("decision_node_123")
            
            # Focus on the root node
            compass_widget.focus_on_node("root")
        
        Args:
            node_id: ID of the node to focus on
        """
        if hasattr(self, 'tree_view') and self.tree_view:
            self.tree_view.focus_on_branch(node_id)
            self._show_status_message(f"Focused on node {node_id}", "info")
            
            # Update navigation options after focusing on a node
            self.update_navigation_options()
        
    def show_branch(self, node_id, levels=2):
        """Show only a specific branch of the tree
        
        This is a public method that allows other components to programmatically
        control which parts of the conversation tree are visible. It will:
        1. Hide all nodes except those in the specified branch
        2. Show the specified number of levels from the given node
        3. Show a status message
        
        This is useful for:
        - Focusing on a specific part of the conversation
        - Reducing visual complexity by hiding irrelevant branches
        - Highlighting decision paths or important conversation segments
        
        Usage example:
            # Show a node and its immediate children
            compass_widget.show_branch("objection_node_456", 1)
            
            # Show a node and multiple levels of descendants
            compass_widget.show_branch("root", 3)
        
        Args:
            node_id: ID of the root node of the branch to show
            levels: Number of levels to show (default: 2)
        """
        if hasattr(self, 'tree_view') and self.tree_view:
            self.tree_view.show_only_branch(node_id, levels)
            self._show_status_message(f"Showing branch from node {node_id}", "info")
            
            # Update navigation options after showing branch
            self.update_navigation_options()
            
    def connect_to_live_text(self, text_widget):
        """Connect to a live text widget to detect keywords
        
        Args:
            text_widget: The QTextEdit widget containing the live text
        """
        self.live_text_widget = text_widget
        self._show_status_message("Connected to live text source", "info")
        
    def process_live_text(self, text):
        """Process incoming live text to detect keywords and navigate the tree
        
        Args:
            text: The new text to process
            
        Returns:
            bool: True if a navigation action was triggered, False otherwise
        """
        if not text or not hasattr(self, 'tree_view'):
            return False
            
        # Get the most recent text (last few sentences)
        recent_text = self._get_recent_text(text)
        
        # Check for number triggers (e.g., "option 1", "number 2")
        if self._check_for_number_triggers(recent_text):
            return True
            
        # Check for keyword triggers
        if self._check_for_keyword_triggers(recent_text):
            return True
            
        return False
    
    def _get_recent_text(self, text, max_chars=200):
        """Get the most recent portion of the text"""
        if len(text) <= max_chars:
            return text
        return text[-max_chars:]
    
    def _check_for_number_triggers(self, text):
        """Check for number triggers in text"""
        import re
        
        # Look for patterns like "option 1", "number 2", "choice 3", or just "1", "2", "3"
        patterns = [
            r'option\s+(\d+)',
            r'number\s+(\d+)',
            r'choice\s+(\d+)',
            r'\b(\d+)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                number = matches[-1]  # Take the last match if multiple
                return self._navigate_by_number(int(number))
                
        return False
    
    def _navigate_by_number(self, number):
        """Navigate the tree based on a number trigger
        
        Args:
            number: The number to navigate to (1-based index)
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        # Find nodes with this number
        if hasattr(self, 'tree_service') and self.tree_service:
            # If using tree service, find child nodes of current node
            current_node_id = self.tree_service.current_node_id
            if current_node_id:
                current_node = self.tree_service.get_node(current_node_id)
                if current_node and hasattr(current_node, 'children') and len(current_node.children) >= number:
                    # Get the nth child
                    child_id = current_node.children[number-1]
                    self._show_status_message(f"Navigating to option {number}", "info")
                    self.focus_on_node(child_id)
                    return True
        
        # Fallback: Look for nodes with this number in their content
        for node_id, node in self.tree_view.nodes.items():
            if f"Option {number}" in node.content or f"#{number}" in node.content:
                self._show_status_message(f"Found node with option {number}", "info")
                self.focus_on_node(node_id)
                return True
                
        self._show_status_message(f"No option {number} found", "warning")
        return False
    
    def _check_for_keyword_triggers(self, text):
        """Check for keyword triggers in text
        
        Args:
            text: The text to check for keywords
            
        Returns:
            bool: True if a keyword was found and navigation occurred, False otherwise
        """
        # Define keywords for different node types
        keywords = {
            "question": ["question", "ask", "inquiry", "wondering"],
            "decision": ["decide", "decision", "choose", "select", "option"],
            "objection": ["object", "concern", "issue", "problem", "disagree"],
            "statement": ["statement", "point", "mention", "note"]
        }
        
        # Check each keyword category
        for node_type, word_list in keywords.items():
            for word in word_list:
                if word.lower() in text.lower():
                    return self._navigate_by_keyword(word, node_type)
                    
        return False
    
    def _navigate_by_keyword(self, keyword, node_type):
        """Navigate the tree based on a keyword trigger
        
        Args:
            keyword: The keyword that triggered navigation
            node_type: The type of node to look for
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        # Find nodes of this type
        matching_nodes = []
        
        for node_id, node in self.tree_view.nodes.items():
            if node.node_type == node_type or keyword.lower() in node.content.lower():
                matching_nodes.append(node_id)
                
        if matching_nodes:
            # Navigate to the first matching node
            self._show_status_message(f"Found {len(matching_nodes)} nodes matching '{keyword}'", "info")
            self.focus_on_node(matching_nodes[0])
            return True
            
        self._show_status_message(f"No nodes found matching '{keyword}'", "warning")
        return False
        
    def _create_navigation_panel(self):
        """Create a panel showing available navigation options"""
        from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSplitter
        
        # Create panel
        self.nav_panel = QFrame()
        self.nav_panel.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.nav_panel.setMaximumWidth(250)
        
        layout = QVBoxLayout(self.nav_panel)
        
        # Header
        header = QLabel("Navigation Options")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Say these keywords or numbers to navigate:")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Options container
        self.nav_options_layout = QVBoxLayout()
        layout.addLayout(self.nav_options_layout)
        
        # Add to right panel (assuming there's a right panel in the splitter)
        right_panel = None
        splitter = self.findChild(QSplitter)
        if splitter:
            for i in range(splitter.count()):
                widget = splitter.widget(i)
                if i > 0:  # Assuming right panel is not the first widget
                    right_panel = widget
                    break
                
            if right_panel and hasattr(right_panel, 'layout'):
                right_panel.layout().addWidget(self.nav_panel)
        
    def update_navigation_options(self):
        """Update the navigation options panel"""
        if not hasattr(self, 'nav_panel'):
            self._create_navigation_panel()
            
        if not hasattr(self, 'nav_options_layout'):
            return
            
        # Clear existing options
        while self.nav_options_layout.count():
            item = self.nav_options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Get options from tree service
        options = []
        if hasattr(self, 'tree_service') and self.tree_service:
            # Get current node
            current_node_id = self.tree_service.current_node_id
            if current_node_id:
                current_node = self.tree_service.get_node(current_node_id)
                if current_node and hasattr(current_node, 'children'):
                    # Get child nodes
                    for i, child_id in enumerate(current_node.children):
                        child = self.tree_service.get_node(child_id)
                        if child:
                            options.append({
                                "number": i + 1,
                                "node_id": child_id,
                                "content": child.content,
                                "type": child.node_type
                            })
        
        # If no tree service or no options, use fallback with tree view
        if not options and hasattr(self, 'tree_view'):
            # Get current node
            current_node_id = self.tree_view.current_node_id
            if current_node_id and current_node_id in self.tree_view.nodes:
                current_node = self.tree_view.nodes[current_node_id]
                
                # Get child nodes
                for i, child_id in enumerate(current_node.children):
                    if child_id in self.tree_view.nodes:
                        child = self.tree_view.nodes[child_id]
                        options.append({
                            "number": i + 1,
                            "node_id": child_id,
                            "content": child.content,
                            "type": child.node_type
                        })
                        
        # Add options to panel
        from PyQt6.QtWidgets import QLabel, QHBoxLayout, QPushButton
        
        if options:
            for option in options:
                # Create option row
                option_layout = QHBoxLayout()
                
                # Number button
                num_btn = QPushButton(str(option["number"]))
                num_btn.setMaximumWidth(30)
                num_btn.clicked.connect(lambda checked=False, id=option["node_id"]: self.focus_on_node(id))
                option_layout.addWidget(num_btn)
                
                # Content label
                content = option["content"]
                if len(content) > 40:
                    content = content[:37] + "..."
                content_label = QLabel(content)
                content_label.setWordWrap(True)
                option_layout.addWidget(content_label, 1)
                
                self.nav_options_layout.addLayout(option_layout)
        else:
            # No options available
            no_options = QLabel("No navigation options available")
            no_options.setStyleSheet("color: #999; font-style: italic;")
            self.nav_options_layout.addWidget(no_options)
