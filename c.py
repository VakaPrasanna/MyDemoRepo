import re
import yaml

class JenkinsfileConverter:
    def __init__(self, filepath):
        self.filepath = filepath
        self.content = self._read_file()

    def _read_file(self):
        with open(self.filepath, "r") as f:
            return f.read()

    def convert(self):
        workflow = {
            "name": "Converted Workflow",
            "on": {
                "push": {"branches": ["main"]},
                "pull_request": {},
                "schedule": [{"cron": "0 0 * * 0"}]
            },
            "inputs": {},
            "env": {},
            "jobs": {},
            "post": {}
        }

        actions = {}

        # Extract parameters
        param_block = re.findall(r'parameters\s*\{([^}]*)\}', self.content, re.S)
        if param_block:
            for line in param_block[0].splitlines():
                m = re.match(r'(\w+)\s+name:\s*[\'"]?(\w+)[\'"]?', line.strip())
                if m:
                    param_type, param_name = m.groups()
                    workflow["inputs"][param_name] = {
                        "description": f"Parameter {param_name}",
                        "required": False
                    }

        # Extract env
        env_block = re.findall(r'environment\s*\{([^}]*)\}', self.content, re.S)
        if env_block:
            for line in env_block[0].splitlines():
                if "=" in line:
                    k, v = map(str.strip, line.split("=", 1))
                    workflow["env"][k] = v

        # Extract post
        post_block = re.findall(r'post\s*\{([^}]*)\}', self.content, re.S)
        if post_block:
            for line in post_block[0].splitlines():
                if line.strip():
                    workflow["post"][line.strip()] = "true"

        # Extract stages
        stage_blocks = re.findall(r'stage\s*\([\'"]([^\'"]+)[\'"]\)\s*\{([^}]*)\}', self.content, re.S)
        for stage_name, stage_body in stage_blocks:
            steps = []
            for line in stage_body.splitlines():
                line = line.strip()
                if line.startswith("sh"):
                    cmd = re.findall(r'["\']([^"\']+)["\']', line)
                    if cmd:
                        steps.append({"run": cmd[0], "shell": "bash"})
                elif line.startswith("echo"):
                    msg = re.findall(r'["\']([^"\']+)["\']', line)
                    if msg:
                        steps.append({"run": f"echo {msg[0]}"})
                elif "docker" in line:
                    steps.append({"run": line})
                elif "kubectl" in line:
                    steps.append({"run": line})

            actions[stage_name] = {
                "name": stage_name,
                "description": f"Composite action for {stage_name}",
                "runs": {"using": "composite", "steps": steps},
                "with": {p: f"${{{{ inputs.{p} }}}}" for p in workflow["inputs"]}
            }

            workflow["jobs"][stage_name] = {
                "name": stage_name,
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"uses": f"./.github/actions/{stage_name}", "with": {p: f"${{{{ github.event.inputs.{p} }}}}" for p in workflow["inputs"]}}
                ]
            }

        return workflow, actions
