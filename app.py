from openai import OpenAI
from dotenv import load_dotenv
from constants import DOCUMENTS, DOCUMENTS_TO_ADD_TO_INDEX
import os
import pickle

from document_processor import DocumentProcessor
from graph_database import GraphDatabaseConnection
from graph_manager import GraphManager
from logger import Logger
from query_handler import QueryHandler

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PATH = os.getenv("DB_PATH")
MODEL = "gpt-4o-2024-08-06"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize document processor
document_processor = DocumentProcessor(client, MODEL)

# Initialize database connection
db_connection = GraphDatabaseConnection(db_path=DB_PATH)

# Initialize graph manager
graph_manager = GraphManager(db_connection)

# Initialize query handler
query_handler = QueryHandler(graph_manager, client, MODEL)

# Initialize logger
logger = Logger("AppLogger").get_logger()

# Functions related to document processing


def load_or_run(file_path, run_function, *args):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory {directory}")

    if os.path.exists(file_path):
        logger.info(f"Loading data from {file_path}")
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
    else:
        logger.info(f"Running function to generate data for {file_path}")
        data = run_function(*args)
        if data is not None:
            with open(file_path, 'wb') as file:
                pickle.dump(data, file)
    return data


def initial_indexing(documents, graph_manager: GraphManager):
    chunks = document_processor.split_documents(documents)
    elements_file = 'data/initial_elements_data.pkl'
    summaries_file = 'data/initial_summaries_data.pkl'

    elements = load_or_run(
        elements_file, document_processor.extract_elements, chunks)
    summaries = load_or_run(
        summaries_file, document_processor.summarize_elements, elements)

    graph_manager.build_graph(summaries)


def reindex_with_new_documents(new_documents, graph_manager: GraphManager):
    chunks = document_processor.split_documents(new_documents)
    elements_file = 'data/new_elements_data.pkl'
    summaries_file = 'data/new_summaries_data.pkl'

    elements = load_or_run(
        elements_file, document_processor.extract_elements, chunks)
    summaries = load_or_run(
        summaries_file, document_processor.summarize_elements, elements)

    graph_manager.build_graph(summaries)
    graph_manager.reproject_graph()


if __name__ == "__main__":

    initial_documents = DOCUMENTS

    # Index the initial documents
    initial_indexing(initial_documents, graph_manager)

    # First question after initial indexing
    query_1 = "What are the main themes in these documents?"
    logger.info('Query 1: %s', query_1)
    answer_1 = query_handler.ask_question(query_1)
    logger.info('Answer to query 1: %s', answer_1)

    # Adding new documents and reindexing
    new_documents = DOCUMENTS_TO_ADD_TO_INDEX
    reindex_with_new_documents(new_documents, graph_manager)

    # Second question after reindexing with new documents
    query_2 = "What are the main themes in these documents?"
    logger.info('Query 2: %s', query_2)
    answer_2 = query_handler.ask_question(query_2)
    logger.info('Answer to query 2: %s', answer_2)
