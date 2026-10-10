package body Worldline.Root_Custody_Phase_Values with SPARK_Mode is
   function Single_Root_Image
     (Before : M.Root_State; Event : M.Event_Record) return M.Root_State
   is
      Result : M.Root_State := Before;
   begin
      Result.Phase := Root_Target (Before, Event.Kind);
      Result.Head := Event.Event_Id;
      if Event.Kind = M.Prepared_Event then
         Result.Operation := Event.Operation;
      end if;
      if Event.Kind = M.Front_Closed_Event then
         Result.Owners_Open := False;
      end if;
      case Event.Kind is
         when M.Held_Event => Result.Physical.Launched := True;
         when M.Closed_NS_Event => Result.Physical.NS := True;
         when M.Closed_Outer_Event => Result.Physical.Outer := True;
         when M.Closed_Raw_Event => Result.Physical.Raw := True;
         when M.Closed_Witness_Event => Result.Physical.Witness := True;
         when M.Physical_Settled_Event => Result.Physical.Settled := True;
         when others => null;
      end case;
      return Result;
   end Single_Root_Image;
end Worldline.Root_Custody_Phase_Values;
