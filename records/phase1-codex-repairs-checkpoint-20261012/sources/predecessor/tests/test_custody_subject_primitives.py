"""Authentic unprivileged Linux capture controls; no authority mock or native verdict.

Source-only enrollment. Main must run these on the integrated same-source frame.
"""
import array,fcntl,os,socket,unittest
from worldline.custody_subject_capture import (
    actor_identity,close_descriptor,fd_identity,original_roles,role_roster,socket_capture)
from worldline.root_worker_custody import _send_fd,_receive_fd
from worldline.root_worker_codec import raw_archive,raw_restore_archive

class CustodySubjectPrimitiveControls(unittest.TestCase):
    def test_real_rights_raw_credentials_and_lossless_archive(self):
        sender,receiver=socket.socketpair(socket.AF_UNIX,socket.SOCK_STREAM)
        receiver.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        original=os.memfd_create('custody-subject-authentic-control',os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
        incoming=None
        try:
            payload={b'actual-bytes-key':{b'bytes':b'\x00\xff','tuple':(None,False,0)},'actor':actor_identity(sender)}
            raw=raw_archive(payload);os.write(original,raw)
            seals=fcntl.F_SEAL_SEAL|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_GROW|fcntl.F_SEAL_WRITE
            fcntl.fcntl(original,fcntl.F_ADD_SEALS,seals)
            source={'schema':'worldline.actual-control-source-v1','actor':actor_identity(sender)}
            sent=_send_fd(sender,original,source=source);received=[]
            incoming,credentials=_receive_fd(receiver,received,source)
            self.assertEqual(sent['result'],len(sent['frame']))
            self.assertEqual(sent['rights'],array.array('i',[original]).tobytes())
            self.assertEqual(received[0]['rights'],array.array('i',[incoming]).tobytes())
            self.assertEqual(credentials,sent['sender'])
            self.assertTrue(received[0]['input_flags'] & socket.MSG_CMSG_CLOEXEC)
            self.assertFalse(received[0]['flags'] & (socket.MSG_CTRUNC|socket.MSG_TRUNC))
            self.assertFalse(os.get_inheritable(incoming))
            self.assertEqual(os.pread(incoming,len(raw),0),raw)
            self.assertEqual(raw_restore_archive(raw),payload)
            self.assertEqual(fcntl.fcntl(incoming,fcntl.F_GET_SEALS)&seals,seals)
        finally:
            if incoming is not None:os.close(incoming)
            os.close(original);sender.close();receiver.close()
    def test_listener_failure_is_raw_not_connected_requester_success(self):
        listener=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        try:
            listener.bind(b'\0worldline-custody-control-'+str(os.getpid()).encode());listener.listen()
            source={'actor':actor_identity()}
            capture=socket_capture(listener.fileno(),source)
            self.assertEqual(capture['peername']['result'],-1)
            self.assertNotEqual(capture['peername']['errno'],0)
            roles=original_roles({'actual-listener':listener.fileno()},source,actor_identity(),None,{})
            self.assertEqual(roles[0]['socket_document']['schema'],'worldline.custody-role-socket-v1')
            self.assertEqual(roles[0]['socket_document']['socket']['peername']['result'],-1)
            self.assertIsNone(roles[0]['worker_pidfd'])
        finally:listener.close()
    def test_actual_close_has_same_descriptor_ebadf_readback(self):
        fd=os.memfd_create('custody-close-authentic-control',os.MFD_CLOEXEC)
        source={'actor':actor_identity()};before=fd_identity(fd)
        receipt=close_descriptor(fd,source)
        self.assertEqual(receipt['fd'],receipt['readback']['fd'])
        self.assertEqual(receipt['result'],0)
        self.assertEqual(receipt['readback']['result'],-1)
        self.assertEqual(receipt['readback']['errno'],9)
        self.assertIsInstance(before['fdinfo'],bytes)

if __name__=='__main__':unittest.main()
