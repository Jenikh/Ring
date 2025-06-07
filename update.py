import sys
import os
import requests
import time
if len(sys.argv) > 1 and sys.argv[1] == "Can_Be_Updated":
    if os.path.exists("new_update.py"):
        os.remove("new_update.py")
    
    upd = requests.get("https://jenikh.github.io/Ring/main.py")
    with open("main.py", "r") as fi: old = fi.readlines()
    with open("new_update.py", "w") as fi: fi.write(upd.text)
    with open("new_update.py", "r") as fi: new = fi.readlines()
    if old == new:
        os.remove("new_update.py")
        exit(0)
    if not os.system(f"py new_update.py Test_run") == 0:
        exit(1)
    try:
        os.remove("main.py")
        with open("main.py", "w") as fi: fi.write(upd.text)
    except:
        print("Reverting update...")
        os.remove("main.py")
        with open("main.py", "w") as fi: fi.writelines(old)
        os.remove("new_update.py")
        exit(1)