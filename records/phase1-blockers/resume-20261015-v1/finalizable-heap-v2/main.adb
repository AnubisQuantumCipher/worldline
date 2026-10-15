with Lifetime;
procedure Main with SPARK_Mode is
   A : Lifetime.Value := Lifetime.Make ("alpha duplicate alpha");
   B : Lifetime.Value;
begin
   B := A;
   pragma Assert (Lifetime.Read (A) = "alpha duplicate alpha");
   pragma Assert (Lifetime.Read (B) = "alpha duplicate alpha");
   Lifetime.Touch (A);
   Lifetime.Replace_First (A, 'z');
   pragma Assert (Lifetime.Read (B) = "alpha duplicate alpha");
   pragma Assert (Lifetime.Read (A) = "zlpha duplicate alpha");
end Main;
