import os
import argparse
from converter import JenkinsfileConverter
from github_actions_manager import GitHubActionsManager

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file == "Jenkinsfile":
                jenkinsfile_path = os.path.join(root, file)
                rel_dir = os.path.relpath(root, directory)
                workflow_name = rel_dir.replace(os.sep, "_")

                print(f"Processing {jenkinsfile_path}...")

                converter = JenkinsfileConverter(jenkinsfile_path)
                workflow_data, actions_data = converter.convert()

                gha_manager = GitHubActionsManager()
                gha_manager.write_workflow(workflow_name, workflow_data)
                gha_manager.write_actions(actions_data)

def main():
    parser = argparse.ArgumentParser(description="Convert Jenkinsfiles to GitHub Actions")
    parser.add_argument("--dir", required=True, help="Directory containing Jenkinsfiles")
    args = parser.parse_args()

    process_directory(args.dir)

if __name__ == "__main__":
    main()


