from SearchWithWhoosh.QueryRetreivalModel import QueryRetrievalModel
import math
import numpy as np
import Classes.Document as Document

class PseudoRFRetreivalModel:

    indexReader=[]

    def __init__(self, ixReader):
        self.indexReader = ixReader
        return

    # Search for the topic with pseudo relevance feedback.
    # The returned results (retrieved documents) should be ranked by the score (from the most relevant to the least).
    # query: The query to be searched for.
    # TopN: The maximum number of returned document
    # TopK: The count of feedback documents
    # alpha: parameter of relevance feedback model
    # return TopN most relevant document, in List structure

    def retrieveQuery(self, query, topN, topK, alpha):
        # this method will return the retrieval result of the given Query, and this result is enhanced with pseudo relevance feedback
        # (1) you should first use the original retrieval model to get TopK documents, which will be regarded as feedback documents
        # (2) implement GetTokenRFScore to get each query token's P(token|feedback model) in feedback documents
        # (3) implement the relevance feedback model for each token: combine the each query token's original retrieval score P(token|document) with its score in feedback documents P(token|feedback model)
        # (4) for each document, use the query likelihood language model to get the whole query's new score, P(Q|document)=P(token_1|document')*P(token_2|document')*...*P(token_n|document')


        # get P(token|feedback documents)
        TokenRFScore = self.GetTokenRFScore(query, topK)

        # sort all retrieved documents from most relevant to least, and return TopN
        ##results=[]保留

        words = query.queryContent.split(' ')
        words = [word for word in words if word != 'OR']
        num_docs = self.indexReader.searcher.doc_count()
        scores = [0 for _ in range(num_docs)]
        postings = [self.indexReader.getPostingList(words[i]) for i in range(len(words))]
        DocFreq = {}

        for i in range(len(words)):
            DocFreq[words[i]] = self.indexReader.DocFreq(words[i]) / num_docs

        for docId in range(num_docs):
            mu = 2000
            logp = 0
            denominator = self.indexReader.getDocLength(docId) + mu
            score_zero = False

            for i in range(len(words)):
                nominator = mu * DocFreq[words[i]]
                if nominator == 0 and words[i] not in postings[i]:
                    scores[docId] = 0
                    score_zero = True
                    break
                if docId in postings[i]:
                    nominator += postings[i][docId]
                logp += math.log(alpha * nominator / denominator + (1 - alpha) * TokenRFScore[words[i]])

            if not score_zero:
                scores[docId] = math.exp(logp)

        # Normalize scores for better readability
        max_score = max(scores)
        if max_score > 0:
            scores = [score / max_score for score in scores]

        # Sort scores in descending order
        indices = np.argsort(scores)[::-1]
        results = []
        for idx in indices[:topN]:
            document = Document.Document()
            document.setDocId(idx)
            document.setDocNo(self.indexReader.getDocNo(idx))
            document.setScore(scores[idx])
            results.append(document)
        return results

    def GetTokenRFScore(self, query, topK):
        # for each token in the query, you should calculate token's score in feedback documents: P(token|feedback documents)
        # use Dirichlet smoothing
        # save {token: score} in dictionary TokenRFScore, and return it
        TokenRFScore = {}
        search = QueryRetrievalModel(self.indexReader)
        feedback = search.retrieveQuery(query, topK)
        words = query.queryContent.split(' ')
        postings = [self.indexReader.getPostingList(words[i]) for i in range(len(words))]
        doc_ids = [doc.getDocId() for doc in feedback]
        num_docs = self.indexReader.searcher.doc_count()
        DocFreq = {}

        for i in range(len(words)):
            DocFreq[words[i]] = self.indexReader.DocFreq(words[i]) / num_docs

        mu = 2000 # Dirichlet smoothing parameter
        denominator = sum([self.indexReader.getDocLength(docId) for docId in doc_ids]) + mu #Total feedback doc length

        for i in range(len(words)):
            nominator = mu * DocFreq[words[i]]
            try:
                nominator += sum([postings[i][docId] for docId in doc_ids])  # Add word frequency in feedback docs
            except KeyError:
                pass  # If word does not occur in feedback documents, skip

            TokenRFScore[words[i]] = nominator / denominator

        return TokenRFScore

