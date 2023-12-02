"""
Just creates some snapshots tests to make it easier to test this stuff
"""
import os
import json

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
                    print(f"Failed {self.test_name}")
                    print(self.output)
                    print(reference)
                    exit(0)
        else:
            with open(path, "w") as file:
                file.write(json.dumps(self.output))
        return True
    
