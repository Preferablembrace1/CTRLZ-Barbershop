import glob

for file in glob.glob('ui/*.ui'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('<property name="objectName">', '<property name="cssClass">')
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

with open('styles/light_theme.qss', 'r', encoding='utf-8') as f:
    qss = f.read()
qss = qss.replace('#btnSecondary', '[cssClass="btnSecondary"]')
qss = qss.replace('#btnAction', '[cssClass="btnAction"]')
with open('styles/light_theme.qss', 'w', encoding='utf-8') as f:
    f.write(qss)
