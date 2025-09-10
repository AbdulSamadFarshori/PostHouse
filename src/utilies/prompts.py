

def create_on_page_audit_report():
    prompt = """You are an expert in on-page SEO auditing.

                INPUT:
                - You will receive website data in this exact format: {docs}
                - Each item is a <Document ...> block with:
                - url=..., page_name=...
                - observations about keywords/meta tags
                - raw meta fields: <title>...</title>, <description>...</description>
                - <content>...</content> (plain text snippet or full text)
                - Use ONLY the provided data. Do not assume, crawl, or hallucinate missing fields. If something is not present, write “N/A”.

                TASK:
                For EACH <Document> page, produce a compact, plain-English audit. Keep logic simple and clear. Be specific and actionable. Avoid generic advice. All outputs must be in ONE Markdown-formatted string.

                SCORING (0–100 total per page):
                - Meta (titles/descriptions): 25
                - Headings (H1–H3 usage & keyword placement): 15
                - Content relevance & coverage: 25
                - Keywords (primary/secondary/LSI usage & risk of stuffing): 10
                - Internal/External links (if inferable from content text): 10
                - Social/OG/Twitter tags (presence): 5
                - Structured data / Canonical / Robots (if mentioned): 10
                Explain any score deductions briefly.

                BEST-PRACTICE CHECKS (use these rules to score/flag):
                - Title length ideal: 50–60 chars; include primary keyword near start; brand optional.
                - Description length ideal: 150–160 chars; include primary and supporting keyword naturally.
                - Headings: exactly one H1 is preferred; keywords appear in H1/H2 without stuffing.
                - Content: on-topic terms appear naturally; avoid repetition; include local cues if present (e.g., city/region).
                - Social tags: OG and Twitter present = good.
                - Technical: note canonical/robots/indexability/schema ONLY if the doc mentions them; otherwise N/A.

                OUTPUT FORMAT (one Markdown string; repeat the following block for each page):

                ### page_name — url
                **Overall status:** OK | Needs Work | Critical  
                **Page Score (0–100):** score

                **1) Meta Audit**
                - **Current Title:** “title_text”  
                - Length: char_count chars → Within 50–60 | Short | Long  
                - Keyword Use: Good | Missing | Overused  
                - **Suggested Title (≤60 chars):** “rewrite_title” (count: len)
                - **Current Description:** “description_text”  
                - Length: char_count chars → Within 150–160 | Short | Long  
                - Keyword Use: Good | Missing | Overused  
                - **Suggested Description (≤160 chars):** “rewrite_description” (count: len)
                - **OG Tags:** Present | N/A  
                - **Twitter Card:** Present | N/A

                **2) Headings & Structure**
                - H1 present and focused: Yes/No/Unclear  
                - Keyword in H1: Yes/No  
                - H2/H3 coverage (brief): e.g., “mentions services and location”, or N/A  
                - Issues: e.g., duplicate H1, missing H1, shallow hierarchy, or N/A  
                - Fixes (2–3 bullets): 
                - actionable fix 1
                - actionable fix 2

                **3) Keywords & Intent**
                - Top keywords observed: list from “Top keywords Observation” if present; else N/A
                - **Primary Keyword (pick one):** primary_kw  
                - **Secondary/LSI (2–5):** kw2, kw3, ...  
                - Stuffing risk: Low/Medium/High with note  
                - Gap hints (2 bullets): 
                - missing topical/entity term
                - location/service variant if applicable

                **4) Content Review**
                - Word count (estimate from <content>): count or N/A  
                - Relevance summary (1–2 lines): simple summary tied to intent  
                - **Quick Wins (max 3):**  
                - add a short customer proof/FAQ/benefit  
                - clarify service scope or coverage area  
                - add internal link to pricing/case studies
                - **FAQ ideas (2):**  
                - Q1
                - Q2

                **6) Technical Notes**
                - Canonical: Present/Not mentioned  
                - Robots/Indexability: indexable/noindex/Not mentioned  
                - Structured Data (Schema): Present/Not mentioned  
                - Mobile/readability hints from text: brief note or N/A

                **7) Priority Actions (Top 5)**
                1) highest-impact change  
                2) next  
                3) next  
                4) next  
                5) next

                ---

                SITE-LEVEL WRAP-UP (after all pages):
                - Duplicate or near-duplicate titles/descriptions across pages: list or N/A
                - Keyword cannibalization risk (same primary keyword on multiple pages): brief note
                - Missing social tags across pages: count/pages  
                - Quick sitewide wins (max 3):
                - win 1
                - win 2
                - win 3

                REQUIREMENTS:
                - Use only the provided observations, meta fields, and content text.
                - Report exact character counts for title/description and label “Within range / Short / Long”.
                - If a field is absent, output “N/A” and do not invent it.
                - Keep each page section concise, concrete, and actionable.
                - Return ONE single Markdown string as the final report.
                - Words count not more than 1000 words.

                """
    return prompt


def classify_industry():
    prompt = """you are an expert in identify business industry type, your task is to identify business industry by given website home page text data, 
            Home Page Data - : {docs}

            Instructions:
                - don't give the broad terms, be specific in giving industry  
                - give only name of the industry.
            """
    return prompt


def generate_search_query():

    prompt = """you are expert in doing research online, your task is to create a search query for search engine, our aim is to find other companies of the given industry.
            industry - : {industry}

            Instruction
            - give only main keywords in query
            - it should be one query, don't generate query more than one.  

            """
    return prompt

def classify_search_results():
    prompt = """you are an expert in identify which is blog, article or business website url, so your task is to identify the blogs, articles and business website url and return blogs, articles and business-website. You can identify them by provided title and description. list of urls :- {arr}:
                Instructions:
                1. give only url as first key and classification as a second key, example of json: {example}
                2. classify those urls as closed those industry are different from given industry : {industry}
            """
    return prompt

def classify_search_root_domain():
    prompt = """you are an expert in identify/classify which is relavent or irrelavent url, so your task is to identify the relavent or irrelavent url and return relavent or irrelavent. You can identify them by provided title and description, you can classify relavent the website when it is dealing in the relavent industry otherwise it is irrelavent. list of urls :- {arr}:
                Instructions:
                1. give only url as first key and classification as a second key, example of json: {example}
                2. classify urls based on this industry : {industry}
                3. business listing site, listing website, or web directory websites should be classified them as irrelavent"""
    return prompt


def url_filter_prompt():
    prompts = """you are a website analyst for SEO, your task to find out the urls where can get website information and keywords.
            you don't have to consider useful urls like login url or registration url, etc.
            here is the list of urls:
            URLS : {urls} 
            """
    return prompts 

def generate_remaining_report_prompt():
    prompt = """your task is to write a small summary/paragraph regarding true competitors, organic keywords research, keywords gap and backlinks gap. you are provided with keywords list 
    which are missing in client website and backlings which missing and competitors list with domain authority score and organic keywords which are used by competitors. you need to show given data in proper tabular form
    
    Organic Keywords Research List : {organic_keywords}
    Keywords Gap List : {keywords}
    Backlinks Gap List : {backlinks}
    True Competitors List : {competitors}
    


    instruction:
    - words count not more than 500 words.
    """
    return prompt

