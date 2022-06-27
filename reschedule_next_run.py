
# This script only works within Github Actions
# pip install pyyaml
# ---

import os
import yaml


workflow_file = os.environ["workflow_path"]

with open(workflow_file, "r") as file:
	wf = yaml.safe_load(file)

	try:
		print(
			f'''
	
	
	
			Steps if caller workflow fails:
			{wf["jobs"].get("on-failure").get("steps")}
	
			
			
			'''
		)
		
	finally:
		print("\n\nWhole workflow:\n", wf, "\n\n")


print("\n\nFile path of failed workflow: " , os.environ["workflow_path"])