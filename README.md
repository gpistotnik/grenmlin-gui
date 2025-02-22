# GUI Application Documentation

## Overview
This application provides a PyQt5-based graphical user interface for visualizing and interacting with network graphs. The GUI integrates features for creating, editing, and plotting nodes and edges, supporting both user interaction and advanced graph functionalities.

## Classes

### NodeItem
- **Description:** A simple node that can be 'input', 'output', or 'normal'.
- **Attributes:**
  - `node_data`: Contains label and node_type.
- **Methods:**
  - `__init__()`: Initialize the node with its properties.
  - `boundingRect()`: Define the node's bounding rectangle.
  - `paint(painter, option, widget)`: Render the node.
  - `mouseDoubleClickEvent(event)`: Double-click a node to rename it.
  - `itemChange(change, value)`: Update edges when the node position changes.

### EdgeItem
- **Description:** Directed edge from source_node -> target_node.
- **Attributes:**
  - `source_node`: Starting node of the edge.
  - `target_node`: Ending node of the edge.
- **Methods:**
  - `__init__()`: Initialize the edge with source and target nodes.
  - `boundingRect()`: Define the edge's bounding rectangle.
  - `paint(painter, option, widget)`: Render the edge.
  - `itemChange(change, value)`: Handle edge updates.
  - `mouseDoubleClickEvent(event)`: Edit edge properties.

### GraphScene
- **Description:** Manages graph interactions including edge creation, node snapping, and rendering.
- **Methods:**
  - `__init__()`: Initialize the scene.
  - `set_target_node(node)`: Set a target node for edge creation.
  - `update_positions()`: Update the positions of nodes and edges.
  - `mousePressEvent(event)`: Handle mouse press for edge creation.
  - `mouseMoveEvent(event)`: Handle mouse movement for edge snapping.
  - `mouseReleaseEvent(event)`: Finalize edge creation.
  - `clear_pinned_node()`: Clear any pinned nodes.
  - `find_nearest_node()`: Search all nodes and return the nearest one.

### MainWindow
- **Description:** Main application window managing all components and user interactions.
- **Methods:**
  - `__init__()`: Initialize the main window.
  - `on_edge_mode_toggled()`: Toggle edge creation mode.
  - `add_input_node()`: Add an input node.
  - `add_output_node()`: Add an output node.
  - `delete_selected_node()`: Delete the selected node.
  - `delete_selected_edge()`: Delete the selected edge.
  - `open_simulation_gui()`: Open the simulation GUI.
  - `add_interval_column()`: Add interval columns.
  - `import_nx_graph()`: Import a graph from a file.
  - `export_nx_graph()`: Export the current graph.
  - `plot_network()`: Render the network graph.
  - `plot_simulation()`: Plot simulation results.
  - `plot_grn()`: Plot a gene regulatory network.

## Functions

- `add_input_species()`: Add an input species to the graph.
- `add_species()`: Add a species node.
- `add_edge()`: Add an edge between nodes.
- `plot_network()`: Render the current graph network.
- `plot_simulation()`: Display simulation results.
- `find_nearest_node()`: Return the nearest node to the current pointer.
- `handle_pinned_node()`: Handle the pinned node during mouse movement.
- `remove_edge()`: Remove a selected edge.

## Usage

1. **Start the Application:**
   ```bash
   python gui.py
   ```
2. **Add Nodes:** Right-click and select "Add Node"
3. **Create Edges:** Drag from one node to another.
4. **Edit Nodes/Edges:** Double-click to edit properties.
5. **Save/Export:** Use the menu bar to save or export graphs.

## Authors
- **Developers:** Gašper Pistotnik, Jakob Adam Šircelj, Martin Korelič, Jonas Lasan
- **Organization:** Faculty of Computer and Information Science, University of Ljubljana