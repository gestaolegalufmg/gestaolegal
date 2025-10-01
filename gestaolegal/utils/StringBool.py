from typing_extensions import override

class StringBool():
    value: bool

    def __init__(self, value: str):
        self.value = value == "true"
    
    def __bool__(self):
        return self.value
    
    @override
    def __str__(self):
        return str(self.value)