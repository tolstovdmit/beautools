def tracking_setattr(monkeypatch, history_list, cls, attr_name):
    original_setter = cls.__setattr__
    
    
    def tracking_setattr(self, name, value):
        if name == attr_name:
            history_list.append(value)
        original_setter(self, name, value)
    
    
    monkeypatch.setattr(cls, '__setattr__', tracking_setattr)


class AttrSpy:
    def __init__(self, initial_value=None):
        self.value = initial_value
        self.history = [initial_value]
    
    
    def __set__(self, instance, value):
        self.value = value
        self.history.append(value)
    
    
    def __get__(self, instance, owner):
        return self.value
