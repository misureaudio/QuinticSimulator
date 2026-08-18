# The outer automorphism of S6, acting on the two S5- and A5-classes.
# Aut(S6) is represented in GAP as a permutation group on the 720 elements of S6.
Print("GAP version: ", GAPInfo.Version, "\n");
S6 := SymmetricGroup( 6 );
els := Elements( S6 );

norb := function( g, pts ) return Length( Orbits( g, pts ) ); end;

cls := ConjugacyClassesSubgroups( S6 );
s5cls := Filtered( cls, c -> Size( Representative( c ) ) = 120
                   and StructureDescription( Representative( c ) ) = "S5" );
a5cls := Filtered( cls, c -> Size( Representative( c ) ) = 60
                   and StructureDescription( Representative( c ) ) = "A5" );

# image of a subgroup under the automorphism phi
img := function( h, phi )
  local im;
  im := List( GeneratorsOfGroup( h ), g -> Image( phi, g ) );
  return Group( im );
end;

AutS6 := AutomorphismGroup( S6 );
phi := fail;
for a in Elements( AutS6 ) do
  if not IsInnerAutomorphism( a ) then phi := a; break; fi;
od;
Print( "outer automorphism found: ", phi <> fail, "\n" );

Print( "-- S5 classes --\n" );
for c in s5cls do
  h := Representative( c );
  hp := img( h, phi );
  Print( "  src trans=", norb( h, [1..6] )=1, "  ->  img trans=",
         norb( hp, [1..6] )=1,
         "  img Stab1=", StructureDescription( Stabilizer( hp, 1 ) ), "\n" );
od;
Print( "-- A5 classes --\n" );
for c in a5cls do
  h := Representative( c );
  hp := img( h, phi );
  Print( "  src trans=", norb( h, [1..6] )=1, "  ->  img trans=",
         norb( hp, [1..6] )=1,
         "  img Stab1=", StructureDescription( Stabilizer( hp, 1 ) ), "\n" );
od;
Print( "DONE\n" );
