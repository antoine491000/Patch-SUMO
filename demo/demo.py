import subprocess


scripts = {
    "apply_patch": ["subnetwork.net.xml", "subnetwork_corrected.net.xml", "input_network", "output_network"],
}

for script, params in scripts.items():
    subprocess.run(["python", script] + params)
