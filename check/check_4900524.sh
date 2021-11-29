wmo=4900524
path=c:/Users/GordonC/Documents/data/Argo/dac/meds/D/$wmo/profiles
logfile=../log/log_$wmo.xml
echo "***FileChecker log for float $wmo***" > $logfile
echo >> $logfile
for f in $path/BD*.nc; do
    echo $f >> $logfile
    python argo-checker.py check $f >> $logfile
    echo >> $logfile
done