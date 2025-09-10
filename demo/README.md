# Demo PATCH - SUMO

This repository contains scripts to automatically apply corrections to a SUMO network. By running `demo.py`, the process is fully automated: it converts source network files, applies patches, and generates the final network.

## Contents

- `demo.py` – Main script to run the full workflow.
- `apply_patch.py` – Script to apply modifications (diffs) to a network.
- `subnetwork.net.xml` – Original subnetwork file.
- `subnetwork_corrected.net.xml` – Corrected version of the subnetwork.
- `input_network.nod.xml`, `input_network.edg.xml`, `input_network.con.xml` – Plain network files.
- Any other required SUMO files.

## Prerequisites

- Python 3.9+ installed.
- SUMO installed and `netconvert` available in your PATH.
- All input network files and subnetwork files are in the same folder as `demo.py`.

## Usage

1. **Clone the repository:**

    `git clone https://github.com/antoine491000/Patch-SUMO/tree/main`

2. Place all required network files (input_network.*.xml, subnetwork.net.xml, subnetwork_corrected.net.xml) in the same folder as demo.py
3. **Run the demo script:**

    `python demo.py`

### The script will :

- Convert the plain input files into `input_network.net.xml`  
- Run `apply_patch.py` to:
     - Compare `subnetwork.net.xml` and `subnetwork_corrected.net.xml` with **netdiff**  
     - Generate diff files (`diff.*.xml`) inside `.temp/`  
     - Split `input_network.net.xml` into source files inside `.temp/`  
     - Apply the diffs to produce patched source files (`*_modified.*.xml` in `.temp/`)  
     - Rebuild the final patched network as `output_network.net.xml`  
    - If `subnetwork.taz.xml` exists:
     - Convert it into `subnetwork.poly.xml`  
     - Open **Netedit** with `output_network.net.xml` and the generated poly overlay  

---

## Output Files

- **`.temp/` folder**  
  Contains all intermediate files:
  - `diff.nod.xml`, `diff.edg.xml`, `diff.con.xml`  
  - `input_network_modified.*.xml`  
  - `subnetwork_plain.*.xml`, `subnetwork_corrected_plain.*.xml`
  - 
- **`output_network.net.xml`**  
  Final patched network  

- **`subnetwork.poly.xml`** *(optional)*  
  Generated if a `subnetwork.taz.xml` is present, used for visualization in Netedit  

---

## Notes

- To clean up `.temp/` automatically after patching, run `apply_patch.py` with the `--clean` option (e.g. if calling it directly).  
- If no `subnetwork.taz.xml` is found, the poly step is skipped.  
- Always ensure your XML files are valid SUMO formats, otherwise `netconvert` will fail. 
