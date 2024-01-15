from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

query = """
query MyQuery {
  query
}
"""

def make_request():
    requests.post("http://localhost:8001/graphql", json={"query": query})


with ThreadPoolExecutor() as executor:
    jobs = [
        executor.submit(make_request)
        for i in range(10)
    ]
    for future in as_completed(jobs):
        print(future.result())
