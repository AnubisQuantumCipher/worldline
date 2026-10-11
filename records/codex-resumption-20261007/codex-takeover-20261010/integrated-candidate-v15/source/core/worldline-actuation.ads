with Interfaces;
with Worldline.Collapse;

package Worldline.Actuation with SPARK_Mode is
   use type Hash;
   use type Interfaces.Unsigned_64;
   use type Collapse.Decision;

   type Entry_Identity is record
      Present : Boolean;
      Device  : Interfaces.Unsigned_64;
      Inode   : Interfaces.Unsigned_64;
   end record;

   function Same_Entry (Left, Right : Entry_Identity) return Boolean is
     (Left.Present and Right.Present
      and Left.Device = Right.Device
      and Left.Inode = Right.Inode);

   type Request is record
      Collapse_Facts        : Collapse.Collapse_Request;
      Expected_Live         : Entry_Identity;
      Observed_Live         : Entry_Identity;
      Expected_Stage        : Entry_Identity;
      Observed_Stage        : Entry_Identity;
      Expected_Marker_Digest : Hash;
      Observed_Marker_Digest : Hash;
      Payload_Durable       : Boolean;
      Recovery_Clean        : Boolean;
   end record;

   type Decision is
     (Authorized,
      Collapse_Denied,
      Live_Changed,
      Stage_Changed,
      Same_Entry_Refused,
      Marker_Mismatch,
      Payload_Not_Durable,
      Recovery_Unclean);

   function Decide (Facts : Request) return Decision
     with Global => null,
          Post =>
            (Decide'Result = Authorized) =
              (Collapse.Decide (Facts.Collapse_Facts) = Collapse.Authorized
               and Same_Entry (Facts.Expected_Live, Facts.Observed_Live)
               and Same_Entry (Facts.Expected_Stage, Facts.Observed_Stage)
               and not Same_Entry (Facts.Observed_Live, Facts.Observed_Stage)
               and Facts.Expected_Marker_Digest /= Zero_Hash
               and Facts.Expected_Marker_Digest = Facts.Observed_Marker_Digest
               and Facts.Payload_Durable
               and Facts.Recovery_Clean);
end Worldline.Actuation;
