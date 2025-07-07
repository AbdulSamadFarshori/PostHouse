from tavily import TavilyClient

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key="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")

# Step 2. Executing a simple search query
response = tavily_client.search("top 10 afghan resturants in uk")

# Step 3. That's it! You've done a Tavily Search!
print(response)