with Worldline.Custody_V2_History;
package Worldline.Custody_V2_Request_Step with SPARK_Mode is
   package H renames Worldline.Custody_V2_History;
   package D renames H.D;
   package C renames H.C;
   package RA renames D.RA;
   package A renames D.A;
   package M renames D.M;
   package Q renames D.Q;
   use type Q.Byte_Count;
   use type M.Root_State_Array;
   use type M.Subject_State_Array;
   use type RA.Decision_Status;
   type Status is (Archive_Or_Decode_Refused, Wrong_Event_Family,
                   Native_Request_Decided_Prestate_Fold_Open);
   type Observation (State : Status := Archive_Or_Decode_Refused) is record
      Position : Q.Byte_Count := 0;
      case State is
         when Native_Request_Decided_Prestate_Fold_Open =>
            Decision : RA.Decision;
         when others => null;
      end case;
   end record;
   -- Every field of the original expected root/request, whole alternative
   -- roster, whole roots/subjects and complete authenticated history is used.
   -- A successful value step still requires predecessor fold/provenance.
   procedure Apply
     (Data : C.E.Bytes; Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text : C.E.Span;
      Raw : C.Event_Rows; Heads : C.Head_Rows; Position : Q.Byte_Index;
      Roots : in out M.Root_State_Array; Subjects : in out M.Subject_State_Array;
      Alternatives : A.Alternative_Rows; Root : A.Expected_Root;
      Expected : RA.Expected_Request; Result : out Observation)
   with Global => null, Always_Terminates,
     Pre => Position in Raw'Range,
     Post => Roots = Roots'Old and then
       (if Result.State /= Native_Request_Decided_Prestate_Fold_Open or else
           Result.Decision.Status /= RA.Append_Request_Abandon
        then Subjects = Subjects'Old);
end Worldline.Custody_V2_Request_Step;
