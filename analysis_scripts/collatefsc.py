import numpy as np
import glob
import sys

files = glob.glob(sys.argv[1])
res5 = [0] * len(files)
res143 = [0] * len(files)
best_res = float(sys.argv[2])
skip = int(sys.argv[3]) if len(sys.argv) > 3 else 1

for file in files:
    epoch = int(file.split(".")[-4])//skip if "align" in file \
        else int(file.split(".")[-3])//skip
    f = open(file, "r")
    for line in f:
        if line.startswith("0.143: "):
            w = line.split("0.143: ")[1]
            try:
                res143[epoch] = float(w.split(" ")[0][1:])
            except:
                res143[epoch] = best_res
        elif line.startswith("0.5: "):
            w = line.split("0.5: ")[1]
            try:
                res5[epoch] = float(w.split(" ")[0][1:])
            except:
                res143[epoch] = best_res

print("0.143: {}".format(res143))
print("0.5: {}".format(res5))
print("0.143 best = ", min(res143))
print("0.5 best = ", min(res5))
print("0.143 best epoch = ", np.argmin(res143)*skip + skip)
print("0.5 best epoch = ", np.argmin(res5)*skip + skip)
print("0.143 final = ", res143[-1])
print("0.5 final = ", res5[-1])
