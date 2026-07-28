with open('psLauncher.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 7237 (index 7236) - add missing closing parenthesis
lines[7236] = lines[7236].replace('side="right)', 'side="right")')

with open('psLauncher.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed line 7237')
