import os, sys, shutil, traceback
import re
import json
import yaml # pip install pyyaml
from deepyaml import loadYaml
from jsonschema import validate # pip install jsonschema
from http.client import HTTPSConnection
from tracer import CaseTracer
from render import render, deepRender

httpVersion = {
    10: 'HTTP/1.0',
    11: 'HTTP/1.1'
}

def val(obj, *keys):
    result = obj
    for key in keys:
        if key not in result:
            return None
        result = result[key]
    return result

def basename(path):
    return os.fsdecode(os.path.splitext(os.path.basename(os.fsencode(path)))[0])

def makeRequest(template, context):
    return {
        'method': template['method'],
        'target': render(template['target'], context),
        'headers': {k.lower():render(v, context) for k, v in template['headers'].items()},
        'body': deepRender(template['body'], context) if 'body' in template else None
    }

def logYaml(path, message):
    with open(path, 'w') as file:
        yaml.dump(message, file, default_flow_style=False)

def valid(message, schema):
    if schema and message['body']:
        try:
            validate(message['body'], schema)
        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
            return "schema did not match body"
    return None

def sendRequest(request):
    conn = HTTPSConnection(request['headers']['host'])
    conn.request(
        request['method'], 
        request['target'], 
        json.dumps(request['body']).encode(), 
        request['headers'])
    response = conn.getresponse()
    body = response.read().decode()
    return {
        'protocol': httpVersion[response.version],
        'status': response.status,
        'reason': response.reason,
        'headers': {k.lower():v for k, v in dict(response.headers).items()},
        'body': json.loads(body) if body else None
    }

def compare(actual, expectPath):
    if os.path.exists(expectPath):
        expect = loadYaml(expectPath)
        if expect != actual:
            return "Did not match"
    return None

def normalize(response, template):
    if not template:
        return response
    if isinstance(response, list):
        return [normalize(v, template) for v in response]
    if isinstance(response, dict):
        return {k:normalize(v, template[k] if k in template else None) for k, v in response.items()}
    if isinstance(response, str):
        if re.fullmatch(template[1:-1], response):
            return template
        else:
            raise Exception("ERROR '%s' failed to match %s"%(response, template))
    return response

def lowerHeaders(response):
    if 'headers' in response:
        response['headers'] = {k.lower():v for k, v in response['headers'].items()}
    return response

def execExchange(tracer, exchange, context):
    try:
        tracer.trace('create request')
        request = makeRequest(val(exchange,'request'), context)
        tracer.trace('log request')
        logYaml(tracer.requestLog(), request)
        tracer.trace('validate request')
        result = valid(request, val(exchange,'request','schema'))
        tracer.check('request valid', result)

        tracer.trace('send request')
        response = sendRequest(request)
        tracer.trace('log response')
        logYaml(tracer.responseLog(), response)
        tracer.trace('validate response')
        result = valid(response, val(exchange,'response','schema'))
        tracer.check('response valid', result)

        tracer.trace('normalize response')
        actual = normalize(response, lowerHeaders(val(exchange,'response')))
        tracer.trace('log actual')
        logYaml(tracer.actualLog(), actual)
        tracer.trace('load expected')
        expect = loadYaml(tracer.expectSource())
        tracer.trace('log expect')
        logYaml(tracer.expectLog(), expect)
        tracer.trace('compare actual to expected')
        result = compare(actual, tracer.expectLog())
        tracer.check('actual match', result)

        return {
            'request': request,
            'response': response
        }
    except Exception as e:
        tracer.fail(e)
        return {}
    finally:
        tracer.done()

def execCase(tracer, case, context):
    for name, exchange in case.items():
        context[name] = execExchange(tracer.case(name), exchange, context)

def execSuite(suite, env, verbose):
    for name, case in suite.items():
        execCase(CaseTracer(name, verbose), case, {'env': env, 'os': os.environ})

context = loadYaml(sys.argv[1])
execSuite(context['suite'], context['env'], context['verbose'])
