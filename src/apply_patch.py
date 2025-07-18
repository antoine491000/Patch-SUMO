import lxml.etree as ET
import argparse
import subprocess
from collections import defaultdict


parser = argparse.ArgumentParser(description="Apply a diff patch to a SUMO network file.")
parser.add_argument("--patch", required=True, help="Path to the network file to patch")
parser.add_argument("--base", required=True, help="Path to the base (reference) network file")
parser.add_argument("--output", required=True, help="Path to save the output patched network file")
parser.add_argument("--diff_node", default="diff.nod.xml", help="Diff file for nodes")
parser.add_argument("--diff_edge", default="diff.edg.xml", help="Diff file for edges")
parser.add_argument("--diff_conn", default="diff.con.xml", help="Diff file for connections")
parser.add_argument("--diff_tls", default="diff.tll.xml", help="Diff file for traffic lights")

args = parser.parse_args()


network_file_patch = args.patch
network_file_base = args.base
output_file = args.output

diff_files = {
    "node": args.diff_node,
    "edge": args.diff_edge,
    "connection": args.diff_conn,
    "tlLogic": args.diff_tls,
}


tree = ET.parse(network_file_patch)
root = tree.getroot()

tree_base = ET.parse(network_file_base)
root_base = tree_base.getroot()



def get_element_id(elem):
    """Returns the 'id' attribute of an element."""
    return elem.get("id")

def get_connection_key(elem):
    """Returns a tuple uniquely identifying a connection."""
    return (
        elem.get("from"),
        elem.get("to"),
        elem.get("fromLane"),
        elem.get("toLane")
    )

def index_elements(root_section, tags, key_function):
    """Indexes elements in the XML by a given key function and tag list."""
    index = {}
    for tag in tags:
        for elem in root_section.xpath(tag):
            key = key_function(elem)
            if key is not None:
                index[key] = elem
    return index

# Create indexes from the base network
index_nodes_base = index_elements(root_base, ["node", "junction"], get_element_id)
index_edges_base = index_elements(root_base, ["edge"], get_element_id)
index_tls_base = index_elements(root_base, ["tlLogic"], get_element_id)
index_conns_base = index_elements(root_base, ["connection"], get_connection_key)

def rebuild_index():
    """Rebuilds the index of elements from the current root tree."""
    index = {
        "node": {},
        "edge": {},
        "connection": {},
        "tlLogic": {}
    }
    for e in root.xpath("node | junction"):
        index["node"][e.get("id")] = e
    for e in root.xpath("edge"):
        index["edge"][e.get("id")] = e
    for e in root.xpath("connection"):
        key = (e.get("from"), e.get("to"), e.get("fromLane"), e.get("toLane"))
        index["connection"][key] = e
    for e in root.xpath("tlLogic"):
        index["tlLogic"][e.get("id")] = e
    return index

def get_edge_lanes(edge_id):
    """Returns the lane indices for a given edge."""
    edge = index["edge"].get(edge_id)
    if edge is not None:
        return [lane.get("index") for lane in edge.findall("lane")]
    else:
        return []

# Tag insertion order for maintaining XML structure
insertion_order = ["location", "type", "edge", "junction", "connection", "tlLogic"]

def insert_ordered(root, element, tag_order):
    """Inserts an XML element into the root, maintaining tag order."""
    tag = element.tag
    if tag not in tag_order:
        root.append(element)
        return

    target_index = tag_order.index(tag)
    inserted = False

    for i, child in enumerate(root):
        if child.tag in tag_order:
            if tag_order.index(child.tag) > target_index and not inserted:
                root.insert(i, element)
                inserted = True

    if not inserted:
        root.append(element)

# Identify traffic lights with all connections removed
original_tree = ET.parse(network_file_patch)
original_root = original_tree.getroot()

deleted_conns_by_tl = defaultdict(set)
diff_tls_tree = ET.parse(diff_files["tlLogic"])
diff_tls_root = diff_tls_tree.getroot()

# Deleted connections from diff file
for delete in diff_tls_root.findall("delete"):
    tl = delete.get("tl")
    if tl:
        key = (
            delete.get("from"),
            delete.get("to"),
            delete.get("fromLane"),
            delete.get("toLane"),
        )
        deleted_conns_by_tl[tl].add(key)

# Existing connections in original patched file
existing_conns_by_tl = defaultdict(set)
for conn in original_root.findall("connection"):
    tl = conn.get("tl")
    if tl:
        key = (
            conn.get("from"),
            conn.get("to"),
            conn.get("fromLane"),
            conn.get("toLane"),
        )
        existing_conns_by_tl[tl].add(key)

# Identify traffic lights to be removed
tls_to_remove = []
for tl, deleted_keys in deleted_conns_by_tl.items():
    if existing_conns_by_tl.get(tl) == deleted_keys:
        tls_to_remove.append(tl)

# MAIN

index = rebuild_index()
nodes_to_add = []
edges_to_add = []
tlLogics_to_add = []
connections_to_add = []
delayed_connections = []
invalid_connections = []

tag_order = ["node", "edge", "tlLogic", "connection"]

for tag in tag_order:
    diff_file = diff_files.get(tag)
    diff_tree = ET.parse(diff_file)
    diff_root = diff_tree.getroot()

    # Handle deletions
    for delete in diff_root.findall("delete"):
        attribs = delete.attrib
        if tag == "connection":
            key = (
                attribs.get("from"),
                attribs.get("to"),
                attribs.get("fromLane"),
                attribs.get("toLane")
            )
            target = index["connection"].get(key)
            if target is not None:
                root.remove(target)
        else:
            key = attribs.get("id")
            if key is not None:
                if tag == "node":
                    target = root.find(f"node[@id='{key}']") or root.find(f"junction[@id='{key}']")
                else:
                    target = index[tag].get(key)
                if target is not None:
                    root.remove(target)

    # Remove internal connections linked to deleted nodes
    if tag == "node":
        removed_nodes = {e.get("id") for e in diff_root.findall("delete")}
        for conn in list(root.findall("connection")):
            from_edge = conn.get("from")
            if from_edge.startswith(":") and "_" in from_edge:
                internal_node_id = from_edge[1:].split("_")[0]
                if internal_node_id in removed_nodes:
                    root.remove(conn)

    # Handle additions / replacements
    for elem in diff_root:
        if elem.tag == tag:
            attribs = elem.attrib
            existing = None
            source_elem = None

            if tag == "connection":
                key = (
                    attribs.get("from"),
                    attribs.get("to"),
                    attribs.get("fromLane"),
                    attribs.get("toLane")
                )
                if None not in key:
                    from_lanes = get_edge_lanes(attribs["from"])
                    to_lanes = get_edge_lanes(attribs["to"])
                    source_elem = index_conns_base.get(key)

                    if source_elem is not None:
                        if attribs["fromLane"] in from_lanes and attribs["toLane"] in to_lanes:
                            existing = index["connection"].get(key)
                            new_elem = ET.fromstring(ET.tostring(source_elem))
                            connections_to_add.append(new_elem)
                        else:
                            delayed_connections.append(source_elem)
            else:
                key = attribs.get("id")
                if key is not None:
                    existing = index[tag].get(key)
                    if tag == "node":
                        source_elem = index_nodes_base.get(key)
                    elif tag == "edge":
                        source_elem = index_edges_base.get(key)
                    elif tag == "tlLogic":
                        source_elem = index_tls_base.get(key)

                    if source_elem is not None:
                        if existing is not None:
                            root.remove(existing)
                        new_elem = ET.fromstring(ET.tostring(source_elem))
                        if tag == "node":
                            nodes_to_add.append(new_elem)
                        elif tag == "edge":
                            edges_to_add.append(new_elem)
                        elif tag == "tlLogic":
                            tlLogics_to_add.append(new_elem)

    # Handle additional tlLogic and connection definitions
    if tag == "tlLogic":
        for elem in diff_root:
            if elem.tag == "tlLogic":
                tl_id = elem.get("id")
                if tl_id and tl_id not in index["tlLogic"]:
                    new_elem = ET.fromstring(ET.tostring(elem))
                    tlLogics_to_add.append(new_elem)
            elif elem.tag == "connection":
                key = (
                    elem.get("from"),
                    elem.get("to"),
                    elem.get("fromLane"),
                    elem.get("toLane")
                )
                from_lanes = get_edge_lanes(elem.get("from"))
                to_lanes = get_edge_lanes(elem.get("to"))

                if elem.get("fromLane") in from_lanes and elem.get("toLane") in to_lanes:
                    new_elem = ET.fromstring(ET.tostring(elem))
                    connections_to_add.append(new_elem)
                else:
                    delayed_connections.append(elem)

    index = rebuild_index()

# add elements to XML
for n in nodes_to_add:
    insert_ordered(root, n, insertion_order)
for e in edges_to_add:
    insert_ordered(root, e, insertion_order)
for t in tlLogics_to_add:
    insert_ordered(root, t, insertion_order)
for c in connections_to_add:
    insert_ordered(root, c, insertion_order)

# Handle delayed connections
index = rebuild_index()
for elem in delayed_connections:
    attribs = elem.attrib
    from_lanes = get_edge_lanes(attribs["from"])
    to_lanes = get_edge_lanes(attribs["to"])
    if attribs["fromLane"] in from_lanes and attribs["toLane"] in to_lanes:
        insert_ordered(root, elem, insertion_order)
    else:
        invalid_connections.append(elem)

# Remove traffic lights
for tl in tls_to_remove:
    # Remove traffic light
    tl_elem = root.find(f"tlLogic[@id='{tl}']")
    if tl_elem is not None:
        root.remove(tl_elem)

    # Remove associated connections
    for conn in root.findall("connection"):
        if conn.get("tl") == tl:
            root.remove(conn)

    # Update associated junction type
    junction = root.find(f"junction[@id='{tl}']")
    if junction is not None and junction.get("type") == "traffic_light":
        junction.set("type", "priority")


tree.write(output_file, encoding="UTF-8", xml_declaration=True, pretty_print=True)

# Validation using netconvert
cmd = ["netconvert", "--sumo-net-file", output_file, "-o", "check_output.net.xml"]
try:
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("Netconvert check passed successfully.")
except subprocess.CalledProcessError as e:
    print("Netconvert error:", e.stderr)
