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
        "htmlcov",
        "egg-info",
    }
    
    # Extensions and explicit filenames to include
    target_extensions = {".py", ".md", ".ini", ".yaml", ".yml", ".json", ".toml", ".txt"}
    target_exact_files = {"Dockerfile", "Makefile", ".flake8", ".gitignore", "pytest.ini"}
    
    # Ignore the dump script and output text itself
    ignore_files = {output_filename, "dump_repo.py", ".coverage"}

    repo_root = Path.cwd()

    with open(output_filename, "w", encoding="utf-8") as out_file:
        out_file.write("========================================================\n")
        out_file.write("PROJECT DIRECTORY STRUCTURE\n")
        out_file.write("========================================================\n\n")

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
                if file in ignore_files:
                    continue
                if Path(file).suffix in target_extensions or file in target_exact_files:
                    out_file.write(f"{sub_indent}📄 {file}\n")

        out_file.write("\n\n========================================================\n")
        out_file.write("FILE CONTENTS\n")
        out_file.write("========================================================\n\n")

        for root, dirs, files in os.walk(repo_root):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in sorted(files):
                if file in ignore_files:
                    continue
                filepath = Path(root) / file
                
                if Path(file).suffix in target_extensions or file in target_exact_files:
                    rel_path = filepath.relative_to(repo_root)
                    suffix = filepath.suffix.lstrip(".")
                    
                    # Choose syntax highlighting key
                    lang = suffix if suffix else ("ini" if file.startswith(".") else "text")

                    out_file.write(f"\n{'='*80}\n")
                    out_file.write(f"FILE: {rel_path}\n")
                    out_file.write(f"{'='*80}\n\n")
                    out_file.write(f"```{lang}\n")

                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            out_file.write(f.read())
                    except Exception as e:
                        out_file.write(f"[Error reading file: {e}]\n")
                        
                    out_file.write("\n```\n")

    print(f"Successfully created '{output_filename}' in root!")


if __name__ == "__main__":
    generate_repo_summary()