#!/bin/bash
	(arrays=(
		pkgname
		arch
		license
		groups
		categories
		depends
		makedepends
		optdepends
		provides
		conflicts
		replaces
		backup
		options
		hooks
		source
		noextract
		md5sums
		sha1sums
		sha224sums
		sha256sums
		sha384sums
		sha512sums
	)

	before=$(env -0|base64)
	set -a
	source ${1:-PKGBUILD} >/dev/null 2>/dev/null
	set +a

	IFS=$'\n'
	pkgarrays="$(for array in ${arrays[@]}; do
		echo -n "${array}=( "
		for value in $(eval "for v in $(echo \${$array[@]}); do echo \$v; done;"); do
			echo -ne "'${value// /\0}' "
		done
		echo ")"
	done|base64)"

	pkgvars.py <(base64 -d <<< "$before") <(env -0) <(base64 -d <<< "$pkgarrays"))
