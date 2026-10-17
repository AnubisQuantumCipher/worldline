package body Lifetime with SPARK_Mode is
   procedure Adjust (Object : in out Value) is
   begin
      null;
   end Adjust;
   procedure Finalize (Object : in out Value) is
   begin
      null;
   end Finalize;
   procedure Increment (Object : in out Value) is
   begin
      Object.Data := Object.Data + 1;
   end Increment;
end Lifetime;
