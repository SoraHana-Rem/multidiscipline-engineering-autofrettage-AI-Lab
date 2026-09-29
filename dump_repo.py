import os
from pathlib import Path


def generate_repo_summary(output_filename="PROJECT_CODE_DUMP.txt"):
    ignore_dirs = {
        ".git",
        "__pycache__",
        "venv",
        ".venv",
        ".pytest_cache",
        ".vscode",
        ".idea",
        "build",
        "dist",
    }
    target_extensions = {
        ".py",
        ".md",
        ".ini",
        ".yaml",
        ".yml",
        ".json",
        ".m",
        ".csv",
        ".txt",
        ".toml",
        ".cfg",
        ".ipynb",
    }
    target_names = {"Dockerfile", "Makefile", ".gitignore"}

    repo_root = Path.cwd()

    with open(output_filename, "w", encoding="utf-8") as out_file:
        out_file.write(
            "========================================================\n"
        )
        out_file.write("PROJECT DIRECTORY STRUCTURE\n")
        out_file.write(
            "========================================================\n\n"
        )

        for root, dirs, files in os.walk(repo_root):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            level = Path(root).relative_to(repo_root).parts
            indent = "  " * len(level)
            if root != str(repo_root):
                out_file.write(f"{indent}📂 {Path(root).name}/\n")
            else:
                out_file.write(f"📂 {repo_root.name}/\n")

            sub_indent = "  " * (len(level) + 1)
            for file in sorted(files):
                if Path(file).suffix in target_extensions or file in {
                    "Dockerfile",
                    "Makefile",
                }:
                    out_file.write(f"{sub_indent}📄 {file}\n")

        out_file.write(
            "\n\n========================================================\n"
        )
        out_file.write("FILE CONTENTS\n")
        out_file.write(
            "========================================================\n\n"
        )

        for root, dirs, files in os.walk(repo_root):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in sorted(files):
                filepath = Path(root) / file
                if (
                    filepath.name == output_filename
                    or filepath.name == "dump_repo.py"
                ):
                    continue
                if Path(file).suffix in target_extensions or file in {
                    "Dockerfile",
                    "Makefile",
                }:
                    rel_path = filepath.relative_to(repo_root)
                    out_file.write(f"\n{'='*80}\n")
                    out_file.write(f"FILE: {rel_path}\n")
                    out_file.write(f"{'='*80}\n\n")

                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            out_file.write(f.read())
                    except Exception as e:
                        out_file.write(f"[Error reading file: {e}]\n")
                    out_file.write("\n")

    print(f"Successfully created '{output_filename}' in the root folder!")


if __name__ == "__main__":
    generate_repo_summary()