from __future__ import print_function, absolute_import, unicode_literals
import os
import re
import glob




package_path = os.path.dirname(__file__)
#pkg_cnt = __name__.count('.')
#package_name = __name__.split('.')[:-pkg_cnt]
#root_path = os.path.join(*(os.path.split(package_path)[:-pkg_cnt]))
root_path = os.path.split(package_path)[0]

print('from __future__ import absolute_import, unicode_literals')
print('#  vim: set ts=8 sw=4 tw=0 fileencoding=utf-8 filetype=python expandtab:')

for module in sorted(glob.glob(os.path.join(package_path, "*.py"))):
    if module == __file__ or '__init__' in module:
        continue

#    print('# ' + '.'.join(package_name + list(os.path.splitext(os.path.basename(module))[:1])))
    print('# ' + os.path.relpath(module, root_path))

    with open(module, 'r') as fp:
        data = fp.read()
        in_main = False
        for line in data.split('\n'):
            if 'from __future__' in line:
                continue

            if 'from .' in line:
                continue

            if line.startswith('if __name__ =='):
                in_main = True
                continue

            elif in_main:
                if re.match(r'^\s+', line):
                    continue
                else:
                    in_main = False

            print(line)
