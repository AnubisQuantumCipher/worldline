with Worldline.Runner_Lifecycle;
with Worldline.Runner_Outcome;
with Worldline.Producer_Values;
--  Source-only genuine codec fixtures; every original assertion is retained.
procedure Runner_Lifecycle_Controls is
   package L renames Worldline.Runner_Lifecycle;
   package O renames Worldline.Runner_Outcome;
   package V renames Worldline.Producer_Values;
   function Bytes (Value : String) return L.E.Bytes is
      Result : L.E.Bytes (1 .. L.E.Count (Value'Length));
   begin
      for I in Value'Range loop
         Result (L.E.Count (I - Value'First + 1)) := L.E.Q.Byte (Character'Pos (Value (I)));
      end loop;
      return Result;
   end Bytes;
   function Whole (Data : L.E.Bytes) return L.E.Span is
     ((Data'First, L.E.Count (Data'Length)));
   Quiet : constant L.E.Bytes := Bytes
     ("[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""YWN0aXZlQ29udHJvbGxlckNhbGxz""],[""array" &
      """,[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Y2xlYW51cFN0YXJ0ZWQ=""],[""array"",[[""str" &
      """,""c2NhbGFy""],[""bool"",true]]]]],[""array"",[[""str"",""Y29udHJvbGxlckNhbGxzQWZ0ZXJDbG9zdXJl""],[""arra" &
      "y"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Z3VhcmRQcmVzZW50""],[""array"",[[""str"",""" &
      "c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""bGF1bmNoZXJQcmVzZW50""],[""array"",[[""str"",""c2NhbG" &
      "Fy""],[""bool"",false]]]]],[""array"",[[""str"",""cHJveHlQcmVzZW50""],[""array"",[[""str"",""c2NhbGFy""],[""boo" &
      "l"",false]]]]],[""array"",[[""str"",""c2FtcGxlckFsaXZl""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]" &
      "]]],[""array"",[[""str"",""c3RyZWFtRW9mT2JzZXJ2ZWQ=""],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]],[""ar" &
      "ray"",[[""str"",""c3RyZWFtcw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dG" &
      "FpbERyYWlucw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dGltZXJBbGl2ZQ" &
      "==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""dW5jbG9zZWRDb21tYW5kcw==" &
      """],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]]]]]]");
   Sampler_Alive : constant L.E.Bytes := Bytes
     ("[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""YWN0aXZlQ29udHJvbGxlckNhbGxz""],[""array" &
      """,[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Y2xlYW51cFN0YXJ0ZWQ=""],[""array"",[[""str" &
      """,""c2NhbGFy""],[""bool"",true]]]]],[""array"",[[""str"",""Y29udHJvbGxlckNhbGxzQWZ0ZXJDbG9zdXJl""],[""arra" &
      "y"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Z3VhcmRQcmVzZW50""],[""array"",[[""str"",""" &
      "c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""bGF1bmNoZXJQcmVzZW50""],[""array"",[[""str"",""c2NhbG" &
      "Fy""],[""bool"",false]]]]],[""array"",[[""str"",""cHJveHlQcmVzZW50""],[""array"",[[""str"",""c2NhbGFy""],[""boo" &
      "l"",false]]]]],[""array"",[[""str"",""c2FtcGxlckFsaXZl""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]" &
      "]],[""array"",[[""str"",""c3RyZWFtRW9mT2JzZXJ2ZWQ=""],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]],[""arr" &
      "ay"",[[""str"",""c3RyZWFtcw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dGF" &
      "pbERyYWlucw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dGltZXJBbGl2ZQ=" &
      "=""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""dW5jbG9zZWRDb21tYW5kcw==""" &
      "],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]]]]]]");
   Reader_Alive : constant L.E.Bytes := Bytes
     ("[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""YWN0aXZlQ29udHJvbGxlckNhbGxz""],[""array" &
      """,[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Y2xlYW51cFN0YXJ0ZWQ=""],[""array"",[[""str" &
      """,""c2NhbGFy""],[""bool"",true]]]]],[""array"",[[""str"",""Y29udHJvbGxlckNhbGxzQWZ0ZXJDbG9zdXJl""],[""arra" &
      "y"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Z3VhcmRQcmVzZW50""],[""array"",[[""str"",""" &
      "c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""bGF1bmNoZXJQcmVzZW50""],[""array"",[[""str"",""c2NhbG" &
      "Fy""],[""bool"",false]]]]],[""array"",[[""str"",""cHJveHlQcmVzZW50""],[""array"",[[""str"",""c2NhbGFy""],[""boo" &
      "l"",false]]]]],[""array"",[[""str"",""c2FtcGxlckFsaXZl""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]" &
      "]]],[""array"",[[""str"",""c3RyZWFtRW9mT2JzZXJ2ZWQ=""],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]],[""ar" &
      "ray"",[[""str"",""c3RyZWFtcw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""b2JqZWN0""" &
      "],[""array"",[[""array"",[[""str"",""YWxpdmU=""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]]]]]]]]]]" &
      "]],[""array"",[[""str"",""dGFpbERyYWlucw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array""," &
      "[[""str"",""dGltZXJBbGl2ZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""d" &
      "W5jbG9zZWRDb21tYW5kcw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]]]]]]");
   Waited_No_Eof : constant L.E.Bytes := Bytes
     ("[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""YWN0aXZlQ29udHJvbGxlckNhbGxz""],[""array" &
      """,[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Y2xlYW51cFN0YXJ0ZWQ=""],[""array"",[[""str" &
      """,""c2NhbGFy""],[""bool"",true]]]]],[""array"",[[""str"",""Y29udHJvbGxlckNhbGxzQWZ0ZXJDbG9zdXJl""],[""arra" &
      "y"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Z3VhcmRQcmVzZW50""],[""array"",[[""str"",""" &
      "c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""bGF1bmNoZXJQcmVzZW50""],[""array"",[[""str"",""c2NhbG" &
      "Fy""],[""bool"",false]]]]],[""array"",[[""str"",""cHJveHlQcmVzZW50""],[""array"",[[""str"",""c2NhbGFy""],[""boo" &
      "l"",false]]]]],[""array"",[[""str"",""c2FtcGxlckFsaXZl""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]" &
      "]]],[""array"",[[""str"",""c3RyZWFtRW9mT2JzZXJ2ZWQ=""],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]],[""ar" &
      "ray"",[[""str"",""c3RyZWFtcw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dG" &
      "FpbERyYWlucw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dGltZXJBbGl2ZQ" &
      "==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""dW5jbG9zZWRDb21tYW5kcw==" &
      """],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""st" &
      "r"",""cHJvY2Vzc0NyZWF0ZWRPYnNlcnZlZA==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]],[""array""," &
      "[[""str"",""cHJvY2Vzc1dhaXRSZXR1cm5PYnNlcnZlZA==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]]," &
      "[""array"",[[""str"",""c3RkZXJyUmVhY2hlZEVvZg==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]],[""a" &
      "rray"",[[""str"",""c3Rkb3V0UmVhY2hlZEVvZg==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]]]]]]]]" &
      "]]]]]]]]");
   Returned_And_Drained : constant L.E.Bytes := Bytes
     ("[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""YWN0aXZlQ29udHJvbGxlckNhbGxz""],[""array" &
      """,[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Y2xlYW51cFN0YXJ0ZWQ=""],[""array"",[[""str" &
      """,""c2NhbGFy""],[""bool"",true]]]]],[""array"",[[""str"",""Y29udHJvbGxlckNhbGxzQWZ0ZXJDbG9zdXJl""],[""arra" &
      "y"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Z3VhcmRQcmVzZW50""],[""array"",[[""str"",""" &
      "c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""bGF1bmNoZXJQcmVzZW50""],[""array"",[[""str"",""c2NhbG" &
      "Fy""],[""bool"",false]]]]],[""array"",[[""str"",""cHJveHlQcmVzZW50""],[""array"",[[""str"",""c2NhbGFy""],[""boo" &
      "l"",false]]]]],[""array"",[[""str"",""c2FtcGxlckFsaXZl""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]" &
      "]]],[""array"",[[""str"",""c3RyZWFtRW9mT2JzZXJ2ZWQ=""],[""array"",[[""str"",""c2NhbGFy""],[""null""]]]]],[""ar" &
      "ray"",[[""str"",""c3RyZWFtcw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dG" &
      "FpbERyYWlucw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dGltZXJBbGl2ZQ" &
      "==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""dW5jbG9zZWRDb21tYW5kcw==" &
      """],[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""st" &
      "r"",""cHJvY2Vzc0NyZWF0ZWRPYnNlcnZlZA==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]],[""array""," &
      "[[""str"",""cHJvY2Vzc1dhaXRSZXR1cm5PYnNlcnZlZA==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]]," &
      "[""array"",[[""str"",""c3RkZXJyUmVhY2hlZEVvZg==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]],[""a" &
      "rray"",[[""str"",""c3Rkb3V0UmVhY2hlZEVvZg==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]]]]]]]]]" &
      "]]]]]]]");
   Eof_Absent : constant L.E.Bytes := Bytes
     ("[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""YWN0aXZlQ29udHJvbGxlckNhbGxz""],[""array" &
      """,[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Y2xlYW51cFN0YXJ0ZWQ=""],[""array"",[[""str" &
      """,""c2NhbGFy""],[""bool"",true]]]]],[""array"",[[""str"",""Y29udHJvbGxlckNhbGxzQWZ0ZXJDbG9zdXJl""],[""arra" &
      "y"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Z3VhcmRQcmVzZW50""],[""array"",[[""str"",""" &
      "c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""bGF1bmNoZXJQcmVzZW50""],[""array"",[[""str"",""c2NhbG" &
      "Fy""],[""bool"",false]]]]],[""array"",[[""str"",""cHJveHlQcmVzZW50""],[""array"",[[""str"",""c2NhbGFy""],[""boo" &
      "l"",false]]]]],[""array"",[[""str"",""c2FtcGxlckFsaXZl""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]" &
      "]]],[""array"",[[""str"",""c3RyZWFtRW9mT2JzZXJ2ZWQ=""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array" &
      """,[[""str"",""c3Rkb3V0""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]]]]]]]],[""array"",[[""str"",""c" &
      "3RyZWFtcw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dGFpbERyYWlucw==""" &
      "],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dGltZXJBbGl2ZQ==""],[""array"",[" &
      "[""str"",""c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""dW5jbG9zZWRDb21tYW5kcw==""],[""array"",[[""" &
      "str"",""bGlzdA==""],[""array"",[]]]]]]]]]]");
   Eof_Present : constant L.E.Bytes := Bytes
     ("[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""YWN0aXZlQ29udHJvbGxlckNhbGxz""],[""array" &
      """,[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Y2xlYW51cFN0YXJ0ZWQ=""],[""array"",[[""str" &
      """,""c2NhbGFy""],[""bool"",true]]]]],[""array"",[[""str"",""Y29udHJvbGxlckNhbGxzQWZ0ZXJDbG9zdXJl""],[""arra" &
      "y"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""Z3VhcmRQcmVzZW50""],[""array"",[[""str"",""" &
      "c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""bGF1bmNoZXJQcmVzZW50""],[""array"",[[""str"",""c2NhbG" &
      "Fy""],[""bool"",false]]]]],[""array"",[[""str"",""cHJveHlQcmVzZW50""],[""array"",[[""str"",""c2NhbGFy""],[""boo" &
      "l"",false]]]]],[""array"",[[""str"",""c2FtcGxlckFsaXZl""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]" &
      "]]],[""array"",[[""str"",""c3RyZWFtRW9mT2JzZXJ2ZWQ=""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array" &
      """,[[""str"",""c3Rkb3V0""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]]]]]]]],[""array"",[[""str"",""c3" &
      "RyZWFtcw==""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dGFpbERyYWlucw==""]" &
      ",[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]],[""array"",[[""str"",""dGltZXJBbGl2ZQ==""],[""array"",[[" &
      """str"",""c2NhbGFy""],[""bool"",false]]]]],[""array"",[[""str"",""dW5jbG9zZWRDb21tYW5kcw==""],[""array"",[[""s" &
      "tr"",""bGlzdA==""],[""array"",[]]]]]]]]]]");
   Supplied_Flags : constant L.E.Bytes := Bytes
     ("[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""cXVpZXNjZW50""],[""array"",[[""str"",""c2Nhb" &
      "GFy""],[""bool"",true]]]]],[""array"",[[""str"",""ZmluaXNoZWQ=""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",t" &
      "rue]]]]]]]]]");
   Late_Controller : constant L.E.Bytes := Bytes
     ("[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""Y29udHJvbGxlckNhbGxzQWZ0ZXJDbG9zdXJl""]" &
      ",[""array"",[[""str"",""bGlzdA==""],[""array"",[[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str""" &
      ",""Y2FsbGJhY2tSZXR1cm5lZA==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",true]]]]]]]]]]]]]]]]]]]");
   Canonical_Quiet : constant L.E.Bytes := Bytes
     ("{""activeControllerCalls"":[],""cleanupStarted"":true,""controllerCallsAfterClosure"":[],""guardPresent"":false,""launcherPresent"":false,""proxyPresent"":false,""samplerAlive"":false,""streamEofObserved"":null,""streams"":[],""tailDrains"":[],""timerAlive"":false,""unclosedCommands"":[]}");
   Capture : constant L.E.Bytes := Bytes
     ("[""array"",[[""str"",""b2JqZWN0""],[""array"",[" &
      "[""array"",[[""str"",""bW9kZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""cG9saWN5LW9ubHktdjE=""]]]]]," &
      "[""array"",[[""str"",""c2NoZW1h""],[""array"",[[""str"",""c2NhbGFy""" &
      "],[""str"",""d29ybGRsaW5lLnJ1bm5lci10ZXJtaW5hbC12Mg==""]]]]],[""array"",[[""str"",""cmVzb3VyY2VPYnNlcnZh" &
      "dGlvbg==""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""cHJvZmlsZQ==""],[""array"",[[""" &
      "str"",""c2NhbGFy""],[""str"",""YnVpbHRpbi12MQ==""]]]]],[""array"",[[""str"",""dmFsdWU=""],[""array"",[[""str"",""" &
      "b2JqZWN0""],[""array"",[[""array"",[[""str"",""c3RhdGU=""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""T0JTRVJW" &
      "RUQ=""]]]]],[""array"",[[""str"",""aGl0TWVtb3J5Q2VpbGluZw==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",fa" &
      "lse]]]]],[""array"",[[""str"",""b29tS2lsbGVk""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]]]]]]]]" &
      "]]]]]],[""array"",[[""str"",""cmVzb3VyY2VDb250YWluZXI=""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""ar" &
      "ray"",[[""str"",""cHJvZmlsZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""cHl0aG9uLWFjdHVhbC1wcm90b2Nvb" &
      "C12MQ==""]]]]],[""array"",[[""str"",""cmVmZXJlbmNl""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""MQ==""]]]]]," &
      "[""array"",[[""str"",""dHlwZVJlZmVyZW5jZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Mg==""]]]]]]]]]]]," &
      "[""array"",[[""str"",""bWFuYWdlclJlc3VsdA==""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str" &
      """,""cHJvZmlsZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""YnVpbHRpbi12MQ==""]]]]],[""array"",[[""str""," &
      """dmFsdWU=""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""c3VjY2Vzcw==""]]]]]]]]]]],[""array"",[[""str"",""ZXh" &
      "pdENvZGU=""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""cHJvZmlsZQ==""],[""array"",[[" &
      """str"",""c2NhbGFy""],[""str"",""YnVpbHRpbi12MQ==""]]]]],[""array"",[[""str"",""dmFsdWU=""],[""array"",[[""str""," &
      """c2NhbGFy""],[""int"",false,""""]]]]]]]]]]],[""array"",[[""str"",""c3VwZXJ2aXNpb25LaW5k""],[""array"",[[""str" &
      """,""b2JqZWN0""],[""array"",[[""array"",[[""str"",""cHJvZmlsZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""c" &
      "Hl0aG9uLWFjdHVhbC1wcm90b2NvbC12MQ==""]]]]],[""array"",[[""str"",""cmVmZXJlbmNl""],[""array"",[[""str"",""c2" &
      "NhbGFy""],[""str"",""Mw==""]]]]],[""array"",[[""str"",""dHlwZVJlZmVyZW5jZQ==""],[""array"",[[""str"",""c2NhbGFy" &
      """],[""str"",""Mg==""]]]]],[""array"",[[""str"",""bG9va3Vw""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Z2V0aXR" &
      "lbQ==""]]]]],[""array"",[[""str"",""a2V5""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""a2luZA==""]]]]]]]]]]]," &
      "[""array"",[[""str"",""c3RvcE1lbWJlcnNoaXA=""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str" &
      """,""Y2FuY2VsbGVk""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""cHJvZmlsZQ==""],[""arr" &
      "ay"",[[""str"",""c2NhbGFy""],[""str"",""YnVpbHRpbi1zZXQtc3RyaW5nLXYx""]]]]],[""array"",[[""str"",""cmVxdWVzdG" &
      "Vk""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""am9i""]]]]],[""array"",[[""str"",""cm9zdGVy""],[""array"",[[""s" &
      "tr"",""bGlzdA==""],[""array"",[]]]]]]]]]]]],[""array"",[[""str"",""dGltZWRPdXQ=""],[""array"",[[""str"",""b2JqZ" &
      "WN0""],[""array"",[[""array"",[[""str"",""cHJvZmlsZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""YnVpbHRpb" &
      "i1zZXQtc3RyaW5nLXYx""]]]]],[""array"",[[""str"",""cmVxdWVzdGVk""],[""array"",[[""str"",""c2NhbGFy""],[""str""," &
      """am9i""]]]]],[""array"",[[""str"",""cm9zdGVy""],[""array"",[[""str"",""bGlzdA==""],[""array"",[]]]]]]]]]]]]]]]" &
      "]]],[""array"",[[""str"",""cHVibGlzaENlaWxpbmdGaXJlZA==""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""a" &
      "rray"",[[""str"",""cHJvZmlsZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""cHl0aG9uLWFjdHVhbC1wcm90b2Nv" &
      "bC12MQ==""]]]]],[""array"",[[""str"",""b3BlcmF0aW9u""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""c2V0aXRlbQ" &
      "==""]]]]],[""array"",[[""str"",""a2V5""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Y2VpbGluZ0ZpcmVk""]]]]],[" &
      """array"",[[""str"",""bGVmdFJlZmVyZW5jZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""MQ==""]]]]],[""array" &
      """,[[""str"",""bGVmdFR5cGVSZWZlcmVuY2U=""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Mg==""]]]]],[""array""," &
      "[[""str"",""b3BlcmFuZA==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]]]]]]]],[""array"",[[""str""," &
      """Y2VpbGluZ0V2aWRlbmNlTm9uZUxvb2t1cA==""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str""" &
      ",""cHJvZmlsZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""cHl0aG9uLWFjdHVhbC1wcm90b2NvbC12MQ==""]]]]" &
      "],[""array"",[[""str"",""b3BlcmF0aW9u""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Z2V0aXRlbV9pc19ub25l""]]" &
      "]]],[""array"",[[""str"",""a2V5""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Y2VpbGluZ0ZpcmVk""]]]]],[""arra" &
      "y"",[[""str"",""bGVmdFJlZmVyZW5jZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""MQ==""]]]]],[""array"",[[""" &
      "str"",""bGVmdFR5cGVSZWZlcmVuY2U=""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Mg==""]]]]],[""array"",[[""st" &
      "r"",""cmV0dXJuZWRSZWZlcmVuY2U=""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""NA==""]]]]],[""array"",[[""str""" &
      ",""cmV0dXJuZWRUeXBlUmVmZXJlbmNl""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""NQ==""]]]]],[""array"",[[""st" &
      "r"",""bG9va3VwVmFsdWU=""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""cHJvZmlsZQ==""]," &
      "[""array"",[[""str"",""c2NhbGFy""],[""str"",""YnVpbHRpbi12MQ==""]]]]],[""array"",[[""str"",""dmFsdWU=""],[""arra" &
      "y"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]]]]]]]]]]]]]],[""array"",[[""str"",""cHVibGlzaENlaWxpbmdFdml" &
      "kZW5jZQ==""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""cHJvZmlsZQ==""],[""array"",[[" &
      """str"",""c2NhbGFy""],[""str"",""cHl0aG9uLWFjdHVhbC1wcm90b2NvbC12MQ==""]]]]],[""array"",[[""str"",""b3BlcmF0" &
      "aW9u""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""c2V0aXRlbQ==""]]]]],[""array"",[[""str"",""a2V5""],[""array" &
      """,[[""str"",""c2NhbGFy""],[""str"",""Y2VpbGluZ0V2aWRlbmNl""]]]]],[""array"",[[""str"",""bGVmdFJlZmVyZW5jZQ==" &
      """],[""array"",[[""str"",""c2NhbGFy""],[""str"",""MQ==""]]]]],[""array"",[[""str"",""bGVmdFR5cGVSZWZlcmVuY2U=""]" &
      ",[""array"",[[""str"",""c2NhbGFy""],[""str"",""Mg==""]]]]],[""array"",[[""str"",""b3BlcmFuZA==""],[""array"",[[""s" &
      "tr"",""c2NhbGFy""],[""str"",""bm8gY2VpbGluZyBldmVudCB3YXMgcmVjb3JkZWQ=""]]]]]]]]]]],[""array"",[[""str"",""" &
      "Y2VpbGluZ1JlYXNvbkxvb2t1cA==""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""cHJvZml" &
      "sZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""cHl0aG9uLWFjdHVhbC1wcm90b2NvbC12MQ==""]]]]],[""array" &
      """,[[""str"",""b3BlcmF0aW9u""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Z2V0X3RydXRo""]]]]],[""array"",[[""s" &
      "tr"",""a2V5""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Y2VpbGluZ0ZpcmVk""]]]]],[""array"",[[""str"",""bGVmd" &
      "FJlZmVyZW5jZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""MQ==""]]]]],[""array"",[[""str"",""bGVmdFR5cGV" &
      "SZWZlcmVuY2U=""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Mg==""]]]]],[""array"",[[""str"",""cmV0dXJuZWRSZ" &
      "WZlcmVuY2U=""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""NA==""]]]]],[""array"",[[""str"",""cmV0dXJuZWRUeXB" &
      "lUmVmZXJlbmNl""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""NQ==""]]]]],[""array"",[[""str"",""cmV0dXJuZWRUc" &
      "nV0aA==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]]]]]]]],[""array"",[[""str"",""bGF1bmNoQ29tc" &
      "GFyaXNvbg==""],[""array"",[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""cHJvZmlsZQ==""],[""array""," &
      "[[""str"",""c2NhbGFy""],[""str"",""cHl0aG9uLWFjdHVhbC1wcm90b2NvbC12MQ==""]]]]],[""array"",[[""str"",""b3Blcm" &
      "F0aW9u""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""ZXE=""]]]]],[""array"",[[""str"",""b3BlcmFuZA==""],[""arr" &
      "ay"",[[""str"",""c2NhbGFy""],[""str"",""TEFVTkNIX0ZBSUxFRA==""]]]]],[""array"",[[""str"",""c291cmNlUmVmZXJlbm" &
      "Nl""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Mw==""]]]]],[""array"",[[""str"",""c291cmNlVHlwZVJlZmVyZW5j" &
      "ZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Mg==""]]]]],[""array"",[[""str"",""c291cmNlT3BlcmF0aW9u""]" &
      ",[""array"",[[""str"",""c2NhbGFy""],[""str"",""Z2V0aXRlbQ==""]]]]],[""array"",[[""str"",""c291cmNlS2V5""],[""arr" &
      "ay"",[[""str"",""c2NhbGFy""],[""str"",""a2luZA==""]]]]],[""array"",[[""str"",""bGVmdFJlZmVyZW5jZQ==""],[""array" &
      """,[[""str"",""c2NhbGFy""],[""str"",""Ng==""]]]]],[""array"",[[""str"",""bGVmdFR5cGVSZWZlcmVuY2U=""],[""array""," &
      "[[""str"",""c2NhbGFy""],[""str"",""Nw==""]]]]],[""array"",[[""str"",""cmV0dXJuZWRSZWZlcmVuY2U=""],[""array"",[[" &
      """str"",""c2NhbGFy""],[""str"",""NA==""]]]]],[""array"",[[""str"",""cmV0dXJuZWRUeXBlUmVmZXJlbmNl""],[""array""," &
      "[[""str"",""c2NhbGFy""],[""str"",""NQ==""]]]]],[""array"",[[""str"",""cmV0dXJuZWRUcnV0aA==""],[""array"",[[""str" &
      """,""c2NhbGFy""],[""bool"",false]]]]]]]]]]],[""array"",[[""str"",""c3VwZXJ2aXNlZENvbXBhcmlzb24=""],[""array" &
      """,[[""str"",""b2JqZWN0""],[""array"",[[""array"",[[""str"",""cHJvZmlsZQ==""],[""array"",[[""str"",""c2NhbGFy""],[" &
      """str"",""cHl0aG9uLWFjdHVhbC1wcm90b2NvbC12MQ==""]]]]],[""array"",[[""str"",""b3BlcmF0aW9u""],[""array"",[[""" &
      "str"",""c2NhbGFy""],[""str"",""bmU=""]]]]],[""array"",[[""str"",""b3BlcmFuZA==""],[""array"",[[""str"",""c2NhbGFy" &
      """],[""str"",""U1VQRVJWSVNFRA==""]]]]],[""array"",[[""str"",""c291cmNlUmVmZXJlbmNl""],[""array"",[[""str"",""c2" &
      "NhbGFy""],[""str"",""Mw==""]]]]],[""array"",[[""str"",""c291cmNlVHlwZVJlZmVyZW5jZQ==""],[""array"",[[""str"",""" &
      "c2NhbGFy""],[""str"",""Mg==""]]]]],[""array"",[[""str"",""c291cmNlT3BlcmF0aW9u""],[""array"",[[""str"",""c2NhbG" &
      "Fy""],[""str"",""Z2V0aXRlbQ==""]]]]],[""array"",[[""str"",""c291cmNlS2V5""],[""array"",[[""str"",""c2NhbGFy""],[" &
      """str"",""a2luZA==""]]]]],[""array"",[[""str"",""bGVmdFJlZmVyZW5jZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""s" &
      "tr"",""Ng==""]]]]],[""array"",[[""str"",""bGVmdFR5cGVSZWZlcmVuY2U=""],[""array"",[[""str"",""c2NhbGFy""],[""str" &
      """,""Nw==""]]]]],[""array"",[[""str"",""cmV0dXJuZWRSZWZlcmVuY2U=""],[""array"",[[""str"",""c2NhbGFy""],[""str""," &
      """NA==""]]]]],[""array"",[[""str"",""cmV0dXJuZWRUeXBlUmVmZXJlbmNl""],[""array"",[[""str"",""c2NhbGFy""],[""str" &
      """,""NQ==""]]]]],[""array"",[[""str"",""cmV0dXJuZWRUcnV0aA==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",fal" &
      "se]]]]]]]]]]],[""array"",[[""str"",""aW5kZXRlcm1pbmF0ZUNvbXBhcmlzb24=""],[""array"",[[""str"",""b2JqZWN0""]" &
      ",[""array"",[[""array"",[[""str"",""cHJvZmlsZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""cHl0aG9uLWFjdH" &
      "VhbC1wcm90b2NvbC12MQ==""]]]]],[""array"",[[""str"",""b3BlcmF0aW9u""],[""array"",[[""str"",""c2NhbGFy""],[""st" &
      "r"",""ZXE=""]]]]],[""array"",[[""str"",""b3BlcmFuZA==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""SU5ERVRFUk" &
      "1JTkFURQ==""]]]]],[""array"",[[""str"",""c291cmNlUmVmZXJlbmNl""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""" &
      "Mw==""]]]]],[""array"",[[""str"",""c291cmNlVHlwZVJlZmVyZW5jZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str""" &
      ",""Mg==""]]]]],[""array"",[[""str"",""c291cmNlT3BlcmF0aW9u""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Z2V0" &
      "aXRlbQ==""]]]]],[""array"",[[""str"",""c291cmNlS2V5""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""a2luZA==""]" &
      "]]]],[""array"",[[""str"",""bGVmdFJlZmVyZW5jZQ==""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Ng==""]]]]],[" &
      """array"",[[""str"",""bGVmdFR5cGVSZWZlcmVuY2U=""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""Nw==""]]]]],[""a" &
      "rray"",[[""str"",""cmV0dXJuZWRSZWZlcmVuY2U=""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""NA==""]]]]],[""arr" &
      "ay"",[[""str"",""cmV0dXJuZWRUeXBlUmVmZXJlbmNl""],[""array"",[[""str"",""c2NhbGFy""],[""str"",""NQ==""]]]]],[""a" &
      "rray"",[[""str"",""cmV0dXJuZWRUcnV0aA==""],[""array"",[[""str"",""c2NhbGFy""],[""bool"",false]]]]]]]]]]]]]]]");
begin
   pragma Assert (L.Finalization_Quiescent (Quiet, Whole (Quiet)));
   pragma Assert (L.Quiescent (Canonical_Quiet, Whole (Canonical_Quiet)));
   pragma Assert (L.Finished (Quiet, Whole (Quiet)));
   pragma Assert (not L.Finalization_Quiescent (Sampler_Alive, Whole (Sampler_Alive)));
   pragma Assert (not L.Finalization_Quiescent (Reader_Alive, Whole (Reader_Alive)));
   pragma Assert (not L.Finalization_Quiescent (Waited_No_Eof, Whole (Waited_No_Eof)));
   pragma Assert (L.Finalization_Quiescent (Returned_And_Drained, Whole (Returned_And_Drained)));
   pragma Assert (not L.Finalization_Quiescent (Eof_Absent, Whole (Eof_Absent)));
   pragma Assert (L.Finalization_Quiescent (Eof_Present, Whole (Eof_Present)));
   pragma Assert (not L.Finalization_Quiescent (Supplied_Flags, Whole (Supplied_Flags)));
   pragma Assert (not L.Generation_Stable (Late_Controller, Whole (Late_Controller)));
   pragma Assert (V.Text (V.Field (O.Decide (Capture, Whole (Capture)), "agentStatus")) = "PASS");
end Runner_Lifecycle_Controls;
