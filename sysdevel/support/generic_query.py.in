#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**************************************************************************
# 
# This material was prepared by the Los Alamos National Security, LLC 
# (LANS), under Contract DE-AC52-06NA25396 with the U.S. Department of 
# Energy (DOE). All rights in the material are reserved by DOE on behalf 
# of the Government and LANS pursuant to the contract. You are authorized 
# to use the material for Government purposes but it is not to be released 
# or distributed to the public. NEITHER THE UNITED STATES NOR THE UNITED 
# STATES DEPARTMENT OF ENERGY, NOR LOS ALAMOS NATIONAL SECURITY, LLC, NOR 
# ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR 
# ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY, 
# COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR 
# PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE 
# PRIVATELY OWNED RIGHTS.
# 
#**************************************************************************

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
