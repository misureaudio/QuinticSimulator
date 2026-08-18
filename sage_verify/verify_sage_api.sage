# Label all verified representatives via NumberField.galois_group().transitive_label()
# (the API the review cites) and pair with the polynomial-API structure description.
R.<x> = QQ[]

def label_of(f):
    lab = None
    try:
        K.<a> = NumberField(f)
        G = K.galois_group()
        lab = G.transitive_label()
    except Exception as e:
        lab = "ERR:" + repr(e)[:40]
    # structure description + order from the polynomial API (robust)
    g2 = f.galois_group()
    if isinstance(g2, tuple): g2 = g2[0]
    sd = g2.structure_description()
    return (lab, sd, g2.order(), g2.is_solvable())

QU = {
 "C5":  x^5 + x^4 - 4*x^3 - 3*x^2 + 3*x + 1,
 "D10": x^5 - 5*x + 12,
 "F20": x^5 - 5,
 "A5":  x^5 - 5*x^4 - 5*x^3 + 4*x^2 + x - 5,
 "S5":  x^5 - 5*x - 5,
}
SE = {
 "C6":      x^6 - x^3 + 1,
 "S3":      x^6 + 3,
 "D12":     x^6 - 3*x^3 - 1,
 "C3xS3":   x^6 - 3*x^3 + 3,
 "S3xS3":   x^6 - 3*x^3 - 3,
 "C2xS4":   x^6 - 3*x + 5,
 "W72":     x^6 - 3*x + 3,
 "A6":      x^6 - 4*x^4 - x^3 - 3*x^2 + 4*x - 1,
 "S6":      x^6 - 3*x^3 - 3*x - 3,
}
print("### transitive_label (NumberField API) | structure_description | order | solvable ###")
for name, f in QU.items():
    print("Q", name, "->", label_of(f))
for name, f in SE.items():
    print("S", name, "->", label_of(f))
print("DONE")
