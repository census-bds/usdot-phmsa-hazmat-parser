import table
import soup


def packaging(hazmat_id, bulk=True):
    '''
    Looks up the non_bulk_packaging or bulk_packaging table and returns the part
    of section 173 that details packaging requirements for that material
    '''
    if bulk:
        table_name = "bulk_packaging"
    else:
        table_name = "non_bulk_packaging"
    requirement = table.cur.execute(
        "SELECT requirement FROM {} WHERE hazmat_id = {}".format(
            table_name, hazmat_id))
    subpart_string = requirement.fetchall()[0][0]
    subpart_tag = soup.SOUP.find(
        'sectno', text="§ 173.{}".format(subpart_string))
    return subpart_tag.parent
