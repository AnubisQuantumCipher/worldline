with Evaluation_Finalization;
with Canonical_Artifacts;
with Worldline;

-- UNRUN regression/control source. No native producer, custody or proof credit.
-- Exact prior whole array projection controls; old physical witnesses are HISTORY.
procedure Test_Finalization_Projection is
   package F renames Evaluation_Finalization;
   package T renames F.T;
   use type T.Count;
   use type F.R.Measured_Result;
   use type F.P.Span;
   S : constant F.Start_Record :=
     (Store => (1, 0), Subject => (1, 0), Run => (1, 0), Sequence => (1, 0),
      Requirement => (Present => False), Policy => (1, 0), Verifier_Plan => (1, 0),
      Base_Context => (1, 0), Parent => Worldline.Zero_Hash,
      Config => Worldline.Zero_Hash, Repository => Worldline.Zero_Hash,
      Required => (1, 0), Declaration => F.R.Old.Missing_Declaration);
   Row : constant F.Start_Row :=
     (Start => S, Check => (1, 0), Source => (1, 0),
      Execution => (Present => False), Verifier => (Present => False),
      State => T.E.Incomplete_Unknown, Outcome => T.E.No_Outcome,
      Payload => (1, 0), Declared => (1, 0), Raw => F.W.Zero_Record, Confinement => 0);

   procedure Projection (Rows : F.Start_Rows) is
      Bound : constant F.R.Measured_Array := F.Bind_Rows (S, (1, 0), Rows);
      Payloads : constant Canonical_Artifacts.Span_Array := F.Payload_Spans (Rows);
   begin
      pragma Assert (Bound'First = Rows'First and then Bound'Last = Rows'Last);
      pragma Assert (Payloads'First = Rows'First and then Payloads'Last = Rows'Last);
      for K in Rows'Range loop
         pragma Assert (Bound (K) = F.Bind_Row (S, (1, 0), Rows (K)));
         pragma Assert (Payloads (K) = F.P.Span (Rows (K).Payload));
      end loop;
   end Projection;

begin
   Projection ((1 .. 0 => Row));
   Projection ((7 .. 9 => Row));
   Projection ((T.Index'Last .. T.Index'Last => Row));
   Projection ((T.Index'Last .. T.Index'Last - 1 => Row));
end Test_Finalization_Projection;
