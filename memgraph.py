from typing import Any, Dict, List
from langchain.graphs import Neo4jGraph

node_query = """
CALL meta_util.schema(true) YIELD nodes RETURN nodes AS output;
"""

rel_properties_query = """
CALL meta_util.schema(true) YIELD relationships RETURN relationships AS output;
"""

rel_query = """
CALL meta_util.schema() YIELD relationships RETURN relationships AS output;
"""


def build_schema(nodes, rel_properties, relationships) -> str:
    node_dict: Dict = {}
    node_prop_str: str = ""
    rel_prop_str: str = ""
    rel_str: str = ""

    # iterate over nodes in the graph schema
    node_list = nodes[0]["output"]
    for node in node_list:
        node_label_list = []
        node_id = node["id"]
        for node_label in node["labels"]:
            node_label_list.append(node_label)
        node_dict[node_id] = node_label_list

        # create list of all node properties
        node_property_list = list(node["properties"]["properties_count"].keys())

        # form property string(s) for prompt injection
        node_properties_str = ""
        for property in node_property_list:
            node_properties_str += f"""('property': '{property}', 'type': 'STRING'),"""

        # form the full label and property string per node label for prompt injection
        for node_label in node_dict[node_id]:
            node_prop_str += f"""Node Name: '{node_label}', Node Properties: [{node_properties_str}]\n"""

    # form the relationship property string(s) for prompt injection
    rel_prop_list = rel_properties[0]["output"]
    for rel in rel_prop_list:
        rel_property_list = list(rel["properties"]["properties_count"].keys())

        if rel_property_list:  # only add if there are properties
            # form property string(s) for prompt injection
            rel_properties_str = ""
            for property in rel_property_list:
                if property != "count":  # don't add count property
                    rel_properties_str += (
                        f"""('property': '{property}', 'type': 'STRING'),"""
                    )

                    # form the full label and property string per node label for prompt injection
                    rel_label = rel["label"]
                    rel_prop_str += f"""Relationship Name: '{rel_label}', Node Properties: [{rel_properties_str}]\n"""

    # form the relationship strings for prompt injection
    rel_list = relationships[0]["output"]
    # each node may have more than one label, so iterate through
    # each permutatation of start and end labels for each relationship
    for rel in rel_list:
        for start_label in node_dict[rel["start"]]:
            for end_label in node_dict[rel["end"]]:
                rel_str += f"['(:{start_label})-[:{rel['label']}]->(:{end_label})']\n"

    schema = f"""
Node properties are the following:
{node_prop_str}
Relationship properties are the following:
{rel_prop_str}
The relationships are the following:
{rel_str}
    """

    print(schema)  # TODO: remove this in final implementation
    return schema


class MemgraphGraph(Neo4jGraph):
    """Memgraph wrapper for graph operations."""

    def __init__(
        self, url: str, username: str, password: str, database: str = "memgraph"
    ) -> None:
        """Create a new Memgraph graph wrapper instance."""
        try:
            import neo4j
        except ImportError:
            raise ValueError(
                "Could not import neo4j python package. "
                "Please install it with `pip install neo4j`."
            )

        self._driver = neo4j.GraphDatabase.driver(url, auth=(username, password))
        self._database = database
        self.schema = ""
        # Verify connection
        try:
            self._driver.verify_connectivity()
        except neo4j.exceptions.ServiceUnavailable:
            raise ValueError(
                "Could not connect to Memgraph database. "
                "Please ensure that the url is correct"
            )
        except neo4j.exceptions.AuthError:
            raise ValueError(
                "Could not connect to Memgraph database. "
                "Please ensure that the username and password are correct"
            )
        # Set schema
        self.refresh_schema()

    @property
    def get_schema(self) -> str:
        """Returns the schema of the Memgraph database"""
        return self.schema

    def query(self, query: str, params: dict = {}) -> List[Dict[str, Any]]:
        """Query Memgraph database."""
        from neo4j.exceptions import CypherSyntaxError

        with self._driver.session(database=self._database) as session:
            try:
                data = session.run(query, params)
                # Hard limit of 50 results
                return [r.data() for r in data][:50]
            except CypherSyntaxError as e:
                raise ValueError("Generated Cypher Statement is not valid\n" f"{e}")

    def refresh_schema(self) -> None:
        """
        Refreshes the Memgraph graph schema information.
        """
        node_properties = self.query(node_query)
        relationships_properties = self.query(rel_properties_query)
        relationships = self.query(rel_query)

        self.schema = build_schema(
            node_properties, relationships_properties, relationships
        )
