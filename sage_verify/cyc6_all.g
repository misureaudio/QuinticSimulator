# Cycle-type SETS for all 16 transitive groups of S6, to (a) fix the A5/A6
# discriminator in the essay and (b) find which pairs (if any) share a
# cycle-type set (the genuine "cycle types do not decide" cases).
Print("GAP version: ", GAPInfo.Version, "\n\n");

CycStr := function( el )
  local orl, s, o;
  orl := List( Orbits( Group( el ), [ 1..6 ] ), Length );
  orl := SortedList( Reversed( orl ) );
  s := "";
  for o in orl do
    s := Concatenation( s, "(", String( o ), ")" );
  od;
  return s;
end;

CycTypes := function( g )
  local cls;
  cls := ConjugacyClasses( g );
  return Set( List( cls, c -> CycStr( Representative( c ) ) ) );
end;

Print( "=== cycle-type set per transitive group of S6 ===\n" );
all := [];
for i in [ 1..16 ] do
  g := TransitiveGroup( 6, i );
  ct := CycTypes( g );
  Print( "6T", i, " (order=", Size( g ), "): ", Set( ct ), "\n" );
  Add( all, [ i, Size( g ), ct ] );
od;

Print( "\n=== pairs of indices with IDENTICAL cycle-type set ===\n" );
for i in [ 1..16 ] do
  for j in [ i+1..16 ] do
    if all[i][3] = all[j][3] then
      Print( "6T", all[i][1], " (order ", all[i][2], ")  ==  6T",
             all[j][1], " (order ", all[j][2], ")\n" );
    fi;
  od;
od;
Print( "(done)\n" );
