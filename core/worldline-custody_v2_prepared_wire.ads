with Worldline.Custody_V2_Prepared;
with Worldline.Operation_Authority_Wire;
package Worldline.Custody_V2_Prepared_Wire with SPARK_Mode is
   package P renames Worldline.Custody_V2_Prepared;
   package W renames Worldline.Operation_Authority_Wire;
   package O renames P.O;
   package Q renames P.Q;
   package M renames P.M;
   package CW renames W.C;
   use type M.Root_State;
   type Raw_Grants is array (Q.Byte_Index range <>) of W.Raw_Grant;
   type Raw_Uses is array (Q.Byte_Index range <>) of W.Raw_Use;
   type Raw_Rows is array (Q.Byte_Index range <>) of CW.Raw_Row;
   type Status is (Malformed_Reserve, Malformed_Intent, Malformed_Roster,
     Operation_Or_Grant_Changed, Native_Prepared_Refused,
     Prepared_Value_Step_Only);
   -- No authentication flag: this is a checked value adapter, never X4 Ready.
   -- Original snapshot archives and protected acquisition remain caller inputs
   -- to the still-open authenticated fold/export boundary.
   procedure Try_Next
     (Data : Q.Byte_Array; Event : P.C.Event_Row; Before : M.Root_State;
      Reserve, Intent : W.Raw_Input; Reserve_Grants, Intent_Grants : Raw_Grants;
      Reserve_Uses, Intent_Uses : Raw_Uses;
      Reserve_Receipts, Reserve_Events, Intent_Receipts, Intent_Events : Raw_Rows;
      After : out M.Root_State; Disposition : out Status)
   with Global => null, Always_Terminates,
     Post => (if Disposition /= Prepared_Value_Step_Only then After = Before);
end Worldline.Custody_V2_Prepared_Wire;
