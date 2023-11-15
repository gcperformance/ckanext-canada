#!/bin/bash

set -e;

function error_message {

    if [[ $1 ]]; then

        printf "\n\033[1;33m${1}\033[0;0m\n\n";
        exit;

    fi

}

function success_message {

    if [[ $1 ]]; then

        printf "\n\033[0;36m\033[1m${1}\033[0;0m\n\n";

    fi

}

config_file=${REGISTRY_INI};

if [[ -z "${config_file}" ]]; then

    error_message 'REGISTRY_INI environment variable not set.';

fi

if [[ -z "$(command -v ckanapi)" ]]; then

    error_message 'ckanapi command not found. Is it accessible in the PATH variable?';

fi

if [[ ! -d "/opt/tbs/tmp" ]]; then

    error_message '/opt/tbs/tmp directory does not exist.';

fi

###
# Get the file path generated from Drupal
# The SMB directories are different on some servers
# hence the checks for the different file paths
###
generated_file='/opt/tbs/ckan/smb_portal/portal/public/ati-informal-requests-analytics.csv';

if [[ ! -f "${generated_file}" ]]; then

    generated_file='/opt/tbs/ckan/smb/portal/public/ati-informal-requests-analytics.csv';

    if [[ ! -f "${generated_file}" ]]; then

        generated_file='/opt/tbs/ckan/smb_portal/portal/public/static/ati-informal-requests-analytics.csv';

        if [[ ! -f "${generated_file}" ]]; then

            generated_file='/opt/tbs/ckan/smb/portal/public/static/ati-informal-requests-analytics.csv';

            if [[ ! -f "${generated_file}" ]]; then

                error_message '/opt/tbs/ckan/[smb_portal|smb]/portal/public/[static/]ati-informal-requests-analytics.csv does not exist.';

            fi

        fi

    fi

fi
###
# END
# Get the file generated from Drupal
# END
###

tmp_dir=$(mktemp -p /opt/tbs/tmp -d);
tmp_file="${tmp_dir}/ati-informal-requests-analytics.csv";

if [[ ! -d "${tmp_dir}" ]]; then

    error_message 'Failed to create temporary file directory.';

fi

###
# We do not want the current month's counts
###
filter_date="$(date +%Y),$(echo $(date +%m) | sed 's/^0*//'),";
echo "Filtering out rows: ${filter_date}";
# sed should be safe, as there should not be newlines in the CSV
# that is generated in Drupal from PHP's fputcsv
sed "/^${filter_date}*/d" < ${generated_file} > ${tmp_file};

resource_id='e664cf3d-6cb7-4aaa-adfa-e459c2552e3e';
ckanapi action resource_patch -c ${config_file} id=${resource_id} upload@"${tmp_file}";

if [[ -d "${tmp_dir}" ]]; then

    rm -rf ${tmp_dir};

fi

success_message 'Done!';
