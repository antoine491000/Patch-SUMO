# Patch-SUMO

Apply modifications from diff files generated with a network A and a network B (network A modified) using netdiff.py tool to a different network C which contains network A.
It applies to all type of diff (except diff.typ).
See https://sumo.dlr.de/docs/Tools/Net.html (netdiff section).

# Structure of the project

geoJSonToTAZ.py : take polygon file .geojson, return the taz file associated .taz.xml
taz_to_net.py : take taz.xml file, return the network associated .net.xml
netdiff.py : take a network A and a network B (network A modified) and return diff files
apply_patch.py : take diff files, networks B & C files .net.xml and return network C patched file .net.xml








