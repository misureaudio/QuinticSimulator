from sage.all import gap

gap.eval("LoadPackage(\"transgrp\");")

def tgroup_table(d):
    # AllTransitiveGroups(d) is a list of [group, id] pairs
    pairs = gap.eval("AllTransitiveGroups(%d);" % d)
    print("=== Transitive groups of degree %d ===" % d)
    # pairs is a list; get its length
    n = int(gap.eval("Length(%s);" % pairs))
    print("count:", n)
    for i in range(1, n+1):
        g = gap.eval("%s[%d][1]" % (pairs, i))
        order = gap.eval("Size(%s)" % g)
        solv = gap.eval("IsSolvableGroup(%s)" % g)
        # simple?
        simple = gap.eval("IsSimpleGroup(%s)" % g)
        # composition factors
        cf = gap.eval("CompositionSeries(%s);" % g)
        cfstr = gap.eval("List(CompositionSeries(%s), x -> Size(x));" % g)
        print("T%d : order=%s solvable=%s simple=%s comp=%s" % (i, order, solv, simple, cfstr))
    print()

tgroup_table(5)
tgroup_table(6)
print("DONE")
