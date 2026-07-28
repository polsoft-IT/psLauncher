with open('psLauncher.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 7662 (index 7661) - add missing comma
lines[7661] = lines[7661].replace('side="left" fill="x"', 'side="left", fill="x"')

with open('psLauncher.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed syntax error on line 7662')
