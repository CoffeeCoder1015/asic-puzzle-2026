from program import asic

I_seq = [1]*121+[0]*11
for i in range(len(I_seq)):
    I = I_seq[i]
    s, O = asic(None,I,1,1)
    out_bus_raw = "".join(map(lambda x: str(int(x)),reversed(O)))
    out_bus_dec = int(out_bus_raw,2)
    print(chr(out_bus_dec),end="")
