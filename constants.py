import os

EXAMPLE_TEXT_DIRECTORY = "example_text"

# Function to read the content of each document from the example_text directory


def read_documents_from_files(filenames, directory=EXAMPLE_TEXT_DIRECTORY):
    documents = []
    for filename in filenames:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            documents.append(file.read())
    return documents


# Read documents and store them in the DOCUMENTS list
DOCUMENTS = read_documents_from_files(["doc_1.txt", "doc_2.txt"])
DOCUMENTS_TO_ADD_TO_INDEX = read_documents_from_files(["doc_3.txt"])
