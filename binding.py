import argparse
import datetime
from os import name, sendfile
import toml
import re


def extract_signature(module, func, body):

    REGEX_FUNC_RETUREN = '^ *[a-z,A-Z,_]+[\w,_]+ +\*?'
    REGEX_FUNCNAME = ' +[a-z]+[\w,_,]\('
    REGEX_FUNCPARAM = '\([a-z,A-Z,0-9,_, ,\*]*\,*\)'

    signature = dict()

    signature['module'] = module
    signature['method'] = func

    retval = re.search(REGEX_FUNC_RETUREN, body)

    if retval == None:
        raise RuntimeError(
            'No return value found for {module}.{function}({rawbody})'.format(module=module, function=func, body=body))
    signature['return'] = retval[0].strip()

    retval = re.search(REGEX_FUNCNAME, body)
    if retval == None:
        raise RuntimeError(
            'No function name found for {module}.{function}({rawbody})'.format(module=module, function=func, rawbody=body))

    signature['function'] = retval[0].split('(')[0].strip()

    retval = re.search(REGEX_FUNCPARAM, body)

    if retval == None:
        raise RuntimeError('No function param found for {module}.{function}({rawbody})'.format(
            module=module, function=func, rawbody=body))

    # remove '(' & ')' , split by ','
    retval = retval[0].strip('(').strip(')').strip().split(',')

    signature['params'] = retval

    return signature


class Backend(object):
    def __init__(self):
        pass

    def gen_include(self):
        return ''

    def gen_func(self, sign: dict):
        return ''

    def gen_entry(self, module):
        return ''


class Duktape(Backend):
    def __init__(self):
        Backend.__init__(self)

    def gen_include(self):
        return '#include \"duktape.h\"\n'

    def gen_module(self, name, module: dict):
        code = ''
        if 'function' in module or 'const' in module:
            code += '\n  duk_push_object(ctx);\n'
            code += '  idx = duk_get_top_index(ctx);\n'
            if 'function' in module:
                for n, v in module['function'].items():
                    sign = extract_signature('dummy', n, v)
                    code += '  duk_push_string(ctx, \"{}\");\n'.format(n)
                    code += '  duk_push_c_function(ctx, js_{}, {});\n'.format(
                        n, len(sign['params']))
                    code += '  duk_def_prop(ctx, idx, DUK_DEFPROP_HAVE_VALUE);\n'
            if 'const' in module:
                for n, v in module['const'].items():
                    code += '  duk_push_string(ctx, \"{}\");\n'.format(n)
                    tn = type(v).__name__
                    if tn == 'int':
                        code += '  duk_push_int(ctx, {});\n'.format(v)
                    elif tn == 'str':
                        code += '  duk_push_string(ctx, \"{}\");\n'.format(v)
                    else:
                        raise RuntimeError(
                            'Constant type not supported:{}'.format(tn))
                    code += '  duk_def_prop(ctx, idx, DUK_DEFPROP_HAVE_VALUE);\n'
            code += '  duk_put_global_string(ctx, \"{}\");\n'.format(name)
        return code

    def gen_global_module(self, module: dict):
        code = ''
        if 'function' in module or 'const' in module:
            if 'function' in module:
                for n, v in module['function'].items():
                    sign = extract_signature('dummy', n, v)
                    code += '  duk_push_c_function(ctx, js_{}, {});\n'.format(
                        n, len(sign['params']))
                    code += '  duk_put_global_string(ctx, \"{}\");\n\n'.format(n)
        if 'const' in module:
            for n, v in module['const'].items():
                tn = type(v).__name__
                if tn == 'int':
                    code += '  duk_push_int(ctx, {});\n'.format(v)
                elif tn == 'str':
                    code += '  duk_push_string(ctx, \"{}\");\n'.format(v)
                else:
                    raise RuntimeError(
                        'Constant type not supported:{}'.format(tn))

                code += '  duk_put_global_string(ctx, \"{}\");\n\n'.format(n)
        return code

    def gen_entry(self, module: dict):
        code = 'void js_binding_init(duk_context *ctx)\n{\n'
        code += '  int idx = 0;\n'

        for n, v in module.items():
            if n != 'include':
                if n == 'global':
                    code += self.gen_global_module(v)
                else:
                    code += self.gen_module(n, v)

        code += '}'
        return code

    def gen_func(self, sign: dict):
        code = 'static duk_ret_t js_{func}(duk_context *ctx)\n'.format(
            func=sign['method'])
        code += '{\n'
        param = sign['params']
        param_num = len(param)
        if param_num == 1:
            if param[0] == '':
                param_num = 0

        # Generate local variable
        ret = sign['return']
        if ret != 'void':
            code += '  {param} ret;\n'.format(param=ret)

        for i in range(param_num):
            t: str = param[i]
            if t.endswith('*'):
                code += '  {param}p{idx};\n'.format(param=t, idx=i)
            else:
                code += '  {param} p{idx};\n'.format(param=t, idx=i)

        code += '\n'

        # Get variable from context

        for i in range(param_num):
            t: str = param[i]
            if re.search('char *\*', t) != None:
                code += '  p{idx} = duk_to_string(ctx, {idx});\n'.format(idx=i)
            elif re.search('(uint[0-9]{0,2}(_t)*)', t) != None:
                code += '  p{idx} = duk_to_uint(ctx, {idx});\n'.format(idx=i)
            elif re.search('(int[0-9]{0,2}(_t)*)', t) != None:
                code += '  p{idx} = duk_to_int(ctx, {idx});\n'.format(idx=i)
        if param_num > 0:
            code += '\n'

        if ret != 'void':
            code += '  ret = '
        else:
            code += '  '
        code += sign['function']
        code += '('

        for i in range(param_num):
            code += 'p{idx}'.format(idx=i)
            if i < param_num - 1:
                code += ', '

        code += ');\n'

        if re.search('char *\*', ret) != None:
            code += '  duk_push_string(ctx, ret);\n'
        elif re.search('(uint[0-9]{0,2}(_t)*)', ret) != None:
            code += '  duk_push_uint(ctx, ret);\n'
        elif re.search('(int[0-9]{0,2}(_t)*)', ret) != None:
            code += '  duk_push_int(ctx, ret);\n'

        if ret != 'void':
            code += '\n  return 1;\n}'
        else:
            code += '\n  return 0;\n}'

        return code

    def gen_const(self, sign: dict):
        pass


class Context(object):
    def __init__(self, backend: str):
        self.code = ""
        if backend == 'Duktape':
            self.backend = Duktape()
        else:
            raise RuntimeError('Unknown backend')
        self.__tmp_file_header = \
            '''\
/****************************************************************************
 * {file}
 * 
 * Generated from {origin}
 * By binding.py @ {date}
 *
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.  The
 * ASF licenses this file to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance with the
 * License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
 * License for the specific language governing permissions and limitations
 * under the License.
 *
 ****************************************************************************/

/****************************************************************************
 * Included Files
 ****************************************************************************/
'''
        self.__tmp_publibc_func_header = \
            '''\
/****************************************************************************
 * Public Functions
 ****************************************************************************/
'''
        self.__tmp_private_func_header = \
            '''\
/****************************************************************************
 * Private Functions
 ****************************************************************************/
'''
        self.__tmp_inc_sys = '#include <{inc}>'
        self.__tmp_inc_custom = '#include "{inc}"'

    def gen_header(self, origin: str, file: str):
        self.code += self.__tmp_file_header.format(file=file,
                                                   origin=origin,
                                                   date=datetime.datetime.now())

    def gen_newline(self):
        self.code += '\n'

    def gen_inc_system(self, header: list):
        for inc in header:
            self.code += self.__tmp_inc_sys.format(inc=inc)
            self.gen_newline()

    def gen_backend_include(self):
        self.code += self.backend.gen_include()

    def gen_inc_custom(self, header: list):
        for inc in header:
            self.code += self.__tmp_inc_custom.format(inc=inc)
            self.gen_newline()

    def gen_func_header(self):
        self.code += self.__tmp_private_func_header

    def gen_func_body(self, sign: dict):
        self.code += self.backend.gen_func(sign)

    def gen_entry_header(self):
        self.code += self.__tmp_publibc_func_header

    def gen_entry(self, module):
        self.code += self.backend.gen_entry(module)

    def gen_const(self, sign: dict):
        self.backend.gen_const(sign)

    def flush(self, file: str):
        with open(file, 'w+') as f:
            f.write(self.code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Script Language Binding Tool')
    parser.add_argument('file')
    parser.add_argument(
        '-t', '--target', help='target language (default Duktape)', default='Duktape')
    parser.add_argument(
        '-o', '--output', help='output'
    )
    param = parser.parse_args()

    if param.output == None:
        param.output = param.file.split('.toml')[0] + '.c'

    module = toml.load(param.file)

    ctx = Context(param.target)

    ctx.gen_header(param.file, param.output)
    ctx.gen_newline()

    if 'include' in module:
        v = module['include']
        if 'system' in v:
            ctx.gen_inc_system(v['system'])
            ctx.gen_newline()
        if 'custom' in v:
            ctx.gen_inc_custom(v['custom'])
            ctx.gen_newline()

    ctx.gen_backend_include()
    ctx.gen_newline()

    ctx.gen_func_header()
    ctx.gen_newline()

    # generate wrapper

    for n, v in module.items():
        if n == 'include':
            pass
        else:
            if 'function' in v:
                for gn, gv in v['function'].items():
                    signature = extract_signature(n, gn, gv)
                    ctx.gen_func_body(signature)
                    ctx.gen_newline()
                    ctx.gen_newline()

    ctx.gen_entry_header()
    ctx.gen_newline()
    ctx.gen_entry(module)
    ctx.gen_newline()
    ctx.flush(param.output)
