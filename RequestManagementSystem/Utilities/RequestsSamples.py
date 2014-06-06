'''
Examples of requests and how tto set them up. Can be used also as methods.

Created on Jun 6, 2014

@author: stephanep
'''
from DIRAC.RequestManagementSystem.Client.Request import Request
from DIRAC.RequestManagementSystem.Client.Operation import Operation
from DIRAC.Core.Utilities import DEncode
from DIRAC.RequestManagementSystem.Client.ReqClient import ReqClient
from DIRAC.RequestManagementSystem.Client.File import File

def submitDISET(rpcStub, reqName):
    """ Create a ForwardDISET operation for failover
    """
    request = Request()
    request.RequestName = "%s" % ( reqName )
    
    forwardDISETOp = Operation()
    forwardDISETOp.Type = "ForwardDISET"
    forwardDISETOp.Arguments = DEncode.encode( rpcStub )
    
    request.addOperation( forwardDISETOp )
    
    return ReqClient().putRequest( request )

def submitRemoveReplica(lfn, se, reqName):
    """ Create a replication request
    """
    request = Request()
    request.RequestName = "%s" % ( reqName )

    replicaToRemove = File()
    replicaToRemove.LFN = lfn

    removeReplica = Operation()
    removeReplica.Type = "RemoveReplica"
    removeReplica.TargetSE = se
    removeReplica.addFile( replicaToRemove )
    
    request.addOperation( removeReplica )
    
    return ReqClient().putRequest( request )
