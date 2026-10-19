with Worldline.Archive_Envelope;
with Interfaces;
with Worldline.Operation_Authority;
with Worldline.Chain_Authority_Wire;
with Worldline.Recovery_Authorization_V3_Wire;
package Worldline.Operation_Authority_Wire with SPARK_Mode is
   package A renames Worldline.Operation_Authority;
   package C renames Worldline.Chain_Authority_Wire;
   package RW renames Worldline.Recovery_Authorization_V3_Wire;
   use type Interfaces.Unsigned_8; use type Interfaces.Unsigned_32;
   use type Interfaces.Integer_64;
   subtype Raw_Digest is C.Raw_Digest;
   type Raw_Quantity is record
      Present, Negative : Interfaces.Unsigned_8;
      First, Length : Interfaces.Integer_64;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Quantity use record
      Present at 0 range 0 .. 7;
      Negative at 1 range 0 .. 7;
      First at 8 range 0 .. 63;
      Length at 16 range 0 .. 63;
   end record;
   for Raw_Quantity'Size use 192;
   for Raw_Quantity'Object_Size use 192;
   for Raw_Quantity'Alignment use 8;
   type Raw_UID is record
      Present : Interfaces.Unsigned_8;
      Value : Interfaces.Unsigned_32;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_UID use record
      Present at 0 range 0 .. 7;
      Value at 4 range 0 .. 31;
   end record;
   for Raw_UID'Size use 64;
   for Raw_UID'Object_Size use 64;
   for Raw_UID'Alignment use 4;
   type Raw_Ids is array (A.Identity_Field) of Raw_Digest with Convention => C;
   --  Preserve compiler-observed C array layout.
   for Raw_Ids'Component_Size use 264;
   for Raw_Ids'Size use 7128;
   for Raw_Ids'Object_Size use 7128;
   for Raw_Ids'Alignment use 1;
   type Raw_Rights is array (A.Operation) of Interfaces.Unsigned_8 with Convention => C;
   --  Preserve compiler-observed C array layout.
   for Raw_Rights'Component_Size use 8;
   for Raw_Rights'Size use 328;
   for Raw_Rights'Object_Size use 328;
   for Raw_Rights'Alignment use 1;
   type Raw_Binding is record
      Action : Interfaces.Unsigned_8;
      Id : Raw_Ids;
      Peer, Preparer, Owner, Target_Owner : Raw_UID;
      Policy_Epoch, Resource_Epoch : Raw_Quantity;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Binding use record
      Action at 0 range 0 .. 7;
      Id at 1 range 0 .. 7127;
      Peer at 892 range 0 .. 63;
      Preparer at 900 range 0 .. 63;
      Owner at 908 range 0 .. 63;
      Target_Owner at 916 range 0 .. 63;
      Policy_Epoch at 928 range 0 .. 191;
      Resource_Epoch at 952 range 0 .. 191;
   end record;
   for Raw_Binding'Size use 7808;
   for Raw_Binding'Object_Size use 7808;
   for Raw_Binding'Alignment use 8;
   type Raw_Grant is record
      Id, Parent, Issuer, Instance, Root_Set, Policy : Raw_Digest;
      Subject, Owner : Raw_UID;
      Allowed : Raw_Rights;
      State : Interfaces.Unsigned_8;
      Epoch, Ceiling, Issued_At, Expires_At : Raw_Quantity;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Grant use record
      Id at 0 range 0 .. 263;
      Parent at 33 range 0 .. 263;
      Issuer at 66 range 0 .. 263;
      Instance at 99 range 0 .. 263;
      Root_Set at 132 range 0 .. 263;
      Policy at 165 range 0 .. 263;
      Subject at 200 range 0 .. 63;
      Owner at 208 range 0 .. 63;
      Allowed at 216 range 0 .. 327;
      State at 257 range 0 .. 7;
      Epoch at 264 range 0 .. 191;
      Ceiling at 288 range 0 .. 191;
      Issued_At at 312 range 0 .. 191;
      Expires_At at 336 range 0 .. 191;
   end record;
   for Raw_Grant'Size use 2880;
   for Raw_Grant'Object_Size use 2880;
   for Raw_Grant'Alignment use 8;
   type Raw_Use is record
      Bound : Raw_Binding;
      State : Interfaces.Unsigned_8;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Use use record
      Bound at 0 range 0 .. 7807;
      State at 976 range 0 .. 7;
   end record;
   for Raw_Use'Size use 7816;
   for Raw_Use'Object_Size use 7872;
   for Raw_Use'Alignment use 8;
   type Raw_Evidence is record
      Effect_Binding : Raw_Binding;
      Actual_Receipt_Root, Actual_Causal_Root : Raw_Digest;
      No_Effect_Binding, Owner_Resolution : Raw_Binding;
      Quarantine_Head, Witnessed_Receipt_Head, Witnessed_Causal_Head : Raw_Digest;
      Recovery : RW.Raw_Request;
      Original_Use : Raw_Digest;
      Effect_Material_First : Interfaces.Integer_64 := 1;
      Effect_Material_Length : Interfaces.Integer_64 := 0;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Evidence use record
      Effect_Binding at 0 range 0 .. 7807;
      Actual_Receipt_Root at 976 range 0 .. 263;
      Actual_Causal_Root at 1009 range 0 .. 263;
      No_Effect_Binding at 1048 range 0 .. 7807;
      Owner_Resolution at 2024 range 0 .. 7807;
      Quarantine_Head at 3000 range 0 .. 263;
      Witnessed_Receipt_Head at 3033 range 0 .. 263;
      Witnessed_Causal_Head at 3066 range 0 .. 263;
      Recovery at 3104 range 0 .. 15743;
      Original_Use at 5072 range 0 .. 263;
      Effect_Material_First at 5112 range 0 .. 63;
      Effect_Material_Length at 5120 range 0 .. 63;
   end record;
   for Raw_Evidence'Size use 41024;
   for Raw_Evidence'Object_Size use 41024;
   for Raw_Evidence'Alignment use 8;
   type Raw_Input is record
      Schema : Interfaces.Unsigned_32;
      Mode : Interfaces.Unsigned_8;
      Bound : Raw_Binding;
      Now : Raw_Quantity;
      Facts : Raw_Evidence;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Input use record
      Schema at 0 range 0 .. 31;
      Mode at 4 range 0 .. 7;
      Bound at 8 range 0 .. 7807;
      Now at 984 range 0 .. 191;
      Facts at 1008 range 0 .. 41023;
   end record;
   for Raw_Input'Size use 49088;
   for Raw_Input'Object_Size use 49088;
   for Raw_Input'Alignment use 8;
   type Raw_Result is record
      Disposition : Interfaces.Unsigned_8;
   end record with Convention => C;
   --  Preserve compiler-observed C field layout.
   for Raw_Result use record
      Disposition at 0 range 0 .. 7;
   end record;
   for Raw_Result'Size use 8;
   for Raw_Result'Object_Size use 8;
   for Raw_Result'Alignment use 1;
   function Well_Formed (V : Raw_Quantity) return Boolean is
     (V.Present<=1 and then V.Negative<=1 and then V.First>=1 and then V.Length>=0
      and then (V.Present=1 or else (V.Negative=0 and then V.First=1 and then V.Length=0))) with Global => null;
   function Well_Formed (V : Raw_UID) return Boolean is
     (V.Present<=1 and then (V.Present=1 or else V.Value=0)) with Global => null;
   function Well_Formed (V : Raw_Binding) return Boolean is
     (V.Action<=A.Operation'Pos(A.Operation'Last)
      and then (for all F in A.Identity_Field => C.Well_Formed(V.Id(F)))
      and then Well_Formed(V.Peer) and then Well_Formed(V.Preparer)
      and then Well_Formed(V.Owner) and then Well_Formed(V.Target_Owner)
      and then Well_Formed(V.Policy_Epoch) and then Well_Formed(V.Resource_Epoch)) with Global => null;
   function Well_Formed (V : Raw_Grant) return Boolean is
     (C.Well_Formed(V.Id) and then C.Well_Formed(V.Parent) and then C.Well_Formed(V.Issuer)
      and then C.Well_Formed(V.Instance) and then C.Well_Formed(V.Root_Set) and then C.Well_Formed(V.Policy)
      and then Well_Formed(V.Subject) and then Well_Formed(V.Owner)
      and then (for all Op in A.Operation => V.Allowed(Op)<=1)
      and then V.State<=A.Grant_State'Pos(A.Grant_State'Last)
      and then Well_Formed(V.Epoch) and then Well_Formed(V.Ceiling) and then V.Ceiling.Present=1
      and then Well_Formed(V.Issued_At) and then V.Issued_At.Present=1
      and then Well_Formed(V.Expires_At) and then V.Expires_At.Present=1) with Global => null;
   function Well_Formed (V : Raw_Use) return Boolean is
     (Well_Formed(V.Bound) and then V.State<=A.Use_State'Pos(A.Use_State'Last)) with Global => null;
   function Effect_Material_Well_Formed (V : Raw_Evidence) return Boolean is
     (V.Effect_Material_Length >= 0 and then
      (V.Effect_Material_Length = 0 or else
       (V.Effect_Material_First >= 1 and then
        V.Effect_Material_First <= Interfaces.Integer_64 (A.Q.Byte_Index'Last)
        and then V.Effect_Material_Length <=
          Interfaces.Integer_64 (Worldline.Archive_Envelope.Count'Last))))
     with Global => null;
   function Well_Formed (V : Raw_Input) return Boolean is
     (V.Schema=1 and then V.Mode<=A.Command'Pos(A.Command'Last)
      and then Well_Formed(V.Bound) and then Well_Formed(V.Now) and then V.Now.Present=1
      and then Well_Formed(V.Facts.Effect_Binding) and then Well_Formed(V.Facts.No_Effect_Binding)
      and then Well_Formed(V.Facts.Owner_Resolution)
      and then C.Well_Formed(V.Facts.Actual_Receipt_Root) and then C.Well_Formed(V.Facts.Actual_Causal_Root)
      and then C.Well_Formed(V.Facts.Quarantine_Head)
      and then C.Well_Formed(V.Facts.Witnessed_Receipt_Head) and then C.Well_Formed(V.Facts.Witnessed_Causal_Head)
      and then Effect_Material_Well_Formed (V.Facts)) with Global => null;
   function Decode (V : Raw_Quantity) return A.R.Optional_Epoch is
     (if V.Present=0 then (Present=>False) else
       (Present=>True,Value=>(Negative=>V.Negative=1,First=>A.Q.Byte_Index(V.First),Length=>A.Q.Byte_Count(V.Length))))
     with Global => null, Pre => Well_Formed(V);
   function Decode (V : Raw_UID) return A.Optional_UID is
     (Present=>V.Present=1,Value=>V.Value) with Global => null, Pre => Well_Formed(V);
   function Decode (V : Raw_Binding) return A.Binding with Global => null, Pre => Well_Formed(V);
   function Decode (V : Raw_Grant) return A.Grant with Global => null, Pre => Well_Formed(V);
   function Decode (V : Raw_Use) return A.Use_Row is
     (Bound=>Decode(V.Bound),State=>A.Use_State'Val(V.State)) with Global => null, Pre => Well_Formed(V);
   function Recovery_Well_Formed(Data : A.Q.Byte_Array; V : Raw_Evidence) return Boolean is
     (V.Recovery.Schema_Version=3 and then V.Recovery.State=1 and then V.Recovery.Fresh=1
      and then V.Recovery.Historical<=1 and then V.Recovery.Grant_Eligible=0
      and then RW.Well_Formed(Data,V.Recovery.Issued_Binding)
      and then RW.Well_Formed(Data,V.Recovery.Recovered_Binding)
      and then RW.Well_Formed(V.Recovery.Native.Live_Mapping) and then RW.Well_Formed(V.Recovery.Native.Live_Root)
      and then C.Well_Formed(V.Original_Use)) with Global=>null;
   function Decode (Data : A.Q.Byte_Array; V : Raw_Evidence) return A.Evidence with Global => null,
     Pre => Well_Formed(V.Effect_Binding) and then Well_Formed(V.No_Effect_Binding)
       and then Well_Formed(V.Owner_Resolution) and then C.Well_Formed(V.Actual_Receipt_Root)
       and then C.Well_Formed(V.Actual_Causal_Root) and then C.Well_Formed(V.Quarantine_Head)
       and then C.Well_Formed(V.Witnessed_Receipt_Head) and then C.Well_Formed(V.Witnessed_Causal_Head)
       and then Recovery_Well_Formed(Data,V)
       and then Effect_Material_Well_Formed (V);
end Worldline.Operation_Authority_Wire;
