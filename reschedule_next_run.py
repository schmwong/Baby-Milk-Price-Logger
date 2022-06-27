
# This script only works within Github Actions
# pip install ruamel.yaml
# ---

import os
from ruamel.yaml import YAML


workflow_file = os.environ["workflow_path"]
yaml = YAML()  # defaults to round-trip (typ="rt")

with open(workflow_file, "r") as file:
	wf = yaml.load(file)
	
	
wf["jobs"]["scrape"]["runs-on"] = "ubuntu-latest"


with open(workflow_file, "w") as file:
	yaml.dump(wf, file)
	
try:
	print(
		f'''

		
		Scraper runs on {wf["jobs"]["scrape"]["runs-on"]}
		Scraper uses Python {wf["jobs"]["scrape"]["steps"][1]["with"]["python-version"]}


		Steps if caller workflow fails:
		{wf["jobs"]["scrape"]["steps"]}

		
		'''
	)

finally:
	print("\n\nWhole workflow:\n", wf, "\n\n")


print("\n\nFile path of failed workflow: " , os.environ["workflow_path"])