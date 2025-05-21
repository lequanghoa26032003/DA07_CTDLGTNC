class AVLNode:
    def __init__(self, keyword, doc_id):
        self.keyword = keyword
        self.doc_ids = set([doc_id])
        self.height = 1
        self.left = None
        self.right = None

class AVLTree:
    def __init__(self):
        self.root = None
    
    def height(self, node):
        if not node:
            return 0
        return node.height
    
    def balance_factor(self, node):
        if not node:
            return 0
        return self.height(node.left) - self.height(node.right)
    
    def update_height(self, node):
        if not node:
            return
        node.height = max(self.height(node.left), self.height(node.right)) + 1
    
    def right_rotate(self, y):
        x = y.left
        T2 = x.right
        
        x.right = y
        y.left = T2
        
        self.update_height(y)
        self.update_height(x)
        
        return x
    
    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        
        y.left = x
        x.right = T2
        
        self.update_height(x)
        self.update_height(y)
        
        return y                                                        
    
    def insert(self, node, keyword, doc_id):
        if not node:
            return AVLNode(keyword, doc_id)
        
        if keyword < node.keyword:
            node.left = self.insert(node.left, keyword, doc_id)
        elif keyword > node.keyword:
            node.right = self.insert(node.right, keyword, doc_id)
        else:
            node.doc_ids.add(doc_id)
            return node
        
        self.update_height(node)
        
        balance = self.balance_factor(node)
        
        if balance > 1 and keyword < node.left.keyword:
            return self.right_rotate(node)
        
        if balance < -1 and keyword > node.right.keyword:
            return self.left_rotate(node)
        
        if balance > 1 and keyword > node.left.keyword:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        
        if balance < -1 and keyword < node.right.keyword:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)
        
        return node
    
    def add_document(self, keywords, doc_id):
        for keyword in keywords:
            self.root = self.insert(self.root, keyword, doc_id)

    def _search_partial(self, partial_keyword):
        results = set()
        self._search_partial_recursive(self.root, partial_keyword, results)
        return results

    def _search_partial_recursive(self, node, partial, results):
        if not node:
            return
        if node.keyword.startswith(partial):
            results.update(node.doc_ids)
        if partial < node.keyword:
            self._search_partial_recursive(node.left, partial, results)
        elif partial > node.keyword:
            self._search_partial_recursive(node.right, partial, results)

    def delete_document(self, doc_id):
        self._delete_document_recursive(self.root, doc_id)

    def _delete_document_recursive(self, node, doc_id):
        if not node:
            return
        if doc_id in node.doc_ids:
            node.doc_ids.remove(doc_id)
        self._delete_document_recursive(node.left, doc_id)
        self._delete_document_recursive(node.right, doc_id)

    def search(self, keywords):

        if not keywords:
            return set()
        result = None
        for keyword in keywords:
            docs = self._search_partial(keyword)
            if result is None:
                result = docs
            else:
                result = result.intersection(docs)
            if not result:
                return set()
        return result if result else set()

