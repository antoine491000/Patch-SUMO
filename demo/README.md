# Demo PATCH - SUMO

- Use netdiff.py to have diff files (diff.nod.xml, diff.edg.xml, diff.con.xml, diff.tll.xml) between network A and network B (you can use the diff files provided)

      python netdiff.py networkA.net.xml networkB.net.xml diff 
  
- Use apply_patch.py with diff files (diff.nod.xml, diff.edg.xml, diff.con.xml) and source files of network C (C.nod.xml, C.edg.xml, C.con.xml).
- If you want to generate your own source files, you first need to export the network C file using the following command (this one is for brussels, but you can change the coordinates and the pbf in input to the network you want)  : osmconvert belgium.osm.pbf -b=4.30,50.79,4.55,50.92 -o=brussels.osm ;
- To separate network C into source files, you need to use the following command : netconvert -s networkC.net.xml --plain-output-prefix C

      python apply_patch.py C.nod.xml C.edg.xml C.con.xml diff.nod.xml diff.edg.xml diff.con.xml -o C_patched.net.xml
      
