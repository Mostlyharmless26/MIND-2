
def pretty_chainGraphLayer(chainGraphLayer):
    rv = ""
    for n in chainGraphLayer.chainGraph.graph.nodes:
        rv += str(n.dataNode.dataType.dataTypeName) + ": "
        for key in n.dataClasses.keys():
            if n.dataClasses[key]:
                rv += " " + key + " : " + n.dataClasses[key].dataClassString
            else:
                rv += " " + key + " : None"
        rv += "\n"
    return rv
