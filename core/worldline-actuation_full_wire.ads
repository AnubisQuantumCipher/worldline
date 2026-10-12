with Interfaces;
with Worldline.Actuation;
with Worldline.Collapse_Wire;
package Worldline.Actuation_Full_Wire with SPARK_Mode is
   package A renames Worldline.Actuation;
   package C renames Worldline.Collapse_Wire;
   use type C.Byte; use type Interfaces.Unsigned_64;
   type Raw_Entry is record
      Present:C.Byte; Device,Inode:Interfaces.Unsigned_64;
   end record with Convention=>C;
   type Raw_Request is record
      Collapse_Facts:C.Raw_Request;
      Expected_Live,Observed_Live,Expected_Stage,Observed_Stage:Raw_Entry;
      Expected_Marker_Digest,Observed_Marker_Digest:Hash;
      Payload_Durable,Recovery_Clean:C.Byte;
   end record with Convention=>C;
   function Well_Formed(E:Raw_Entry) return Boolean is
     (E.Present<=1 and then (E.Present=1 or else (E.Device=0 and E.Inode=0))) with Global=>null;
   function Well_Formed(R:Raw_Request) return Boolean is
     (C.Well_Formed(R.Collapse_Facts) and then Well_Formed(R.Expected_Live)
      and then Well_Formed(R.Observed_Live) and then Well_Formed(R.Expected_Stage)
      and then Well_Formed(R.Observed_Stage) and then R.Payload_Durable<=1 and then R.Recovery_Clean<=1)
      with Global=>null;
   function Decode(E:Raw_Entry) return A.Entry_Identity is
     (Present=>E.Present=1,Device=>E.Device,Inode=>E.Inode) with Global=>null,Pre=>Well_Formed(E);
   function Decode(R:Raw_Request) return A.Request is
     (Collapse_Facts=>C.Decode(R.Collapse_Facts),Expected_Live=>Decode(R.Expected_Live),
      Observed_Live=>Decode(R.Observed_Live),Expected_Stage=>Decode(R.Expected_Stage),
      Observed_Stage=>Decode(R.Observed_Stage),Expected_Marker_Digest=>R.Expected_Marker_Digest,
      Observed_Marker_Digest=>R.Observed_Marker_Digest,Payload_Durable=>R.Payload_Durable=1,
      Recovery_Clean=>R.Recovery_Clean=1) with Global=>null,Pre=>Well_Formed(R);
end Worldline.Actuation_Full_Wire;
