import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import subprocess

def clean_lanes(element):
    """
    Remove <lane> tags whose index is greater than or equal to numLanes.
    """
    if "numLanes" in element.attrib:
        try:
            max_index = int(element.attrib["numLanes"]) - 1
        except ValueError:
            return

        lanes_to_remove = []
        for lane in element.findall("lane"):
            try:
                lane_index = int(lane.get("index", -1))
            except ValueError:
                lane_index = -1
            if lane_index > max_index:
                lanes_to_remove.append(lane)

        for lane in lanes_to_remove:
            element.remove(lane)


def apply_diff(source_file, diff_file, element_type):
    """
    Apply an XML diff (add / update / delete) to a SUMO file
    and return the path of the modified file.
    """
    # Load XML files
    source_tree = ET.parse(source_file)
    source_root = source_tree.getroot()
    diff_tree = ET.parse(diff_file)
    diff_root = diff_tree.getroot()

    # Create quick index for source elements
    def create_index(root, element_type):
        index = {}
        for elem in root.findall("./*"):
            if element_type == "connection":
                key = (
                    elem.get("from"),
                    elem.get("fromLane"),
                    elem.get("to"),
                    elem.get("toLane")
                )
            else:
                key = elem.get("id")
            index[key] = elem
        return index

    source_index = create_index(source_root, element_type)

    # --- Deletion ---
    for delete_elem in diff_root.findall("./delete"):
        if element_type == "connection":
            key = (
                delete_elem.get("from"),
                delete_elem.get("fromLane"),
                delete_elem.get("to"),
                delete_elem.get("toLane")
            )
        else:
            key = delete_elem.get("id")

        if key in source_index:
            source_root.remove(source_index[key])
            source_index.pop(key)

    # --- Addition / Update ---
    for diff_elem in diff_root.findall("./*"):
        if diff_elem.tag != "delete" and diff_elem.tag is not ET.Comment:
            if element_type == "connection":
                key = (
                    diff_elem.get("from"),
                    diff_elem.get("fromLane"),
                    diff_elem.get("to"),
                    diff_elem.get("toLane")
                )
            else:
                key = diff_elem.get("id")

            if key in source_index:
                # Update attributes
                for attr_name, attr_value in diff_elem.attrib.items():
                    source_index[key].set(attr_name, attr_value)

                # Add missing children
                existing_children = [
                    (child.tag, tuple(child.attrib.items()))
                    for child in source_index[key]
                ]
                for child in diff_elem:
                    child_signature = (child.tag, tuple(child.attrib.items()))
                    if child_signature not in existing_children:
                        source_index[key].append(child)

                if element_type == "edge":
                    clean_lanes(source_index[key])
            else:
                # Add new element
                source_root.append(diff_elem)
                source_index[key] = diff_elem
                if element_type == "edge":
                    clean_lanes(source_index[key])

    # Save modified file with correct extension
    if element_type == "node":
        suffix = ".nod.xml"
    elif element_type == "edge":
        suffix = ".edg.xml"
    elif element_type == "connection":
        suffix = ".con.xml"
    else:
        suffix = source_file.suffix

    new_name = source_file.stem + "_modified" + suffix
    output_path = source_file.with_name(new_name)
    source_tree.write(output_path, encoding="utf-8", xml_declaration=True)

    print(f"Changes applied: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Apply SUMO diffs and regenerate network.")
    parser.add_argument("subnetwork", type=Path, help="Original subnetwork .net.xml file")
    parser.add_argument("subnetwork_corrected", type=Path, help="Corrected subnetwork .net.xml file")
    parser.add_argument("input_network", type=Path, help="Input .net.xml network file to patch")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Final .net.xml output file")
    args = parser.parse_args()

    # Run netdiff
    print("Running netdiff.py...")
    subprocess.run([
        "python",
        "netdiff.py",
        str(args.subnetwork),
        str(args.subnetwork_corrected),
        "diff"
    ], check=True)

    diff_node = Path("diff.nod.xml")
    diff_edge = Path("diff.edg.xml")
    diff_con  = Path("diff.con.xml")

    # Split input network into source files
    print("Splitting input_network into .nod, .edg, .con...")
    subprocess.run([
        "netconvert",
        "-s", str(args.input_network),
        "--plain-output-prefix", str(args.input_network.stem)
    ], check=True)

    node_file = args.input_network.with_suffix(".nod.xml")
    edge_file = args.input_network.with_suffix(".edg.xml")
    con_file  = args.input_network.with_suffix(".con.xml")

    # Apply diffs
    modified_node = apply_diff(node_file, diff_node, "node")      # crée input_network_modified.nod.xml
    modified_edge = apply_diff(edge_file, diff_edge, "edge")      # crée input_network_modified.edg.xml
    modified_con  = apply_diff(con_file, diff_con, "connection") # crée input_network_modified.con.xml

    # Run netconvert to generate final network
    print("Running netconvert...")
    subprocess.run([
        "netconvert",
        "--node-files", str(modified_node),
        "--edge-files", str(modified_edge),
        "--connection-files", str(modified_con),
        "-o", str(args.output)
    ], check=True)

    print(f"Network generated: {args.output}")


if __name__ == "__main__":
    main()
