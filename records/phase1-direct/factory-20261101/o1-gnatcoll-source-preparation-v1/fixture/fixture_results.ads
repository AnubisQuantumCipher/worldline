package Fixture_Results is
   type Case_Id is (C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C10R);
   procedure Search
     (Id : Case_Id; Expected : Integer; Oracle : Integer; Actual : Integer);
   procedure Free_Completed (Id : Case_Id);
   procedure Consumer_D01 (First, Second, Third : Boolean);
   procedure Consumer_D02 (First, Second : Boolean);
   procedure Complete;
end Fixture_Results;
