import os

def create_dir_if_not_exist(dirname: str):
    if os.path.exists(dirname):
        os.makedirs(dirname)
    else:
        print("NO")
        
