package body Worldline.Operation_Authority_Wire with SPARK_Mode is
   function Decode (V : Raw_Binding) return A.Binding is
      Id : A.Identities;
   begin
      for F in A.Identity_Field loop Id(F):=C.Decode(V.Id(F)); end loop;
      return (Action=>A.Operation'Val(V.Action),Id=>Id,Peer=>Decode(V.Peer),Preparer=>Decode(V.Preparer),
              Owner=>Decode(V.Owner),Target_Owner=>Decode(V.Target_Owner),
              Policy_Epoch=>Decode(V.Policy_Epoch),Resource_Epoch=>Decode(V.Resource_Epoch));
   end Decode;
   function Decode (V : Raw_Grant) return A.Grant is
      Allowed : A.Rights;
   begin
      for Op in A.Operation loop Allowed(Op):=V.Allowed(Op)=1; end loop;
      return (Id=>C.Decode(V.Id),Parent=>C.Decode(V.Parent),Issuer=>C.Decode(V.Issuer),
              Instance=>C.Decode(V.Instance),Root_Set=>C.Decode(V.Root_Set),Policy=>C.Decode(V.Policy),
              Subject=>Decode(V.Subject),Owner=>Decode(V.Owner),Allowed=>Allowed,
              State=>A.Grant_State'Val(V.State),Epoch=>Decode(V.Epoch),
              Ceiling=>Decode(V.Ceiling).Value,Issued_At=>Decode(V.Issued_At).Value,
              Expires_At=>Decode(V.Expires_At).Value);
   end Decode;
   function Decode (Data : A.Q.Byte_Array; V : Raw_Evidence) return A.Evidence is
     (Effect_Binding=>Decode(V.Effect_Binding),Actual_Receipt_Root=>C.Decode(V.Actual_Receipt_Root),
      Actual_Causal_Root=>C.Decode(V.Actual_Causal_Root),No_Effect_Binding=>Decode(V.No_Effect_Binding),
      Owner_Resolution=>Decode(V.Owner_Resolution),Quarantine_Head=>C.Decode(V.Quarantine_Head),
      Witnessed_Receipt_Head=>C.Decode(V.Witnessed_Receipt_Head),Witnessed_Causal_Head=>C.Decode(V.Witnessed_Causal_Head),
      Recovery_Issued=>RW.Decode(Data,V.Recovery.Issued_Binding),Recovery_Recovered=>RW.Decode(Data,V.Recovery.Recovered_Binding),
      Recovery_Historical=>A.R.Historical_Verdict'Val(V.Recovery.Historical),
      Recovery_Native=>(Live_Mapping=>RW.Decode(V.Recovery.Native.Live_Mapping),Live_Root=>RW.Decode(V.Recovery.Native.Live_Root)),
      Original_Use=>C.Decode(V.Original_Use),
      Effect_Material=>(if V.Effect_Material_Length = 0 then (1, 0) else
        (A.Q.Byte_Index (V.Effect_Material_First),
         Worldline.Archive_Envelope.Count (V.Effect_Material_Length))));
end Worldline.Operation_Authority_Wire;
