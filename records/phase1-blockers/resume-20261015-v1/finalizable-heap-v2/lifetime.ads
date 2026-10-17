package Lifetime with SPARK_Mode is
   type Value is private;
   function Read (Object : Value) return String with Global => null;
   function Make (Text : String) return Value
     with Global => null, Post => Read (Make'Result) = Text
       and then Read (Make'Result)'First = Text'First
       and then Read (Make'Result)'Last = Text'Last;
   procedure Touch (Object : in out Value)
     with Global => null, Post => Read (Object) = Read (Object'Old);
   procedure Replace_First (Object : in out Value; Ch : Character)
     with Global => null, Pre => Read (Object)'Length > 0,
          Post => Read (Object)'First = Read (Object'Old)'First
            and then Read (Object)'Last = Read (Object'Old)'Last
            and then (for all K in Read (Object'Old)'Range =>
              Read (Object) (K) =
                (if K = Read (Object'Old)'First then Ch
                 else Read (Object'Old) (K)));
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
