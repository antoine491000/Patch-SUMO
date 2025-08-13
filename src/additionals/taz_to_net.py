#!/usr/bin/env python3
"""
Extract a subnetwork from an original SUMO network based on TAZ edges.

Usage:
    python extract_subnet.py <taz_file> <network_file> <output_file>

Example:
    python extract_subnet.py map.taz.xml brussels.net.xml map.net.xml
"""

import sys
from lxml import etree

def main():

    taz_file = sys.argv[1]      # File containing TAZ zones
    network_file = sys.argv[2]  # Original SUMO network file
    output_file = sys.argv[3]   # Output subnetwork file

    # Read TAZ file and collect edges
    taz_tree = etree.parse(taz_file)
    taz_root = taz_tree.getroot()

    edges_in_taz = set()
    for taz in taz_root.findall("taz"):
        edges = taz.get("edges", "")
        for edge in edges.split():
            edges_in_taz.add(edge.strip())

    # Load the tree of the original network file
    net_tree = etree.parse(network_file)
    net_root = net_tree.getroot()

    # Collect all nodes (including <node> and <junction>)
    all_nodes = {node.get("id"): node for node in net_root.findall("node")}
    all_nodes.update({junc.get("id"): junc for junc in net_root.findall("junction")})

    # Collect all edges
    all_edges = {edge.get("id"): edge for edge in net_root.findall("edge")}

    # Determine which edges and nodes will be used
    used_nodes = set()
    missing_edges = []
    updated_edges_in_taz = set()

    for edge_id in edges_in_taz:
        edge = all_edges.get(edge_id)
        if edge is not None:
            used_nodes.add(edge.get("from"))
            used_nodes.add(edge.get("to"))
            updated_edges_in_taz.add(edge_id)
        else:
            # Try the reverse edge ID (for example : "-123" to "123")
            reverse_id = edge_id[1:] if edge_id.startswith("-") else "-" + edge_id
            reverse_edge = all_edges.get(reverse_id)
            if reverse_edge is not None:
                print(f"[INFO] Edge {edge_id} found as reversed '{reverse_id}'")
                used_nodes.add(reverse_edge.get("from"))
                used_nodes.add(reverse_edge.get("to"))
                updated_edges_in_taz.add(reverse_id)
            else:
                print(f"[WARNING] Edge {edge_id} not found in the network")
                missing_edges.append(edge_id)

    edges_in_taz = updated_edges_in_taz

    # Create a new subnetwork
    new_net = etree.Element("net", {
        "version": "1.3",
        "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation":
            "http://sumo.dlr.de/xsd/net_file.xsd"
    })

    # Add the used nodes
    for node_id in used_nodes:
        node = all_nodes.get(node_id)
        if node is not None:
            new_net.append(node)

    # Add the used edges
    for edge_id in edges_in_taz:
        edge = all_edges.get(edge_id)
        if edge is not None:
            new_net.append(edge)

    # Add connections between the edges we kept
    used_tls_ids = set()
    for conn in net_root.findall("connection"):
        if conn.get("from") in edges_in_taz and conn.get("to") in edges_in_taz:
            new_net.append(conn)
            if conn.get("tl"):
                used_tls_ids.add(conn.get("tl"))

    # Add the types used by these edges
    used_types = {edge.get("type") for edge in new_net.findall("edge") if edge.get("type")}
    for type_elem in net_root.findall("type"):
        if type_elem.get("id") in used_types:
            new_net.append(type_elem)

    # Add the traffic lights we referenced
    for tl in net_root.findall("tlLogic"):
        if tl.get("id") in used_tls_ids:
            new_net.append(tl)

    # Save the output file
    output_tree = etree.ElementTree(new_net)
    output_tree.write(output_file, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    print(f"Subnetwork exported to: {output_file}")

if __name__ == "__main__":
    main()
