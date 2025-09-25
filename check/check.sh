wmo=$1
path=c:/Users/GordonC/Documents/data/Argo/dac/meds/D/$wmo/profiles
mkdir ./out/$wmo
files=`ls $path/BD*.nc > tmp.txt`
echo $files
java -jar file_checker_exec-2.9.2.jar meds ./file_checker_spec/ ./out/$wmo/ $path $files
python summarize_filecheck.py $wmo