import json

def json_tree_search(root, key):
    for child_key in root:
        if child_key == key:
            return root[child_key]
        # --- DEBUG: warning, list may be a tuple ---
        if not (isinstance(root[child_key], dict) or isinstance(root[child_key], list)): 
            # child is a leaf
            return None, False
        else:
            # child is an internal node
            node = json_tree_search(root[child_key], key)
            if node == None:
                # this node does not contain what we are looking for
                pass
            else:
                return node


with open('../test_data/welland/Welland_business_directory.json', encoding='latin-1') as f:
    jsondata = json.load(f)

subtree = json_tree_search(jsondata, "Welland_Business_Directory")
print(subtree)
