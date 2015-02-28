#! /usr/bin/python3.3
# -*- coding: utf8 -*-
'''
Module to ease error handling

@author:     Johannes Pfeffer
        
@version:    0.4

@release:    dolphin-01

'''

__all__ = ["Error", "CLIError", "CardinalityError"]

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class CLIError(Error):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
    
class CardinalityError(Error):
    """Exception raised for errors in cardinality.

    Attributes:
        cardinality -- required cardinality
        observed -- observed cardinality
        message -- explanation of the error
    """

    def __init__(self, cardinality, observed, message):
        super(CardinalityError).__init__(type(self))
        self.cardinality = cardinality
        self.observed = observed
        self.message = "%s (Expected: %d, Observed: %d)" % (message, cardinality, observed)