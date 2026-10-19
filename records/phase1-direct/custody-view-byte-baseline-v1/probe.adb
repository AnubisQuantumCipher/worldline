with Ada.Text_IO;
with Worldline.Custody_V2_Load_Input;
procedure Probe is
   package E renames Worldline.Custody_V2_Load_Input.E;
   package Q renames Worldline.Custody_V2_Load_Input.Q;
   use type E.Count;
   use type E.Encoding_Level;
   use type Q.Byte;
   function Sextet (B : Q.Byte) return E.Count is
     (if B in 65 .. 90 then E.Count (B - 65)
      elsif B in 97 .. 122 then E.Count (B - 97) + 26
      elsif B in 48 .. 57 then E.Count (B - 48) + 52
      elsif B = 43 then 62 elsif B = 47 then 63 else 0);
   function View_Length (Data : E.Bytes; Item : E.Byte_View) return E.Count
     with Global => null, Subprogram_Variant => (Decreases => Item.Level);
   function View_Byte (Data : E.Bytes; Item : E.Byte_View; Offset : E.Count)
      return Q.Byte with Global => null,
      Subprogram_Variant => (Decreases => Item.Level);
   function View_Byte (Data : E.Bytes; Item : E.Byte_View; Offset : E.Count)
      return Q.Byte is
   begin
      if Item.Level = 0 then
         if Offset >= Item.Encoded.Length or else
            not E.C.P.Valid (Data, Item.Encoded) then return 0; end if;
         return Data (Item.Encoded.First + Offset);
      end if;
      declare
         Prior : constant E.Byte_View := (Item.Encoded, Item.Level - 1);
         Base : constant E.Count := Offset / 3 * 4;
         A0 : constant E.Count := Sextet (View_Byte (Data, Prior, Base));
         A1 : constant E.Count := Sextet (View_Byte (Data, Prior, Base + 1));
         A2 : constant E.Count := Sextet (View_Byte (Data, Prior, Base + 2));
         A3 : constant E.Count := Sextet (View_Byte (Data, Prior, Base + 3));
      begin
         return Q.Byte
           (case Offset mod 3 is
              when 0 => A0 * 4 + A1 / 16,
              when 1 => A1 mod 16 * 16 + A2 / 4,
              when others => A2 mod 4 * 64 + A3);
      end;
   end View_Byte;
   function View_Length (Data : E.Bytes; Item : E.Byte_View) return E.Count is
   begin
      if Item.Level = 0 then return Item.Encoded.Length; end if;
      declare
         Prior : constant E.Byte_View := (Item.Encoded, Item.Level - 1);
         L : constant E.Count := View_Length (Data, Prior);
      begin
         if L = 0 then return 0; end if;
         if L mod 4 /= 0 then return 0; end if;
         return L / 4 * 3 -
           (if View_Byte (Data, Prior, L - 1) = 61 then
              (if View_Byte (Data, Prior, L - 2) = 61 then 2 else 1) else 0);
      end;
   end View_Length;
   Data : constant E.Bytes := [65, 81, 73, 68];
   Item : constant E.Byte_View := ((1, 4), 1);
   Actual : Q.Byte;
begin
   Actual := View_Byte (Data, Item, E.Count'Last);
   pragma Assert (Actual = 0);
   Ada.Text_IO.Put_Line ("PASS out-of-view byte is zero without arithmetic overflow");
end Probe;
