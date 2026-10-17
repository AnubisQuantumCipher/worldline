with Lifetime;
procedure Main with SPARK_Mode is
   Text : constant String := "alpha";
   A : Lifetime.Value := Lifetime.Capture (Text);
   B : Lifetime.Value := Lifetime.Capture (Text);
begin
   pragma Assert (Lifetime.Read (A) = Text);
   pragma Assert (Lifetime.Read (B) = Text);
   pragma Assert (Lifetime.Read (A)'First = Text'First);
   Lifetime.Check_Fresh (Text);
   pragma Assert (Lifetime.Read (A) = Text);
end Main;
