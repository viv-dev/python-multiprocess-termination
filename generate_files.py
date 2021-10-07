import random
import os

INPUT_FILES_DIR = "input_files"
FILES_TO_GENERATE = 1000

def generate_files():
  # Make sure the directory to generate our files exists
  if not os.path.exists(INPUT_FILES_DIR):
    os.makedirs(INPUT_FILES_DIR)

  # Generate the files
  for i in range(1000):
    filename = f"input_file_{i+1}.txt"
    filepath = os.path.join(INPUT_FILES_DIR, filename)
    if not os.path.exists(filepath):
      with open(filepath, 'w') as file:
        file.write(str(random.randint(0, 999999999)))


if __name__ == "__main__":
  generate_files()