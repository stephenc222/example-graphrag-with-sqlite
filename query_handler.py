from graph_manager import GraphManager
from openai import OpenAI
from logger import Logger


class QueryHandler:
    logger = Logger("QueryHandler").get_logger()

    def __init__(self, graph_manager: GraphManager, client: OpenAI, model: str):
        self.graph_manager = graph_manager
        self.client = client
        self.model = model

    def ask_question(self, query):
        centrality_data = self.graph_manager.calculate_centrality_measures()
        centrality_summary = self.graph_manager.summarize_centrality_measures(
            centrality_data)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Use the centrality measures to answer the following query."},
                {"role": "user", "content": f"Query: {query} Centrality Summary: {centrality_summary}"}
            ]
        )
        self.logger.debug("Query answered: %s",
                          response.choices[0].message.content)
        final_answer = response.choices[0].message.content
        return final_answer
