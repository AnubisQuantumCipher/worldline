package Lifetime with SPARK_Mode is
   type Value is private;
   function Read (Object : Value) return String with Global => null;
   function Capture (Text : String) return Value
     with Global => null,
       Post => Read (Capture'Result) = Text
         and Read (Capture'Result)'First = Text'First
         and Read (Capture'Result)'Last = Text'Last;
   procedure Check_Fresh (Text : String)
     with Global => null,
       Post => Read (Capture (Text)'Old) = Text
         and Read (Capture (Text)'Old)'First = Text'First
         and Read (Capture (Text)'Old)'Last = Text'Last;
private
   type Text_Access is access String;
   type Value is record
      Data : Text_Access := null;
   end record
     with Finalizable => (Adjust => Adjust, Finalize => Finalize,
                          Relaxed_Finalization => False);
   procedure Adjust (Object : in out Value)
     with Global => null,
       Post => Read (Object) = Read (Object)'Old
         and Read (Object)'First = Read (Object)'First'Old
         and Read (Object)'Last = Read (Object)'Last'Old;
   procedure Finalize (Object : in out Value)
     with Global => null, Post => Object.Data = null;
end Lifetime;
