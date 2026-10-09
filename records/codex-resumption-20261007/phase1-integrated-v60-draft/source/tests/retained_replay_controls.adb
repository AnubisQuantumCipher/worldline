package body Retained_Replay_Controls with SPARK_Mode is
   use type R.Replay_State;
   use type R.J.Status;
   use type R.Scoped_Entry;
   use type R.A.Command;
   use type R.A.Decision;
   use type Interfaces.Unsigned_32;
   use type R.H.Decision;
   use type R.CEX.Decision;
   use type R.Operation_Entry;
   procedure Assert_Expectation (State : R.Replay_State; Material_Matches : Boolean; Expected : Expectation) is
   begin
      case Expected is
         when Match => pragma Assert (State = R.Native_Redecided and then Material_Matches);
         when Decode_Refused => pragma Assert (State = R.Decode_Refused);
         when Output_Conflict => pragma Assert (State = R.Output_Conflict);
         when Not_Jointly_Matched => pragma Assert (State /= R.Native_Redecided or else not Material_Matches);
      end case;
   end Assert_Expectation;
   procedure Assert_Root_Controls
     (Data : E.Bytes; Faithful_Observation, Faithful_Material : E.Span;
      Expected_Status : R.J.Status; Cases : Controls)
   is
      Faithful : constant R.Root_Replay_Result := R.Reestablish_Root_Observation (Data, Faithful_Observation);
   begin
      pragma Assert (Faithful.State = R.Native_Redecided);
      pragma Assert (Faithful.Native_Status = Expected_Status);
      pragma Assert (R.Root_Material_Matches (Data, Faithful_Observation, Faithful_Material));
      for C of Cases loop
         declare
            Replay : constant R.Root_Replay_Result := R.Reestablish_Root_Observation (Data, C.Observation);
            Joined : constant Boolean := R.Root_Material_Matches (Data, C.Observation, C.Material);
         begin
            Assert_Expectation (Replay.State, Joined, C.Expected);
            if C.Expected = Match then
               pragma Assert (Replay.Native_Status = Expected_Status);
            end if;
         end;
      end loop;
   end Assert_Root_Controls;
   procedure Assert_Scoped_Controls
     (Data : E.Bytes; Faithful_Observation, Faithful_Material : E.Span;
      Expected_Entry : R.Scoped_Entry; Expected_Status : Interfaces.Unsigned_32; Cases : Controls)
   is
      Faithful : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Data, Faithful_Observation);
   begin
      pragma Assert (Faithful.State = R.Native_Redecided);
      pragma Assert (Faithful.Native_Status = Expected_Status);
      pragma Assert (Faithful.Entry = Expected_Entry);
      pragma Assert (R.Scoped_Material_Matches (Data, Faithful_Observation, Faithful_Material));
      for C of Cases loop
         declare
            Replay : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Data, C.Observation);
            Joined : constant Boolean := R.Scoped_Material_Matches (Data, C.Observation, C.Material);
         begin
            Assert_Expectation (Replay.State, Joined, C.Expected);
            if C.Expected = Match then
               pragma Assert (Replay.Native_Status = Expected_Status);
               pragma Assert (Replay.Entry = Expected_Entry);
            end if;
         end;
      end loop;
   end Assert_Scoped_Controls;
   procedure Assert_Operation_Controls
     (Data : E.Bytes; Faithful_Observation, Faithful_Material : E.Span;
      Expected_Command : R.A.Command; Expected_Status : R.A.Decision; Cases : Controls)
   is
      Faithful : constant R.Operation_Replay_Result := R.Reestablish_Operation_Observation (Data, Faithful_Observation);
   begin
      pragma Assert (Faithful.State = R.Native_Redecided);
      pragma Assert (Faithful.Native_Status = Expected_Status);
      pragma Assert (Faithful.Command = Expected_Command);
      pragma Assert (R.Operation_Material_Matches (Data, Faithful_Observation, Faithful_Material));
      for C of Cases loop
         declare
            Replay : constant R.Operation_Replay_Result := R.Reestablish_Operation_Observation (Data, C.Observation);
            Joined : constant Boolean := R.Operation_Material_Matches (Data, C.Observation, C.Material);
         begin
            Assert_Expectation (Replay.State, Joined, C.Expected);
            if C.Expected = Match then
               pragma Assert (Replay.Native_Status = Expected_Status);
               pragma Assert (Replay.Command = Expected_Command);
            end if;
         end;
      end loop;
   end Assert_Operation_Controls;
   procedure Assert_Historical_Controls
     (Data : E.Bytes; Faithful_Observation, Faithful_Material : E.Span;
      Expected_Status : R.H.Decision; Cases : Controls) is
      Faithful : constant R.Operation_Replay_Result := R.Reestablish_Operation_Observation (Data, Faithful_Observation);
   begin
      pragma Assert (Faithful.State = R.Native_Redecided and then Faithful.Historical_Status = Expected_Status);
      pragma Assert (Faithful.Entry = R.Historical_Completion_Entry);
      pragma Assert (R.Operation_Material_Matches (Data, Faithful_Observation, Faithful_Material));
      for C of Cases loop
         declare
            Replay : constant R.Operation_Replay_Result := R.Reestablish_Operation_Observation (Data, C.Observation);
            Joined : constant Boolean := R.Operation_Material_Matches (Data, C.Observation, C.Material);
         begin
            Assert_Expectation (Replay.State, Joined, C.Expected);
            if C.Expected = Match then pragma Assert (Replay.Historical_Status = Expected_Status); end if;
         end;
      end loop;
   end Assert_Historical_Controls;
   procedure Assert_Exchange_Controls
     (Data : E.Bytes; Faithful_Observation, Faithful_Material : E.Span;
      Expected_Status : R.CEX.Decision; Cases : Controls) is
      Faithful : constant R.Exchange_Replay_Result := R.Reestablish_Exchange_Observation (Data, Faithful_Observation);
   begin
      pragma Assert (Faithful.State = R.Native_Redecided and then Faithful.Native_Status = Expected_Status);
      pragma Assert (R.Exchange_Material_Matches (Data, Faithful_Observation, Faithful_Material));
      for C of Cases loop
         declare
            Replay : constant R.Exchange_Replay_Result := R.Reestablish_Exchange_Observation (Data, C.Observation);
            Joined : constant Boolean := R.Exchange_Material_Matches (Data, C.Observation, C.Material);
         begin
            Assert_Expectation (Replay.State, Joined, C.Expected);
            if C.Expected = Match then pragma Assert (Replay.Native_Status = Expected_Status); end if;
         end;
      end loop;
   end Assert_Exchange_Controls;
   procedure Assert_Reservation_Controls
     (Data : E.Bytes; Faithful_Observation, Faithful_Material : E.Span;
      Expected_Status : R.A.Decision; Cases : Controls) is
      Faithful : constant R.Operation_Replay_Result := R.Reestablish_Reservation_Observation (Data, Faithful_Observation);
   begin
      pragma Assert (Faithful.State = R.Native_Redecided and then Faithful.Native_Status = Expected_Status);
      pragma Assert (Faithful.Command = R.A.Reserve_Use);
      pragma Assert (R.Reservation_Material_Matches (Data, Faithful_Observation, Faithful_Material));
      for C of Cases loop
         declare
            Replay : constant R.Operation_Replay_Result := R.Reestablish_Reservation_Observation (Data, C.Observation);
            Joined : constant Boolean := R.Reservation_Material_Matches (Data, C.Observation, C.Material);
         begin
            Assert_Expectation (Replay.State, Joined, C.Expected);
            if C.Expected = Match then pragma Assert (Replay.Native_Status = Expected_Status); end if;
         end;
      end loop;
   end Assert_Reservation_Controls;
   procedure Assert_Image_Control
     (Data : E.Bytes; Image, Value : E.Span;
      Image_Scoped, Value_Scoped, Carrier_Scoped, Expected : Boolean) is
   begin
      pragma Assert
        (R.Archive_Image_Matches
           (Data, Image, Value, Image_Scoped, Value_Scoped, Carrier_Scoped) = Expected);
   end Assert_Image_Control;
end Retained_Replay_Controls;
