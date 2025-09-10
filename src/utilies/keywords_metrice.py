from src.tools.seo_engines import KeywordMetrice


class KeywordsAnalysis:
    def __init__(self, keywords, organic_keywords):
        self.keywords = keywords
        self.organic_keywords = organic_keywords
        self.keywords_report = []
        self.report = ""
        self.total_hits = 0 

    def merge_keywords(self):
        for keyword in self.organic_keywords:
            sent = keyword.get('keyword', "")
            tokens = sent.split(" ")
            for token in tokens:
                if token not in self.keywords:
                    self.keywords.append(token)

    def get_keyword_metrice(self):
        self.merge_keywords()
        km = KeywordMetrice()
        temp = []
        self.report = "Keywords Volume Organic-CTR \n"
        for keyword in self.keywords:
            foo = {}
            data, hits = km.metrice(keyword)
            self.total_hits += hits
            result = data.get('result', {})
            metrics_dict = result.get('keyword_metrics', {})
            foo['keyword'] = keyword
            volume = metrics_dict.get('volume', 0)
            ctr = metrics_dict.get('organic_ctr', 0)
            foo['volume'] = volume
            foo['organic_ctr'] = ctr
            temp.append(foo)
            self.report += f"{keyword} {volume} {ctr} \n"
        self.keywords_report = temp
        return self.report, self.keywords_report, self.total_hits
        


            
