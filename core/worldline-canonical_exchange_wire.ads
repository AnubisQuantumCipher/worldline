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
   --  Preserve compiler-observed C field layout.
   for Raw_Material use record
      Worker_Issued at 0 range 0 .. 7551;
      Worker_Recovered at 944 range 0 .. 7551;
      Canonical_Issued at 1888 range 0 .. 7551;
      Canonical_Recovered at 2832 range 0 .. 7551;
      Worker_Native at 3776 range 0 .. 527;
      Canonical_Native at 3842 range 0 .. 527;
      Worker_Receipt_Genesis at 3908 range 0 .. 263;
      Owner_Receipt_Genesis at 3941 range 0 .. 263;
      Worker_Receipt_Head at 3974 range 0 .. 263;
      Worker_Causal_Genesis at 4007 range 0 .. 263;
      Owner_Causal_Genesis at 4040 range 0 .. 263;
      Worker_Causal_Head at 4073 range 0 .. 263;
      Quarantine_Head at 4106 range 0 .. 263;
   end record;
   for Raw_Material'Size use 33112;
   for Raw_Material'Object_Size use 33152;
   for Raw_Material'Alignment use 8;
   type Raw_Input is record
      Operation_Input : W.Raw_Input;
      Material : Raw_Material;
      Before, Mode : Interfaces.Unsigned_8;
   end record with Convention=>C;
   --  Preserve compiler-observed C field layout.
   for Raw_Input use record
      Operation_Input at 0 range 0 .. 61439;
      Material at 7680 range 0 .. 33151;
      Before at 11824 range 0 .. 7;
      Mode at 11825 range 0 .. 7;
   end record;
   for Raw_Input'Size use 94608;
   for Raw_Input'Object_Size use 94656;
   for Raw_Input'Alignment use 8;
   type Raw_Result is record Disposition : Interfaces.Unsigned_8; end record with Convention=>C;
   --  Preserve compiler-observed C field layout.
   for Raw_Result use record
      Disposition at 0 range 0 .. 7;
   end record;
   for Raw_Result'Size use 8;
   for Raw_Result'Object_Size use 8;
   for Raw_Result'Alignment use 1;
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
