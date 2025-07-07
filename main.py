from linkup import LinkupClient


client = LinkupClient(api_key="e722b372-ff82-422c-9295-8408e2ed8427")


prompt = f"""Using the company's official website, LinkedIn profile, and any publicly available content, determine the Ideal Customer Profile (ICP) for the following company.

Include details on:
- Industry
- Target customer segment (e.g., SMB, mid-market, enterprise)
- Geography (if relevant)
- Buyer personas (typical roles or job titles targeted)
- Common pain points the company addresses
- Core value proposition
- Purchase triggers
- Notable customers (if publicly available)

Context:
- Company: New England Solar and Green
- Company website: https://nesolarandgreen.com/
- Company LinkedIn: https://www.linkedin.com/company/new-england-solar-&-green-solutions/
"""

response = client.search(
  query= prompt,
  depth="deep",
  output_type="searchResults",
  include_images=False,
)

print(response)