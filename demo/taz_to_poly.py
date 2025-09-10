import xml.etree.ElementTree as ET
from pathlib import Path

def taz_to_poly(taz_file, poly_file):
    tree = ET.parse(taz_file)
    root = tree.getroot()

    add_root = ET.Element("additionals", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/additional_file.xsd"
    })

    for taz in root.findall("taz"):
        poly = ET.SubElement(add_root, "poly", {
            "id": f"taz_{taz.get('id')}",
            "type": "taz",
            "color": taz.get("color", "1,0,0"),
            "fill": "1",
            "shape": taz.get("shape")
        })

    ET.ElementTree(add_root).write(poly_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ {poly_file} écrit avec {len(root.findall('taz'))} polygones.")

taz_to_poly("subnetwork.taz.xml", "subnetwork.poly.xml")
