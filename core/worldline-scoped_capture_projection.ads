with SPARK.Big_Integers;
with Worldline.Retained_Evidence_Replay;

-- Complete factual projection; authentication, lifecycle and original native
-- policies are separate conjuncts. No producer readiness/matches flags.
package Worldline.Scoped_Capture_Projection with SPARK_Mode is
   package R renames Worldline.Retained_Evidence_Replay;
   package E renames R.E;
   use type E.Count;
   function Scoped_Capture_Matches
     (Data : E.Bytes; Observation, Provenance : E.Span) return Boolean
     with Global => null;
   function Subject_Capture_Matches
     (Data : E.Bytes; Subject, Primary, Packet : E.Span) return Boolean
     with Global => null;
   function Value_Matches (Data : E.Bytes; Left, Right : E.Span) return Boolean with Global => null;
   function JSON_Value_Matches (Data : E.Bytes; JSON, Item : E.Span) return Boolean with Global => null;
   function Current_Source_Matches (Data : E.Bytes; Packet, Projection : E.Span) return Boolean with Global => null;
   function Hash_Field (Data : E.Bytes; Raw, Id : E.Span; Prefix : String := "") return Boolean with Global => null;
   function Property (Data : E.Bytes; Manager : E.Span; Name : String; Id : E.Span) return Boolean with Global => null;
   function Number (Data : E.Bytes; Item : E.Span) return SPARK.Big_Integers.Valid_Big_Integer with Global => null;
   function Id_Hex (Data : E.Bytes; Id, Encoded : E.Span) return Boolean with Global => null;
   function Namespace_Matches (Data : E.Bytes; Id, Identity : E.Span) return Boolean with Global => null;
   function Head_Source_Matches (Data : E.Bytes; Fact, Source : E.Span) return Boolean with Global => null;
   function Role_Roster_Matches (Data : E.Bytes; Inventory : E.Span) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Inventory.Length);
   function Member_Value (Data : E.Bytes; Item, Name : E.Span) return E.Span with Global => null;
   function Raw_Source_Field (Data : E.Bytes; Item : E.Span; Name : String) return E.Span with Global => null;
   function Process_Source_Matches (Data : E.Bytes; Item, Inventory, Namespace, Unit, Invocation : E.Span) return Boolean with Global => null;
   function Scoped_Descriptor_Alias_Matches (Data, Actual_Data : E.Bytes;
     Inventory, Role, FD, Identity : E.Span) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Inventory.Length);
   function JSON_Source_Value_Matches (Data : E.Bytes; Raw, Value : E.Span; Canonical : Boolean; Scoped : Boolean := False) return Boolean with Global => null;
   function Scoped_Record_Matches (Data : E.Bytes; Encoded, Typed : E.Span; Scoped, Typed_Scoped : Boolean := False) return Boolean with Global => null;
   function Source_Record_Matches (Data : E.Bytes; Encoded, Raw_Source : E.Span; Scoped, Raw_Scoped : Boolean := False) return Boolean with Global => null;
   function Line (Raw : E.Bytes; Name : String; Separator : E.Q.Byte) return E.Span with Global => null;
   function Word (Raw : E.Bytes; Item : E.Span; Index : Positive) return E.Span with Global => null,
     Post => Word'Result.Length = 0 or else
       (Word'Result.First >= Item.First and then
        Word'Result.Length <= Item.Length - (Word'Result.First - Item.First));
   function Decimal (Raw : E.Bytes; Item : E.Span) return SPARK.Big_Integers.Valid_Big_Integer with Global => null;
   function Stat_Number (Raw : E.Bytes; Index : Positive) return SPARK.Big_Integers.Valid_Big_Integer with Global => null;
   function Process_Cgroup_Matches (Data : E.Bytes; Raw, Native : E.Span) return Boolean with Global => null;
   function Maps_Match (Data : E.Bytes; Maps, Inventory : E.Span) return Boolean with Global => null;
   function Archive_Image_Matches (Data : E.Bytes; Image, Value : E.Span;
     Image_Scoped, Value_Scoped : Boolean := False; Carrier_Scoped : Boolean := False) return Boolean
     renames R.Archive_Image_Matches;
end Worldline.Scoped_Capture_Projection;
