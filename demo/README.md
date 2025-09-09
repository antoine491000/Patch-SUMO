# Demo PATCH - SUMO

This repository contains scripts to automatically apply corrections to a SUMO network. By running `demo.py`, the process is fully automated: it converts plain network files, applies patches, and generates the final network.

## Contents

- `demo.py` – Main script to run the full workflow.
- `apply_patch.py` – Script to apply modifications (diffs) to a network.
- `subnetwork.net.xml` – Original subnetwork file.
- `subnetwork_corrected.net.xml` – Corrected version of the subnetwork.
- `input_network.nod.xml`, `input_network.edg.xml`, `input_network.con.xml` – Plain network files.
- Any other required SUMO files.

## Prerequisites

- Python 3.x installed.
- SUMO installed and `netconvert` available in your PATH.
- All input network files and subnetwork files are in the same folder as `demo.py`.

## Usage

1. **Clone the repository:**


`git clone https://github.com/antoine491000/Patch-SUMO/tree/main`

2. Place all required network files (input_network.*.xml, subnetwork.net.xml, subnetwork_corrected.net.xml) in the same folder as demo.py
3. **Run the demo script:**
python demo.py

### The script will :

- Convert the source network files (`input_network.nod.xml`, `input_network.edg.xml`, `input_network.con.xml`) into `input_network.net.xml` using SUMO’s `netconvert`.
- Apply the patch from `subnetwork.net.xml` and `subnetwork_corrected.net.xml` using `apply_patch.py`.
- Generate the final patched network as `output_network.net.xml`.

### Output File

- `output_network.net.xml` – The final patched network.

### Notes

- Ensure SUMO’s `netconvert` is in your system PATH so that Python can call it from `demo.py`.
- Make sure Python scripts and XML files are in the same folder, or adjust the paths in `demo.py` accordingly.

