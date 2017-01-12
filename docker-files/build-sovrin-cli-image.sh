#!/bin/bash -x

# Let this helper script be here. But the main helper should be in special ci repo.

# Get parameter of current git repo to download sovrin code
curr_branch=$(git rev-parse --abbrev-ref HEAD)
curr_commit=$(git rev-parse HEAD)
curr_url=$(git config --get remote.origin.url)

package_name="sovrin-client"
repo_string="git+$curr_url@$curr_commit#egg=$package_name"

do_dev_version=0
img_tag="sovrin-client-pub"
folder='./'

while getopts "dr:f:t:" opt; do
  case $opt in
    d)
      do_dev_version=1
      img_tag="sovrin-client-dev"
      ;;
    r)
      repo_string="$OPTARG"
      ;;
    f)
      folder="$OPTARG"
      ;;
    t)
      img_tag="$OPTARG"
      ;;
  esac
done

shift $((OPTIND-1))

if [ $do_dev_version -eq 1 ] ; then
  install_sovrin_cmd="pip3 install --no-cache-dir -e $repo_string"
  docker build -t "$img_tag" --build-arg install_sovrin="$install_sovrin_cmd" "$folder"
else
  docker build -t "$img_tag" "$folder"
fi
