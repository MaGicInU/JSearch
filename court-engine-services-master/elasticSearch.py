
import json
import uuid
import requests

from doc_preprocessor.grammar import getProcessedQueryText
from elasticSearchModel import SearchModel
base_url = "http://localhost:9200/"
indexName = "finaljudgements/"


class ElasticSearchUtil():
    def __init__(self) -> None:
        pass

    def getDoc(self, id):
        response = requests.get(base_url+indexName+"_doc/"+id)
        return response.json()

    def insertToIndex(self, doc, id):

        response = requests.post(base_url+indexName+"_doc/"+str(id), json=doc)
        return response.text

    def search(self, searchModel: SearchModel):
        processedQueryText = getProcessedQueryText(
            queryText=searchModel.queryText)
        searchModel.queryText = processedQueryText
        query = self.generateFullQuery(searchModel)
        response = requests.post(
            base_url+indexName+"_search", json=query)  # json.dumps(query, 1))
        print(query)
        return response.json()

    def searchQuery(self, queryString: str):
        queryJson = {
            "query": {
                "simple_query_string": {
                    "query": "{}*".format(queryString),
                    "fields": ["queryText"]
                }
            }
        }

        response = requests.post(base_url+indexName+"_search", json=queryJson)

        return response.json()

    def generateFullQuery(self, searchModel: SearchModel):
        baseQuery = {}
        queryList = []
        queryList.extend(self.generateSingleQuery(
            searchModel.respondent, "respondent"))
        queryList.extend(self.generateSingleQuery(
            searchModel.petitioner, "petitioner"))
        queryList.extend(self.generateSingleQuery(
            searchModel.section, "section"))
        queryList.extend(self.generateSingleQuery(
            searchModel.text_sections, "textSections"))
        queryList.extend({
            "match": {
                "queryText": searchModel.queryText
            }
        })
        yearList = []
        try:
            for year in range(int(searchModel.fromYear), int(searchModel.toYear)):
                yearList.append(str(year))
        except:
            pass
        queryList.extend(self.generateSingleQuery(
            yearList, "date"))
        queryList.extend(self.generateSingleQuery(
            searchModel.court, "court"))
        if("high court".lower() in [c.lower() for c in searchModel.court]):
            queryList.extend(self.generateSingleQuery(
                [searchModel.highCourtLocation], "highCourtLocation"
            ))
        queryList.extend(self.generateSingleQuery(
            [searchModel.JudgementNumber], "JudgementNumber"))
        baseQuery["query"] = {
            "bool": {
                "must": queryList
            }
        }
        return baseQuery

    def generateSingleQuery(self, stringList, fieldName):  # level match, filter
        subQuery = []
        for pet in stringList:
            if pet != "":
                subQuery.append(
                    {
                        "match": {
                            fieldName: pet
                        }
                    }
                )
        return subQuery
