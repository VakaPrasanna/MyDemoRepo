import os
import argparse
from converter import parse_jenkinsfile
from github_actions_manager import create_workflow_and_actions


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def process_file(jenkinsfile, workflows_dir, actions_root_dir):
    print(f"\nProcessing {jenkinsfile}...")

    params, stages, cron, env, post = parse_jenkinsfile(jenkinsfile)

    workflow_yaml = os.path.join(
        workflows_dir, f"{os.path.basename(jenkinsfile)}.yml"
    )

    actions_dir = os.path.join(
        actions_root_dir, os.path.splitext(os.path.basename(jenkinsfile))[0]
    )
    ensure_dir(actions_dir)

    create_workflow_and_actions(
        jenkinsfile,
        workflow_yaml,
        actions_dir,
        params,
        stages,
        cron,
        env,
        post,
    )


def main():
    parser = argparse.ArgumentParser(description="Convert Jenkinsfile → GitHub Actions")
    parser.add_argument(
        "--file", help="Path to a single Jenkinsfile", default=None
    )
    parser.add_argument(
        "--dir", help="Directory containing Jenkinsfiles", default=None
    )
    args = parser.parse_args()

    workflows_dir = ".github/workflows"
    actions_root_dir = ".github/actions"
    ensure_dir(workflows_dir)
    ensure_dir(actions_root_dir)

    if args.file:
        process_file(args.file, workflows_dir, actions_root_dir)
    elif args.dir:
        for root, _, files in os.walk(args.dir):
            for f in files:
                if f == "Jenkinsfile":
                    process_file(
                        os.path.join(root, f), workflows_dir, actions_root_dir
                    )
    else:
        print("❌ Please provide --file or --dir")


if __name__ == "__main__":
    main()