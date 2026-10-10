"""Concrete intent-only root endpoint and owned original-client transport.
No caller sends a grant, reservation, receipt, epoch, protected fact or verdict.
Root installation, complete source identity and existing owner Genesis required.
"""
import json
import os
from pathlib import Path
import socket
import socketserver
import stat
import struct
import uuid
from .errors import WorldlineError
from .client_peer import KernelPeer,RequestPeer,request_scope
from .protected_owner import ProtectedOwnerPrincipal,canonical,exact,require

class OwnerIntentEndpoint:
    def __init__(self,owner):
        require(type(owner) is ProtectedOwnerPrincipal,'OWNER_ENDPOINT_PRINCIPAL_UNAVAILABLE')
        owner.intact();self.owner=owner
        root=Path(owner.lease.spec['paths']['authority_root'])
        self.path=root/'authority/protected-runtime/owner-intents.sock'
        parent=self.path.parent.lstat()
        require(stat.S_ISDIR(parent.st_mode) and parent.st_uid==0 and not parent.st_mode&0o022,'OWNER_ENDPOINT_DIRECTORY_CUSTODY')
        require(not os.path.lexists(self.path),'OWNER_ENDPOINT_ALREADY_PRESENT')
    def handle(self,connection):
        self.owner.intact()
        peer=KernelPeer.capture_descriptor(connection.fileno())
        request=None;identifier=None
        try:
            observed=peer.observation()
            require(observed['uid']==self.owner.policy['owner_uid'],'OWNER_KERNEL_PEER_REFUSED')
            # Owner-authorized full line. No identity/epoch/history word cap is
            # introduced. Real parser allocation/host profile obligations OPEN.
            with connection.makefile('rb') as stream:line=stream.readline()
            document=exact(line)
            require(type(document) is dict and set(document)=={'id','op','args'} and type(document['id']) is str
                    and document['id'] and type(document['args']) is dict,'OWNER_INTENT_REQUEST_SCHEMA')
            identifier=document['id'];operation=document['op'];args=document['args']
            request=RequestPeer(peer,{'schema':'worldline.client-request-observation-v1','observationId':uuid.uuid4().hex,
                'requestId':identifier,'operation':operation,'rawRequest':line.hex(),'peer':observed})
            with request_scope(request):
                if operation=='owner.retry':
                    require(set(args)=={'world','reason'},'OWNER_RETRY_ARGUMENTS')
                    result=self.owner.retry(request,args['world'],args['reason'])
                elif operation=='owner.adopt':
                    require(set(args)=={'world','reason','expectedRequirement'},'OWNER_ADOPT_ARGUMENTS')
                    result=self.owner.prepare_adopt(request,args['world'],args['reason'],args['expectedRequirement'])
                elif operation=='owner.recover':
                    require(set(args)=={'intent'} and type(args['intent']) is str,'OWNER_RECOVER_ARGUMENTS')
                    result=self.owner.recover(request,args['intent'])
                else:raise WorldlineError('OWNER_INTENT_OPERATION_REFUSED','intent-only owner operation differs')
            response={'id':identifier,'ok':True,'result':result,'error':None}
        except WorldlineError as error:
            response={'id':identifier,'ok':False,'result':None,'error':{'code':error.code,'message':error.message,'details':error.details}}
        finally:
            if request is not None:request.close()
            else:peer.close()
        connection.sendall(canonical(response)+b'\n')

class Handler(socketserver.BaseRequestHandler):
    def handle(self):self.server.endpoint.handle(self.request)
class OwnerIntentServer(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):
    daemon_threads=False
    def __init__(self,endpoint):
        require(type(endpoint) is OwnerIntentEndpoint,'OWNER_ENDPOINT_SOURCE_UNAVAILABLE')
        self.endpoint=endpoint
        super().__init__(str(endpoint.path),Handler)
        # Root-provisioned runtime parent and owner group admit the real owner.
        # Directory provision/chmod is an operator deployment action, not here.
        os.chown(endpoint.path,0,endpoint.owner.policy['owner_gid']);os.chmod(endpoint.path,0o660)

class OwnerClient:
    def __init__(self,endpoint):
        self.path=Path(endpoint)
    def request(self,operation,args,*,request_id):
        require(type(request_id) is str and request_id,'OWNER_REQUEST_ID_REQUIRED')
        for parent in self.path.parents:
            info=parent.lstat()
            require(stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022,'OWNER_CLIENT_ENDPOINT_CUSTODY')
        info=self.path.lstat()
        require(stat.S_ISSOCK(info.st_mode) and info.st_uid==0,'OWNER_CLIENT_ENDPOINT_CUSTODY')
        packet=canonical({'id':request_id,'op':operation,'args':args})+b'\n'
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
            connection.connect(str(self.path))
            ucred=struct.Struct('@iII')
            _pid,uid,_gid=ucred.unpack(connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,ucred.size))
            require(uid==0,'OWNER_CLIENT_SERVER_PRINCIPAL')
            connection.sendall(packet)
            with connection.makefile('rb') as stream:raw=stream.readline()
        result=exact(raw)
        require(type(result) is dict and set(result)=={'id','ok','result','error'} and result['id']==request_id,'OWNER_CLIENT_RESPONSE_SCHEMA')
        if result['ok'] is not True:
            error=result['error'];raise WorldlineError(error['code'],error['message'],error.get('details'))
        return result['result']
