import requests

BASE_URL = "http://localhost:8080/api/v1"

def getEndpoint(endpoint, params=None):
    URL = BASE_URL + endpoint
    r = requests.get(url=URL, params=params)
    return r.json()

def getAllJoularDataForMethodsHavingAtLeast25Values(sha=""):
    allResults = []
    endpoint = "/joular/aggregates"
    if (sha != ""):
        endpoint += "/by-commit/" + sha
    result = getEndpoint(endpoint)
    allResults.extend(result["content"])
    while(not result["last"]):
        page = result["number"] + 1
        result = getEndpoint(endpoint, {"page": page})
        allResults.extend(result["content"])
    return allResults

def getSeveralCkDataForOneMethod(commitSha: str, className: str, methodName: str, ckMetrics: list[str]):
    endpoint = "/ck-entities/by-commit-and-ast-elem/" + commitSha
    params = {
        "className": className,
        "methodName": methodName,
        "names": ckMetrics
    }
    return getEndpoint(endpoint=endpoint, params=params)