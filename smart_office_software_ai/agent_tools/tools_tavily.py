from langchain_community.tools.tavily_search import TavilySearchResults


def get_search():
    search = TavilySearchResults(
        tavily_api_key="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",
        max_results=1
    )
    # print(search.invoke("今天上海天气怎么样"))
    return search
