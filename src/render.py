from string import Template

class FlatDict:
    def __init__(self, obj):
        self._obj = obj
    def __getitem__(self, key):
        o = self._obj
        hold = None
        for k in key.split('.'):
            if hold:
                hold = hold + '.' + k
            else:
                try:
                    o = o[int(k)]
                    hold = None
                    continue
                except:
                    hold = k
            if hold in o:
                o = o[hold]
                hold = None
        if not hold:
            print('Warning: could not resolve %s'%(hold))
        return o

class DotTemplate(Template):
    braceidpattern = '(?a:[_a-z][_a-z0-9.]*)'
    def __init__(self, template):
        super().__init__(template)

def render(template, context):
    try:
        return DotTemplate(template).substitute(FlatDict(context))
    except:
        print(template)
        raise

def deepRender(template, context):
    if isinstance(template, list):
        return [deepRender(v, context) for v in template]
    if isinstance(template, dict):
        return {k:deepRender(v, context) for k, v in template.items()}
    if isinstance(template, str):
        return render(template, context)
    return template
