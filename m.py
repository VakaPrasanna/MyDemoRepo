import os
import argparse
from converter import JenkinsToGithubConverter
from github_actions_manager import GithubActionsManager

def process_jenkinsfile(jenkinsfile_path, output_dir):
    converter = JenkinsToGithubConverter()
    stages, workflow_metadata = converter.parse_jenkinsfile(jenkinsfile_path)

    # Create workflow file
    manager = GithubActionsManager(output_dir)
    manager.create_workflow(jenkinsfile_path, stages, workflow_metadata)

    # Create composite actions per stage
    for stage in stages:
        manager.create_composite_action(stage)

def main():
    parser = argparse.ArgumentParser(description="Convert Jenkinsfile to GitHub Actions")
    parser.add_argument("--dir", required=True, help="Directory containing Jenkinsfile")
    args = parser.parse_args()

    jenkinsfile_path = os.path.join(args.dir, "Jenkinsfile")
    output_dir = ".github"
    os.makedirs(output_dir, exist_ok=True)

    process_jenkinsfile(jenkinsfile_path, output_dir)

if __name__ == "__main__":
    main()


