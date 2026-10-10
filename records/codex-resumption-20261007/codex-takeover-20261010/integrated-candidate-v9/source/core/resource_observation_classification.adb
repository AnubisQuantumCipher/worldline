with Ada.Characters.Latin_1;
package body Resource_Observation_Classification with SPARK_Mode is
   function Current (Data : Q.Byte_Array; State : L.Ledger_State; F : Facts) return Boolean is
   begin
      return L.Context_Valid (Data, State.Scope)
        and then L.Same_Context (Data, State.Scope, F.Current)
        and then L.Same_Epoch (Data, State.Resource_Epoch, F.Current_Epoch)
        and then L.Same (Data, State.Universe_Head, F.Current_Universe_Head)
        and then L.Same (Data, State.Ledger_Head, F.Current_Ledger_Head);
   end Current;
   function Genesis_Current (Data : Q.Byte_Array; State : L.Ledger_State; F : Facts) return Boolean is
   begin
      return (Current (Data, State, F)
      and then L.Same (Data, F.Actual_Store_Genesis, F.Owner_Store_Genesis)
      and then L.Same (Data, F.Actual_Store_Id, F.Owner_Store_Id)
      and then L.Same (Data, State.Scope.Universe, F.Genesis_Universe)
      and then L.Same (Data, State.Scope.Instance, F.Genesis_Instance)
      and then L.Id_Valid (Data, F.Genesis_Context_Head)
      and then not F.Genesis_Prime.Present
      and then Zero (Data, F.Genesis_Root_Count));
   end Genesis_Current;
   function Events (Data : Q.Byte_Array; Raw : Identity) return Population is
   begin
      if Text (Data, Raw, "populated 0" & Ada.Characters.Latin_1.LF & "frozen 0" & Ada.Characters.Latin_1.LF)
        or else Text (Data, Raw, "frozen 0" & Ada.Characters.Latin_1.LF & "populated 0" & Ada.Characters.Latin_1.LF)
        or else Text (Data, Raw, "populated 0" & Ada.Characters.Latin_1.LF & "frozen 1" & Ada.Characters.Latin_1.LF)
        or else Text (Data, Raw, "frozen 1" & Ada.Characters.Latin_1.LF & "populated 0" & Ada.Characters.Latin_1.LF) then return Empty;
      elsif Text (Data, Raw, "populated 1" & Ada.Characters.Latin_1.LF & "frozen 0" & Ada.Characters.Latin_1.LF)
        or else Text (Data, Raw, "frozen 0" & Ada.Characters.Latin_1.LF & "populated 1" & Ada.Characters.Latin_1.LF)
        or else Text (Data, Raw, "populated 1" & Ada.Characters.Latin_1.LF & "frozen 1" & Ada.Characters.Latin_1.LF)
        or else Text (Data, Raw, "frozen 1" & Ada.Characters.Latin_1.LF & "populated 1" & Ada.Characters.Latin_1.LF) then return Populated;
      else return Population_Unknown; end if;
   end Events;
   function Classify (Data : Q.Byte_Array; State : L.Ledger_State; Item : L.Row; F : Facts) return L.Liveness is
   begin
      if not Common (Data, State, Item, F) then return L.Unknown;
      elsif Never_Holds (Data, Item, F) then return L.Never_Launched;
      elsif Live_Holds (Data, Item, F) then return L.Live;
      elsif Reaped_Holds (Data, Item, F) then return L.Reaped;
      else return L.Unknown; end if;
   end Classify;
end Resource_Observation_Classification;
