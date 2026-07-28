with open('psLauncher.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 7658 (index 7657)
lines[7657] = lines[7657].replace('side="left, fill="x"', 'side="left" fill="x"')

with open('psLauncher.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed syntax error on line 7658')
