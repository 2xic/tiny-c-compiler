"""
Just creates some snapshots tests to make it easier to test this stuff
"""
import os
import json

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_green(text):
    print(bcolors.OKGREEN + text + bcolors.ENDC)

def print_red(text):
    print(bcolors.FAIL + text + bcolors.ENDC)

class Snapshot:
    def __init__(self, test_name, output) -> None:
        self.test_name = test_name
        self.output = output

    def check(self):
        path = os.path.join(
            ".snapshots",
            self.test_name
        )
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.isfile(path):
            with open(path, "r") as file:
                reference = file.read()
                if not reference == json.dumps(self.output):
                    print_red(f"\tFailed {self.test_name}")
                    print_green("New " + str(self.output))
                    print_red("Old " + str(json.loads(reference)))
                    exit(0)
        else:
            with open(path, "w") as file:
                file.write(json.dumps(self.output))
        return True
    
