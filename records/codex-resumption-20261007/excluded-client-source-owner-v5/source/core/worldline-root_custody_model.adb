package body Worldline.Root_Custody_Model with SPARK_Mode is
   function Actor_Owner (Item : Actor) return Owner is
   begin
      case Item is
         when Front      => return Front;
         when Worker     => return Worker;
         when Collector  => return Collector;
         when Reconciler => return Reconciler;
      end case;
   end Actor_Owner;

   function Is_Worker_Phase (Phase : Root_Phase) return Boolean is
   begin
      case Phase is
         when Worker_Owned | Original_Result | Handler_Terminal |
              Worker_Relinquish =>
            return True;
         when others =>
            return False;
      end case;
   end Is_Worker_Phase;

   function Same_Present_Digest
     (Left, Right : Optional_Digest) return Boolean
   is
   begin
      if not Left.Present or else not Right.Present then
         return False;
      end if;
      return Left.Value = Right.Value;
   end Same_Present_Digest;

   function Failed_Append (Cause : Cause_Record)
      return Optional_Replay_Identity
   is
   begin
      case Cause.Class is
         when C_Append =>
            return (Present => True, Value => Cause.Failed_Event);
         when C_Channel | C_Deadline | C_Evidence =>
            return (Present => False);
      end case;
   end Failed_Append;
end Worldline.Root_Custody_Model;
