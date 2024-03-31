import uuid
from fastapi import FastAPI,  UploadFile

from PyPDF2 import PdfFileReader
from io import BytesIO
import requests
from elasticSearch import ElasticSearchUtil
from doc_preprocessor.documentParser import DocumentParser
from pydantic import BaseModel
from elasticSearchModel import SearchModel
from idRequestModel import IdRequestModel
from mongodb.mongo_util import getDocument, searchSections, uploadToMongo
from fastapi.middleware.cors import CORSMiddleware

from sectionModel import SectionModel
# from mongodb.mongo_util import uploadToMongo
from fastapi.middleware.cors import CORSMiddleware

from searchQueryModel import SearchQueryModel
import sys
import typing
from borb.pdf.document.document import Document
from borb.pdf.pdf import PDF
from borb.toolkit.text.simple_text_extraction import SimpleTextExtraction
sys.setrecursionlimit(150000)
app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:9200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
summarization_url = "http://c8c8-34-74-123-138.ngrok.io"


@app.get("/")
def root():
    return "Hello World"


@app.post("/pdfUpload")
async def uploadPdf(file: UploadFile):

    bytes = BytesIO(await file.read())
    parser = DocumentParser(await processPdf(bytes))
    parsedMap = parser.parse()
    parsedMap["raw_text"] = await rawTextProcess(bytes)
    id = uuid.uuid4()
    elasticSearch = ElasticSearchUtil()
    # await uploadToMongo(bytes, id)
    return elasticSearch.insertToIndex(parsedMap, id)


@app.post("/getPDf")
def getPdf(request: IdRequestModel):
    # file = getDocument(request.id)
    elasticSearch = ElasticSearchUtil()
    return elasticSearch.getDoc(request.id)
    # doc: typing.Optional[Document] = None
    # l: SimpleTextExtraction = SimpleTextExtraction()
    # with open("output.pdf", "rb") as in_file_handle:
    # doc = PDF.loads(file.read(), [l])
    # check whether we have read a Document
    # assert doc is not None

    # print the text on the first Page
    # doc_text = l.get_text_for_page(0)

    # pdf = PdfFileReader(file)
    # doc_text = ""
    # for pageNo in range(pdf.numPages):
    #     page = pdf.getPage(pageNo)
    #     text = page.extractText()
    #     doc_text = doc_text + text+"\n"
    # print("Docc {0}".format(doc_text))
    return doc_text


@app.post("/summarize")
async def receivePdf(file: UploadFile):
    summary = {"error": "error"}
    print(file.filename)
    docText = await processPdf(file)
    api = summarization_url+"/summarize"
    print("APII: {0}".format(api))
    summary = requests.post(api, json={"text": docText})

    return {"result": summary.text}


@app.post("/search")
def search(searchModel: SearchModel):
    elasticSearch = ElasticSearchUtil()
    print(searchModel.dict)
    print("Hereee")
    result = elasticSearch.search(searchModel)
    return result


@app.post("/section")
def section(sectionModel: SectionModel):
    finalMap = searchSections(sectionModel.sections)
    return finalMap


@app.post("/searchQuery")
def searchQuery(queryStringModel: SearchQueryModel):
    elasticSearch = ElasticSearchUtil()
    result = elasticSearch.searchQuery(queryStringModel.queryString)
    response = processSearchQueryResponse(result, queryStringModel.queryString)
    return response


async def processPdf(bytes):
    pdf = PdfFileReader(bytes)
    doc_text = ""
    for pageNo in range(pdf.numPages):
        page = pdf.getPage(pageNo)
        text = page.extractText()
        text = " ".join(text.split("\n"))
        doc_text += text
    return doc_text


async def rawTextProcess(bytes):
    pdf = PdfFileReader(bytes)
    doc_text = ""
    for pageNo in range(pdf.numPages):
        page = pdf.getPage(pageNo)
        text = page.extractText()
        # text = " ".join(text.split("\n"))
        doc_text += text
    return doc_text


def processSearchQueryResponse(response, queryString):
    hitsList = response["hits"]["hits"]
    responseList = []
    nextWordList = []
    for hit in hitsList:

        nextWordList = []
        text = hit["_source"]["queryText"]
        raw = hit["_source"]["raw_text"]
        print(queryString.replace(" ", "$"))
        if(queryString != ""):
            if(len(text.split(queryString)) < 2):
                continue
            for i in text.split(queryString)[1].split(" "):
                if (i.strip() == ""):
                    continue
                if ('.' in i):
                    nextWordList.append(i)
                    break
                if (len(nextWordList) == 5):
                    break
                nextWordList.append(i)
            responseList.append({
                "id": hit["_id"],
                "raw_text": raw,
                "textString": text,
                "nextWords": nextWordList
            })
    return responseList
