# Cycle-type sets for all 5 transitive groups of S5 + identical-pair check.
Print("GAP version: ", GAPInfo.Version, "\n\n");

CycStr := function( el, n )
  local orl, s, o;
  orl := List( Orbits( Group( el ), [ 1..n ] ), Length );
  orl := SortedList( Reversed( orl ) );
  s := "";
  for o in orl do
    s := Concatenation( s, "(", String( o ), ")" );
  od;
  return s;
end;

CycTypes := function( g, n )
  local cls;
  cls := ConjugacyClasses( g );
  return Set( List( cls, c -> CycStr( Representative( c ), n ) ) );
end;

Print( "=== S5 ===\n" );
all5 := [];
for i in [ 1..5 ] do
  g := TransitiveGroup( 5, i );
  ct := CycTypes( g, 5 );
  Print( "5T", i, " (order=", Size( g ), "): ", Set( ct ), "\n" );
  Add( all5, [ i, Size( g ), ct ] );
od;
Print( "\nS5 identical-cycle-type pairs:\n" );
found := false;
for i in [ 1..5 ] do
  for j in [ i+1..5 ] do
    if all5[i][3] = all5[j][3] then
      Print( "5T", all5[i][1], " == 5T", all5[j][1], "\n" );
      found := true;
    fi;
  od;
od;
if not found then Print( "(none)\n" ); fi;
