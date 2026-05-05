class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

def make_tree(depth):
    if depth == 0:
        return Node(0)
    node = Node(depth)
    node.left = make_tree(depth - 1)
    node.right = make_tree(depth - 1)
    return node

def tree_sum(node):
    if node is None:
        return 0
    return node.value + tree_sum(node.left) + tree_sum(node.right)

root = make_tree(12)
print(tree_sum(root))
