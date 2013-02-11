# -*- coding: utf-8 -*-
"""
WebSocket handling
"""
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

import threading
import logging


class WebHandlerService(threading.Thread):
    '''
    Abstract class for handling messages from a web client
    '''
    def __init__(self, name):
        threading.Thread.__init__(self, name=name)
        self.log = logging.getLogger(self.__class__.__name__)

    def closing(self):
        raise NotImplementedError('WebHandlerService must be subclassed.')

    def quit(self):
        raise NotImplementedError('WebHandlerService must be subclassed.')

    def handle_message(self, message):
        raise NotImplementedError('WebHandlerService must be subclassed.')



class WebResourceFactory(object):
    '''
    Abstract callable factory class for creating WebHandlerServices
    Takes a dispatch.Dispatcher instance and a web resource string
    Returns a WebHandlerService instance
    '''
    def __call__(self, dispatcher, resource):
        raise NotImplementedError('WebResourceFactory must be subclassed.')



