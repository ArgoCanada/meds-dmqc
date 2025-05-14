wmo=$1
path=c:/Users/GordonC/Documents/data/Argo/dac/meds/D/$wmo/profiles
mkdir ./out/$wmo
files=`ls $path/BD*.nc > tmp.txt`
echo $files
java -jar ValidateSubmit.jar meds ./spec/ ./out/$wmo/ $path $files
python summarize_filecheck.py $wmo