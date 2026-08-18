# Enumerate transitive groups of degrees 5 and 6 via TransitiveGroup(d, i).
# No `local`-before-statement bugs, no `try`, no `AllTransitiveGroups`.
# Run: gap -q enumerate2.g
Print("GAP version: ", GAPInfo.Version, "\n\n");

DoTable := function( d, max )
  local i, g, n, printed;
  Print("=== Transitive groups of degree ", d, " ===\n");
  n := 0;
  printed := 0;
  for i in [1..max] do
    g := TransitiveGroup( d, i );
    if g <> fail then
      n := n + 1;
      printed := printed + 1;
      Print("T", i, " : order=", Size( g ),
            "  solvable=", IsSolvableGroup( g ),
            "  desc=", StructureDescription( g ), "\n");
    fi;
  od;
  Print("(count with i<=", max, " : ", n, ")\n\n");
  return n;
end;

c5 := DoTable( 5, 5 );
c6 := DoTable( 6, 16 );
Print("DONE  (5: ", c5, "  6: ", c6, ")\n");
Quit();
