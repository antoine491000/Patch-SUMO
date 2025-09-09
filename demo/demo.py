import subprocess

# Netconvert arguments
netconvert_args = [
    "netconvert",
    "--node-files", "input_network.nod.xml",
    "--edge-files", "input_network.edg.xml",
    "--connection-files", "input_network.con.xml",
    "-o", "input_network.net.xml"
]

subprocess.run(netconvert_args, check=True)

# Apply patch arguments
apply_patch = [
    "python", "apply_patch.py",
    "-o", "output_network.net.xml",
    "subnetwork.net.xml",
    "subnetwork_corrected.net.xml",
    "input_network.net.xml"
]

subprocess.run(apply_patch, check=True)
