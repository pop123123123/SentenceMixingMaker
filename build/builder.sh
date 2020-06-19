#!/bin/sh

wget https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/download/v1.0.1/montreal-forced-aligner_linux.tar.gz

tar -xzf montreal-forced-aligner_linux.tar.gz

mkdir out

git clone https://github.com/nbusser/SM-Dictionaries.git

wget http://mlmlab.org/mfa/mfa-models/french_prosodylab.zip

echo "
{
    \"align_exe\": \"aligner/bin/mfa_align\",
    \"trained_model\": \"aligner/pretrained_models/french_prosodylab.zip\",
    \"dict_path\": \"aligner/fr.dict\",
    \"dict_consonant_vowel_path\": \"aligner/fr_consonant_vowel.dict\",
    \"lang\": \"fr\",
    \"folder\": \".subs\"
}" > ../config.json

pyinstaller --name="P00pMaker" --windowed ../main.py --add-data montreal-forced-aligner/bin:aligner/bin --add-data montreal-forced-aligner/pretrained_models:aligner/pretrained_models --add-data montreal-forced-aligner/lib:aligner/bin --add-data out:aligner/out --add-data SM-Dictionaries/fr.dict:aligner --add-data SM-Dictionaries/fr_consonant_vowel.dict:aligner --add-data french_prosodylab.zip:aligner/pretrained_models --add-data ../config.json:.

rm dist/P00pMaker/aligner/bin/thirdparty/bin/libopenblas.so.0

ln -s /usr/lib/x86_64-linux-gnu/libpython3.6m.so dist/P00pMaker/aligner/bin/libpython3.6m.so

rm montreal-forced-aligner_linux.tar.gz
rm french_prosodylab.zip
rm -rf montreal-forced-aligner
rm -rf out
rm -rf SM-Dictionaries
rm ../config.json
