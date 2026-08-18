# Full verified characterization of the 16 transitive groups of S6:
# order, structure_description, point stabilizer (structure), cycle-type set.
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
  return Set( List( ConjugacyClasses( g ), c -> CycStr( Representative( c ) ) ) );
end;

for i in [ 1..16 ] do
  g := TransitiveGroup( 6, i );
  ps := Stabilizer( g, 1 );
  Print( "6T", i, "  order=", Size( g ),
         "  desc=", StructureDescription( g ),
         "  |Stab|=", Size( ps ),
         "  Stab=", StructureDescription( ps ),
         "  cyc=", Set( CycTypes( g ) ), "\n" );
od;
