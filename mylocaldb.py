import os
import json

class MyLocalKVDb():
    def __init__(self, path='temp.db'):
        self.path = path
        self.kvdb = {}
        self._load()
    

    def _load(self):
        if os.path.exists(self.path):
            self.kvdb = json.load(open(self.path))
        else:
            f = open(self.path, 'w')
            f.write('{}')
            f.close()
    
    def exists(self, key):
        if key in self.kvdb:
            return True
        return False
    
    def put(self, key, value):
        self.kvdb[key] = value
        json.dump(self.kvdb, open(self.path, 'w'))


def main():
    kv = MyLocalKVDb()

    # kv.put('hello', 'ok')
    
    if kv.exists('hello'):
        print('=========')
    else:
        print('xxxx')

    pass


if __name__ == '__main__':
    main()
    