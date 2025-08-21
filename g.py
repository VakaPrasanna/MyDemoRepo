import os
import yaml

class GithubActionsManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def create_workflow(self, jenkinsfile_path, stages, metadata):
        dir_name = os.path.basename(os.path.dirname(jenkinsfile_path))
        workflow_dir = os.path.join(self.base_dir, "workflows")
        os.makedirs(workflow_dir, exist_ok=True)

        workflow = {
            "name": metadata["name"],
            "on": metadata["on"],
            "env": metadata["env"],
            "inputs": metadata["inputs"],
            "jobs": {}
        }

        for stage in stages:
            job_id = stage["name"].replace(" ", "_").lower()
            workflow["jobs"][job_id] = {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "uses": f"./.github/actions/{stage['name'].replace(' ', '_').lower()}"
                    }
                ]
            }

        if metadata["post"]:
            workflow["post"] = metadata["post"]

        workflow_file = os.path.join(workflow_dir, f"{dir_name}.yml")
        with open(workflow_file, "w") as f:
            yaml.dump(workflow, f, sort_keys=False)

    def create_composite_action(self, stage):
        action_dir = os.path.join(self.base_dir, "actions", stage["name"].replace(" ", "_").lower())
        os.makedirs(action_dir, exist_ok=True)

        action = {
            "name": stage["name"],
            "description": f"Composite action for {stage['name']}",
            "runs": {
                "using": "composite",
                "steps": []
            }
        }

        for step in stage["steps"]:
            if "run" in step:
                action["runs"]["steps"].append({"run": step["run"], "shell": "bash"})

        action_file = os.path.join(action_dir, "action.yml")
        with open(action_file, "w") as f:
            yaml.dump(action, f, sort_keys=False)
