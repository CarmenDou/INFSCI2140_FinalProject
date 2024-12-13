import IndexingWithWhoosh.MyIndexReader as MyIndexReader
import SearchWithWhoosh.QueryRetreivalModel as QueryRetreivalModel
import SearchWithWhoosh.ExtractQuery as ExtractQuery
import PseudoRFSearch.PseudoRFRetrievalModel as PseudoRFRetrievalModel
import datetime


# This is for INFSCI 2140 in Fall 2023

if __name__ == '__main__':
    startTime = datetime.datetime.now()
    index = MyIndexReader.MyIndexReader("trectext")
    pesudo_search = PseudoRFRetrievalModel.PseudoRFRetreivalModel(index)
    extractor = ExtractQuery.ExtractQuery()
    queries= extractor.getQuries()
    for query in queries:
        print(query.topicId,"\t",query.queryContent)
        results = pesudo_search.retrieveQuery(query, 20, 100, 0.4)
        rank = 1
        for result in results:
            print(query.getTopicId()," Q0 ",result.getDocNo(),' ',rank," ",result.getScore()," MYRUN",)
            rank += 1

        """print(query.topicId, "\t", query.queryContent)
        results = pesudo_search.retrieveQuery(query, 20, 100, 0.4)  # 检索文档
        rank = 1
        for result in results:
            # 获取文档编号
            docNo = result.getDocNo()

            # 通过文档编号获取文档标题
            docTitle = index.getDocTitle(docNo)  # 假设 MyIndexReader 中有 getDocTitle 方法

            # 打印结果，包含标题
            print(f"{query.getTopicId()} Q0 {docNo} {rank} {result.getScore():.4f} MYRUN")
            print(f"   Title: {docTitle}")  # 输出文档标题
            rank += 1"""

    endTime = datetime.datetime.now()
    print("query search time: ", endTime - startTime)

