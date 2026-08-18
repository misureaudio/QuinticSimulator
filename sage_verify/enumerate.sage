# Drive GAP through the sage gap interface.
# Key: use a SINGLE GAP expression that RETURNs a value (no Print, no local,
# no multi-line), so sage's gap.eval returns the value's string form.
from sage.all import gap

gap.eval("LoadPackage(\"TransGrp\");")

def table(d):
    # AllTransitiveGroups(d) -> list of [group, id]
    expr = ("List(AllTransitiveGroups(%d), "
            "r -> [Size(r[1]), IsSolvableGroup(r[1]), "
            "IsPrimitiveGroup(r[1]), StructureDescription(r[1])])") % d
    val = gap.eval(expr)
    print("=== degree %d ===" % d)
    print(val)
    print()

table(5)
table(6)
print("DONE")
