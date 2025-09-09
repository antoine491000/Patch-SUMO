import subprocess
import os

out_dir = "data"

args = [
    "netconvert",
    "--node-files", os.path.join(out_dir, "input_network.nod.xml"),
    "--edge-files", os.path.join(out_dir, "input_network.edg.xml"),
    "--connection-files", os.path.join(out_dir, "input_network.con.xml"),
    "-o", "input_network.net.xml"
]

scripts = {
    "apply_patch": ["subnetwork.net.xml", "subnetwork_corrected.net.xml", "input_network.net.xml", "output_network.net.xml"],
}

for script, params in scripts.items():
    subprocess.run(["python", script] + params)


