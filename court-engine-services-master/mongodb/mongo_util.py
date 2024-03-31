from fileinput import filename
import pymongo
import gridfs

conn_str = "mongodb+srv://akil:akil@court-engine-atlas.lavyisw.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)


async def uploadToMongo(bytes, id):
    client = pymongo.MongoClient(conn_str)
    db = client['court-engine-db']
    fs = gridfs.GridFS(db)

    fid = fs.put(bytes)
    print(type(fid))
    print(fid)
    print(id)
    collection = db["judgements"]
    print("IDDDDDDDDDDD:")
    collection.insert_one({"file_id": fid, "doc_id": str(id)})

    # print(fs.get(fid).read())


def getDocument(id):
    client = pymongo.MongoClient(conn_str)
    db = client['court-engine-db']
    fs = gridfs.GridFS(db)

    collection = db["judgements"]
    result = collection.find_one({"doc_id": id})
    print(result)
    file = fs.get(result["file_id"])
    return file


def searchSections(sectionList: list):
    client = pymongo.MongoClient(conn_str)
    db = client['court-engine-db']
    collection = db["law"]

    crpc = collection.find_one({"category": "crpc"})
    ipc = collection.find_one({"category": "ipc"})
    cpc = collection.find_one({"category": "cpc"})
    finalMap = {

    }
    for section in sectionList:
        number = section.split("-")[0]
        law = section.split("-")[1]
        filtered = []
        print(law)
        if law == "cpc":
            for obj in cpc["law"]:
                if (str(obj["section"]) == str(number)):
                    filtered.append(obj)
                    break

        if law == "crpc":

            for obj in crpc["law"]:
                if (str(obj["section"]) == str(number)):
                    filtered.append(obj)
                    break

        if law == "ipc":
            for obj in ipc["law"]:
                if (str(obj["Section"]) == str(number)):
                    filtered.append(obj)
                    break
        print(filtered)
        if (filtered != []):
            finalMap[section] = filtered[0]
    return finalMap
