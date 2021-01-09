import re

# Nodes in a CD.
class Node:
    # Class constructor.
    def __init__(self, value):
        self.value = value
        self.neighbors = []
        self.edgelabels = []
        self.visited = False

    # Links two nodes together.
    def linkTo(self, node, label):
        self.neighbors.append(node)
        self.edgelabels.append(label)
        node.neighbors.append(self)
        node.edgelabels.append(label)

    # Gets the connected component of a node.
    def component(self):
        Node.__comp = []
        self.__component()
        
        return Node.__comp

    # Auxiliary function for component.
    def __component(self):
        self.visited = True
        Node.__comp.append(self)
        for node in self.neighbors:
            if not node.visited:
                node.__component()

# The CD as a graph.
class Graph:
    # Class constructor.
    def __init__(self, array):
        self.array = array
        self.idx = 0
        
    # Class iterator.
    def __iter__(self):
        self.idx = 0
        return self
        
    # Next iterator method.
    def __next__(self):
        if self.idx < len(self.array):
            x = self.array[self.idx]
            self.idx += 1
            return x

        raise StopIteration

    # Gets the connected components of a graph.
    def components(self):
        components = []

        for node in self:
            if not node.visited:
                components.append(node.component())
        
        return components

# Converts a textual Coxeter Diagram to a graph.
def CDToGraph(cd):
    nodes = []
    index = 0
    readnum = False
    memnum = ""
    possvalues = "[oxqfvhkuwFes]"
    cd = cd.translate({45: None})
    
    asterisk = False
    
    test = 0
    
    # Reads through string.
    for i in range(len(cd)):
        # Spaces
        if cd[i] == " ":
            continue
        
        # Asterisk
        elif cd[i] == "*":
            asterisk = True
            
        # Virtual nodes
        elif asterisk:
            if ord(cd[i]) - 97 > 25 or ord(cd[i]) - 97 < 0:
                raise ValueError("One of those virtual nodes is not a lowercase letter")
                
            if cd[i - 2].isdigit():
                nodes[index - 1].linkTo(nodes[ord(cd[i]) - 97], memnum)
                
            if cd[i + 1].isdigit() or re.findall():
                # Start wait to read node
                readnum = True
                
            asterisk = False
        
        # Edge Values
        elif cd[i].isdigit() or cd[i] == "/":
            if not readnum:                
                memnum = ""
                j = i
                
                while cd[j].isdigit() or cd[j] == "/":
                    memnum += cd[j]
                    j += 1
                
                readnum = True
            
        # Node Values
        elif re.findall(possvalues, cd[i]):
            newnode = Node(cd[i])
            nodes.append(newnode)
            
            if readnum:
                if re.findall(possvalues, cd[i - len(memnum) - 1]):
                    nodes[index - 1].linkTo(nodes[index], memnum)
                else:
                    nodes[ord(cd[i - (len(memnum) + 1)]) - 97].linkTo(nodes[index], memnum)
            readnum = False
            index += 1
        
        # No Matches
        else:
            raise ValueError("I don't know one of these symbols! Failed at index " + str(test) + ".")
            
        test += 1
        
    return Graph(nodes)
