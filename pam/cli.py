import os
import sys
import re
import shutil
import glob
import subprocess
import pkg_resources 

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("Usage: pam <command> [args]")
        return
    
    cmd = args[0]

    if cmd == "init":
        init_project()
    elif cmd == "new":
        create_type = args[1]
        if create_type == "service":
            name = args[2]
            create_service(name)
    elif cmd == "test":
        if len(args) < 2:
            print("Usage: pam test <modulename>")
            return
        module_name = args[1]
        test_module(module_name)
    else:
        print(f"Unknown command: {args.command}")

def test_module(module_name):
    """Run all test files matching '*.test.py' in the specified module directory."""
    # Locate all test files in the module directory
    test_files = glob.glob(f"{module_name}/*.test.py")
    
    if not test_files:
        print(f"Error: No test files found in module '{module_name}' (expected '*.test.py').")
        return
    
    print(f"Found {len(test_files)} test file(s) in '{module_name}':")
    for test_file in test_files:
        print(f" - {test_file}")
    
    # Run each test file
    for test_file in test_files:
        print(f"\nRunning tests in {test_file}...")
        result = subprocess.run([sys.executable, test_file], capture_output=True, text=True, check=True)

        print("\nTest Output:")
        print(result.stdout)
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
        print("-" * 40)  # Separator for clarity



def to_pascal_case(input_string: str) -> str:
    """
    Convert a string to PascalCase.

    :param input_string: The string to convert.
    :return: The string in PascalCase.
    """
    # Split the string into words using non-alphanumeric characters as delimiters
    words = re.split(r'\W+', input_string)
    
    # Capitalize each word and join them
    pascal_case = ''.join(word.capitalize() for word in words if word)

    return pascal_case


def cpy(src, dest):
    template_dir = pkg_resources.resource_filename("pam", "templates")
    src_file = os.path.join(template_dir, src)
    shutil.copy(src_file, dest)

def replace_template_content(service_name, file_name):
    file_path = os.path.join(service_name, file_name)
    with open(file_path, 'r+', encoding='utf-8') as file:
        filedata = file.read()
        updated_data = filedata.replace('#CLASS_NAME#', to_pascal_case(service_name))
        updated_data = updated_data.replace('#MODULE_NAME#', service_name)
        file.seek(0)  # Move the file pointer to the beginning of the file
        file.write(updated_data)
        file.truncate()  # Remove any leftover content after the replacement

def create_service(name):
    if os.path.exists(name):
        response = input(f"Service {name} already exists. Do you want to overwrite it? (y/N): ").strip().lower()
        if response == 'y':
            shutil.rmtree(name)
        else:
            print("Cancelled.")
            return

    os.mkdir(name)
    open(os.path.join(name, "__init__.py"), 'a', encoding='utf-8').close()
    cpy("service/service_class.tmpl", os.path.join(name, name+"_service.py") )
    cpy("service/service.yaml", os.path.join(name, "service.yaml") )
    cpy("service/functions.tmpl", os.path.join(name, "functions.py") )
    cpy("service/service.test.tmpl", os.path.join(name, name+".test.py") )

    replace_template_content(name, name+"_service.py")
    replace_template_content(name, "service.yaml")
    replace_template_content(name, name+".test.py")

    print(f"Service {name} created.")
    print(f"Run `pam test {name}` to run tests for the service.")


def init_project():
    cpy("init/main.tmpl", "main.py")
    cpy("docker/Dockerfile", "Dockerfile")
    cpy("buildcmd/pamb", "pamb")
    cpy("buildcmd/pamb-base.sh", "pamb-base.sh")
    cpy("init/pylintrc.tmpl", ".pylintrc")

    if not os.path.exists("requirements.txt"):
        open("requirements.txt", 'a', encoding='utf-8').close()
    
    with open("requirements.txt", "w", encoding='utf-8') as f:
        subprocess.run(["pip", "freeze"], stdout=f, check=True)

    if not os.path.exists("__init__.py"):
        open("__init__.py", 'a', encoding='utf-8').close()

    print("--- Welcome to PAM ---\n")
    print("To create a new servive run\n`pam new service <service_name>`\n\n")
