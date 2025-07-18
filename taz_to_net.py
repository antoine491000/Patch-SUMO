from lxml import etree

# Input and output file names
taz_file = "map1_v2.taz.xml"       # TAZ file: contains zones with referenced edges
net_file = "brussels_exp.net.xml"  # Full SUMO network file
output_file = "map1_v2.net.xml"    # Output file for the extracted subnet

# --- Load the TAZ (Traffic Assignment Zones) file ---
tree_taz = etree.parse(taz_file)
taz_root = tree_taz.getroot()

# Collect all edges referenced in the TAZ file
edges_in_taz = set()
for taz in taz_root.findall("taz"):
    edges = taz.get("edges", "")
    for edge in edges.split():
        edge = edge.strip()
        # Add both normal and reverse edge references
        if edge.startswith("-"):
            edges_in_taz.add(edge)
        else:
            edges_in_taz.add(edge)

# --- Load the full SUMO network ---
tree_net = etree.parse(net_file)
net_root = tree_net.getroot()

# Index all nodes and junctions by their IDs
all_nodes = {}
for node in net_root.findall("node"):
    all_nodes[node.get("id")] = node
for junction in net_root.findall("junction"):
    all_nodes[junction.get("id")] = junction

# Index all edges by their IDs
all_edges = {}
for edge in net_root.findall("edge"):
    edge_id = edge.get("id")
    all_edges[edge_id] = edge

# --- Initialize sets for used nodes, missing edges, and updated edge list ---
used_nodes = set()
missing_edges = []
updated_edges_in_taz = set()

# --- Validate the existence of each TAZ edge in the network ---
for edge_id in edges_in_taz:
    edge = all_edges.get(edge_id)
    if edge is not None:
        # Edge found, record its nodes
        used_nodes.add(edge.get("from"))
        used_nodes.add(edge.get("to"))
        updated_edges_in_taz.add(edge_id)
    else:
        # Check if the reversed version exists
        reverse_id = edge_id[1:] if edge_id.startswith("-") else "-" + edge_id
        edge_rev = all_edges.get(reverse_id)
        if edge_rev is not None:
            print(f"[INFO] Edge {edge_id} found as reversed '{reverse_id}'")
            used_nodes.add(edge_rev.get("from"))
            used_nodes.add(edge_rev.get("to"))
            updated_edges_in_taz.add(reverse_id)
        else:
            print(f"[WARNING] Edge {edge_id} not found in the network")
            missing_edges.append(edge_id)

# Use only verified edges
edges_in_taz = updated_edges_in_taz

# --- Create a new subnet XML structure ---
new_net = etree.Element("net", {
    "version": "1.3",
    "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation":
        "http://sumo.dlr.de/xsd/net_file.xsd"
})

# --- Add all used nodes to the new subnet ---
added_nodes = set()
for node_id in used_nodes:
    node = all_nodes.get(node_id)
    if node is not None:
        new_net.append(node)
        added_nodes.add(node_id)
    else:
        # If node not found in the original network, create a dummy junction at (0,0)
        junction = etree.Element("junction", {
            "id": node_id,
            "x": "0.0",
            "y": "0.0",
            "type": "priority"
        })
        new_net.append(junction)
        added_nodes.add(node_id)

# --- Add all relevant edges to the new subnet ---
for edge_id in edges_in_taz:
    edge = all_edges.get(edge_id)
    if edge is not None:
        new_net.append(edge)

# --- Add connections between included edges ---
used_tls_ids = set()
for conn in net_root.findall("connection"):
    if conn.get("from") in edges_in_taz and conn.get("to") in edges_in_taz:
        new_net.append(conn)
        # Track referenced traffic light systems
        tl = conn.get("tl")
        if tl:
            used_tls_ids.add(tl)

# --- Add edge types that are actually used ---
used_types = {edge.get("type") for edge in new_net.findall("edge") if edge.get("type")}
for type_elem in net_root.findall("type"):
    if type_elem.get("id") in used_types:
        new_net.append(type_elem)

# --- Add traffic light definitions that are referenced ---
for tl in net_root.findall("tlLogic"):
    if tl.get("id") in used_tls_ids:
        new_net.append(tl)

# --- Write the new subnet to the output file ---
tree_out = etree.ElementTree(new_net)
tree_out.write(output_file, pretty_print=True, xml_declaration=True, encoding="UTF-8")

print(f"Subnet exported to: {output_file}")
