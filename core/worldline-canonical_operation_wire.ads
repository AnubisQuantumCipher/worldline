with Interfaces;
with Worldline.Canonical_Operation;
with Worldline.Operation_Authority_Wire;
with Resource_Run_Ledger_Wire;
package Worldline.Canonical_Operation_Wire with SPARK_Mode is
   package K renames Worldline.Canonical_Operation;
   package W renames Worldline.Operation_Authority_Wire;
   package L renames Resource_Run_Ledger_Wire;
   type Raw_Input is record
      Authority : W.Raw_Input;
      State : L.Raw_State;
      Bound : L.Raw_Binding;
      Requester : L.Raw_Id;
      Peer : W.Raw_UID;
      Collapse : K.C.Raw_Request;
   end record with Convention=>C;
   type Raw_Result is record Disposition : Interfaces.Unsigned_8; end record with Convention=>C;
   function Well_Formed(Data:K.A.Q.Byte_Array; V:Raw_Input) return Boolean is
     (W.Well_Formed(V.Authority) and then W.Recovery_Well_Formed(Data,V.Authority.Facts)
      and then L.Well_Formed(Data,V.State) and then L.Well_Formed(Data,V.Bound)
      and then L.Well_Formed(Data,V.Requester) and then W.Well_Formed(V.Peer)
      and then K.C.Well_Formed(V.Collapse)) with Global=>null;
end Worldline.Canonical_Operation_Wire;
