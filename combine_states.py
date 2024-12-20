import os
import glob

def calculate_or(input_dir, output_file):
    # Find all state_*.txt files
    state_files = glob.glob(os.path.join(input_dir, "state_*.txt"))

    # Initialize the logical OR results
    active = False
    waking = False

    # Read each file and perform a logical OR operation
    for state_file in state_files:
        with open(state_file, "r") as f:
            content = f.read().strip()
            # Convert to boolean and apply OR
            active = active or (content.lower() == "active")
            waking = waking or (content.lower() == "waking")

    # Write the result to the output file
    with open(output_file, "w") as f:
        f.write("active" if active else "waking" if waking else "inactive")

if __name__ == "__main__":
    input_dir = "./states"  # Directory containing state_*.txt files
    output_file = "./state.txt"
    calculate_or(input_dir, output_file)
