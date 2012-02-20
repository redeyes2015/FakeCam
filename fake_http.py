from bottle import route, request, run, response
import re
import sys

@route('/')
def hello():
	return 'Hello world!'

getparam_cache = {}
@route('/cgi-bin/admin/getparam.cgi', mothod='GET')
def getparam():
	response.content_type = 'text/plain'
	print(repr(request.query_string))
	q = request.query_string
	if request.query_string in getparam_cache:
		return getparam_cache[q]
	
	if request.query_string == '':
		ret = param_getter([])
	else:
		ret = param_getter(q.split('&'))
	getparam_cache[q] = ret
	return ret

def path_add(root, path, value):
	ptr = root
	for p in path[:-1]:
		if p not in ptr:
			ptr[p] = {}
		ptr = ptr[p]
	ptr[path[-1]] = value

def path_get(root, path):
	if len(path) == 0:
		return root
	ptr = root
	for p in path[:-1]:
		ptr = ptr[p]
	return ptr[path[-1]]

def path_check(root, path):
	if len(path) == 0:
		return True
	ptr = root
	for p in path:
		if p not in ptr:
			return False
		ptr = ptr[p]
	return True

def get_all_leaf(root):
	if not isinstance(root, dict):
		return [root]
	ret = []
	for k in root:
		if isinstance(root[k], dict):
			ret.extend( get_all_leaf(root[k]) )
		else:
			ret.append( root[k] )
			
	return ret
		
def param_parser(f):
	result = {}
	for line in f:
		m = re.match("[^=]+", line)
		if m is not None:
			path_add(result, m.group(0).split('_'), line.strip()) 
	return result

def param_getter(req_params):
	global params
	global param_idx
	if len(req_params) == 0:
		return '\r\n'.join(get_all_leaf(params))

	req_dup = sorted(filter(lambda a: len(a)>0, req_params))
	req_dup2 = tuple(req_dup)
	guessed_prefix = req_dup2[0]
	for req in req_dup2[1:]:
		if req.startswith(guessed_prefix):
			req_dup.remove(req)
		else:
			guessed_prefix = req
	ret = []
	for req in req_dup:
		if len(req) <= 0:
			continue
		path = req.split('_')
		if path_check(params, path):
			ret.extend(get_all_leaf(path_get(params, path)))
	ret.sort(cmp=lambda a,b: 
		cmp(param_idx.get(a, -1), param_idx.get(b, -1)))

	return '\r\n'.join(ret)
			
def gen_param_idx(f):
	i = 0
	ret = {}
	for line in f:
		l = line.strip()
		ret[l] = i
		i  = i+1
	return ret
	
		
with open(sys.argv[1]) as param_file:
	param_idx = gen_param_idx(param_file)
with open(sys.argv[1]) as param_file:
	params = param_parser(param_file)

run(host='172.16.4.83', port=8080)
