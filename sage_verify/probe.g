Print("GAP version: ", GAPInfo.Version, "\n");

g5 := AllTransitiveGroups( 5 );
Print("AllTransitiveGroups(5) count=", Length(g5), "\n");
Print("type of g5[1]: ", Type(g5[1]), "\n");
Print("g5[1] = ", g5[1], "\n");

# Inspect structure of one entry
e := g5[1];
Print("Length(e)=", Length(e), "\n");
Print("e[1]=", e[1], "\n");
Print("e[2]=", e[2], "\n");

# If entries are [group, id]
gg := e[1];
Print("Size(gg)=", Size(gg), "\n");
Print("IsSolvableGroup(gg)=", IsSolvableGroup(gg), "\n");

Quit();
