with Worldline.Custody_V2_Archive_Chain;
package Worldline.Custody_V2_Domain_Hmac with SPARK_Mode is
   package C renames Worldline.Custody_V2_Archive_Chain;
   package E renames C.E;
   package SHA renames C.SHA;
   function Mac (Data : E.Bytes; Key, Message : E.Span; Domain : String)
      return SHA.Digest with Global => null,
      Pre => E.C.P.Valid (Data, Key) and then E.C.P.Valid (Data, Message);
   -- Key and original canonical message remain in their own owned arenas.
   function Mac (Key_Data, Message_Data : E.Bytes;
                 Key, Message : E.Span; Domain : String)
      return SHA.Digest with Global => null,
      Pre => E.C.P.Valid (Key_Data, Key) and then
             E.C.P.Valid (Message_Data, Message);
end Worldline.Custody_V2_Domain_Hmac;
