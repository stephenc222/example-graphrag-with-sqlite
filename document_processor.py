from logger import Logger


class DocumentProcessor:
    logger = Logger("DocumentProcessor").get_logger()

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def split_documents(self, documents, chunk_size=600, overlap_size=100):
        chunks = []
        for document in documents:
            for i in range(0, len(document), chunk_size - overlap_size):
                chunk = document[i:i + chunk_size]
                chunks.append(chunk)
        self.logger.debug("Documents split into %d chunks", len(chunks))
        return chunks

    def extract_elements(self, chunks):
        elements = []
        for index, chunk in enumerate(chunks):
            self.logger.debug(
                f"Extracting elements and relationship strength from chunk {index + 1}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                        "content": "Extract entities, relationships, and their strength from the following text. Use common terms such as 'related to', 'depends on', 'influences', etc., for relationships, and estimate a strength between 0.0 (very weak) and 1.0 (very strong). Format: Parsed relationship: Entity1 -> Relationship -> Entity2 [strength: X.X]. Do not include any other text in your response. Use this exact format: Parsed relationship: Entity1 -> Relationship -> Entity2 [strength: X.X]."},
                    {"role": "user", "content": chunk}
                ]
            )
            entities_and_relations = response.choices[0].message.content
            elements.append(entities_and_relations)
        self.logger.debug("Elements extracted")
        return elements

    def summarize_elements(self, elements):
        summaries = []
        for index, element in enumerate(elements):
            self.logger.debug(f"Summarizing element {index + 1}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Summarize the following entities and relationships in a structured format. Use common terms such as 'related to', 'depends on', 'influences', etc., for relationships. Use '->' to represent relationships after the 'Relationships:' word."},
                    {"role": "user", "content": element}
                ]
            )
            summary = response.choices[0].message.content
            summaries.append(summary)
        self.logger.debug("Summaries created")
        return summaries
