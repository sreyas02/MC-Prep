class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.head = Node(None, None)
        self.tail = Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self._move_to_head(node)
            return node.value
        return None

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_head(node)
            if len(self.cache) > self.capacity:
                removed_node = self._remove_tail()
                del self.cache[removed_node.key]

    def _add_to_head(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_head(self, node):
        self._remove_node(node)
        self._add_to_head(node)

    def _remove_tail(self):
        node = self.tail.prev
        self._remove_node(node)
        return node
    

class LRUCacheDemo:
    @staticmethod
    def run():
        cache = LRUCache(3)

        cache.put(1, "Value 1")
        cache.put(2, "Value 2")
        cache.put(3, "Value 3")

        print(cache.get(1))  # Output: Value 1
        print(cache.get(2))  # Output: Value 2

        cache.put(4, "Value 4")

        print(cache.get(3))  # Output: None
        print(cache.get(4))  # Output: Value 4

        cache.put(2, "Updated Value 2")

        print(cache.get(1))  # Output: Value 1
        print(cache.get(2))  # Output: Updated Value 2

if __name__ == "__main__":
    LRUCacheDemo.run()