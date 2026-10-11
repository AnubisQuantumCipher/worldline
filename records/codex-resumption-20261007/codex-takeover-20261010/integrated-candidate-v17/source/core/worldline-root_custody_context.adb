--  Termination remains REQUIRED for every precondition-satisfying input:
--  these ordinary side-effect-free SPARK functions have the intrinsic
--  termination obligation documented by this toolchain's E0016. Explicit
--  per-function Always_Terminates is illegal here; no obligation is waived.
package body Worldline.Root_Custody_Context with SPARK_Mode is
   --  Called only after selecting a non-Ended current row. No historical
   --  owner meaning is assigned by this internal helper.
   function Current_Row_Owner (State : M.Root_State) return M.Owner
   with Pre => State.Phase /= M.Ended, Global => null,
     Post => Current_Row_Owner'Result = Original_Owner_Equation (State)
   is
   begin
      return Original_Owner_Equation (State);
   end Current_Row_Owner;

   function Current_Store_Owner
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Reference : Root_Reference) return Store_Owner_Result
   is
   begin
      if not Root_Roster_Consistent (Data, Roots) then
         return (Status => Binding_Not_Established);
      elsif Roots'Length = 0 then
         return (Status => Implicit_Genesis);
      end if;
      for I in Roots'Range loop
         if Roots (I).Phase /= M.Ended and then
           Root_Joined (Data, Roots (I), Reference)
         then
            return (Status => Projected, Index => I,
                    Value => Current_Row_Owner (Roots (I)));
         end if;
         --  A matching current row returned above. Every examined row in
         --  the complete prefix therefore fails the original selection.
         pragma Loop_Invariant
           (for all J in Roots'First .. I =>
              not (Roots (J).Phase /= M.Ended and then
                   Root_Joined (Data, Roots (J), Reference)));
      end loop;
      return (Status => Binding_Not_Established);
   end Current_Store_Owner;

   function Physical_Actor
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Original_Root : Root_Reference) return Physical_Actor_Result
   is
   begin
      if not Root_Roster_Consistent (Data, Roots) or else
        not L.Id_Valid (Data, Original_Root.Operation)
      then
         return (Status => Physical_Binding_Not_Established);
      end if;
      for I in Roots'Range loop
         if Root_Joined (Data, Roots (I), Original_Root) then
            return
              (Status => Physical_Projected, Index => I,
               Value =>
                 (if Roots (I).Owners_Open or else Roots (I).Phase in
                    M.Abandoned | M.Front_Retained_Escrow | M.Handoff_Aborted
                  then M.Front else M.Collector));
         end if;
         --  Physical selection includes historical Ended rows. Retain the
         --  exact original-root join; do not substitute current ownership.
         pragma Loop_Invariant
           (for all J in Roots'First .. I =>
              not Root_Joined (Data, Roots (J), Original_Root));
      end loop;
      return (Status => Physical_Binding_Not_Established);
   end Physical_Actor;
end Worldline.Root_Custody_Context;
