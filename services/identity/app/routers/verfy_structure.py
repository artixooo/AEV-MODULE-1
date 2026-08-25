import os
import sys
import json
from datetime import datetime

# Folders you're responsible for verifying
REQUIRED_FOLDERS = [
    "app/models",
    "app/schemas",
    "app/api",
    "app/routers",
]

def verify_folder_exists(path):
    return os.path.isdir(path)

def verify_folder_not_empty(path):
    if not os.path.isdir(path):
        return False
    contents = [f for f in os.listdir(path) if not f.startswith("__")]
    return len(contents) > 0

def get_python_files(path):
    if not os.path.isdir(path):
        return []
    return [f for f in os.listdir(path) if f.endswith(".py") and f != "__init__.py"]

def check_init_file(path):
    """Python packages should have __init__.py"""
    return os.path.isfile(os.path.join(path, "__init__.py"))

def verify_folder(folder):
    exists = verify_folder_exists(folder)
    not_empty = verify_folder_not_empty(folder) if exists else False
    files = get_python_files(folder) if exists else []
    has_init = check_init_file(folder) if exists else False

    status = "PASS" if (exists and not_empty and has_init) else "FAIL"

    return {
        "folder": folder,
        "exists": exists,
        "not_empty": not_empty,
        "has_init": has_init,
        "files": files,
        "status": status,
    }

def verify_project_structure():
    """Check overall expected FastAPI-style layout"""
    checks = {
        "app/ exists": os.path.isdir("app"),
        "main.py or app/main.py exists": os.path.isfile("main.py") or os.path.isfile("app/main.py"),
        "requirements.txt or pyproject.toml exists": os.path.isfile("requirements.txt") or os.path.isfile("pyproject.toml"),
    }
    return checks

def print_report(results, structure_checks):
    print("=" * 55)
    print("PROJECT STRUCTURE VERIFICATION")
    print(f"Run at: {datetime.now().isoformat()}")
    print("=" * 55)

    for r in results:
        print(f"\n[{r['status']}] {r['folder']}")
        print(f"  Exists:        {r['exists']}")
        print(f"  Has files:     {r['not_empty']}")
        print(f"  Has __init__:  {r['has_init']}")
        if r["files"]:
            print(f"  Files:         {', '.join(r['files'])}")

    print("\n" + "-" * 55)
    print("PROJECT STRUCTURE CHECKS")
    print("-" * 55)
    for check, passed in structure_checks.items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {check}")

    all_folder_pass = all(r["status"] == "PASS" for r in results)
    all_structure_pass = all(structure_checks.values())

    print("\n" + "=" * 55)
    if all_folder_pass and all_structure_pass:
        print("RESULT: ALL CHECKS PASSED")
    else:
        print("RESULT: SOME CHECKS FAILED — see above")
    print("=" * 55)

    return all_folder_pass and all_structure_pass

def write_markdown_report(results, structure_checks, all_passed):
    os.makedirs("docs", exist_ok=True)
    path = "docs/folder_verification.md"

    with open(path, "w") as f:
        f.write("# Folder Verification Report\n\n")
        f.write(f"**Run date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**Overall result:** {'✅ PASS' if all_passed else '❌ FAIL'}\n\n")

        f.write("## Responsible Folders\n\n")
        f.write("| Folder | Exists | Has Files | Has `__init__.py` | Status |\n")
        f.write("|--------|--------|-----------|--------------------|---------|\n")
        for r in results:
            f.write(f"| `{r['folder']}` | {r['exists']} | {r['not_empty']} | {r['has_init']} | {r['status']} |\n")

        f.write("\n## Project Structure Checks\n\n")
        for check, passed in structure_checks.items():
            f.write(f"- [{'x' if passed else ' '}] {check}\n")

        f.write("\n## Files Found\n\n")
        for r in results:
            f.write(f"**{r['folder']}**\n")
            if r["files"]:
                for file in r["files"]:
                    f.write(f"- {file}\n")
            else:
                f.write("- (no files found)\n")
            f.write("\n")

    print(f"\nMarkdown report written to: {path}")

def main():
    results = [verify_folder(f) for f in REQUIRED_FOLDERS]
    structure_checks = verify_project_structure()
    all_passed = print_report(results, structure_checks)
    write_markdown_report(results, structure_checks, all_passed)

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
    
