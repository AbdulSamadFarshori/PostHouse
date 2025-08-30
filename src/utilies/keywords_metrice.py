from src.tools.seo_engines import KeywordMetrice


class KeywordsAnalysis:
    def __init__(self, keywords):
        self.keywords = keywords
        self.keywords_report = []
        self.report = ""

    def get_keyword_metrice(self):
        km = KeywordMetrice()
        temp = []
        self.report = "Keywords Volume Organic-CTR \n"
        for keyword in self.keywords:
            foo = {}
            data = km.metrice(keyword)
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
        return self.report, self.keywords_report
        


            
