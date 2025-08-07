# Patch-SUMO

Apply a set of XML diff files (`.nod`, `.edg`, `.con`, `.tll`) to a SUMO network file.  

It handles:  
- additions and deletions of **nodes**, **edges**, **connections**, and **traffic lights**  
- final validation of the patched network via `netconvert`  

See https://sumo.dlr.de/docs/Tools/Net.html (netdiff section).  

# Structure of the project

### Src

- `apply_patch.py` : take diff files, networks B & C files .net.xml and return network C patched file .net.xml

### Additionals

- `geoJSonToTAZ.py` : take polygon file .geojson, return the taz file associated .taz.xml  
- `taz_to_net.py` : take taz.xml file, return the network associated .net.xml  
- `netdiff.py` : take a network A and a network B (network A modified) and return diff files  

### Example

- Use netdiff.py to have diff files between networkA and networkB (you can use the diff files provided)

      python netdiff.py networkA.net.xml networkB.net.xml diff 
  
- Use apply_patch.py with diff files and networkB. A network of Brussels (networkC) is also needed, you can use the following command : osmconvert belgium.osm.pbf -b=4.30,50.79,4.55,50.92 -o=brussels.osm 

      python apply_patch.py --patch networkC.net.xml --base networkB.net.xml --output networkC_patched.net.xml

# Requirements

- Python 3.7+
- SUMO (Simulation of Urban Mobility) installed and accessible via the SUMO_HOME environment variable
- Python dependencies (listed in Requirements.txt)

# Licence

This project is licensed under the MIT License.



