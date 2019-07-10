import os

class Tracer:
    def __init__(self, label):
        self.label = label
        self._message = None
        self._state = None
    def log(self):
        if self._message:
            if self._state:
                print("%s: %s %s"%(self.label, self._state, self._message))
            else:
                print("%s: %s"%(self.label, self._message))
        self._state = None
        self._message = None
    def trace(self, message):
        self.log()
        self._message = message
    def check(self, message, result):
        self.log()
        self._state = 'PASS' if not result else 'FAIL'
        self._message = message
        self.log()
    def fail(self, obj):
        self._state = 'ERROR'
        self.log()
        print(obj)
    def done(self):
        self.log()
    def requestLog(self):
        return 'target/log/%s.request' % self.label
    def responseLog(self):
        return 'target/log/%s.response' % self.label
    def actualLog(self):
        return 'target/actual/%s.response' % self.label
    def expectSource(self):
        return 'test/expect/%s.response' % self.label
    def expectLog(self):
        return 'target/expect/%s.response' % self.label

class TerseTracer(Tracer):
    tick = {
        'PASS': '+',
        'FAIL': '-',
        'ERROR': 'X',
        None: '.'
    }
    def __init__(self, label):
        super().__init__(label)
        print('%s: '%label, end='', flush=True)
    def log(self):
        if self._message:
            print(TerseTracer.tick[self._state], end='', flush=True)
        self._state = None
        self._message = None
    def done(self):
        super().done()
        print('')

class CaseTracer:
    def __init__(self, name, verbose=False):
        self._name = name
        self._verbose = verbose
        os.makedirs('target/log/%s' % name)
        os.makedirs('target/actual/%s' % name)
        os.makedirs('target/expect/%s' % name)
        self._index = 0
    def case(self, name):
        self._index += 1
        label = '%s/%04d.%s' % (self._name, self._index, name)
        return Tracer(label) if self._verbose else TerseTracer(label)

