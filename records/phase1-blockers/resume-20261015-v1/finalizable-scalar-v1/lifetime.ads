package Lifetime with SPARK_Mode is
   type Value is record
      Data : Integer := 0;
   end record
     with Finalizable => (Adjust => Adjust, Finalize => Finalize,
                          Relaxed_Finalization => False);
   procedure Adjust (Object : in out Value)
     with Global => null, Post => Object.Data = Object.Data'Old;
   procedure Finalize (Object : in out Value)
     with Global => null, Post => Object.Data = Object.Data'Old;
   procedure Increment (Object : in out Value)
     with Global => null, Pre => Object.Data < Integer'Last,
          Post => Object.Data = Object'Old.Data + 1;
end Lifetime;
