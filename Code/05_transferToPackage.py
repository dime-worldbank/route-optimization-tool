import os
import shutil
import glob
import re
import pathlib
from os import listdir
from os.path import isfile, join

# Create main directory
main_dir = "package"
os.makedirs(main_dir, exist_ok=True)

# Transfer Atlas
#original = "/RiverCrossings/Survey/CreateRoutesPerDistrict/Atlasses/Atlas_allDistricts_28102020.pdf"
#target = os.path.join(main_dir, "Atlas_allDistricts_28102020.pdf")
#shutil.copyfile(original, target)

# Transfer gpx to Dropbox
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
    "97": "Gurue",
    "98": "aroundNampula",
    # "99": "Maputo"
}

dest_dir = os.path.join(main_dir, "txt_files")
os.makedirs(dest_dir, exist_ok=True)
for file in glob.glob('*.txt'):
    print(file)
    shutil.copy(file, dest_dir)

for dis in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
    dist = districts['{}'.format(dis)]
    print(dist)

    folder = os.path.join(main_dir, "PC2Phone/TrilhasECheckpoints")
    try:
        dist_path = os.path.join(folder, "District_{}".format(dist))
        if os.path.exists(dist_path):
            if os.path.isfile(dist_path) or os.path.islink(dist_path):
                os.unlink(dist_path)
            elif os.path.isdir(dist_path):
                shutil.rmtree(dist_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (dist_path, e))

    os.makedirs(dist_path, exist_ok=True)
    for bb in ["Troco", ""]:
        for base in range(1, 5):
            check_base = pathlib.Path(os.path.join(main_dir, "RiverCrossings/Survey/CreateRoutesPerDistrict/OutputVRP/{}/Base{}{}".format(dist, bb, base)))
            if check_base.exists() and len(os.listdir(check_base)) > 0:
                path = os.path.join(main_dir, "RiverCrossings/Survey/CreateRoutesPerDistrict/OutputVRP/{}/Base{}{}/Day1".format(dist, bb, base))
                onlyfiles = [f for f in listdir(path) if isfile(join(path, f)) and 'dbf' in f]
                print(onlyfiles[1])
                result = re.search('_Base(.*)_Day', onlyfiles[1])
                get_base = result.group(1)
                print(get_base)
                os.makedirs(os.path.join(dist_path, "Base_{}".format(get_base)), exist_ok=True)

                for day in range(1, 30):
                    check_day = pathlib.Path(os.path.join(main_dir, "RiverCrossings/Survey/CreateRoutesPerDistrict/OutputVRP/{}/Base{}{}/Day{}".format(dist, bb, base, day)))
                    if check_day.exists():
                        dest_dir = os.path.join(main_dir, "PC2Phone/TrilhasECheckpoints/District_{}/Base_{}/Day{}".format(dist, get_base, day))
                        os.makedirs(dest_dir, exist_ok=True)
                        orig_dir = os.path.join(main_dir, "RiverCrossings/Survey/CreateRoutesPerDistrict/OutputVRP/{}/Base{}{}/Day{}".format(dist, bb, base, day))

                        for file in glob.glob(os.path.join(orig_dir, '*.gpx')):
                            shutil.copy(file, dest_dir)
                    else:
                        print("{} does not exist".format(check_day))
            else:
                print("{} does not exist".format(check_base))
