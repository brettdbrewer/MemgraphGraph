# MemgraphGraph
Query Memgraph databases using Langchain

lc_cypher.py - a test file for querying a Memgraph database using natural language. You'll need to set the OPENAI_API_KEY environment variable in your OS to your OpenAI key. This file tests against the Game of Thrones deaths dataset you can load from Memgraph Lab.
If you are running Memgraph in Docker, you have to run Memgraph using "-e MEMGRAPH="--bolt-server-name-for-init=Neo4j/" switch to make it compatible with the Neo4j drivers using the bolt protocol. 

memgraph.py - file definining the class MemgraphGraph, a class derived from Neo4jGraph in Langchain
