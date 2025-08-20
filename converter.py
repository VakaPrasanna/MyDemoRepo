import re

def parse_jenkinsfile(jenkinsfile_path):
    """
    Parse Jenkinsfile: extract parameters, env vars, stages, cron triggers, post-actions.
    Generic extraction with regex and naive parsing.
    """
    with open(jenkinsfile_path, "r") as f:
        content = f.read()

    # Parameters
    parameters = re.findall(r'parameters\s*\{([^}]*)\}', content, re.DOTALL)
    parameters = parameters[0].strip().splitlines() if parameters else []

    # Env
    env_block = re.findall(r'environment\s*\{([^}]*)\}', content, re.DOTALL)
    env_vars = {}
    if env_block:
        for line in env_block[0].splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip()

    # Stages
    stages = []
    stage_blocks = re.findall(r'stage\s*\(\s*["\']([^"\']+)["\']\s*\)\s*\{([^}]*)\}', content, re.DOTALL)
    for name, block in stage_blocks:
        steps = re.findall(r'sh\s+[\'"]([^\'"]+)[\'"]', block)
        docker_agent = re.findall(r'agent\s*\{\s*docker\s*\{([^}]*)\}\s*\}', block, re.DOTALL)
        stages.append({
            "name": name,
            "steps": steps,
            "docker": docker_agent[0].strip() if docker_agent else None,
        })

    # Triggers (cron)
    cron_match = re.findall(r'cron\s*\(\s*["\']([^"\']+)["\']\s*\)', content)
    cron_schedule = cron_match[0] if cron_match else None

    # Post-actions
    post_block = re.findall(r'post\s*\{([^}]*)\}', content, re.DOTALL)
    post_actions = post_block[0].strip().splitlines() if post_block else []

    return parameters, stages, cron_schedule, env_vars, post_actions