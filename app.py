from flask import Flask, render_template, request
import requests
import json
from datetime import datetime
import IndexingWithWhoosh.MyIndexReader as MyIndexReader
import SearchWithWhoosh.QueryRetreivalModel as QueryRetreivalModel
import SearchWithWhoosh.ExtractQuery as ExtractQuery
import PseudoRFSearch.PseudoRFRetrievalModel as PseudoRFRetrievalModel
import Classes.Query as Query

app = Flask(__name__)

# LinkedIn API Configuration
API_URL = "https://linkedin-data-api.p.rapidapi.com/search-jobs"
API_COMPANY_DETAIL_URL = "https://linkedin-data-api.p.rapidapi.com/get-company-details"
API_HEADERS = {
    'x-rapidapi-host': 'linkedin-data-api.p.rapidapi.com',
    'x-rapidapi-key': ''
}

# Format the time
def format_time(time_str):
    time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S %z UTC')
    return time_obj.strftime('%Y-%m-%d %H:%M:%S')

# Process the API Request and return the data
def fetch_jobs(keywords, date_posted, job_type, companyIds):
    params = {
        'keywords': keywords,
        'locationId': '103644278', 
        'datePosted': date_posted,
        'jobType': job_type,
        'sort': 'mostRelevant',
        'companyIds': companyIds
    }
    # AFH Wealth Management 751059
    # the LEGO Group 3724
    # next 301832 
    # mydentist UK 838360
    # ibis 1062790

    response = requests.get(API_URL, headers=API_HEADERS, params=params)
    return response.json()

def fetch_company(company_name):
    params = {
        'username': company_name,
    }
    response = requests.get(API_COMPANY_DETAIL_URL, headers=API_HEADERS, params=params)
    return response.json()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        keywords = request.args.get('keywords', '')
        date_posted = request.args.get('datePosted', '')
        job_type = request.args.get('jobType', '')
        reviews = request.args.get('reviews', '')

        if keywords != "" or date_posted != "" or job_type != "" or reviews != "":
            # Get Top Review Companies
            reviewCompanies = []
            if reviews != "":
                index = MyIndexReader.MyIndexReader("trectext")
                pesudo_search = PseudoRFRetrievalModel.PseudoRFRetreivalModel(index)
                # extractor = ExtractQuery.ExtractQuery()
                # queries= extractor.getQuries()
                queries=[]
                aQuery=Query.Query()
                aQuery.setTopicId("901")
                aQuery.setQueryContent(reviews)
                queries.append(aQuery)
                for query in queries:
                    print(query.topicId,"\t",query.queryContent)
                    results = pesudo_search.retrieveQuery(query, 5, 100, 0.4)
                    rank = 1
                    for result in results:
                        # print(query.getTopicId()," Q0 ",result.getDocNo(),' ',rank," ",result.getScore()," MYRUN",)
                        # rank += 1

                        # result.getDocNo() e.g. 427_the-LEGO-Group
                        sCompanyName = result.getDocNo().split("_")[1]
                        sCompanyName = sCompanyName.replace("-", " ")

                        comapnyData = fetch_company(sCompanyName)
                        if comapnyData["data"]:
                            reviewCompanies.append(comapnyData["data"]["id"])

                # example
                # reviewCompanies = ["751059", "3724", "301832", "838360","1062790"]
                # print(reviewCompanies)

            data = fetch_jobs(keywords, date_posted, job_type, ",".join(reviewCompanies))

            jobs = data.get('data', [])
            return render_template('index.html', jobs=jobs, keywords=keywords, date_posted=date_posted, job_type=job_type, reviews=reviews)

    return render_template('index.html', jobs=[], keywords='', date_posted='', job_type='', reviews='')

if __name__ == '__main__':
    app.run(debug=True)

