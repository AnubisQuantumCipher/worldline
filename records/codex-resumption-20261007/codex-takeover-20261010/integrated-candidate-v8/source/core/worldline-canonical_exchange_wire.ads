with Interfaces;
with Worldline.Canonical_Exchange;
with Worldline.Canonical_Operation_Wire;
with Worldline.Recovery_Authorization_V3_Wire;
package Worldline.Canonical_Exchange_Wire with SPARK_Mode is
   package X renames Worldline.Canonical_Exchange;
   package W renames Worldline.Canonical_Operation_Wire;
   package V renames Worldline.Recovery_Authorization_V3_Wire;
   use type Interfaces.Unsigned_8;
   type Raw_Material is record
      Worker_Issued : V.Raw_Binding;
      Worker_Recovered : V.Raw_Binding;
      Canonical_Issued : V.Raw_Binding;
      Canonical_Recovered : V.Raw_Binding;
      Worker_Native : V.Raw_Native;
      Canonical_Native : V.Raw_Native;
      Worker_Receipt_Genesis : V.Raw_Digest;
      Owner_Receipt_Genesis : V.Raw_Digest;
      Worker_Receipt_Head : V.Raw_Digest;
      Worker_Causal_Genesis : V.Raw_Digest;
      Owner_Causal_Genesis : V.Raw_Digest;
      Worker_Causal_Head : V.Raw_Digest;
      Quarantine_Head : V.Raw_Digest;
   end record with Convention=>C;
   type Raw_Input is record
      Operation_Input : W.Raw_Input;
      Material : Raw_Material;
      Before, Mode : Interfaces.Unsigned_8;
   end record with Convention=>C;
   type Raw_Result is record Disposition : Interfaces.Unsigned_8; end record with Convention=>C;
   function Well_Formed(Data:X.A.Q.Byte_Array; Item:Raw_Material) return Boolean is
     (V.Well_Formed(Data,Item.Worker_Issued)
      and then V.Well_Formed(Data,Item.Worker_Recovered)
      and then V.Well_Formed(Data,Item.Canonical_Issued)
      and then V.Well_Formed(Data,Item.Canonical_Recovered)
      and then V.Well_Formed(Item.Worker_Native)
      and then V.Well_Formed(Item.Canonical_Native)
      and then V.Well_Formed(Item.Worker_Receipt_Genesis)
      and then V.Well_Formed(Item.Owner_Receipt_Genesis)
      and then V.Well_Formed(Item.Worker_Receipt_Head)
      and then V.Well_Formed(Item.Worker_Causal_Genesis)
      and then V.Well_Formed(Item.Owner_Causal_Genesis)
      and then V.Well_Formed(Item.Worker_Causal_Head)
      and then V.Well_Formed(Item.Quarantine_Head)) with Global=>null;
   function Well_Formed(Data:X.A.Q.Byte_Array; Item:Raw_Input) return Boolean is
     (Item.Before<=X.Phase'Pos(X.Phase'Last) and then Item.Mode<=X.Command'Pos(X.Command'Last)
      and then W.Well_Formed(Data,Item.Operation_Input)
      and then Well_Formed(Data,Item.Material)) with Global=>null;
   function Decode(Data:X.A.Q.Byte_Array; Item:Raw_Material) return X.Material is
     (Worker_Issued=>V.Decode(Data,Item.Worker_Issued),
      Worker_Recovered=>V.Decode(Data,Item.Worker_Recovered),
      Canonical_Issued=>V.Decode(Data,Item.Canonical_Issued),
      Canonical_Recovered=>V.Decode(Data,Item.Canonical_Recovered),
      Worker_Native=>V.Decode(Item.Worker_Native),
      Canonical_Native=>V.Decode(Item.Canonical_Native),
      Worker_Receipt_Genesis=>V.Decode(Item.Worker_Receipt_Genesis),
      Owner_Receipt_Genesis=>V.Decode(Item.Owner_Receipt_Genesis),
      Worker_Receipt_Head=>V.Decode(Item.Worker_Receipt_Head),
      Worker_Causal_Genesis=>V.Decode(Item.Worker_Causal_Genesis),
      Owner_Causal_Genesis=>V.Decode(Item.Owner_Causal_Genesis),
      Worker_Causal_Head=>V.Decode(Item.Worker_Causal_Head),
      Quarantine_Head=>V.Decode(Item.Quarantine_Head))
     with Global=>null, Pre=>Well_Formed(Data,Item);
end Worldline.Canonical_Exchange_Wire;
