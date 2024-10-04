import pickle
import sys


def print_pkl_file(filename):
    """
    Prints the content of the given pickle file to the console.

    Parameters:
    filename (str): The name of the pickle file.
    """
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
            print(data)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python log_pkl.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    print_pkl_file(filename)
