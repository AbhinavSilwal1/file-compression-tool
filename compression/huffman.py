import heapq


class HuffmanNode:
    def __init__(self, character, frequency):
        self.character = character
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.frequency < other.frequency


def build_frequency_table(text):
    frequency = {}

    for character in text:
        if character in frequency:
            frequency[character] += 1
        else:
            frequency[character] = 1

    return frequency


def build_huffman_tree(frequency_table):
    heap = []

    for character, frequency in frequency_table.items():
        node = HuffmanNode(character, frequency)
        heapq.heappush(heap, node)

    while len(heap) > 1:
        left_node = heapq.heappop(heap)
        right_node = heapq.heappop(heap)

        merged_frequency = left_node.frequency + right_node.frequency

        parent_node = HuffmanNode(None, merged_frequency)

        parent_node.left = left_node
        parent_node.right = right_node

        heapq.heappush(heap, parent_node)

    return heap[0]