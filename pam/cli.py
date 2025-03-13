import os
import sys
import re
import shutil
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
    else:
        print(f"Unknown command: {args.command}")

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

def replace_template_content(service_name, class_name, file_name):
    file_path = os.path.join(service_name, file_name)
    with open(file_path, 'r+', encoding='utf-8') as file:
        filedata = file.read()
        updated_data = filedata.replace('#CLASS_NAME#', class_name)
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

    cpy("service/service_class.tmpl", os.path.join(name, to_pascal_case(name)+"Svc.py") )

    cpy("service/service.yaml", os.path.join(name, "service.yaml") )
    cpy("service/functions.tmpl", os.path.join(name, "functions.py") )
    cpy("service/service.test.tmpl", os.path.join(name, f"test_{name}.py") )

    replace_template_content(name, to_pascal_case(name)+"Svc", to_pascal_case(name)+"Svc.py")
    replace_template_content(name, to_pascal_case(name)+"Svc", "service.yaml")
    replace_template_content(name, to_pascal_case(name)+"Svc", f"test_{name}.py")

    print(f"Service {name} created.")
    print(f"Run `pam test {name}` to run tests for the service.")


def init_project():
    cpy("init/main.tmpl", "main.py")
    cpy("docker/Dockerfile", "Dockerfile")
    cpy("buildcmd/pamb", "pamb")
    cpy("buildcmd/pamb-base.sh", "pamb-base.sh")
    cpy("init/pylintrc.tmpl", ".pylintrc")
    cpy("init/gitignore.tmpl", ".gitignore")
    cpy("init/dockerignore.tmpl", ".dockerignore")
    cpy("init/run_test.sh", "run_unit_test.sh")

    
    if not os.path.exists("requirements.txt"):
        open("requirements.txt", 'a', encoding='utf-8').close()
    
    with open("requirements.txt", "w", encoding='utf-8') as f:
        subprocess.run(["pip", "freeze"], stdout=f, check=True)

    if not os.path.exists("__init__.py"):
        open("__init__.py", 'a', encoding='utf-8').close()

    print("--- Welcome to PAM ---\n")
    print("To create a new servive run\n`pam new service <service_name>`\n\n")
