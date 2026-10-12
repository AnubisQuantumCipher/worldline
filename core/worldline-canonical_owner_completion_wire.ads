with Interfaces;
with Worldline.Canonical_Owner_Completion;
with Worldline.Canonical_Exchange_Wire;
package Worldline.Canonical_Owner_Completion_Wire with SPARK_Mode is
   package Y renames Worldline.Canonical_Owner_Completion;
   package V renames Worldline.Canonical_Exchange_Wire;
   package W renames V.W;
   use type Interfaces.Unsigned_8;
   type Raw_Input is record
      Historical : V.Raw_Input;
      Current : W.W.Raw_Input;
   end record with Convention=>C;
   type Raw_Result is record Disposition : Interfaces.Unsigned_8; end record with Convention=>C;
   function Well_Formed(Data:Y.A.Q.Byte_Array; Item:Raw_Input) return Boolean is
     (V.Well_Formed(Data,Item.Historical)
      and then Item.Historical.Before=Y.X.Phase'Pos(Y.X.Quarantined)
      and then Item.Historical.Mode=Y.X.Command'Pos(Y.X.Resolve_Owner)
      and then W.W.Well_Formed(Item.Current)
      and then Item.Current.Mode=Y.A.Command'Pos(Y.A.Replay_Use)
      and then W.W.Recovery_Well_Formed(Data,Item.Current.Facts))
      with Global=>null;
end Worldline.Canonical_Owner_Completion_Wire;
