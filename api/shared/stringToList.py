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

    def __init__(self, jove:str=None) -> None:
        self.data = jove
    
    def toList(self):
        # in case not string is given for initialization
        if self.data == None:
            return None

        #replacing a single quote " ' " into double quote "
        try:
            double_quoted = self.data.replace("'", "\"")
            toJson = json.loads(double_quoted)
            return toJson # a list
        except json.decoder.JSONDecodeError:
            return None
