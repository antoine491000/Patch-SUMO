#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import subprocess
import shutil
import sys

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


def apply_diff(source_file, diff_file, element_type, temp_folder: Path):
    """
    Apply an XML diff (add / update / delete) to a SUMO file
    and return the path of the modified file (inside temp_folder).
    """
    source_tree = ET.parse(source_file)
    source_root = source_tree.getroot()
    diff_tree = ET.parse(diff_file)
    diff_root = diff_tree.getroot()

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

    # Deletions
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

    # Add / Update
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
                for attr_name, attr_value in diff_elem.attrib.items():
                    source_index[key].set(attr_name, attr_value)

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
                source_root.append(diff_elem)
                source_index[key] = diff_elem
                if element_type == "edge":
                    clean_lanes(source_index[key])

    # Save modified file into temp_folder
    if element_type == "node":
        suffix = ".nod.xml"
    elif element_type == "edge":
        suffix = ".edg.xml"
    elif element_type == "connection":
        suffix = ".con.xml"
    else:
        suffix = source_file.suffix

    new_name = source_file.stem + "_modified" + suffix
    output_path = temp_folder / new_name
    source_tree.write(output_path, encoding="utf-8", xml_declaration=True)

    print(f"Changes applied: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Apply SUMO diffs and regenerate network.")
    parser.add_argument("subnetwork", type=Path, help="Original subnetwork .net.xml file")
    parser.add_argument("subnetwork_corrected", type=Path, help="Corrected subnetwork .net.xml file")
    parser.add_argument("input_network", type=Path, help="Input .net.xml network file to patch")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Final .net.xml output file")
    parser.add_argument("--clean", action="store_true", help="Remove .temp directory at the end")
    args = parser.parse_args()

    temp_folder = Path(".temp").resolve()
    temp_folder.mkdir(parents=True, exist_ok=True)
    print(f"Using temporary folder: {temp_folder}")

    def get_plain_prefix(path):
        if path.name.endswith(".net.xml"):
            return temp_folder / path.name[:-len(".net.xml")]
        else:
            return temp_folder / path.stem

    try:

        sub_prefix = get_plain_prefix(args.subnetwork)
        sub_corr_prefix = get_plain_prefix(args.subnetwork_corrected)

        print("Generating plain for original subnetwork (into .temp)...")
        subprocess.run(
            ["netconvert", "-s", str(args.subnetwork), "--plain-output-prefix", str(sub_prefix)],
            check=True
        )

        print("Generating plain for corrected subnetwork (into .temp)...")
        subprocess.run(
            ["netconvert", "-s", str(args.subnetwork_corrected), "--plain-output-prefix", str(sub_corr_prefix)],
            check=True
        )


        print("Running netdiff.py with --use-prefix (outputs into .temp/diff.*)...")
        subprocess.run(
            [sys.executable, "netdiff.py", "--use-prefix", str(sub_prefix), str(sub_corr_prefix), str(temp_folder / "diff")],
            check=True
        )

        diff_node = temp_folder / "diff.nod.xml"
        diff_edge = temp_folder / "diff.edg.xml"
        diff_con  = temp_folder / "diff.con.xml"


        input_prefix = get_plain_prefix(args.input_network)
        print("Splitting input_network into plain files (into .temp)...")
        subprocess.run(
            ["netconvert", "-s", str(args.input_network), "--plain-output-prefix", str(input_prefix)],
            check=True
        )

        node_file = input_prefix.with_suffix(".nod.xml")
        edge_file = input_prefix.with_suffix(".edg.xml")
        con_file  = input_prefix.with_suffix(".con.xml")


        modified_node = apply_diff(node_file, diff_node, "node", temp_folder)
        modified_edge = apply_diff(edge_file, diff_edge, "edge", temp_folder)
        modified_con  = apply_diff(con_file, diff_con, "connection", temp_folder)


        print("Running netconvert to generate final network (output outside .temp)...")
        subprocess.run([
            "netconvert",
            "--node-files", str(modified_node),
            "--edge-files", str(modified_edge),
            "--connection-files", str(modified_con),
            "-o", str(args.output)
        ], check=True)

        print(f"Network generated: {args.output}")

    except subprocess.CalledProcessError as e:
        print("A subprocess failed:", e)
        sys.exit(1)
    finally:
        if args.clean:
            if temp_folder.exists():
                print(f"Removing temporary folder {temp_folder}...")
                shutil.rmtree(temp_folder)


if __name__ == "__main__":
    main()
