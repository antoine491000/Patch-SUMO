# Patch-SUMO

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

### Example

- Use netdiff.py to have diff files (diff.nod.xml, diff.edg.xml, diff.con.xml, diff.tll.xml) between network A and network B (you can use the diff files provided)

      python netdiff.py networkA.net.xml networkB.net.xml diff 
  
- Use apply_patch.py with diff files (diff.nod.xml, diff.edg.xml, diff.con.xml) and source files of network C (C.nod.xml, C.edg.xml, C.con.xml). If you want to generate your own source files, you first need to export the network C file using the following command (this one is for brussels, but you can change the coordinates and the pbf in input to the network you want)  : osmconvert belgium.osm.pbf -b=4.30,50.79,4.55,50.92 -o=brussels.osm ; To separate network C into source files, you need to use the following command : netconvert -s networkC.net.xml --plain-output-prefix C

      python apply_patch.py C.nod.xml C.edg.xml C.con.xml diff.nod.xml diff.edg.xml diff.con.xml -o C_patched.net.xml
      

# Requirements

- Python 3.7+
- SUMO (Simulation of Urban Mobility) installed and accessible via the SUMO_HOME environment variable
- Python dependencies (listed in Requirements.txt)

# Licence

This project is licensed under the MIT License.



