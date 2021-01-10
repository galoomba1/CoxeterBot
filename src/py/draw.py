from PIL import Image, ImageDraw, ImageFont
from node import Node, Graph
from cdError import CDError
import math

# Constants:
NODE_RADIUS = 12
NODE_BORDER_WIDTH = 4

RING_RADIUS = 24
RING_WIDTH = 4

NODE_SPACING = 90
COMPONENT_SPACING = 90

LINE_WIDTH = 8
TEXT_DISTANCE = 20

EDGE_FONT_SIZE = 24
NODE_FONT_SIZE = 18
HOLOSNUB_FONT_SIZE = 36

FONT_NAME = "Lora-regular"

EDGE_FONT = ImageFont.truetype(f"../ttf/{FONT_NAME}.ttf", EDGE_FONT_SIZE, layout_engine = ImageFont.LAYOUT_BASIC)
NODE_FONT = ImageFont.truetype(f"../ttf/{FONT_NAME}.ttf", NODE_FONT_SIZE, layout_engine = ImageFont.LAYOUT_BASIC)
HOLOSNUB_FONT = ImageFont.truetype(f"../ttf/{FONT_NAME}.ttf", HOLOSNUB_FONT_SIZE, layout_engine = ImageFont.LAYOUT_BASIC)

FONT_OUTLINE = 2

PADDING = 60

# Draws a graph.
class Draw:
    # Class constructor.
    def __init__(self, graph):
        # Variables to see where the next node goes.
        # Provisional, probably.
        self.x, self.y = 0, 0

        # The elements of the graph.
        self.nodes, self.edges = [], []

        # The bounding box of the graph.
        self.minX, self.minY, self.maxX, self.maxY = math.inf, math.inf, -math.inf, -math.inf

        for component in graph.components():
            self.add(component)

    # Adds a new component to the diagram.
    # Currently, just puts everything in a straight line.
    # TODO: make this draw the trees prettily.
    def add(self, component):
        if self.isStraight(component):
            drawingMode = 'line'
        else:
            drawingMode = 'polygon'

        if drawingMode == 'polygon':
            n = len(component)
            radius = NODE_SPACING / (2 * math.sin(math.pi / n))
            self.x += radius

            angle = math.pi / 2 + math.pi / n
            for node in component:
                self.addNode(node, (
                    self.x + radius * math.cos(angle),
                    self.y + radius * math.sin(angle)
                ), drawingMode)
                angle += 2 * math.pi / n

            self.x += radius

        elif drawingMode == 'line':
            self.x -= NODE_SPACING
            for node in component:
                self.x += NODE_SPACING
                self.addNode(node, (self.x, self.y), drawingMode)

        else:
            self.error("Drawing mode not recognized.")

        self.x += COMPONENT_SPACING

    # Adds a node in a particular position.
    def addNode(self, node, coords, drawingMode):
        # Adds the node.
        newNode = {
            "value": node.value,
            "xy": (coords[0], coords[1])
        }
        self.updateBoundingBox(coords)
        self.nodes.append(newNode)

        # Adds edges.
        i = 0
        for neighbor in node.neighbors:
            # Guarantees no duplicates.
            if neighbor.ID < node.ID:
                self.edges.append({
                    0: neighbor.ID,
                    1: node.ID,
                    "label": node.edgeLabels[i],
                    "drawingMode": drawingMode
                })

            i += 1

    # A connected graph is a line graph iff every vertex has degree ≤ 2,
    # and at least one vertex has degree 1.
    def isStraight(self, component):
        if len(component) < 3:
            return True

        isCycle = True

        for node in component:
            degree = node.degree()

            if degree > 2:
                return False
            elif degree == 1:
                isCycle = False

        return not isCycle

    # Transforms node coordinates to image coordinates.
    def transformCoords(self, coords):
        return (coords[0] - self.minX + PADDING, coords[1] - self.minY + PADDING)

    # Updates the bounding box of the nodes.
    def updateBoundingBox(self, coords):
        x, y = coords

        self.minX = min(self.minX, x)
        self.maxX = max(self.maxX, x)
        self.minY = min(self.minY, y)
        self.maxY = max(self.maxY, y)

    # Gets the size of the bounding box.
    def size(self):
        return (
            round(self.maxX - self.minX + 2 * PADDING),
            round(self.maxY - self.minY + 2 * PADDING)
        )

    # Draws the graph.
    def draw(self):
        self.image = Image.new('RGB', size = self.size(), color = 'white')
        self.draw = ImageDraw.Draw(self.image)

        # Draws the edges.
        for edge in self.edges:
            node0, node1, label = self.nodes[edge[0]], self.nodes[edge[1]], edge['label']

            # Edge coordinates.
            edgeXy = (
                self.transformCoords(node0['xy']),
                self.transformCoords(node1['xy']),
            )

            # Text coordinates.
            textXy = list(map(lambda a, b: (a + b) / 2, edgeXy[0], edgeXy[1]))
            if edge['drawingMode'] == 'line':
                textXy[1] += TEXT_DISTANCE

            # Draws edge.
            self.__drawEdge(edgeXy, dotted = (label == "Ø"))

            # Draws label.
            if label != "3" and label != "Ø":
                self.__drawText(textXy, label, textType = 'edge')

        # Draws each node.
        for node in self.nodes:
            value = node['value']
            xy = self.transformCoords(node['xy'])

            # Chooses the fill color.
            if value == 's' or value == '+':
                nodeFill = 'white'
                radius = RING_RADIUS
            else:
                nodeFill = 'black'
                radius = NODE_RADIUS

            # Draws the node.
            self.__drawCircle(xy = xy, radius = radius, fill = nodeFill)

            # Draws the ring.
            if value != 'o' and value != 's':
                self.__drawRing(xy = xy, radius = RING_RADIUS, fill = 'black')

                # Draws the mark.
                if value != 'x':
                    if value == '+':
                        textType = 'holosnub'
                    else:
                        textType = 'node'

                    self.__drawText(xy = xy, text = value, textType = textType)

        return self.image

    # Draws a circle on the image.
    def __drawCircle(self, xy, radius, fill):
        x, y = xy
        self.draw.ellipse(
            xy = (x - radius, y - radius, x + radius, y + radius),
            fill = fill,
            outline = 'black',
            width = NODE_BORDER_WIDTH
        )

    # Draws a ring on the image.
    def __drawRing(self, xy, radius, fill):
        x, y = xy
        self.draw.arc(
            xy = (x - radius, y - radius, x + radius, y + radius),
            start = 0,
            end = 360,
            fill = 'black',
            width = RING_WIDTH
        )

    # Draws a line segment on the image.
    def __drawEdge(self, xy, dotted):
        if not dotted:
            self.draw.line(
                xy = xy,
                width = LINE_WIDTH,
                fill = 'black'
            )
        else:
            dashes = 5
            delta = tuple(map(lambda x, y: (y - x) / (2 * dashes - 1), xy[0], xy[1]))
            xy = list(xy)
            xy[1] = tuple(map(lambda x, y: x + y, xy[0], delta))

            for i in range(dashes):
                self.draw.line(
                    xy = tuple(xy),
                    width = LINE_WIDTH,
                    fill = 'black'
                )

                xy[0] = tuple(map(lambda x, y: x + 2 * y, xy[0], delta))
                xy[1] = tuple(map(lambda x, y: x + 2 * y, xy[1], delta))


    # Draws text with a white border at some particular location.
    def __drawText(self, xy, text, textType):
        xy = list(map(float, xy))

        # Configures text attributes.
        if textType == 'node':
            font = NODE_FONT
            foreColor = 'white'
            backColor = 'black'

            # Offset, seems necessary for some reason.
            xy = list(map(lambda a, b: a + b, xy, (1, -1)))
        elif textType == 'holosnub':
            font = HOLOSNUB_FONT
            foreColor = 'black'
            backColor = 'white'

            # Offset, seems necessary for some reason.
            xy = list(map(lambda a, b: a + b, xy, (0.5, -3)))
        elif textType == 'edge':
            font = EDGE_FONT
            foreColor = 'black'
            backColor = 'white'
        else:
            self.error("Text type not recognized.")

        # Positions text correctly.
        textSize = self.draw.textsize(text = text, font = font)
        xy = list(map(lambda a, b: round(a - b / 2), xy, textSize))

        # Draws border.
        self.draw.text(xy = (xy[0] - FONT_OUTLINE, xy[1]), text = text, fill = backColor, font = font)
        self.draw.text(xy = (xy[0] + FONT_OUTLINE, xy[1]), text = text, fill = backColor, font = font)
        self.draw.text(xy = (xy[0], xy[1] - FONT_OUTLINE), text = text, fill = backColor, font = font)
        self.draw.text(xy = (xy[0], xy[1] + FONT_OUTLINE), text = text, fill = backColor, font = font)

        # Overlays text.
        self.draw.text(xy = xy, text = text, fill = foreColor, font = font)

    # Shows the graph.
    def show(self):
        self.draw().show()

    # Saves the graph.
    def save(self, *args):
        self.draw().save(*args)

    def error(self, text):
        raise CDError(f"Graph drawing failed. {text}")