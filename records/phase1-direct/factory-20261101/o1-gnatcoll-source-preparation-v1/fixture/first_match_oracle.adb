package body First_Match_Oracle with SPARK_Mode is
   function Fold (Value : Character; Sensitive : Boolean) return Character is
   begin
      if not Sensitive and then Value in 'A' .. 'Z' then
         return Character'Val
           (Character'Pos (Value) + Character'Pos ('a') - Character'Pos ('A'));
      end if;
      return Value;
   end Fold;

   function Matches
     (Motif : String; Text : String; Start : Positive;
      Sensitive : Boolean) return Boolean
   with
     Global => null,
     Pre => Motif'Length in 1 .. 6 and then Motif'First = 1
       and then Text'Length <= 10
       and then (Text'First = 1 or else Text'First = 5)
       and then Start >= Text'First
       and then Start <= Text'Last - Motif'Length + 1
   is
   begin
      --  At most six comparisons; Find admits only fitting starts.
      for Offset in 0 .. Motif'Length - 1 loop
         pragma Loop_Invariant
           (for all Prior in 0 .. Offset - 1 =>
              Fold (Motif (Motif'First + Prior), Sensitive) =
              Fold (Text (Start + Prior), Sensitive));
         if Fold (Motif (Motif'First + Offset), Sensitive) /=
           Fold (Text (Start + Offset), Sensitive)
         then
            return False;
         end if;
      end loop;
      return True;
   end Matches;

   function Find
     (Motif : String; Text : String; Case_Sensitive : Boolean) return Integer
   is
   begin
      --  Empty motif follows this pinned implementation's convention.
      if Motif'Length = 0 or else Motif'Length > Text'Length then
         return -1;
      end if;
      --  At most ten starts, in ascending absolute String-index order.
      for Start in Text'First .. Text'Last - Motif'Length + 1 loop
         pragma Loop_Invariant
           (for all Prior in Text'First .. Start - 1 =>
              not Matches (Motif, Text, Prior, Case_Sensitive));
         if Matches (Motif, Text, Start, Case_Sensitive) then
            return Start;
         end if;
      end loop;
      return -1;
   end Find;
end First_Match_Oracle;
