import json
from dataType import DataType
from chainGraph import ChainGraph
from graphNode import GraphNode
from Utilities.guidMapper import GuidMapper
import Data.matchFunctions as matchFunctions


def graphNodeFromJSON(inputJSON, guidMapper=GuidMapper()):
    from Utilities.fileManager import FileManager
    inputObject = json.loads(inputJSON)
    file_manager = FileManager()
    if type(inputObject["dataType"]) is str:
        dataType = file_manager.load_data_type(inputObject["dataType"])
    else:
        node_json = json.dumps(inputObject["dataType"])
        dataType = file_manager.load_data_type(node_json)
    dataClasses = {}
    for key in inputObject["dataClasses"].keys():
        if not inputObject["dataClasses"][key]:
            dataClasses[key] = None
        elif type(inputObject["dataClasses"][key]) in [str]:
            dataClasses[key] = file_manager.load_data_class(inputObject["dataClasses"][key])
        else:
            dataClasses[key] = file_manager.load_data_class(json.dumps(inputObject["dataClasses"][key]))
    graphNode = GraphNode(dataType)
    graphNode.guid = guidMapper.get(inputObject["guid"])
    graphNode.nexts = []
    graphNode.dataClasses = dataClasses
    return graphNode


def graph_nodes_from_cursor(cursor):
    """
    Given a flowGraph cursor, return a list of graphNodes, one for each of the parsedData pieces the cursor found

    :param cursor:
    :return:
    """
    dataTypeName = cursor.graph.name
    dataClasses = {"dataIndex": None}
    matchFunction = getattr(matchFunctions, "matchFunction")
    dataType = DataType(dataTypeName, dataClasses, matchFunction)
    graphNodes = []
    parsedData = cursor.extracted_data
    for pd in parsedData:
        new_pd = ChainGraph(pd, dataTypeName)
        graphNodes.append(GraphNode(dataType, new_pd))
    return graphNodes


def graphFromJSON(inputJSON, guidMapper=GuidMapper()):
    inputObject = json.loads(inputJSON)
    name = inputObject["name"]
    nodes = []
    nodeGuids = {}
    for node in inputObject["nodes"]:
        new_node = graphNodeFromJSON(json.dumps(node), guidMapper=guidMapper)
        nodeGuids[new_node.guid] = new_node
        nodes.append(new_node)
    for node in inputObject["nodes"]:
        current_node = nodeGuids[guidMapper.get(node["guid"])]
        new_nexts = []
        for next_id in node["nexts"]:
            if next_id is None:
                new_nexts.append(None)
            else:
                new_nexts.append(nodeGuids[guidMapper.get(next_id)])
        current_node.nexts = new_nexts
    return nodes, name


def chainGraphFromJSON(inputJSON):
    inputObject = json.loads(inputJSON)
    nodes, name = graphFromJSON(json.dumps(inputObject["graph"]))
    chainGraph = ChainGraph(nodes, name)
    return chainGraph


def chainGraphFromString(inputString):
    from Utilities.fileManager import FileManager
    testDataGraphNodes = []
    previousNode = None
    file_manager = FileManager()
    dataTypes = [file_manager.load_data_type("letter.json"), file_manager.load_data_type("number.json"), file_manager.load_data_type("punctuation.json"), file_manager.load_data_type("whiteSpace.json")]
    for c in inputString:
        cDataTypeName = "char"
        for dataType in dataTypes:
            if dataType.matches(c):
                cDataTypeName = dataType.dataTypeName
        cDataType = file_manager.load_data_type(cDataTypeName + ".json")
        cGraphNode = GraphNode(cDataType, c)
        testDataGraphNodes.append(cGraphNode)
        if previousNode:
            previousNode.nexts.append(cGraphNode)
        previousNode = cGraphNode
    testDataGraphNodes[-1].nexts.append(None)
    return ChainGraph(testDataGraphNodes, "character_stream")


def chainGraphLayerFromString(inputString):
    from chainGraphLayer import ChainGraphLayer
    from Utilities.fileManager import FileManager
    file_manager = FileManager()
    chainGraphLayer = ChainGraphLayer(None)
    chainGraphLayer.chainGraph = chainGraphFromString(inputString)
    chainGraphLayer.classify([file_manager.load_data_type("letter.json")])
    return chainGraphLayer
