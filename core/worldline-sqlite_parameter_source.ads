with Worldline.Retained_Evidence_Replay;

-- Original sqlite3 binding and SQLite 3.53.4 numeric TEXT representation.
-- No database/source custody or operation authority follows from this relation.
package Worldline.SQLite_Parameter_Source with SPARK_Mode is
   package R renames Worldline.Retained_Evidence_Replay;
   package E renames R.E;
   function Truthy
     (Data : E.Bytes; Selector : E.Span; Scoped : Boolean := False)
      return Boolean with Global => null;
   function Text_Affinity_Matches
     (Data : E.Bytes; Selector, Cast_Text : E.Span; Scoped : Boolean := False;
      Precision : Positive := 17) return Boolean with Global => null;
   function Parameter_Equals_Text
     (Data : E.Bytes; Selector, Column : E.Span; Scoped : Boolean := False;
      Precision : Positive := 17) return Boolean with Global => null;
end Worldline.SQLite_Parameter_Source;
