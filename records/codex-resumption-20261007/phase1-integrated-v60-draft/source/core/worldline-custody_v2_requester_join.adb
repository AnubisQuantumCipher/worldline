with Attest;
package body Worldline.Custody_V2_Requester_Join with SPARK_Mode is
   use type Q.Byte_Count;
   use type Q.Byte;
   use type E.Bytes;
   use type E.Value_Kind;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
     (S.Field (Data, Item, Name));
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (S.Valid (Data, Left) and then S.Valid (Data, Right) and then
      S.A.Same_Encoding (Data, Left, Right));
   function Integer_Is (Data : E.Bytes; Item : E.Span; Number : Long_Long_Integer)
      return Boolean
   is
      Rest : Long_Long_Integer := Number;
   begin
      if not V.Is_Integer (Data, Item) then return False; end if;
      if V.Negative (Data, Item) /= (Number < 0) then return False; end if;
      declare
         Magnitude : constant E.Bytes := V.Magnitude_Value (Data, Item);
         Digit : Q.Byte;
      begin
         for I in Magnitude'Range loop
            pragma Loop_Variant (Increases => I);
            Digit := Q.Byte (abs (Rest rem 256));
            if Magnitude (I) /= Digit then return False; end if;
            Rest := Rest / 256;
         end loop;
         return Rest = 0;
      end;
   end Integer_Is;
   function Unsigned_Is (Data : E.Bytes; Item : E.Span; Number : Q.Byte_Count)
      return Boolean is
     (Integer_Is (Data, Item, Long_Long_Integer (Number)));
   function Same_Bytes (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (V.Valid_Bytes (Data, Left) and then V.Valid_Bytes (Data, Right) and then
      V.Bytes_Value (Data, Left) = V.Bytes_Value (Data, Right));
   function Digest_Matches (Data : E.Bytes; Raw, Hex : E.Span) return Boolean
   is
   begin
      if not V.Valid_Bytes (Data, Raw) or else not V.Valid_Text (Data, Hex) then
         return False;
      end if;
      declare
         Bytes : constant E.Bytes := V.Bytes_Value (Data, Raw);
         Text : constant E.Bytes := V.Text_Value (Data, Hex);
      begin
         return C.G.Origin_Matches (Text, (Text'First, Text'Length),
           C.G.Hash (Bytes, (Bytes'First, Bytes'Length)));
      end;
   end Digest_Matches;
   function Frame_Mac_Matches
     (Key_Data, Frame_Data : E.Bytes; Key, Frame : E.Span; Domain : String)
      return Boolean
   is
      package SHA renames C.SHA;
      subtype Block is Attest.Byte_Array (0 .. SHA.Block_Bytes - 1);
      K0 : Block := (others => 0);
      Inner_Pad, Outer_Pad : Block;
      Inner, Outer : SHA.Context := SHA.Initial;
   begin
      if not E.C.P.Valid (Key_Data, Key) or else not E.C.P.Valid (Frame_Data, Frame) or else
         Frame.Length < 32 then return False; end if;
      if Key.Length > SHA.Block_Bytes then
         K0 (SHA.Digest'Range) := C.G.Hash (Key_Data, Key);
      elsif Key.Length > 0 then
         for I in E.Count range 0 .. Key.Length - 1 loop
            pragma Loop_Variant (Increases => I);
            K0 (Natural (I)) := Key_Data (Key.First + I);
         end loop;
      end if;
      for I in Block'Range loop
         pragma Loop_Variant (Increases => I);
         Inner_Pad (I) := K0 (I) xor 16#36#;
         Outer_Pad (I) := K0 (I) xor 16#5C#;
      end loop;
      SHA.Update (Inner, Inner_Pad);
      for B of Domain loop
         SHA.Update (Inner, Attest.Byte_Array'(0 => Character'Pos (B)));
      end loop;
      if Frame.Length > 32 then
         for I in E.Count range 0 .. Frame.Length - 33 loop
            pragma Loop_Variant (Increases => I);
            SHA.Update (Inner, Attest.Byte_Array'(0 => Frame_Data (Frame.First + I)));
         end loop;
      end if;
      SHA.Update (Outer, Outer_Pad);
      SHA.Update (Outer, SHA.Final (Inner));
      declare
         Mac : constant SHA.Digest := SHA.Final (Outer);
      begin
         return (for all I in Mac'Range =>
           Frame_Data (Frame.First + Frame.Length - 32 + E.Count (I - Mac'First)) = Mac (I));
      end;
   end Frame_Mac_Matches;
   function Raw_Integer
     (Data : E.Bytes; Item : E.Span; Raw : E.Bytes; Offset : Q.Byte_Count;
      Signed : Boolean) return Boolean
   is
      Negative : Boolean;
      Carry : Natural := 1;
      Digit : Natural;
   begin
      if not V.Is_Integer (Data, Item) or else Offset > Raw'Length or else
         Raw'Length - Offset < 4 then return False; end if;
      Negative := Signed and then Raw (Raw'First + Offset + 3) >= 128;
      if V.Negative (Data, Item) /= Negative then return False; end if;
      declare
         Magnitude : constant E.Bytes := V.Magnitude_Value (Data, Item);
      begin
         for J in Q.Byte_Count range 0 .. Q.Byte_Count'Max (4, Magnitude'Length) - 1 loop
            pragma Loop_Variant (Increases => J);
            pragma Loop_Invariant (Carry <= 1);
            if J < 4 then
               Digit := Natural (Raw (Raw'First + Offset + J));
               if Negative then
                  Digit := 255 - Digit + Carry;
                  Carry := Digit / 256;
                  Digit := Digit mod 256;
               end if;
            else Digit := 0;
            end if;
            if J < Magnitude'Length then
               if Magnitude (Magnitude'First + J) /= Q.Byte (Digit) then return False; end if;
            elsif Digit /= 0 then return False;
            end if;
         end loop;
         return True;
      end;
   end Raw_Integer;
   function Ucred_Matches (Data : E.Bytes; Raw : E.Span; Peer : E.Span)
      return Boolean
   is
   begin
      if not V.Valid_Bytes (Data, Raw) or else not S.Valid (Data, Peer) or else
         not S.Text_Is (Data, F (Data, Peer, "source"), "linux.SO_PEERCRED") or else
         not V.Valid_Hex_Field (Data, F (Data, Peer, "rawUcred"), "value")
      then return False; end if;
      declare
         Bytes : constant E.Bytes := V.Bytes_Value (Data, Raw);
         Documentary : constant E.Bytes := V.Hex_Value (Data, F (Data, Peer, "rawUcred"), "value");
      begin
         return Bytes'Length = 12 and then Bytes = Documentary and then
           Raw_Integer (Data, F (Data, Peer, "pid"), Bytes, 0, True) and then
           Raw_Integer (Data, F (Data, Peer, "uid"), Bytes, 4, False) and then
           Raw_Integer (Data, F (Data, Peer, "gid"), Bytes, 8, False);
      end;
   end Ucred_Matches;
   function Request_Archive_Matches
     (Document_Data, Archive_Data : E.Bytes; Document, Archive : E.Span)
      return Boolean
   is
      function Scalar (Left, Right : E.Span) return Boolean is
         View : constant E.View := E.Decode (Archive_Data, Right, E.Operation);
      begin
         if V.Valid_Text (Document_Data, Left) then
            return View.Form = E.Text_Value and then
              E.Bytes_Valid (Archive_Data, View.Payload) and then
              V.Text_Value (Document_Data, Left) = E.Materialize (Archive_Data, View.Payload);
         elsif V.Is_Integer (Document_Data, Left) then
            return View.Form = E.Integer_Value and then
              E.Bytes_Valid (Archive_Data, View.Payload) and then
              V.Negative (Document_Data, Left) = View.Sign and then
              V.Magnitude_Value (Document_Data, Left) = E.Materialize (Archive_Data, View.Payload);
         end if;
         return False;
      end Scalar;
      function Member (Left, Right : E.Span; Name : String) return Boolean is
        (Scalar (S.Field (Document_Data, Left, Name),
                 S.A.Field (Archive_Data, Right, Name)));
      Peer : constant E.Span := S.Field (Document_Data, Document, "peer");
      Other_Peer : constant E.Span := S.A.Field (Archive_Data, Archive, "peer");
      ID : constant E.Span := S.Field (Document_Data, Peer, "socketIdentity");
      Other_ID : constant E.Span := S.A.Field (Archive_Data, Other_Peer, "socketIdentity");
      function Object_Count (Item : E.Span; Count : E.Count) return Boolean is
        (E.Decode (Archive_Data, Item, E.Operation).Form = E.Object_Value and then
         E.Array_Length (Archive_Data, E.Decode (Archive_Data, Item, E.Operation).Children) = Count);
   begin
      return S.Valid (Document_Data, Document) and then S.A.Valid (Archive_Data, Archive) and then
        S.Member_Count (Document_Data, Document) = 6 and then Object_Count (Archive, 6) and then
        S.Member_Count (Document_Data, Peer) = 6 and then Object_Count (Other_Peer, 6) and then
        S.Member_Count (Document_Data, ID) = 3 and then Object_Count (Other_ID, 3) and then
        Member (Document, Archive, "schema") and then
        Member (Document, Archive, "observationId") and then
        Member (Document, Archive, "requestId") and then
        Member (Document, Archive, "operation") and then
        Member (Document, Archive, "rawRequest") and then
        Member (Peer, Other_Peer, "source") and then
        Member (Peer, Other_Peer, "rawUcred") and then
        Member (Peer, Other_Peer, "pid") and then
        Member (Peer, Other_Peer, "uid") and then
        Member (Peer, Other_Peer, "gid") and then
        Member (ID, Other_ID, "device") and then
        Member (ID, Other_ID, "inode") and then
        Member (ID, Other_ID, "mode");
   end Request_Archive_Matches;
   function Successful (Data : E.Bytes; Call, FD : E.Span) return Boolean is
     (Same (Data, F (Data, Call, "fd"), FD) and then
      Integer_Is (Data, F (Data, Call, "result"), 0) and then
      Integer_Is (Data, F (Data, Call, "errno"), 0));
   function Getopt
     (Data : E.Bytes; Call, FD : E.Span; Option, Size : Long_Long_Integer)
      return Boolean is
     (Successful (Data, Call, FD) and then
      Integer_Is (Data, F (Data, Call, "level"), 1) and then
      Integer_Is (Data, F (Data, Call, "option"), Option) and then
      Integer_Is (Data, F (Data, Call, "requested"), Size) and then
      V.Valid_Bytes (Data, F (Data, Call, "raw")) and then
      V.Bytes_Value (Data, F (Data, Call, "raw"))'Length = Q.Byte_Count (Size));
   function Socket_Matches (Data : E.Bytes; Socket, Document : E.Span)
      return Boolean
   is
      FD : constant E.Span := F (Data, Socket, "fd");
      Peer : constant E.Span := F (Data, Document, "peer");
      Stat : constant E.Span := F (Data, Socket, "fstat");
      Identity : constant E.Span := F (Data, Stat, "identity");
      Documentary : constant E.Span := F (Data, Peer, "socketIdentity");
      Mode : constant V.Count_Result := V.Nonnegative_Count (Data, F (Data, Identity, "mode"));
      function ID (Name : String) return Boolean is
        (Same (Data, F (Data, Identity, Name), F (Data, Documentary, Name)));
   begin
      if not S.Valid (Data, Socket) or else not S.Valid (Data, Document) or else
         not S.Text_Is (Data, F (Data, Document, "schema"), "worldline.client-request-observation-v1") or else
         S.Member_Count (Data, Document) /= 6 or else
         S.Member_Count (Data, Peer) /= 6 or else
         S.Member_Count (Data, Documentary) /= 3 or else
         not V.Is_Integer (Data, FD) or else V.Negative (Data, FD) or else
         not Successful (Data, Stat, FD) or else not Mode.Present or else
         Mode.Value / 4_096 mod 16 /= 12 or else
         not (ID ("device") and then ID ("inode") and then ID ("mode")) or else
         not V.Is_Integer (Data, F (Data, Identity, "uid")) or else
         not V.Is_Integer (Data, F (Data, Identity, "gid")) or else
         not V.Valid_Bytes (Data, F (Data, Identity, "fdinfo")) or else
         not Getopt (Data, F (Data, Socket, "peercred"), FD, 17, 12) or else
         not Getopt (Data, F (Data, Socket, "domain"), FD, 39, 4) or else
         not Getopt (Data, F (Data, Socket, "type"), FD, 3, 4) or else
         not Successful (Data, F (Data, Socket, "peername"), FD) or else
         not V.Valid_Bytes (Data, F (Data, F (Data, Socket, "peername"), "raw"))
      then return False; end if;
      declare
         Domain : constant E.Bytes := V.Bytes_Value (Data, F (Data, F (Data, Socket, "domain"), "raw"));
         Kind : constant E.Bytes := V.Bytes_Value (Data, F (Data, F (Data, Socket, "type"), "raw"));
      begin
         return Domain = E.Bytes'(1, 0, 0, 0) and then Kind = E.Bytes'(1, 0, 0, 0) and then
           Ucred_Matches (Data, F (Data, F (Data, Socket, "peercred"), "raw"), Peer);
      end;
   end Socket_Matches;
   function Optional_Equal (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (S.Valid (Data, Left) and then S.Valid (Data, Right) and then
      (V.Is_Null (Data, Left) or else V.Is_Null (Data, Right) or else Same (Data, Left, Right)));
   function Fresh_Matches
     (Data : E.Bytes; Document, Front_Socket, Worker_Socket, Transfer : E.Span)
      return Boolean
   is
      Host : constant E.Span := F (Data, F (Data, Front_Socket, "peercred"), "raw");
      Reader : constant E.Span := F (Data, F (Data, Worker_Socket, "peercred"), "raw");
      Worker_Document : constant E.Span := F (Data, Transfer, "worker_document");
      function Optional (Left, Right : String) return Boolean is
        (Optional_Equal (Data, F (Data, Transfer, Left), F (Data, Transfer, Right)));
   begin
      if not Socket_Matches (Data, Front_Socket, Document) or else
         not Socket_Matches (Data, Worker_Socket, Worker_Document) or else
         not Same (Data, F (Data, Worker_Document, "rawRequest"), F (Data, Document, "rawRequest")) or else
         not Same (Data, F (Data, Worker_Document, "observationId"), F (Data, Document, "observationId")) or else
         not Same (Data, F (Data, Worker_Document, "requestId"), F (Data, Document, "requestId")) or else
         not Same (Data, F (Data, Worker_Document, "operation"), F (Data, Document, "operation")) or else
         not Same (Data, F (Data, F (Data, Worker_Document, "peer"), "socketIdentity"),
                         F (Data, F (Data, Document, "peer"), "socketIdentity")) or else
         not Optional ("origin_user_ns", "reader_user_ns") or else
         not Optional ("host_cookie", "reader_cookie") or else
         not S.Valid (Data, F (Data, Transfer, "origin_pid_ns")) or else
         not S.Valid (Data, F (Data, Transfer, "reader_pid_ns")) or else
         not S.Valid (Data, F (Data, Transfer, "held_pid_ns")) or else
         (not V.Is_Null (Data, F (Data, Transfer, "reader_pid_ns")) and then
          not V.Is_Null (Data, F (Data, Transfer, "held_pid_ns")) and then
          not Same (Data, F (Data, Transfer, "reader_pid_ns"), F (Data, Transfer, "held_pid_ns")))
      then return False; end if;
      declare
         Host_Raw : constant E.Bytes := V.Bytes_Value (Data, Host);
         Reader_Raw : constant E.Bytes := V.Bytes_Value (Data, Reader);
      begin
         -- Relative PID is deliberately uninterpreted: only UID/GID crosswalk.
         return Host_Raw'Length = 12 and then Reader_Raw'Length = 12 and then
           (for all I in Q.Byte_Count range 4 .. 11 =>
              Host_Raw (Host_Raw'First + I) = Reader_Raw (Reader_Raw'First + I));
      end;
   end Fresh_Matches;
end Worldline.Custody_V2_Requester_Join;
