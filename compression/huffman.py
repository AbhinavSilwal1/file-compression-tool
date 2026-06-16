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


def generate_huffman_codes(root):
    codes = {}

    def traverse(node, current_code):
        if node is None:
            return

        if node.character is not None:
            codes[node.character] = current_code
            return

        traverse(node.left, current_code + "0")
        traverse(node.right, current_code + "1")

    traverse(root, "")

    return codes


def encode_text(text, huffman_codes):
    encoded_text = ""

    for character in text:
        encoded_text += huffman_codes[character]

    return encoded_text


def calculate_compression_statistics(text, encoded_text):
    original_size = len(text) * 8
    encoded_size = len(encoded_text)
    compression_reduction = ((original_size - encoded_size) / original_size) * 100

    return {
        "original_size": original_size,
        "encoded_size": encoded_size,
        "compression_reduction": compression_reduction
    }


def binary_string_to_bytes(binary_string):
    padding = 8 - (len(binary_string) % 8)

    if padding != 8:
        binary_string += "0" * padding

    byte_array = bytearray()

    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i + 8]
        byte_array.append(int(byte, 2))

    return bytes(byte_array)