import subprocess, os, shutil

root = r'e:\软件开发\云集智能文件清理专家'

def git(*args):
    git_cmd = r"D:\Program Files\Git\cmd\git.exe"
    r = subprocess.run([git_cmd] + list(args), cwd=root, capture_output=True, text=True, timeout=120)
    print(f"git {' '.join(args[:3])}{'...' if len(args)>3 else ''} => {r.returncode}")
    out = r.stdout.strip()
    err = r.stderr.strip()
    if out:
        print(out[:600])
    if err and r.returncode != 0:
        print(err[:400])
    return r

# Remove Lib/ from disk
lib_dir = os.path.join(root, 'Lib')
if os.path.isdir(lib_dir):
    shutil.rmtree(lib_dir)
    print(f"Deleted: {lib_dir}")

# Remove _git_fix.py and _publish.py temp scripts
for f in ['_git_fix.py', 'build/_publish.py']:
    fp = os.path.join(root, f)
    if os.path.exists(fp):
        os.remove(fp)
        print(f"Deleted: {fp}")

# Fix git: remove Lib/ from index, add updated .gitignore
print("\n=== Fixing git ===")
git("rm", "-r", "--cached", "Lib/")
git("add", "-A")

# Check status
r = git("status", "--short")
lines = r.stdout.strip().split('\n') if r.stdout.strip() else []
print(f"\nChanged files: {len(lines)}")
for line in lines[:20]:
    print(f"  {line}")

# Amend last commit
git("commit", "--amend", "-m", "v2026.05.24.0443: 版本列表重构+缓存秒开+懒加载+页面切换修复")

# Force push to both remotes
print("\n=== Force push ===")
git("push", "--force", "origin", "main")
git("push", "--force", "gitee", "main")
