import subprocess

def launch_program(bat_file):
    subprocess.run(bat_file, shell=True)
