 # chdir
ROOT_FOLDER=$(cd "$(dirname "$0")";pwd)"/../"
cd $ROOT_FOLDER
pip uninstall cinspector
pip install .
