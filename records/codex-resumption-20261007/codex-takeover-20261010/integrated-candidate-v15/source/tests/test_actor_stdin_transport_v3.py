"""UNRUN local data/FD controls. No native/helper/protected-authority claim."""
from __future__ import annotations

import array
import errno
import fcntl
import os
import socket
import stat
import threading
import unittest


def full_write(fd, payload, write=os.write):
    """Control oracle for required complete transport, not a selected caller."""
    position=0
    view=memoryview(payload)
    while position<len(view):
        try:
            size=write(fd,view[position:])
        except InterruptedError:
            continue
        if size<=0 or size>len(view)-position:
            raise OSError(errno.EIO,'invalid complete-stream write result')
        position+=size


class ActorStdinTransportV3Tests(unittest.TestCase):
    def pipe_roundtrip(self,payload):
        reader,writer=os.pipe2(os.O_CLOEXEC)
        pieces=[]
        failures=[]
        def receive():
            try:
                while True:
                    data=os.read(reader,65536)
                    if not data:break
                    pieces.append(data)
            except BaseException as exc:
                failures.append(exc)
            finally:
                os.close(reader)
        thread=threading.Thread(target=receive)
        thread.start()
        try:
            full_write(writer,payload)
        finally:
            os.close(writer)
            thread.join()
        if failures:raise failures[0]
        self.assertEqual(b''.join(pieces),payload)

    def test_empty_stream_delivers_exact_eof(self):
        self.pipe_roundtrip(b'')

    def test_full_binary_multibyte_stream_with_backpressure(self):
        reader,writer=os.pipe2(os.O_CLOEXEC)
        try:capacity=fcntl.fcntl(writer,fcntl.F_GETPIPE_SZ)
        finally:os.close(reader);os.close(writer)
        self.pipe_roundtrip((bytes(range(256))+'α🙂\n'.encode('utf-8'))*capacity)

    def test_partial_and_interrupted_writes_preserve_full_bytes(self):
        received=[];interrupt=[True]
        def partial(fd,data):
            del fd
            if interrupt[0]:interrupt[0]=False;raise InterruptedError()
            piece=bytes(data[:1]);received.append(piece);return len(piece)
        payload=b'\x00full\xff'+ '🙂'.encode('utf-8')
        full_write(-1,payload,partial)
        self.assertEqual(b''.join(received),payload)

    def test_write_failure_remains_primary_and_never_success(self):
        failure=BrokenPipeError(errno.EPIPE,'receiver closed')
        def broken(fd,data):del fd,data;raise failure
        with self.assertRaises(BrokenPipeError) as got:full_write(-1,b'full',broken)
        self.assertIs(got.exception,failure)

    def test_zero_write_is_not_complete_delivery(self):
        with self.assertRaises(OSError):full_write(-1,b'x',lambda fd,data:0)

    def test_sixth_right_is_owned_write_pipe_and_received_cloexec(self):
        endpoints=[];received=[]
        left,right=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        measure_l,measure_r=socket.socketpair(socket.AF_UNIX,socket.SOCK_SEQPACKET)
        try:
            for _ in range(5):endpoints.extend(os.pipe2(os.O_CLOEXEC))
            rights=[endpoints[0],endpoints[2],endpoints[4],endpoints[6],measure_r.fileno(),endpoints[9]]
            payload=b'WL-RESOURCE-SUPERVISOR-v3\nHELD\nfixture\n1\n'
            self.assertEqual(left.sendmsg([payload],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',rights))]),len(payload))
            body,anc,flags,_=right.recvmsg(len(payload),socket.CMSG_SPACE(array.array('i').itemsize*len(rights)),socket.MSG_CMSG_CLOEXEC)
            self.assertEqual(body,payload);self.assertFalse(flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC))
            self.assertEqual(len(anc),1)
            level,kind,data=anc[0];self.assertEqual((level,kind),(socket.SOL_SOCKET,socket.SCM_RIGHTS))
            owned=array.array('i');owned.frombytes(data);received=list(owned)
            self.assertEqual(len(received),len(rights))
            writer=received[-1]
            self.assertTrue(stat.S_ISFIFO(os.fstat(writer).st_mode))
            self.assertEqual(fcntl.fcntl(writer,fcntl.F_GETFL)&os.O_ACCMODE,os.O_WRONLY)
            self.assertFalse(os.get_inheritable(writer))
            self.assertEqual((os.fstat(writer).st_dev,os.fstat(writer).st_ino),(os.fstat(endpoints[9]).st_dev,os.fstat(endpoints[9]).st_ino))
            full_write(writer,b'full\x00bytes')
            self.assertEqual(os.read(endpoints[8],65536),b'full\x00bytes')
        finally:
            for fd in received+endpoints:os.close(fd)
            measure_l.close();measure_r.close();left.close();right.close()


if __name__=='__main__':unittest.main()
