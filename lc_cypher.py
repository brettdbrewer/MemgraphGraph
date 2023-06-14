from langchain.chat_models import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from memgraph import MemgraphGraph

query: str = ""

graph = MemgraphGraph(
    url="bolt://127.0.0.1:7687", username="brettb", password="password"
)

chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0, model="gpt-4"),
    graph=graph,
    verbose=True,
)

###### queries that leverage nodes and relationships
# query = "Show me the characters with allegiance to the White Walkers."
# query = "Who is Jon Snow allied with?"
# query = "Which episode had the most deaths?"
# query = "Which location had the most deaths?"
# query = "Where did Jon Snow die?"
# query = "Which episode is the highest rated?"
# query = "Which characters had the most allegiances?"
# query = "Which characters had the most allegiances, and what were they?"
# query = "Who were the victims in the episode called The Long Night?"
# query = "Who died in the red wedding?"

###### queries that leverage the method property of the KILLED relationship
# query = "Which characters were killed by hanging?"  /
# doesn't equate "hanged" with KILLED method of "Noose"
# query = "Which character was killed by a Shadow Demon?"  # returns correct answer
# query = "How was Jon Snow killed?"  # results in unbound variable error
# query = "Which characters were killed by poison?"  /
# fails due to "poison" not being capitalized
# query = "Which characters were killed by Poison?"  /
# correctly creates Cypher query, but final answer incomplete
query = "Which character was killed by Magic?"

results = chain.run(query)

print(results)
