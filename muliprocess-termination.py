import multiprocessing
import time
import os
import signal

INPUT_DIR = "input_files"
OUTPUT_DIR = "output_files"

def ignore_ints():
  signal.signal(signal.SIGINT, signal.SIG_IGN)

def worker(input_file, output_file):
  with open(input_file, "r") as input:
    with open(output_file, "w") as output:
      for line in input:
        output.write(line)
  
  # Artificially lengthen the processing time
  time.sleep(0.1)

def file_list_gen():  
  if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

  for file in os.listdir(INPUT_DIR):
      if file.endswith(".txt"):
        # Create the path to both the input file and the expected output file name
        input_file_path = os.path.join(INPUT_DIR, file)
        output_file_path = os.path.join(OUTPUT_DIR, file.replace("input_", "output_"))
        
        # Skip the output file if it already exists
        if os.path.exists(output_file_path):
          continue

        # Return the pair of files to be processed/generated respectively
        yield input_file_path, output_file_path


def main():
  with multiprocessing.Pool(initializer=ignore_ints) as pool:
    try:
      result = pool.starmap_async(worker, file_list_gen())

      while not result.ready():
        result.wait(5)
    except KeyboardInterrupt:
      print("Terminating pool!")
      pool.terminate()
      pool.join()
    else:
      print("Finished successfully!")


if __name__ == "__main__":
  main()