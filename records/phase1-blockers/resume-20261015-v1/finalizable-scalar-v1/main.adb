with Lifetime;
procedure Main with SPARK_Mode is
   A : Lifetime.Value;
   B : Lifetime.Value;
begin
   A.Data := 1;
   B := A;
   Lifetime.Increment (A);
   pragma Assert (A.Data = 2 and B.Data = 1);
end Main;
