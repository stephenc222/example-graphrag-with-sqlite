import re
import time
from logger import Logger
from graph_database import GraphDatabaseConnection


class GraphManager:
    logger = Logger('GraphManager').get_logger()

    def __init__(self, db_connection: GraphDatabaseConnection):
        self.db_connection = db_connection
        self.db_connection.clear_database()

    def build_graph(self, summaries):
        if self.db_connection is None:
            self.logger.error("Graph database connection is not available.")
            return

        entities = {}
        conn = self.db_connection.get_session()

        with conn:
            for summary in summaries:
                lines = summary.split("\n")
                entities_section = False
                relationships_section = False

                for line in lines:
                    if line.startswith("### Entities:") or line.startswith("**Entities:**") or line.startswith("Entities:"):
                        entities_section = True
                        relationships_section = False
                        continue
                    elif line.startswith("### Relationships:") or line.startswith("**Relationships:**") or line.startswith("Relationships:"):
                        entities_section = False
                        relationships_section = True
                        continue

                    if entities_section and line.strip():
                        if line[0].isdigit() and '.' in line:
                            entity_name = line.split(".", 1)[1].strip()
                        else:
                            entity_name = line.strip()
                        entity_name = self.normalize_entity_name(
                            entity_name.replace("**", ""))
                        self.logger.debug(f"Creating node: {entity_name}")

                        conn.execute(
                            "INSERT OR IGNORE INTO nodes (id, properties) VALUES (?, ?)",
                            (entity_name, '{}')
                        )
                        entities[entity_name] = entity_name

                    elif relationships_section and line.strip():
                        parts = line.split("->")
                        if len(parts) >= 2:
                            source = self.normalize_entity_name(
                                parts[0].strip())
                            target = self.normalize_entity_name(
                                parts[-1].strip())

                            relationship_part = parts[1].strip()
                            relation_name = self.sanitize_relationship_name(
                                relationship_part.split("[")[0].strip())
                            strength = re.search(
                                r"\[strength:\s*(\d\.\d)\]", relationship_part)
                            weight = float(strength.group(
                                1)) if strength else 1.0

                            self.logger.debug(
                                f"Parsed relationship: {source} -> {relation_name} -> {target} [weight: {weight}]")
                            if source in entities and target in entities:
                                conn.execute(
                                    "INSERT OR REPLACE INTO edges (source, target, relationship, weight) VALUES (?, ?, ?, ?)",
                                    (source, target, relation_name, weight)
                                )
                            else:
                                self.logger.debug(
                                    f"Skipping relationship: {source} -> {relation_name} -> {target} (one or both entities not found)")

    def reproject_graph(self):
        # Reprojection isn't needed in SQLite like it is in Neo4j, but we can verify weights.
        self.verify_relationship_weights()

    def calculate_centrality_measures(self):
        conn = self.db_connection.get_session()

        # Degree centrality: count incoming/outgoing edges for each node
        degree_centrality_query = """
            SELECT id, 
                   (SELECT COUNT(*) FROM edges WHERE source = nodes.id) + 
                   (SELECT COUNT(*) FROM edges WHERE target = nodes.id) as degree
            FROM nodes
            ORDER BY degree DESC
            LIMIT 10
        """

        self.logger.debug("Starting degree centrality query")
        start_time = time.time()
        degree_centrality_result = conn.execute(
            degree_centrality_query).fetchall()
        end_time = time.time()
        self.logger.debug(
            f"Degree centrality query completed in {end_time - start_time:.8f} seconds")

        # We won't implement betweenness and closeness for now as SQLite does not have graph-native support
        centrality_data = {
            "degree": [{"entityName": row[0], "score": row[1]} for row in degree_centrality_result],
            "betweenness": [],
            "closeness": []
        }

        return centrality_data

    def summarize_centrality_measures(self, centrality_data):
        summary = "### Centrality Measures Summary:\n"

        summary += "#### Top Degree Centrality Nodes (most connected):\n"
        for record in centrality_data["degree"]:
            summary += f" - {record['entityName']} with score {record['score']}\n"

        summary += "\n#### Top Betweenness Centrality Nodes (influential intermediaries):\n"
        summary += "(Not calculated)\n"

        summary += "\n#### Top Closeness Centrality Nodes (closest to all others):\n"
        summary += "(Not calculated)\n"

        return summary

    def drop_existing_projection(self, graph_name):
        # No need to implement drop projection in SQLite, it is only necessary in Neo4j's GDS
        pass

    def verify_relationship_weights(self):
        conn = self.db_connection.get_session()
        query = "SELECT * FROM edges WHERE weight IS NULL LIMIT 5"

        self.logger.debug("Starting verify relationship weights query")
        start_time = time.time()
        missing_weights = conn.execute(query).fetchall()
        end_time = time.time()
        self.logger.debug(
            f"Verify relationship weights query completed in {end_time - start_time:.8f} seconds")

        if missing_weights:
            self.logger.warning(
                "Warning: Some relationships do not have weights assigned.", missing_weights)

    def get_relationship_types(self):
        conn = self.db_connection.get_session()
        query = "SELECT DISTINCT relationship FROM edges"

        self.logger.debug("Starting get relationship types query")
        start_time = time.time()
        result = conn.execute(query).fetchall()
        end_time = time.time()
        self.logger.debug(
            f"Get relationship types query completed in {end_time - start_time:.8f} seconds")

        return [record[0] for record in result]

    def normalize_entity_name(self, name):
        return name.strip().lower()

    def sanitize_relationship_name(self, name):
        return re.sub(r'\W+', '_', name.strip().lower())
