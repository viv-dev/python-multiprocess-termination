import multiprocessing
import time
import os
import signal

INPUT_DIR = "input_files"
OUTPUT_DIR = "output_files"


# Function to initialise child processes to ignore interrupt signals
def ignore_ints():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


# Dummy processing logic
def process(input_file, output_file):
    # Create an artifical exception
    if (
        input_file == "input_files/input_file_1.txt"
        or input_file == "input_files/input_file_2.txt"
    ):
        raise Exception("I don't like the look of this file...")

    # Dump input contents to output file as dummy processing logic
    with open(input_file, "r") as input:
        with open(output_file, "w") as output:
            for line in input:
                output.write(line)

    # Artificially lengthen processing time - 1000 files should take ~ 13s
    time.sleep(0.1)


# Our worker logic that will run in different processes
def worker(input_file, output_file):
    success = True
    error_message = "N\\A"

    # Try catch to handle exceptions
    try:
        # Run our processing logic
        process(input_file, output_file)

    # Better to catch exceptions ourselves and report them as part of the result
    except Exception as e:
        success = False
        error_message = str(e)

    finally:
        # Return dict with status info about the processing
        return {
            "input": input_file,
            "output": output_file,
            "success": success,
            "error_message": error_message,
        }


# Generator for discoving files in our input directory that we need to process
def file_list_gen():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for file in os.listdir(INPUT_DIR):
        if file.endswith(".txt"):
            # Create the path to both the input file and the expected output
            # file name
            input_file_path = os.path.join(INPUT_DIR, file)
            output_file_path = os.path.join(
                OUTPUT_DIR, file.replace("input_", "output_")
            )

            # Skip the output file if it already exists
            if os.path.exists(output_file_path):
                continue

            # Return the pair of files to be processed/generated respectively
            yield input_file_path, output_file_path


# Function that gets the results of all te processes once they've exited
def result_callback(results):
    # Here you can check the results of each process as per the return value of
    # the worker function when it terminated
    failures = list(filter(lambda result: result["success"] is False, results))
    for failure in failures:
        input_file = failure["input"]
        error_message = failure["error_message"]
        print(f"{input_file} failed to be processed with error: {error_message}")


def main():
    # We need to pass to the Pool an initialiser function that stops the pool
    # processes from responding to interrupts - this lets us handle everything
    # from the main thread
    with multiprocessing.Pool(initializer=ignore_ints) as pool:
        try:
            # Use async so we are not stuck waiting here outside
            # of interrupt capability
            result = pool.starmap_async(
                worker, file_list_gen(), callback=result_callback
            )

            # Start a polling loop, waiting for 5 seconds
            # Interrupts can be handled every 5 seconds in this manner
            while not result.ready():
                result.wait(5)

        except KeyboardInterrupt:
            #
            print("Terminating pool!")
            pool.terminate()
            pool.join()
        else:
            print("Finished processing!")


if __name__ == "__main__":
    main()
