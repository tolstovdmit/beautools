import yaml
import yamlordereddictloader



class YamlFile:
    
    def __init__(self, path):
        self.filepath = path
        self.d = None
    
    
    def read(self):
        with open(self.filepath, 'r', encoding="utf-8") as file:
            self.d = yaml.load(file, yamlordereddictloader.Loader)
        # new_dict = OrderedDict(list({'id': i}.items()) + list(q.items()))
    
    
    def save(self):
        with open(self.filepath, 'w', encoding="utf-8") as file:
            yaml.dump(self.d, file, yamlordereddictloader.Dumper, allow_unicode=True, sort_keys=False)

