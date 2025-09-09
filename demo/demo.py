import subprocess
import os

out_dir = "data"


netconvert_args = [
    "netconvert",
    "--node-files", os.path.join(out_dir, "input_network.nod.xml"),
    "--edge-files", os.path.join(out_dir, "input_network.edg.xml"),
    "--connection-files", os.path.join(out_dir, "input_network.con.xml"),
    "-o", "input_network.net.xml"
]

subprocess.run(netconvert_args, check=True)


apply_patch = [
    "python", "apply_patch.py",
    "-o", "output_network.net.xml",
    "subnetwork.net.xml",
    "subnetwork_corrected.net.xml",
    "input_network.net.xml"
]

subprocess.run(apply_patch, check=True)
