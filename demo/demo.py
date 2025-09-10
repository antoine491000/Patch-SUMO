import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

def taz_to_poly(taz_file: Path, poly_file: Path):
    tree = ET.parse(taz_file)
    root = tree.getroot()
    add_root = ET.Element("additionals", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/additional_file.xsd"
    })
    for taz in root.findall("taz"):
        ET.SubElement(add_root, "poly", {
            "id": f"taz_{taz.get('id')}",
            "type": "taz",
            "color": taz.get("color", "51,128,255"),
            "fill": "1",
            "shape": taz.get("shape")
        })
    ET.ElementTree(add_root).write(poly_file, encoding="utf-8", xml_declaration=True)
    print(f"Converted {taz_file} → {poly_file}")

# Netconvert arguments
netconvert_args = [
    "netconvert",
    "--node-files", "input_network.nod.xml",
    "--edge-files", "input_network.edg.xml",
    "--connection-files", "input_network.con.xml",
    "-o", "input_network.net.xml"
]

subprocess.run(netconvert_args, check=True)

# Apply patch arguments
apply_patch = [
    "python", "apply_patch.py",
    "-o", "output_network.net.xml",
    "subnetwork.net.xml",
    "subnetwork_corrected.net.xml",
    "input_network.net.xml"
]

subprocess.run(apply_patch, check=True)

# Convert TAZ to poly
taz_file = Path("subnetwork.taz.xml")
poly_file = Path("subnetwork.poly.xml")
if taz_file.exists():
    taz_to_poly(taz_file, poly_file)

    subprocess.Popen([
        "netedit",
        "--net-file", "output_network.net.xml",
        "--additional-files", str(poly_file)
    ])
else:
    print("No TAZ detected.")
