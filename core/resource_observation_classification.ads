with Ada.Characters.Latin_1;
with Resource_Run_Ledger;
with Resource_Quantities;
with SPARK.Big_Integers;
package Resource_Observation_Classification with SPARK_Mode is
   package L renames Resource_Run_Ledger;
   package Q renames Resource_Quantities;
   use SPARK.Big_Integers;
   use type Q.Byte;
   use type Q.Byte_Count;
   use type L.Phase;
   use type L.Liveness;
   subtype Identity is L.Identity;
   type Journal_Phase is (Unavailable, Never_Dispatched, Dispatch_Intended,
                          Namespace_Held, Namespace_Closed);
   type Population is (Population_Unknown, Empty, Populated);
   type Facts is record
      Current : L.Context;
      Current_Epoch : Q.Optional_Quantity;
      Retained : L.Binding;
      Current_Universe_Head, Current_Ledger_Head : Identity;
      Intent, Dispatch, Observation_Head : Identity;
      Actual_Unit, Cgroup, Invocation : Identity;
      Namespace, Held_Namespace, Peer, Held_Peer : Identity;
      Helper_Image, Expected_Helper_Image : Identity;
      Challenge, Held_Challenge : Identity;
      Protocol, Closed_Event, Namespace_Wait, Helper_Wait : Identity;
      Cgroup_Events, Cgroup_Type, Manager_Delegate : Identity;
      Cgroup_Owner, Cgroup_Group_Write, Cgroup_Other_Write : Q.Optional_Quantity;
      Actual_Store_Genesis, Actual_Store_Id, Owner_Store_Genesis, Owner_Store_Id, Genesis_Universe, Genesis_Instance, Genesis_Context_Head, Genesis_Prime : Identity;
      Genesis_Root_Count : Q.Optional_Quantity;
      Phase : Journal_Phase;
   end record;
   function Text (Data : Q.Byte_Array; Item : Identity; Value : String) return Boolean is
     (L.Id_Valid (Data, Item) and then Value'Length > 0 and then Item.Value.Length = Value'Length
      and then (for all Offset in Q.Byte_Count range 0 .. Item.Value.Length - 1 =>
        Data (Item.Value.First + Offset) = Q.Byte (Character'Pos (Value (Value'First + Integer (Offset))))))
   with Global => null;
   function Events (Data : Q.Byte_Array; Raw : Identity) return Population is
     (if Text (Data, Raw, "populated 0" & Ada.Characters.Latin_1.LF & "frozen 0" & Ada.Characters.Latin_1.LF)
       or else Text (Data, Raw, "frozen 0" & Ada.Characters.Latin_1.LF & "populated 0" & Ada.Characters.Latin_1.LF)
       or else Text (Data, Raw, "populated 0" & Ada.Characters.Latin_1.LF & "frozen 1" & Ada.Characters.Latin_1.LF)
       or else Text (Data, Raw, "frozen 1" & Ada.Characters.Latin_1.LF & "populated 0" & Ada.Characters.Latin_1.LF) then Empty
      elsif Text (Data, Raw, "populated 1" & Ada.Characters.Latin_1.LF & "frozen 0" & Ada.Characters.Latin_1.LF)
       or else Text (Data, Raw, "frozen 0" & Ada.Characters.Latin_1.LF & "populated 1" & Ada.Characters.Latin_1.LF)
       or else Text (Data, Raw, "populated 1" & Ada.Characters.Latin_1.LF & "frozen 1" & Ada.Characters.Latin_1.LF)
       or else Text (Data, Raw, "frozen 1" & Ada.Characters.Latin_1.LF & "populated 1" & Ada.Characters.Latin_1.LF) then Populated
      else Population_Unknown)
   with Global => null;
   function Zero (Data : Q.Byte_Array; Item : Q.Optional_Quantity) return Boolean is
     (Resource_Run_Ledger.T.Epoch_Valid (Data, Item)
      and then Q.Is_Zero (Data, Item.Value))
   with Global => null,
     Post => Zero'Result =
       (Resource_Run_Ledger.T.Epoch_Valid (Data, Item)
        and then Q.Value (Data, Item.Value) = To_Big_Integer (0));
   function Current_Reference (Data : Q.Byte_Array; State : L.Ledger_State; F : Facts) return Boolean is
     (L.Context_Valid (Data, State.Scope)
      and then L.Same_Context (Data, State.Scope, F.Current)
      and then L.Same_Epoch (Data, State.Resource_Epoch, F.Current_Epoch)
      and then L.Same (Data, State.Universe_Head, F.Current_Universe_Head)
      and then L.Same (Data, State.Ledger_Head, F.Current_Ledger_Head)) with Ghost, Global => null;
   function Current (Data : Q.Byte_Array; State : L.Ledger_State; F : Facts) return Boolean
   with Global => null, Post => Current'Result = Current_Reference (Data, State, F);
   function Genesis_Reference (Data : Q.Byte_Array; State : L.Ledger_State; F : Facts) return Boolean is
     (Current (Data, State, F)
      and then L.Same (Data, F.Actual_Store_Genesis, F.Owner_Store_Genesis)
      and then L.Same (Data, F.Actual_Store_Id, F.Owner_Store_Id)
      and then L.Same (Data, State.Scope.Universe, F.Genesis_Universe)
      and then L.Same (Data, State.Scope.Instance, F.Genesis_Instance)
      and then L.Id_Valid (Data, F.Genesis_Context_Head)
      and then not F.Genesis_Prime.Present
      and then Zero (Data, F.Genesis_Root_Count)) with Ghost, Global => null;
   function Genesis_Current (Data : Q.Byte_Array; State : L.Ledger_State; F : Facts) return Boolean
   with Global => null, Post => Genesis_Current'Result = Genesis_Reference (Data, State, F);
   function Common (Data : Q.Byte_Array; State : L.Ledger_State; Item : L.Row; F : Facts) return Boolean is
     (L.Context_Valid (Data, State.Scope) and then L.Row_Valid (Data, Item)
      and then L.Same_Context (Data, State.Scope, Item.Scope)
      and then Current (Data, State, F)
      and then L.Same_Binding (Data, Item.Bound, F.Retained)
      and then L.Id_Valid (Data, F.Intent) and then L.Id_Valid (Data, F.Observation_Head))
   with Global => null;
   function Custody (Data : Q.Byte_Array; Item : L.Row; F : Facts) return Boolean is
     (L.Id_Valid (Data, F.Dispatch) and then L.Id_Valid (Data, F.Namespace)
      and then L.Same (Data, F.Namespace, F.Held_Namespace)
      and then L.Same (Data, F.Peer, F.Held_Peer)
      and then L.Same (Data, F.Helper_Image, F.Expected_Helper_Image)
      and then L.Same (Data, F.Challenge, F.Held_Challenge)
      and then L.Same (Data, Item.Planned_Unit, F.Actual_Unit)
      and then L.Id_Valid (Data, F.Cgroup) and then L.Id_Valid (Data, F.Invocation)
      and then (if L.Has_Effect (Item) then
        L.Same (Data, Item.Actual_Unit, F.Actual_Unit)
        and then L.Same (Data, Item.Cgroup, F.Cgroup)
        and then L.Same (Data, Item.Invocation, F.Invocation))
      and then Zero (Data, F.Cgroup_Owner)
      and then Zero (Data, F.Cgroup_Group_Write)
      and then Zero (Data, F.Cgroup_Other_Write)
      and then Text (Data, F.Cgroup_Type, "domain" & Ada.Characters.Latin_1.LF)
      and then Text (Data, F.Manager_Delegate, "no")) with Global => null;
   function Never_Holds (Data : Q.Byte_Array; Item : L.Row; F : Facts) return Boolean is
     (L.Id_Valid (Data, F.Intent) and then F.Phase = Never_Dispatched and then not F.Dispatch.Present
      and then not F.Protocol.Present and then not F.Peer.Present
      and then not F.Namespace.Present and then not F.Actual_Unit.Present
      and then not F.Cgroup.Present and then not F.Invocation.Present
      and then Item.State in L.Reserved | L.Launch_Intent | L.Settlement_Unknown
      and then not L.Has_Effect (Item)) with Global => null;
   function Live_Holds (Data : Q.Byte_Array; Item : L.Row; F : Facts) return Boolean is
     (F.Phase = Namespace_Held and then Custody (Data, Item, F)
      and then Text (Data, F.Protocol, "HELD") and then Events (Data, F.Cgroup_Events) = Populated
      and then Text (Data, F.Namespace_Wait, "PIDFD_LIVE")
      and then Text (Data, F.Helper_Wait, "PIDFD_LIVE")) with Global => null;
   function Reaped_Holds (Data : Q.Byte_Array; Item : L.Row; F : Facts) return Boolean is
     (F.Phase = Namespace_Closed and then Custody (Data, Item, F)
      and then L.Id_Valid (Data, F.Closed_Event)
      and then Text (Data, F.Protocol, "CLOSED_ECHILD")
      and then Text (Data, F.Namespace_Wait, "PIDFD_TERMINAL")
      and then Text (Data, F.Helper_Wait, "PIDFD_TERMINAL")
      and then Events (Data, F.Cgroup_Events) = Empty) with Global => null;
   function Reference (Data : Q.Byte_Array; State : L.Ledger_State; Item : L.Row; F : Facts) return L.Liveness is
     (if not Common (Data, State, Item, F) then L.Unknown
      elsif Never_Holds (Data, Item, F) then L.Never_Launched
      elsif Live_Holds (Data, Item, F) then L.Live
      elsif Reaped_Holds (Data, Item, F) then L.Reaped else L.Unknown)
   with Ghost, Global => null;
   function Classify (Data : Q.Byte_Array; State : L.Ledger_State; Item : L.Row; F : Facts) return L.Liveness
   with Global => null,
     Post => Classify'Result = Reference (Data, State, Item, F)
       and then (if Classify'Result = L.Reaped then Common (Data, State, Item, F) and then Reaped_Holds (Data, Item, F))
       and then (if Classify'Result = L.Never_Launched then Common (Data, State, Item, F) and then Never_Holds (Data, Item, F));
end Resource_Observation_Classification;
