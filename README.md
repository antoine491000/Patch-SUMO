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

# 








