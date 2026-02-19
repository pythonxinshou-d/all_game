import json
import os


class TreeNode:
    def __init__(self, root_value):
        self.value = root_value
        self.left = None
        self.right = None


def Check(file_path: str, Correct_mistakes_content):
    User_information = Correct_mistakes_content  # 初始化默认值
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                User_information = (
                    json.loads(content) if content else Correct_mistakes_content
                )
        else:
            User_information = Correct_mistakes_content
    except json.JSONDecodeError:
        print("用户数据文件格式损坏，已自动重置！")
        User_information = Correct_mistakes_content
    return User_information


file_path = "tree.txt"
tree = Check(file_path, TreeNode)
parant = tree
times = 0
root = parant
for i in range(100):
    if i == 0:
        tree.value = TreeNode(i)
    elif i % 2 == 1:
        times = i
        while times == 0:
            if times == 0:
                root = TreeNode(i)
                root = parant
            elif i % 2 == 1:
                root = root.left
            else:
                root = root.right
            times -= 1
    else:
        times = i
        while times == 0:
            if times == 0:
                root = TreeNode(i)
                root = parant
            elif i % 2 == 1:
                root = root.left
            else:
                root = root.right
            times -= 1
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(tree, f, ensure_ascii=False)


# ... existing code ...
class TreeNode:
    def __init__(self, value):
        """初始化树节点。

        Args:
            value: 节点存储的值
        """
        self.value = value
        self.left = None
        self.right = None


# ... existing code ...
