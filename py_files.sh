# /bin/bash
commitHash1=$(git rev-list HEAD | head -n 1)
commitHash2=$(git rev-list $commitHash1~1 | head -n 1)
python_files=$(git diff --name-only --diff-filter=AM $commitHash2..$commitHash1 | grep '\.py$');
if [[ -z "$python_files" ]]; then
	echo "No added and modified Python files in the last commit"
else
        files=$python_files
        echo "Added and modified Python files in the last commit:"
        echo "$files"
fi
for file in $files
do
	respond=$(flake8 "./$file" --exit-zero)
	if [ "$respond" != "" ]
	then
		echo "The mistake $respond in file $file"
		echo "Try to improve"
		black "./$file"
		respond_impr=$(flake8 "./$file" --exit-zero)
		echo "The mistake unimproved: $respond_impr in file $file"
		if [ "$respond_impr" != "" ]
		then
			echo "Unimproved syntax in $file"
			exit -1
		else	
			echo "Improved syntax in $file"
		fi
	else
		echo "File satisfies PEP8 synaxt"
	fi
done