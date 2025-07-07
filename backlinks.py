import requests 


username = "mozscape-yiPDqg6PXH"
secret = "MMG4AKQavaWO5AChRtYtLKqQXvLr8JDZ"


endpoint_url = "https://lsapi.seomoz.com/v2/links"

api_token = "bW96c2NhcGUtdVRJTW82ajNjbDpUMldsYlFTdjMydUNlamFQNEhiMUFKaUc0c1F4TGpkag=="

# Define your request headers with the custom API token
headers = {
  "x-moz-token": api_token,
  "Content-Type": "application/json",
}

# Sample payload for a request which won't use any quota:
request_body = {
    "target": "https://nesolarandgreen.com/",
    "target_scope": "root_domain",
    "source_scope":"root_domain",
    "filter": "external+nofollow",
    "limit": 30
}

# Send the POST request with authentication
response = requests.post(endpoint_url, headers=headers, json=request_body)

# Print the response
print(response.json())


data = response.json()


data_level_1 = data.get("results")
pages = []

for h in data_level_1:
    source = h.get("source")
    page = source.get('page')
    pages.append(page)
    
pages