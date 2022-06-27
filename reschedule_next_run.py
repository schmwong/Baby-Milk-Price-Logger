
# This script only works within Github Actions
# pip install pyyaml
# ---

import os
import yaml


workflow_file = os.environ["workflow_path"]

with open(workflow_file) as file:
	wf = yaml.safe_load(file)

	print(
		f'''



		Steps if caller workflow fails:
		{wf["jobs"]["on-failure"]["steps"]}

		
		
		'''
	)
	
	print("\n\nWhole workflow:\n", wf, "\n\n")


print("\n\nFile path of failed workflow: " , os.environ["workflow_path"])