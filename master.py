import os, shutil

code_directory = "Code"
code_directory = os.path.join(os.path.dirname(__file__), "Code")
os.chdir(code_directory)

districts = {
    "1": "ChindeLuabo",
    "2": "Mocubela",
    "3": "Maganja",
    "4": "Morrumbala",
    "5": "Lugela",
    "6": "Pebane",
    "7": "Memba",
    "8": "Erati",
    "9": "Monapo",
    "10": "Mossuril",
    "11": "Mogincual",
    "98": "aroundNampula"
}

# CREATE ROUTES PER DISTRICT - PREPARATION
os.system("python 02_Prep_CreateRoutesPerDistrict.py")

#CREATE ROUTES PER DISTRICT - MAIN
for district_number, district_name in districts.items():
    print(f"Start District {district_number}: {district_name}")
    os.system(f"python 03_PerDist_CreateRoutesPerDistrict.py {district_number}")

# MAKE ATLAS
os.system("python 04_MakeAtlas.py")

# COPY Atlas TO folder
for district_number, district_name in districts.items():
    dest_dir = os.path.expanduser(f"instrucoesEtapa_{district_name}.pdf")
    shutil.copy(f'all_{district_name}.pdf', dest_dir)

# Copy Tracks
os.system("python 05_transferToPackage.py")
