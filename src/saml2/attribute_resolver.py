#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Umeå University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Contains classes and functions that a SAML2.0 Service Provider (SP) may use
to do attribute aggregation.
"""
import os
import urllib
import saml2
import base64

from saml2 import samlp, saml
from saml2.sigver import correctly_signed_response
from saml2.soap import SOAPClient
from saml2.client import Saml2Client

DEFAULT_BINDING = saml2.BINDING_HTTP_REDIRECT

class AttributeResolver():
    def __init__(self, environ, metadata=None, xmlsec_binary=None,
                        key_file=None, cert_file=None):
        self.metadata = metadata
        self.saml2client = Saml2Client(environ, metadata=metadata,
                            xmlsec_binary=xmlsec_binary,
                            key_file=key_file,
                            cert_file=cert_file)
        
    def extend(self, subject_id, issuer, vo_members, nameid_format,
                log=None):
        """ 
        :param subject_id: The identifier by which the subject is know
            among all the participents of the VO
        :param issuer: Who am I the poses the query
        :param vo_members: The entity IDs of the IdP who I'm going to ask
            for extra attributes
        :param nameid_format: Used to make the IdPs aware of what's going
            on here
        :param log: Where to log exciting information
        :return: A dictionary with all the collected information about the
            subject
        """
        extended_identity = {}
        for member in vo_members:            
            for ass in self.metadata.attribute_services(member):
                for attr_serv in ass.attribute_service:
                    log and log.info("Send attribute request to %s" % \
                                        attr_serv.location)
                    resp = self.saml2client.attribute_query(subject_id, 
                                issuer, 
                                attr_serv.location, 
                                format=nameid_format, log=log)
                    if resp:
                        # unnecessary
                        del resp["__userid"]
                        for attr,val in resp.items():
                            try:
                                extended_identity[attr].extend(val)
                            except KeyError:
                                extended_identity[attr] = val
                    
        return extended_identity