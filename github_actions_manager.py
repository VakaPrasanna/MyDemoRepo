import os
import yaml

def create_workflow_and_actions(
    jenkinsfile,
    workflow_yaml,
    actions_dir,
    parameters,
    stages,
    cron,
    env_vars,
    post_actions,
):
    jobs = {}
    for stage in stages:
        stage_id = stage["name"].replace(" ", "_").lower()

        action_file = os.path.join(actions_dir, f"{stage_id}.yml")

        # Create composite action for stage
        action_data = {
            "name": stage["name"],
            "description": f"Auto-generated action for {stage['name']}",
            "runs": {
                "using": "composite",
                "steps": [{"run": step, "shell": "bash"} for step in stage["steps"]],
            },
        }
        with open(action_file, "w") as f:
            yaml.dump(action_data, f, sort_keys=False)

        # Add job reference
        jobs[stage_id] = {
            "runs-on": "ubuntu-latest",
            "steps": [
                {
                    "uses": f"./.github/actions/{os.path.basename(actions_dir)}/{stage_id}"
                }
            ],
        }

    workflow = {
        "name": f"Workflow for {os.path.basename(jenkinsfile)}",
        "on": {"push": {"branches": ["main"]}},
        "jobs": jobs,
    }

    if cron:
        workflow["on"]["schedule"] = [{"cron": cron}]

    if env_vars:
        workflow["env"] = env_vars

    if parameters:
        workflow["on"]["workflow_dispatch"] = {"inputs": {p: {"required": False} for p in parameters}}

    if post_actions:
        workflow["jobs"]["post_actions"] = {
            "runs-on": "ubuntu-latest",
            "steps": [{"run": action} for action in post_actions],
        }

    with open(workflow_yaml, "w") as f:
        yaml.dump(workflow, f, sort_keys=False)

    print(f"Workflow created: {workflow_yaml}")
    print(f"Actions created in: {actions_dir}")
