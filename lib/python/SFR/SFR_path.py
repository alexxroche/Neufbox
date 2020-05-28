def chk_path(*args):
  return os.path.commonpath(args[0], args[1])

def python2_chk_path(*args):
  print os.path.commonprefix([args[0], args[1]])
  paths = args
  common_prefix = os.path.commonprefix(list_of_paths)
  if common_prefix in paths:
        relative_paths = [os.path.relpath(path, common_prefix) for path in paths]

  return PurePath.parents(*args)


def path_rel2(*args):
  from os.path import relpath
  return relpath(*args)

def python35_pp(*args):
  from pathlib import Path
  Path('/usr/var/log').relative_to('/usr/var/log/')
  Path('/usr/var/log').relative_to('/usr/var/')

def _relpath(cwd, path):
    # Create a relative path for path from cwd, if possible
    if sys.platform == "win32":
        cwd = cwd.lower()
        path = path.lower()

    _cwd = os.path.abspath(cwd).split(os.path.sep)
    _path = os.path.abspath(path).split(os.path.sep)
    equal_until_pos = None
    for i in xrange(min(len(_cwd), len(_path))):
        if _cwd[i] != _path[i]:
            break
        else:
            equal_until_pos = i
    if equal_until_pos is None:
        return path
    newpath = [".." for i in xrange(len(_cwd[equal_until_pos + 1:]))]
    newpath.extend(_path[equal_until_pos + 1:])
    if newpath:
        return os.path.join(*newpath)
    return "."

def commonprefix(l):
    # this unlike the os.path.commonprefix version
    # always returns path prefixes as it compares
    # path component wise
    cp = []
    ls = [p.split('/') for p in l]
    ml = min( len(p) for p in ls )

    for i in range(ml):

        s = set( p[i] for p in ls )         
        if len(s) != 1:
            break

        cp.append(s.pop())

    return '/'.join(cp)

def common_path(directories):
    norm_paths = [os.path.abspath(p) + os.path.sep for p in directories]
    return os.path.dirname(os.path.commonprefix(norm_paths))

def common_path_of_filenames(filenames):
    return common_path([os.path.dirname(f) for f in filenames])


