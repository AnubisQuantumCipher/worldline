with Worldline.Custody_V2_Load_Input;
package Projection_Aggregate_Probe with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package S renames L.S;
   procedure Root_Loop (SQL : L.SQL_Rows; Rows : out S.Root_Rows)
     with Post => (for all Row of Rows => Row.Present);
   procedure Root_Aggregate (SQL : L.SQL_Rows; Rows : out S.Root_Rows)
     with Post => (for all Row of Rows => Row.Present);
   procedure Subject_Loop (SQL : L.SQL_Rows; Rows : out S.Subject_Rows)
     with Post => (for all Row of Rows => Row.Present);
   procedure Subject_Aggregate (SQL : L.SQL_Rows; Rows : out S.Subject_Rows)
     with Post => (for all Row of Rows => Row.Present);
   procedure Root_Initialized (SQL : L.SQL_Rows; Rows : out S.Root_Rows)
     with Post => (for all Row of Rows => Row.Present);
   procedure Subject_Initialized (SQL : L.SQL_Rows; Rows : out S.Subject_Rows)
     with Post => (for all Row of Rows => Row.Present);
end Projection_Aggregate_Probe;
