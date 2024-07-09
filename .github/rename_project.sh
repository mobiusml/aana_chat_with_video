#!/usr/bin/env bash
while getopts a:n:d: flag
do
    case "${flag}" in
        a) author=${OPTARG};;
        n) name=${OPTARG};;
        d) description=${OPTARG};;
    esac
done

echo "Author: $author";
echo "Project Name: $name";
echo "Description: $description";

echo "Renaming project..."

original_author="author_name"
original_name="aana_app_project"
original_description="project_description"
for filename in $(git ls-files) 
do
    sed -i "s/$original_author/$author/g" $filename
    sed -i "s/$original_name/$name/g" $filename
    sed -i "s/$original_description/$description/g" $filename
    echo "Renamed $filename"
done

mv $original_name $name

# This command runs only once on GHA!
rm -rf .github/template.yml
rm -rf .github/workflows/rename_project.yaml
rm -rf .github/rename_project.sh