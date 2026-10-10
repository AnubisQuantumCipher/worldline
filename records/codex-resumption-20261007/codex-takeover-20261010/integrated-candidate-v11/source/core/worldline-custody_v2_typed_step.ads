with Worldline.Custody_V2_Archive_Chain;
with Worldline.Custody_V2_Fold_Rows;
with Worldline.Root_Custody_Request_Abandon;
package Worldline.Custody_V2_Typed_Step with SPARK_Mode is
   package C renames Worldline.Custody_V2_Archive_Chain;
   package F renames Worldline.Custody_V2_Fold_Rows;
   package A renames Worldline.Root_Custody_Request_Abandon.A;
   package RA renames Worldline.Root_Custody_Request_Abandon;
   package M renames A.M;
   package Q renames A.Q;
   use type Q.Byte_Count;
   use type M.Event_Kind;
   use type M.Actor;
   use type M.Subject_Kind;
   use type M.Root_State_Array;
   use type M.Subject_State_Array;
   function Kind_Name (Kind : M.Event_Kind) return String with Global => null;
   type Decode_Status is (Malformed_Row, Decoded);
   type Decoded_Event (Status : Decode_Status := Malformed_Row) is record
      case Status is
         when Decoded => Value : M.Event_Record;
         when Malformed_Row => null;
      end case;
   end record;
   function Decode (Data : C.E.Bytes; Raw : C.Event_Row) return Decoded_Event
     with Global => null,
       Post => (if Decode'Result.Status = Decoded then C.Base_Matches (Data, Raw));
   -- Independent valid transitions reuse complete existing Legal clauses,
   -- not table shape alone. Actual X4 and prestate fold authority remain required.
   procedure Apply_Abandon
     (Data : C.E.Bytes; Raw : C.Event_Row; Roots : in out M.Root_State_Array;
      Events : A.R.Retained_Events; Alternatives : A.Alternative_Rows;
      Expected : A.Expected_Root; Applied : out Boolean)
     with Global => null, Always_Terminates,
       Post => (if not Applied then Roots = Roots'Old);
   procedure Apply_Request_Abandon
     (Data : C.E.Bytes; Raw : C.Event_Row; Roots : in out M.Root_State_Array;
      Subjects : in out M.Subject_State_Array; Events : A.R.Retained_Events;
      Alternatives : A.Alternative_Rows; Root : A.Expected_Root;
      Expected : RA.Expected_Request; Applied : out Boolean)
     with Global => null, Always_Terminates,
       Post => Roots = Roots'Old and then (if not Applied then Subjects = Subjects'Old);
   type Fold_Status is (Native_Fold_Refused, Complete_Fold_And_Rows_Equal);
   type Fold_Result is record
      Status : Fold_Status := Native_Fold_Refused;
      Native_Status : Q.Byte_Count := 3;
      Position : Q.Byte_Count := 0;
   end record;
   -- The complete lossless load envelope supplies native genesis, every raw
   -- event/evidence/table/head and authentic owner source. No decode-only
   -- nonempty-chain result and no legacy partial-input overload survives.
   function Fold_From_S0 (Data : C.E.Bytes) return Fold_Result
      with Global => null,
      Post => (if Fold_From_S0'Result.Status = Complete_Fold_And_Rows_Equal then
         Fold_From_S0'Result.Native_Status <= 2 and then
         Fold_From_S0'Result.Position = 0);
end Worldline.Custody_V2_Typed_Step;
