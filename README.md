# Patch - SUMO

Apply a set of XML diff files (`.nod`, `.edg`, `.con`, `.tll`) to sources files of a SUMO network file (`.nod`, `.edg`, `.con`, `.tll`).  

It handles:  
- additions and deletions of **nodes**, **edges**, **connections**, and **traffic lights**  
- Generation of the patched network via `netconvert`  

See https://sumo.dlr.de/docs/Tools/Net.html (netdiff section).  

# Structure of the project

### Src

- `apply_patch.py` : take diff files (diff.nod.xml, diff.edg.xml, diff.con.xml), source files from network C (C.nod.xml, C.edg.xml, C.con.xml) and return network C patched file .net.xml

### Additionals

- `geoJSonToTAZ.py` : take polygon file .geojson, return the taz file associated .taz.xml  
- `taz_to_net.py` : take taz.xml file, return the network associated .net.xml  
- `netdiff.py` : take a network A and a network B (network A modified) and return diff files (diff.nod.xml, diff.edg.xml, diff.con.xml, diff.tll.xml)

### Demo

- `README.md` : Explains how the example works
- `apply_patch.py` : Patch script for the example
- `/data` : Directory which contains data for the example

# Requirements

- Python 3.7+
- SUMO (Simulation of Urban Mobility) installed and accessible via the SUMO_HOME environment variable
- Python dependencies (listed in Requirements.txt)

# Licence

This project is licensed under the MIT License.



