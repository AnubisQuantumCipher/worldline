package First_Match_Oracle with SPARK_Mode is
   function Find
     (Motif : String; Text : String; Case_Sensitive : Boolean) return Integer
   with
     Global => null,
     Pre => Motif'Length <= 6 and then Text'Length <= 10
       and then Motif'First = 1
       and then (Text'First = 1 or else Text'First = 5)
       and then (for all C of Motif => Character'Pos (C) <= 127)
       and then (for all C of Text => Character'Pos (C) <= 127),
     Post => Find'Result = -1 or else
       (Motif'Length > 0 and then Find'Result >= Text'First
        and then Find'Result <= Text'Last - Motif'Length + 1);
end First_Match_Oracle;
