import sqlite3
import json
import sys


def export_graph_data(db_path='data/graph_database.sqlite'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query nodes
    cursor.execute("SELECT id FROM nodes")
    nodes = [{"id": row[0]} for row in cursor.fetchall()]

    # Query edges
    cursor.execute("SELECT source, target, relationship, weight FROM edges")
    edges = [{"source": row[0], "target": row[1], "relationship": row[2],
              "weight": row[3]} for row in cursor.fetchall()]

    # Structure data for D3.js (nodes and links)
    graph_data = {
        "nodes": nodes,
        "links": edges
    }

    # Export to JSON
    with open('public/graph_data.json', 'w') as json_file:
        json.dump(graph_data, json_file, indent=4)

    print("Graph data exported to 'graph_data.json'.")
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python export_graph_data.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    export_graph_data(filename)
