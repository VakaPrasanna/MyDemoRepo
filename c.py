import re

class JenkinsToGithubConverter:
    def parse_jenkinsfile(self, jenkinsfile_path):
        with open(jenkinsfile_path, "r") as f:
            content = f.read()

        stages = self.extract_stages(content)
        workflow_metadata = {
            "name": self.extract_pipeline_name(content),
            "on": self.extract_triggers(content),
            "inputs": self.extract_parameters(content),
            "env": self.extract_env(content),
            "post": self.extract_post(content),
        }
        return stages, workflow_metadata

    def extract_pipeline_name(self, content):
        return "Converted Pipeline"

    def extract_triggers(self, content):
        triggers = {"push": {"branches": ["main"]}, "pull_request": {}}
        cron_match = re.findall(r"cron\(['\"](.+?)['\"]\)", content)
        if cron_match:
            triggers["schedule"] = [{"cron": cron_match[0]}]
        return triggers

    def extract_parameters(self, content):
        params = {}
        param_matches = re.findall(r'parameters\s*{([^}]+)}', content, re.S)
        for block in param_matches:
            string_params = re.findall(r'string\s+name:\s*[\'"](.+?)[\'"],\s*defaultValue:\s*[\'"](.+?)[\'"]', block)
            for name, default in string_params:
                params[name] = {"description": f"Input parameter {name}", "default": default}
        return params

    def extract_env(self, content):
        env_vars = {}
        env_blocks = re.findall(r'environment\s*{([^}]+)}', content, re.S)
        for block in env_blocks:
            lines = block.strip().split("\n")
            for line in lines:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    env_vars[k.strip()] = v.strip()
        return env_vars

    def extract_post(self, content):
        post_actions = {}
        post_match = re.findall(r'post\s*{([^}]+)}', content, re.S)
        if post_match:
            block = post_match[0]
            always = re.findall(r'always\s*{([^}]+)}', block, re.S)
            if always:
                post_actions["always"] = always[0].strip().split("\n")
        return post_actions

    def extract_stages(self, content):
        stages = []
        stage_matches = re.findall(r'stage\s*\(\s*[\'"](.+?)[\'"]\s*\)\s*{([^}]+)}', content, re.S)
        for name, block in stage_matches:
            steps = self.extract_steps(block)
            stages.append({"name": name, "steps": steps})
        return stages

    def extract_steps(self, block):
        steps = []
        sh_cmds = re.findall(r'sh\s+[\'"](.+?)[\'"]', block)
        for cmd in sh_cmds:
            steps.append({"run": cmd})

        echo_cmds = re.findall(r'echo\s+[\'"](.+?)[\'"]', block)
        for cmd in echo_cmds:
            steps.append({"run": f"echo {cmd}"})

        docker_matches = re.findall(r'docker\s*\{([^}]+)}', block, re.S)
        for docker_block in docker_matches:
            steps.append({"run": f"# Docker agent block:\n{docker_block.strip()}"})

        kube_matches = re.findall(r'kubernetes\s*\{([^}]+)}', block, re.S)
        for kube_block in kube_matches:
            steps.append({"run": f"# Kubernetes agent block:\n{kube_block.strip()}"})

        return steps
