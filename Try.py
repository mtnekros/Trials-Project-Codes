distances = [
    {"id": 1, "magnitude":12},
    {"id": 2, "magnitude":34},
    {"id": 3, "magnitude":13},
    {"id": 3, "magnitude":32},
    {"id": 4, "magnitude":1},
    {"id": 5, "magnitude":14},
    {"id": 6, "magnitude":344},
]
print min(distances,key=lambda d: d["magnitude"])
print max(distances,key=lambda d: d["magnitude"])