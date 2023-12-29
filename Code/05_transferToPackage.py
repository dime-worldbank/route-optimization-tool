import os, shutil, glob, re, pathlib
from os import listdir
from os.path import isfile, join

#transfer Atlas
#original = r'C:\Users\tivo9652\Dropbox\RiverCrossings\Survey\CreateRoutesPerDistrict\Atlasses\Atlas_allDistricts_28102020.pdf'
#target = r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\Atlas_allDistricts_28102020.pdf'

#shutil.copyfile(original, target)

#transfer gpx to dropbox

districts={
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
    "98": "aroundNampula"
#    "99": "Maputo"
    }

dest_dir = "C:/test"
for file in glob.glob(r'C:/*.txt'):
    print(file)
    shutil.copy(file, dest_dir)

for dis in [1,2,3,4,5,6,7,8, 9, 10, 11]: # loop over all districts
    dist=districts['{}'.format(dis)]
    print(dist)

    folder = r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\PC2Phone\TrilhasECheckpoints'
    try:
        if os.path.isfile(r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\PC2Phone\TrilhasECheckpoints\District_{}'.format(dist)) or os.path.islink(r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\PC2Phone\TrilhasECheckpoints\District_{}'.format(dist)):
            os.unlink(r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\PC2Phone\TrilhasECheckpoints\District_{}'.format(dist))
        elif os.path.isdir(r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\PC2Phone\TrilhasECheckpoints\District_{}'.format(dist)):
            shutil.rmtree(r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\PC2Phone\TrilhasECheckpoints\District_{}'.format(dist))
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\PC2Phone\TrilhasECheckpoints\District_{}'.format(dist), e))
        
    os.mkdir(r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\PC2Phone\TrilhasECheckpoints\District_{}'.format(dist))
    for bb in ["Troco",""]:
        for base in range(1,5): # loop over all base locations in a district
            checkBase=pathlib.Path(r'C:\Users\tivo9652\Dropbox\RiverCrossings\Survey\CreateRoutesPerDistrict\OutputVRP\{}\Base{}{}'.format(dist,bb,base))
            if checkBase.exists() and len(os.listdir(r'C:\Users\tivo9652\Dropbox\RiverCrossings\Survey\CreateRoutesPerDistrict\OutputVRP\{}\Base{}{}'.format(dist,bb,base)))>0:
                path=r'C:\Users\tivo9652\Dropbox\RiverCrossings\Survey\CreateRoutesPerDistrict\OutputVRP\{}\Base{}{}\Day1'.format(dist, bb,base)
                onlyfiles = [f for f in listdir(path) if isfile(join(path, f)) and f for f in listdir(path) if 'dbf' in f]
                print(onlyfiles[1])
                result = re.search('_Base(.*)_Day', onlyfiles[1])
                getBase=result.group(1)
                print(getBase)
                os.mkdir(r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\PC2Phone\TrilhasECheckpoints\District_{}\Base_{}'.format(dist,getBase))

                for day in range(1,30): # loop over all possible days
                    checkDay=pathlib.Path(r'C:\Users\tivo9652\Dropbox\RiverCrossings\Survey\CreateRoutesPerDistrict\OutputVRP\{}\Base{}{}\Day{}'.format(dist, bb,base, day))
                    if checkDay.exists ():
                        dest_dir = r'C:\Users\tivo9652\Dropbox\MozRoadsSurvey\PC2Phone\TrilhasECheckpoints\District_{}\Base_{}\Day{}'.format(dist, getBase, day)
                        os.mkdir(dest_dir)
                        orig_dir=r'C:\Users\tivo9652\Dropbox\RiverCrossings\Survey\CreateRoutesPerDistrict\OutputVRP\{}\Base{}{}\Day{}'.format(dist, bb,base, day)
                        #print(orig_dir)

                        for file in glob.glob('{}\\*.gpx'.format(orig_dir)):
                            #print(file)
                            shutil.copy(file, dest_dir)
                    else:
                        print("{} does not exist".format(checkDay))
            else:
                print("{} does not exist".format(checkBase))



