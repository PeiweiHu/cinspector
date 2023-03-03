# chdir
ROOT_FOLDER=$(cd "$(dirname "$0")";pwd)"/../"
cd $ROOT_FOLDER
# yapf check
yapf -d -e docs --style=google --recursive .
# mypy check
mypy ./cinspector
