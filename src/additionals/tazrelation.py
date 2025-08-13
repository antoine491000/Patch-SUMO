import xml.etree.ElementTree as ET
import sys

def dict_taz_edges(taz_file):
    """Reads the TAZ file and returns a dictionary {taz_id: [edges]}."""
    tree = ET.parse(taz_file)
    root = tree.getroot()
    taz_edges = {}


    for taz in root.findall('taz'):
        taz_id = taz.attrib['id']
        edges_str = taz.attrib.get('edges', '').strip()

        if edges_str:
            edges = edges_str.split()
            taz_edges[taz_id] = edges

    return taz_edges

def generate_taz_relation(taz_edges, output_file, trips_per_relation=10):
    """
    Generates a tazRelation XML file with a fixed number of trips for each TAZ pair.
    No trips are generated from a TAZ to itself.
    """
    root = ET.Element('data')
    interval = ET.SubElement(root, 'interval', {'begin': '0', 'end': '3600'})

    taz_ids = list(taz_edges.keys())

    for from_id in taz_ids:
        for to_id in taz_ids:
            ET.SubElement(interval, 'tazRelation', {
                'from': from_id,
                'to': to_id,
                'count': str(trips_per_relation)
            })

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

    print(f"TAZ relation file generated: {output_file}")
if __name__ == '__main__':

    taz_file = sys.argv[1]
    out_file = sys.argv[2]

    taz_edges = parse_taz_edges(taz_file)

    if taz_edges:
        generate_taz_relation(taz_edges, out_file)

