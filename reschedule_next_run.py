
# This script only works within Github Actions
# pip install pyyaml
# ---

import os
import yaml


workflow_file = os.environ["workflow_path"]

with open(workflow_file, "r+") as file:
	wf = yaml.safe_load(file)
	wf["jobs"]["scrape"]["runs-on"] = "ubuntu-latest"
	wf = yaml.dump(wf, file)

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