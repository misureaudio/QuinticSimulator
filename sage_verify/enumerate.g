# Pure GAP script: enumerate transitive groups of degrees 5 and 6
# Robust to GAP 4.11 (no transitive_groups package). LoadPackage returns
# `fail` (no error) when a package is absent, so we can attempt both safely.
Print("GAP version: ", GAPInfo.Version, "\n");

LoadPackage( "transitive_groups" );   # modern; absent on GAP 4.11
LoadPackage( "TransGrp" );            # built-in; provides AllTransitiveGroups

hasTG  := IsBound( TransitiveGroups );
hasTGp := IsBound( AllTransitiveGroups );

Print("hasTG (transitive_groups): ", hasTG, "\n");
Print("hasTGp (TransGrp):         ", hasTGp, "\n");
Print("\n");

DoTable := function( d )
  Print("=== Transitive groups of degree ", d, " ===\n");
  local i, g, order, solv, comp, sd, prim;
  if hasTG then
    local groups;
    groups := TransitiveGroups( d );
    Print("count: ", Length( groups ), "\n");
    for i in [1..Length( groups )] do
      g := groups[ i ].group;
      order := Size( g );
      solv := IsSolvableGroup( g );
      comp := List( CompositionSeries( g ), x -> Size( x ) );
      sd := StructureDescription( g );
      prim := IsPrimitiveGroup( g );
      Print("T", i, " : order=", order, " solvable=", solv,
            " primitive=", prim, " comp=", comp, " desc=", sd, "\n");
    od;
  elif hasTGp then
    local groups;
    groups := AllTransitiveGroups( d );
    Print("count: ", Length( groups ), "\n");
    for i in [1..Length( groups )] do
      g := groups[ i ][ 1 ];
      order := Size( g );
      solv := IsSolvableGroup( g );
      comp := List( CompositionSeries( g ), x -> Size( x ) );
      sd := StructureDescription( g );
      prim := IsPrimitiveGroup( g );
      Print("T", i, " : order=", order, " solvable=", solv,
            " primitive=", prim, " comp=", comp, " desc=", sd, "\n");
    od;
  else
    Print("no transitive-groups facility available\n");
  fi;
  Print("\n");
end;

DoTable( 5 );
DoTable( 6 );
Print("DONE\n");
Quit();
