from sage.all import gap
gap.eval("LoadPackage(\"TransGrp\");")

# What does the help say?
print("=== help AllTransitiveGroups ===")
print(gap.eval("??AllTransitiveGroups"))
print("=== help TransitiveGroup ===")
print(gap.eval("??TransitiveGroup"))
print("DONE")
