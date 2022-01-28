def read(table, fields, conditions):
    """ Generates SQL for a SELECT statement matching the kwargs passed. """
    sql = list()
    if fields:
      sql.append("SELECT " + ", ".join("%s" % (X) for X in fields))
      sql.append(" FROM %s " % table)
    else:
      sql.append("SELECT * FROM %s " % table)

    if conditions:
        sql.append("WHERE " + " AND ".join("%s" % (v) for v in conditions))
    sql.append(";")
    return "".join(sql)


def create_list(item=None, value=None, operator=None):
  temp_list = list()
  if item is not None and value is not None and operator is not None:
    temp_list.append(item+operator+str(value))

  return temp_list

fields = ["nombre", "campo"] # Puede venir asi de la lista de campos
dic_data = create_list('perro', 10, '=')
print(read("tbl",fields , dic_data))