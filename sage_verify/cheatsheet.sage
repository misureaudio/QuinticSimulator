# Verify the "cheat sheet" from SageMath_GAP_under_representation.md
# and find what ACTUALLY works in this environment (Sage 10.9).
R.<x> = QQ[]
f = x^5 - x - 1
G = f.galois_group()
print("type(G):", type(G).__name__)
print("order:", G.order())
print("solvable:", G.is_solvable())
print("structure_description:", G.structure_description())
# Does the proposed method exist?
for m in ["transitive_label", "number", "label", "cycle_type", "structure_description"]:
    print("  has", m, ":", hasattr(G, m))
# Frobenius via change_ring (the working path)
print("mod 7:", f.change_ring(GF(7)).factor())
print("DONE")
