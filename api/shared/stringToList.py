"""I have intend of converting a string of list of dictionary into a native list of dictionary.
SCENARIO:

jove = " [{'date': '2025-04', 'qte': 4, 'code_operation': '12dxx9'}, {'date': '2024-08', 'qte': 7, 'code_operation': '23dd'}] "

#to be into

Jove = [
    {'date': '2025-04', 'qte': 4, 'code_operation': '12dxx9'},
    {'date': '2024-08', 'qte': 7, 'code_operation': '23dd'}
]
"""

import json

class StringToList:
    """Have to take the string and convert them into list"""

    def __init__(self, jove:str) -> None:
        self.data = jove
    
    def toList(self):
        #replacing a single quote " ' " into double quote "
        double_quoted = self.data.replace("'", "\"")
        toJson = json.loads(double_quoted)
        print(f"THe result : {(double_quoted)}")
        print(f"And the its Json: {toJson}: of type: {type(toJson)}")
        return toJson # a list
