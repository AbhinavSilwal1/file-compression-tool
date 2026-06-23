import heapq
import json


class HuffmanNode:
    def __init__(self, character, frequency):
        self.character = character
        self.frequency = frequency
        self.left = None
        self.right = None
        self.order = 0

    def __lt__(self, other):
        if self.frequency == other.frequency:
            return self.order < other.order
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
    order_counter = 0

    for character, frequency in frequency_table.items():
        node = HuffmanNode(character, frequency)
        node.order = order_counter
        order_counter += 1
        heapq.heappush(heap, node)

    while len(heap) > 1:
        left_node = heapq.heappop(heap)
        right_node = heapq.heappop(heap)

        merged_frequency = left_node.frequency + right_node.frequency

        parent_node = HuffmanNode(None, merged_frequency)
        parent_node.order = order_counter
        order_counter += 1

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

            if current_code == "":
                codes[node.character] = "0"
            else:
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
    space_saved = original_size - encoded_size
    compression_ratio = (original_size / encoded_size)

    return {
        "original_size": original_size,
        "encoded_size": encoded_size,
        "compression_reduction": compression_reduction,
        "space_saved": space_saved,
        "compression_ratio": compression_ratio
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


def decode_text(encoded_text, huffman_tree):
    decoded_text = ""

    if (huffman_tree.left is None and huffman_tree.right is None):
        return huffman_tree.character * len(encoded_text)

    current_node = huffman_tree

    for bit in encoded_text:
        if bit == "0":
            current_node = current_node.left
        else:
            current_node = current_node.right

        if current_node.character is not None:
            decoded_text += current_node.character
            current_node = huffman_tree

    return decoded_text


def build_tree_from_frequency(frequency_table):
    return build_huffman_tree(frequency_table)


def build_tree_from_codes(huffman_codes):
    root = HuffmanNode(None, 0)

    for character, code in huffman_codes.items():
        current_node = root

        for bit in code:
            if bit == "0":
                if current_node.left is None:
                    current_node.left = HuffmanNode(None, 0)

                current_node = current_node.left

            else:
                if current_node.right is None:
                    current_node.right = HuffmanNode(None, 0)

                current_node = current_node.right

        current_node.character = character

    return root


def parse_huff_file(content):
    lines = content.split("\n")

    if lines[0] != "HUFF1":
        raise ValueError("Unsupported file format")

    body = "\n".join(lines[1:])
    header_str, encoded_text = body.split("\n---\n")

    header = json.loads(header_str.strip())

    frequency_table = header["freq"]
    huffman_codes = header["codes"]

    return frequency_table, huffman_codes, encoded_text, header