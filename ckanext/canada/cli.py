import click
import traceback
from io import StringIO

from ckan.logic import get_action
from ckan import model

from ckanext.canada import utils, triggers


def _get_user(user):
    if user is not None:
        return user
    return get_action('get_site_user')({'ignore_auth': True}).get('name')


def get_commands():
    return canada


@click.group(short_help="Canada management commands")
def canada():
    """Canada management commands.
    """
    pass


@canada.command(short_help="Updates Portal records with Registry records.")
@click.argument("portal_ini")
@click.option(
    "-u",
    "--ckan-user",
    default=None,
    help="Sets the owner of packages created, default: ckan system user",
)
@click.argument("last_activity_date", required=False)
@click.option(
    "-p",
    "--processes",
    default=1,
    help="Sets the number of worker processes, default: 1",
)
@click.option(
    "-m",
    "--mirror",
    is_flag=True,
    help="Copy all datasets, default is to treat unreleased datasets as deleted",
)
@click.option(
    "-l",
    "--log",
    default=None,
    help="Write log of actions to log filename",
)
@click.option(
    "-t",
    "--tries",
    default=1,
    help="Try <num> times, set > 1 to retry on failures, default: 1",
)
@click.option(
    "-d",
    "--delay",
    default=60,
    help="Delay between retries, default: 60",
)
def portal_update(portal_ini,
                  ckan_user,
                  last_activity_date=None,
                  processes=1,
                  mirror=False,
                  log=None,
                  tries=1,
                  delay=60):
    """
    Collect batches of packages modified at local CKAN since activity_date
    and apply the package updates to the portal instance for all
    packages with published_date set to any time in the past.

    Full Usage:\n
        canada portal-update <portal.ini> -u <user>\n
                             [<last activity date> | [<k>d][<k>h][<k>m]]\n
                             [-p <num>] [-m] [-l <log file>]\n
                             [-t <num> [-d <seconds>]]

    <last activity date>: Last date for reading activites, default: 7 days ago\n
    <k> number of hours/minutes/seconds in the past for reading activities
    """
    utils.PortalUpdater(portal_ini,
                        ckan_user,
                        last_activity_date,
                        processes,
                        mirror,
                        log,
                        tries,
                        delay).portal_update()


@canada.command(short_help="Copy records from another source.")
@click.option(
    "-m",
    "--mirror",
    is_flag=True,
    help="Copy all datasets, default is to treat unreleased datasets as deleted",
)
@click.option(
    "-u",
    "--ckan-user",
    default=None,
    help="Sets the owner of packages created, default: ckan system user",
)
@click.option(
    "-o",
    "--source",
    default=None,
    help="Source datastore url to copy datastore records",
)
def copy_datasets(mirror=False, ckan_user=None, source=None):
    """
    A process that accepts packages on stdin which are compared
    to the local version of the same package.  The local package is
    then created, updated, deleted or left unchanged.  This process
    outputs that action as a string 'created', 'updated', 'deleted'
    or 'unchanged'

    Full Usage:\n
        canada copy-datasets [-m] [-o <source url>]
    """
    utils.copy_datasets(source,
                        _get_user(ckan_user),
                        mirror)



@canada.command(short_help="Lists changed records.")
@click.argument("since_date")
@click.option(
    "-s",
    "--server",
    default=None,
    help="Retrieve from <remote server>",
)
@click.option(
    "-b",
    "--brief",
    is_flag=True,
    help="Don't output requested dates",
)
def changed_datasets(since_date, server=None, brief=False):
    """
    Produce a list of dataset ids and requested dates. Each package
    id will appear at most once, showing the activity date closest
    to since_date. Requested dates are preceeded with a "#"

    Full Usage:\n
        canada changed-datasets [<since date>] [-s <remote server>] [-b]
    """
    utils.changed_datasets(since_date,
                           server,
                           brief)


@canada.command(short_help="Load Suggested Datasets from a CSV file.")
@click.argument("suggested_datasets_csv")
@click.option(
    "--use-created-date",
    is_flag=True,
    help="Use date_created field for date forwarded to data owner and other statuses instead of today's date",
)
def load_suggested(suggested_datasets_csv, use_created_date=False):
    """
    A process that loads suggested datasets from Drupal into CKAN

    Full Usage:\n
        canada load-suggested [--use-created-date] <suggested-datasets.csv>
    """
    utils.load_suggested(use_created_date,
                         suggested_datasets_csv)


@canada.command(short_help="Updates/creates database triggers.")
def update_triggers():
    """
    Create/update triggers used by PD tables
    """
    triggers.update_triggers()


@canada.command(short_help="Load Inventory Votes from a CSV file.")
@click.argument("votes_json")
def update_inventory_votes(votes_json):
    """

    Full Usage:\n
        canada update-inventory-votes <votes.json>
    """
    utils.update_inventory_votes(votes_json)


@canada.command(short_help="Tries to update resource sizes from a CSV file.")
@click.argument("resource_sizes_csv")
def resource_size_update(resource_sizes_csv):
    """
    Tries to update resource sizes from a CSV file.

    Full Usage:\n
        canada resource-size-update <resource_sizes.csv>
    """
    utils.resource_size_update(resource_sizes_csv)


@canada.command(short_help="Tries to replace resource URLs from http to https.")
@click.argument("https_report")
@click.argument("https_alt_report")
def update_resource_url_https(https_report, https_alt_report):
    """
    This function updates all broken http links into https links.
    https_report: the report with all of the links (a .json file)
    ex. https://github.com/open-data/opengov-orgs-http/blob/main/orgs_http_data.json.
    https_alt_report: the report with links where alternates exist (a .json file)
    ex. https://github.com/open-data/opengov-orgs-http/blob/main/https_alternative_count.json.
    For more specifications about the files in use please visit,
    https://github.com/open-data/opengov-orgs-http.

    Full Usage:\n
        canada update-resource-url-https <https_report> <https_alt_report>
    """
    utils.resource_https_update(https_report,
                                https_alt_report)


@canada.command(short_help="Runs ckanext-validation for all supported resources.")
def bulk_validate():
    """
    Use this command to bulk validate the resources. Any resources which
    are already in datastore but not validated will be removed.

    Requires stdin

    Full Usage:\n
         ckanapi search datasets include_private=true -c $CONFIG_INI |\n
         ckan -c $CONFIG_INI canada bulk-validate
    """
    utils.bulk_validate()


@canada.command(short_help="Deletes rows from the activity table.")
@click.option(
    u"-d",
    u"--days",
    help=u"Number of days to go back. E.g. 120 will keep 120 days of activities. Default: 90",
    default=90
)
@click.option(u"-q", u"--quiet", is_flag=True, help=u"Suppress human interaction.", default=False)
def delete_activities(days=90, quiet=False):
    """Delete rows from the activity table past a certain number of days.
    """
    activity_count = model.Session.execute(
                        u"SELECT count(*) FROM activity "
                        "WHERE timestamp < NOW() - INTERVAL '{d} days';"
                        .format(d=days)) \
                        .fetchall()[0][0]

    if not bool(activity_count):
        click.echo(u"\nNo activities found past {d} days".format(d=days))
        return

    if not quiet:
        click.confirm(u"\nAre you sure you want to delete {num} activities?"
                          .format(num=activity_count), abort=True)

    model.Session.execute(u"DELETE FROM activity WHERE timestamp < NOW() - INTERVAL '{d} days';".format(d=days))
    model.Session.commit()

    click.echo(u"\nDeleted {num} rows from the activity table".format(num=activity_count))


def _get_site_user_context():
    user = get_action('get_site_user')({'ignore_auth': True}, {})
    return {"user": user['name'], "ignore_auth": True}


def _get_datastore_tables(verbose=False):
    # type: (bool) -> list
    """
    Returns a list of resource ids (table names) from
    the DataStore database.
    """
    tables = get_action('datastore_search')(_get_site_user_context(),
                                            {"resource_id": "_table_metadata",
                                             "offset": 0,
                                             "limit": 100000})
    if not tables:
        return []
    if verbose:
        click.echo("Gathered %s table names from the DataStore." % len(tables.get('records', [])))
    return [r.get('name') for r in tables.get('records', [])]


def _get_datastore_resources(valid=True, is_datastore_active=True, verbose=False):
    # type: (bool, bool, bool) -> list
    """
    Returns a list of resource ids that are DataStore
    enabled and that are of upload url_type.

    Defaults to only return valid resources.
    """
    results = True
    counter = 0
    batch_size = 1000
    datastore_resources = []
    while results:
        _packages = get_action('package_search')(_get_site_user_context(),
                                                 {"q": "*:*",
                                                  "start": counter,
                                                  "rows": batch_size,
                                                  "include_private": True})['results']
        if _packages:
            if verbose:
                if is_datastore_active:
                    click.echo("Looking through %s packages to find DataStore Resources." % len(_packages))
                else:
                    click.echo("Looking through %s packages to find NON-DataStore Resources." % len(_packages))
                if valid == None:
                    click.echo("Gathering Invalid and Valid Resources...")
                elif valid == True:
                    click.echo("Gathering only Valid Resources...")
                elif valid == False:
                    click.echo("Gathering only Invalid Resources...")
            counter += len(_packages)
            for _package in _packages:
                for _resource in _package.get('resources', []):
                    if _resource.get('id') in datastore_resources:  # already in return list
                        continue
                    if _resource.get('url_type') != 'upload' \
                    and _resource.get('url_type') != '':  # we only want upload or link types
                        continue
                    if is_datastore_active and not _resource.get('datastore_active'):
                        continue
                    if not is_datastore_active and _resource.get('datastore_active'):
                        continue
                    if valid == None:
                        datastore_resources.append(_resource.get('id'))
                        continue
                    validation_status = _resource.get('validation_status')
                    if valid == True and validation_status == 'success':
                        datastore_resources.append(_resource.get('id'))
                        continue
                    if valid == False and validation_status == 'failure':
                        datastore_resources.append(_resource.get('id'))
                        continue
        else:
            results = False
    if verbose:
        if is_datastore_active:
            click.echo("Gathered %s DataStore Resources." % len(datastore_resources))
        else:
            click.echo("Gathered %s NON-DataStore Resources." % len(datastore_resources))
    return datastore_resources


def _get_datastore_count(context, resource_id, verbose=False, status=1, max=1):
    # type: (dict, str, bool, int, int) -> int|None
    """
    Returns the count of rows in the DataStore table for a given resource ID.
    """
    if verbose:
        click.echo("%s/%s -- Checking DataStore record count for Resource %s" % (status, max, resource_id))
    info = get_action('datastore_info')(context, {"id": resource_id})
    return info.get('meta', {}).get('count')


def _error_message(message):
    click.echo("\n\033[1;33m%s\033[0;0m\n\n" % message)


def _success_message(message):
    click.echo("\n\033[0;36m\033[1m%s\033[0;0m\n\n" % message)


@canada.command(short_help="Sets datastore_active to False for Invalid Resources.")
@click.option('-r', '--resource-id', required=False, type=click.STRING, default=None,
              help='Resource ID to set the datastore_active flag. Defaults to None.')
@click.option('-d', '--delete-table-views', is_flag=True, type=click.BOOL, help='Deletes any Datatable Views from the Resource.')
@click.option('-v', '--verbose', is_flag=True, type=click.BOOL, help='Increase verbosity.')
@click.option('-q', '--quiet', is_flag=True, type=click.BOOL, help='Suppress human interaction.')
@click.option('-l', '--list', is_flag=True, type=click.BOOL, help='List the Resource IDs instead of setting the flags to false.')
def set_datastore_false_for_invalid_resources(resource_id=None, delete_table_views=False, verbose=False, quiet=False, list=False):
    """
    Sets datastore_active to False for Resources that are
    not valid but are empty in the DataStore database.
    """

    try:
        from ckanext.datastore.logic.action import set_datastore_active_flag
    except ImportError:
        _error_message("DataStore extension is not active.")
        return

    errors = StringIO()

    context = _get_site_user_context()

    datastore_tables = _get_datastore_tables(verbose=verbose)
    resource_ids_to_set = []
    status = 1
    if not resource_id:
        resource_ids = _get_datastore_resources(valid=False, verbose=verbose)
        max = len(resource_ids)
        for resource_id in resource_ids:
            if resource_id in resource_ids_to_set:
                continue
            if resource_id in datastore_tables:
                try:
                    count = _get_datastore_count(context, resource_id, verbose=verbose, status=status, max=max)
                    if int(count) == 0:
                        if verbose:
                            click.echo("%s/%s -- Resource %s has %s rows in DataStore. Let's fix this one..." % (status, max, resource_id, count))
                        resource_ids_to_set.append(resource_id)
                    elif verbose:
                        click.echo("%s/%s -- Resource %s has %s rows in DataStore. Skipping..." % (status, max, resource_id, count))
                except Exception as e:
                    if verbose:
                        errors.write('Failed to get DataStore info for Resource %s with errors:\n\n%s' % (resource_id, e))
                        errors.write('\n')
                        traceback.print_exc(file=errors)
                    pass
            status += 1
    else:
        try:
            count = _get_datastore_count(context, resource_id, verbose=verbose)
            if int(count) == 0:
                if verbose:
                    click.echo("1/1 -- Resource %s has %s rows in DataStore. Let's fix this one..." % (resource_id, count))
                resource_ids_to_set = [resource_id]
            elif verbose:
                click.echo("1/1 -- Resource %s has %s rows in DataStore. Skipping..." % (resource_id, count))
        except Exception as e:
            if verbose:
                errors.write('Failed to get DataStore info for Resource %s with errors:\n\n%s' % (resource_id, e))
                errors.write('\n')
                traceback.print_exc(file=errors)
            pass

    if resource_ids_to_set and not quiet and not list:
        click.confirm("Do you want to set datastore_active flag to False for %s Invalid Resources?" % len(resource_ids_to_set), abort=True)

    status = 1
    max = len(resource_ids_to_set)
    for id in resource_ids_to_set:
        if list:
            click.echo(id)
        else:
            try:
                set_datastore_active_flag(model, {"resource_id": id}, False)
                if verbose:
                    click.echo("%s/%s -- Set datastore_active flag to False for Invalid Resource %s" % (status, max, id))
                if delete_table_views:
                    views = get_action('resource_view_list')(context, {"id": id})
                    if views:
                        for view in views:
                            if view.get('view_type') == 'datatables_view':
                                get_action('resource_view_delete')(context, {"id": view.get('id')})
                                if verbose:
                                    click.echo("%s/%s -- Deleted datatables_view %s from Invalid Resource %s" % (status, max, view.get('id'), id))
            except Exception as e:
                if verbose:
                    errors.write('Failed to set datastore_active flag for Invalid Resource %s with errors:\n\n%s' % (id, e))
                    errors.write('\n')
                    traceback.print_exc(file=errors)
                pass
        status += 1

    has_errors = errors.tell()
    errors.seek(0)
    if has_errors:
        _error_message(errors.read())
    elif resource_ids_to_set and not list:
        _success_message('Set datastore_active flag for %s Invalid Resources.' % len(resource_ids_to_set))
    elif not resource_ids_to_set:
        _success_message('There are no Invalid Resources that have the datastore_active flag at this time.')


@canada.command(short_help="Re-submits valid, empty DataStore Resources to Validation.")
@click.option('-r', '--resource-id', required=False, type=click.STRING, default=None,
              help='Resource ID to re-submit to Validation. Defaults to None.')
@click.option('-v', '--verbose', is_flag=True, type=click.BOOL, help='Increase verbosity.')
@click.option('-q', '--quiet', is_flag=True, type=click.BOOL, help='Suppress human interaction.')
@click.option('-l', '--list', is_flag=True, type=click.BOOL, help='List the Resource IDs instead of submitting them to Validation.')
def resubmit_empty_datastore_resources(resource_id=None, verbose=False, quiet=False, list=False):
    """
    Re-submits valid, empty DataStore Resources to Validation.
    """

    try:
        get_action('resource_validation_run')
    except Exception:
        _error_message("Validation extension is not active.")
        return

    errors = StringIO()

    context = _get_site_user_context()

    datastore_tables = _get_datastore_tables(verbose=verbose)
    resource_ids_to_submit = []
    status = 1
    if not resource_id:
        resource_ids = _get_datastore_resources(verbose=verbose)
        max = len(resource_ids)
        for resource_id in resource_ids:
            if resource_id in resource_ids_to_submit:
                continue
            if resource_id in datastore_tables:
                try:
                    count = _get_datastore_count(context, resource_id, verbose=verbose, status=status, max=max)
                    if int(count) == 0:
                        if verbose:
                            click.echo("%s/%s -- Resource %s has %s rows in DataStore. Let's fix this one..." % (status, max, resource_id, count))
                        resource_ids_to_submit.append(resource_id)
                    elif verbose:
                        click.echo("%s/%s -- Resource %s has %s rows in DataStore. Skipping..." % (status, max, resource_id, count))
                except Exception as e:
                    if verbose:
                        errors.write('Failed to get DataStore info for Resource %s with errors:\n\n%s' % (resource_id, e))
                        errors.write('\n')
                        traceback.print_exc(file=errors)
                    pass
            status += 1
    else:
        # we want to check that the provided resource id has no DataStore rows still
        try:
            count = _get_datastore_count(context, resource_id, verbose=verbose)
            if int(count) == 0:
                if verbose:
                    click.echo("1/1 -- Resource %s has %s rows in DataStore. Let's fix this one..." % (resource_id, count))
                resource_ids_to_submit.append(resource_id)
            elif verbose:
                click.echo("1/1 -- Resource %s has %s rows in DataStore. Skipping..." % (resource_id, count))
        except Exception as e:
            if verbose:
                errors.write('Failed to get DataStore info for Resource %s with errors:\n\n%s' % (resource_id, e))
                errors.write('\n')
                traceback.print_exc(file=errors)
            pass

    if resource_ids_to_submit and not quiet and not list:
        click.confirm("Do you want to re-submit %s Resources to Validation?" % len(resource_ids_to_submit), abort=True)

    status = 1
    max = len(resource_ids_to_submit)
    for id in resource_ids_to_submit:
        if list:
            click.echo(id)
        else:
            try:
                get_action('resource_validation_run')(context, {"resource_id": id, "async": True})
                if verbose:
                    click.echo("%s/%s -- Submitted Resource %s to Validation" % (status, max, id))
            except Exception as e:
                if verbose:
                    errors.write('Failed to submit Resource %s to Validation with errors:\n\n%s' % (id, e))
                    errors.write('\n')
                    traceback.print_exc(file=errors)
                pass
        status += 1

    has_errors = errors.tell()
    errors.seek(0)
    if has_errors:
        _error_message(errors.read())
    elif resource_ids_to_submit and not list:
        _success_message('Re-submitted %s Resources to Validation.' % len(resource_ids_to_submit))
    elif not resource_ids_to_submit:
        _success_message('No valid, empty DataStore Resources to re-submit at this time.')


@canada.command(short_help="Deletes Invalid Resource DataStore tables.")
@click.option('-r', '--resource-id', required=False, type=click.STRING, default=None,
              help='Resource ID to delete the DataStore table for. Defaults to None.')
@click.option('-d', '--delete-table-views', is_flag=True, type=click.BOOL, help='Deletes any Datatable Views from the Resource.')
@click.option('-v', '--verbose', is_flag=True, type=click.BOOL, help='Increase verbosity.')
@click.option('-q', '--quiet', is_flag=True, type=click.BOOL, help='Suppress human interaction.')
@click.option('-l', '--list', is_flag=True, type=click.BOOL, help='List the Resource IDs instead of deleting their DataStore tables.')
def delete_invalid_datastore_tables(resource_id=None, delete_table_views=False, verbose=False, quiet=False, list=False):
    """
    Deletes Invalid Resources DataStore tables. Even if the table is not empty.
    """

    errors = StringIO()

    context = _get_site_user_context()

    datastore_tables = _get_datastore_tables(verbose=verbose)
    resource_ids_to_delete = []
    if not resource_id:
        resource_ids = _get_datastore_resources(valid=False, verbose=verbose)
        for resource_id in resource_ids:
            if resource_id in resource_ids_to_delete:
                continue
            if resource_id in datastore_tables:
                resource_ids_to_delete.append(resource_id)
    else:
        resource_ids_to_delete.append(resource_id)

    if resource_ids_to_delete and not quiet and not list:
        click.confirm("Do you want to delete the DataStore tables for %s Resources?" % len(resource_ids_to_delete), abort=True)

    status = 1
    max = len(resource_ids_to_delete)
    for id in resource_ids_to_delete:
        if list:
            click.echo(id)
        else:
            try:
                get_action('datastore_delete')(context, {"resource_id": id, "force": True})
                if verbose:
                    click.echo("%s/%s -- Deleted DataStore table for Resource %s" % (status, max, id))
                if delete_table_views:
                    views = get_action('resource_view_list')(context, {"id": id})
                    if views:
                        for view in views:
                            if view.get('view_type') == 'datatables_view':
                                get_action('resource_view_delete')(context, {"id": view.get('id')})
                                if verbose:
                                    click.echo("%s/%s -- Deleted datatables_view %s from Invalid Resource %s" % (status, max, view.get('id'), id))
            except Exception as e:
                if verbose:
                    errors.write('Failed to delete DataStore table for Resource %s with errors:\n\n%s' % (id, e))
                    errors.write('\n')
                    traceback.print_exc(file=errors)
                pass
        status += 1

    has_errors = errors.tell()
    errors.seek(0)
    if has_errors:
        _error_message(errors.read())
    elif resource_ids_to_delete and not list:
        _success_message('Deleted %s DataStore tables.' % len(resource_ids_to_delete))
    elif not resource_ids_to_delete:
        _success_message('No Invalid Resources at this time.')


@canada.command(short_help="Deletes all datatable views from non-datastore Resources.")
@click.option('-r', '--resource-id', required=False, type=click.STRING, default=None,
              help='Resource ID to delete the table views for. Defaults to None.')
@click.option('-v', '--verbose', is_flag=True, type=click.BOOL, help='Increase verbosity.')
@click.option('-q', '--quiet', is_flag=True, type=click.BOOL, help='Suppress human interaction.')
@click.option('-l', '--list', is_flag=True, type=click.BOOL, help='List the Resource IDs instead of deleting their table views.')
def delete_table_view_from_non_datastore_resources(resource_id=None, verbose=False, quiet=False, list=False):
    """
    Deletes all datatable views from Resources that are not datastore_active.
    """

    errors = StringIO()

    context = _get_site_user_context()

    view_ids_to_delete = []
    if not resource_id:
        resource_ids = _get_datastore_resources(valid=None, is_datastore_active=False, verbose=verbose)
        for resource_id in resource_ids:
            try:
                views = get_action('resource_view_list')(context, {"id": resource_id})
                if views:
                    for view in views:
                        if view.get('view_type') == 'datatables_view':
                            if view.get('id') in view_ids_to_delete:
                                continue
                            if verbose:
                                click.echo("Resource %s has datatables_view %s. Let's delete this one..." % (resource_id, view.get('id')))
                            view_ids_to_delete.append(view.get('id'))
                elif verbose:
                    click.echo("Resource %s has no views. Skipping..." % (resource_id))
            except Exception as e:
                if verbose:
                    errors.write('Failed to get views for Resource %s with errors:\n\n%s' % (resource_id, e))
                    errors.write('\n')
                    traceback.print_exc(file=errors)
                pass
    else:
        try:
            views = get_action('resource_view_list')(context, {"id": resource_id})
            if views:
                for view in views:
                    if view.get('view_type') == 'datatables_view':
                        if view.get('id') in view_ids_to_delete:
                            continue
                        if verbose:
                            click.echo("%s/%s -- Resource %s has datatables_view %s. Let's delete this one..." % (status, max, resource_id, view.get('id')))
                        view_ids_to_delete.append(view.get('id'))
            elif verbose:
                click.echo("%s/%s -- Resource %s has no datatables_view(s). Skipping..." % (status, max, resource_id))
        except Exception as e:
            if verbose:
                errors.write('Failed to get views for Resource %s with errors:\n\n%s' % (resource_id, e))
                errors.write('\n')
                traceback.print_exc(file=errors)
            pass

    if view_ids_to_delete and not quiet and not list:
        click.confirm("Do you want to delete %s datatables_view(s)?" % len(view_ids_to_delete), abort=True)

    status = 1
    max = len(view_ids_to_delete)
    for id in view_ids_to_delete:
        if list:
            click.echo(id)
        else:
            try:
                get_action('resource_view_delete')(context, {"id": id})
                if verbose:
                    click.echo("%s/%s -- Deleted datatables_view %s" % (status, max, id))
            except Exception as e:
                if verbose:
                    errors.write('Failed to delete datatables_view %s with errors:\n\n%s' % (id, e))
                    errors.write('\n')
                    traceback.print_exc(file=errors)
                pass
        status += 1

    has_errors = errors.tell()
    errors.seek(0)
    if has_errors:
        _error_message(errors.read())
    elif view_ids_to_delete and not list:
        _success_message('Deleted %s datatables_view(s).' % len(view_ids_to_delete))
    elif not view_ids_to_delete:
        _success_message('No datatables_view(s) at this time.')
