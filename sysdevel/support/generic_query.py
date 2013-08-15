#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2013.  Los Alamos National Security, LLC.
This material was produced under U.S. Government contract
DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is
operated by Los Alamos National Security, LLC for the U.S. Department
of Energy. The U.S. Government has rights to use, reproduce, and
distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS
NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should be
clearly marked, so as not to confuse it with the version available
from LANL.

Licensed under the Mozilla Public License, Version 2.0 (the
"License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/2.0/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
"""

import logging


class Query(object):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    @property
    def max_steps(self):
        step_num = 1
        while True:
            try:
                func_name = getattr(self, 'step' + str(step_num))
                valid.append(func_name)
                step_num += 1
            except AttributeError:
                break
        return step_num - 1

    def validate_parameters(self, parameters):
        valid = ['list_steps', 'last_step',]
        for num in range(1, self.max_steps+1):
            valid.append('step' + str(num))
        for param in parameters.keys():
            if not param in valid:
                return False
        return True

    def list_steps(self, parameters):
        raise NotImplementedError

    def step1(self, parameters):
        raise NotImplementedError

    def last_step(self, parameters):
        return self.query(parameters)

    def query(self, kwargs):
        """
        Perform actual computation after setup steps have been completed.
        """
        raise NotImplementedError

    def show(self, results):
        """
        Show results of computation when called directly.
        """
        raise NotImplementedError

    
    def main(self, args=None):
        import sys
        if args is None:
            args = sys.argv

        try:
            ## example: ./query.py --web some_json_encoded_string
            web_idx = args.index('--web')
            step = args[web_idx+1]
            json_str = ' '.join(args[web_idx+2:])
            try:
                import json
            except ImportError:
                import simplejson as json
            params = json.loads(json_str)
            results = self.last_step(params)
            print json.dumps(results, default=json_handler)
        except ValueError:
            ## example: ./query.py --param1=val1 --param2 val2 --param3 = val3
            kwargs = dict()
            param_name = None
            for arg in args:
                if arg == '=':
                    continue  ## ignore bare equals
                if arg.startswith('--'):
                    if param_name:  ## i.e. '--param1 --param2'
                        kwargs[param_name] = None
                    if '=' in arg:
                        args = arg.split('=')
                        param_name = args[0][2:]
                        if args[1] != '':
                            kwargs[param_name] = args[1]  ## i.e. '--param=value'
                            param_name = None
                        else:
                            continue  ## i.e. '--param= value'
                elif param_name:
                    kwargs[param_name] = arg  ## i.e. '--param value'
                else:
                    continue  ## ignore bare values

            self.show(self.query(kwargs))



## singleton
query = Query()

if __name__ == "__main__":
    query.main()
