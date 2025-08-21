import os
import yaml

class GitHubActionsManager:
    def __init__(self, workflows_dir=".github/workflows", actions_dir=".github/actions"):
        self.workflows_dir = workflows_dir
        self.actions_dir = actions_dir
        os.makedirs(self.workflows_dir, exist_ok=True)
        os.makedirs(self.actions_dir, exist_ok=True)

    def write_workflow(self, workflow_name, workflow_data):
        path = os.path.join(self.workflows_dir, f"{workflow_name}.yml")
        with open(path, "w") as f:
            yaml.dump(workflow_data, f, sort_keys=False)
        print(f"✅ Workflow written: {path}")

    def write_actions(self, actions_data):
        for stage, data in actions_data.items():
            stage_dir = os.path.join(self.actions_dir, stage)
            os.makedirs(stage_dir, exist_ok=True)
            path = os.path.join(stage_dir, "action.yml")
            with open(path, "w") as f:
                yaml.dump(data, f, sort_keys=False)
            print(f"✅ Action written: {path}")
