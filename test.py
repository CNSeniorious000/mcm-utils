from app import Team

result = {}
for n in [2208928, 2209237, 2221741, 2209492, 2200717, 2200605, 2218651]:
    team = Team(n)
    result[n] = team.award
    # team.show_bbox()
    print(f"{n} -> {Team(n).award}")

print(result)
