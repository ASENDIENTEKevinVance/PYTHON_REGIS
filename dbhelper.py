from sqlite3 import connect,Row
database:str = "register.db"

def getprocess(sql:str)->list:
    db = connect(database)
    cursor = db.cursor()
    cursor.row_factory = Row
    cursor.execute(sql)
    data:list = cursor.fetchall()
    db.close()
    return data
    
def postprocess(sql:str)->bool:
    try:
        db = connect(database)
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()
    except:
        print("database error")
    return True if cursor.rowcount>0 else False
    
    
def getall_records(table:str)->list:
    sql:str = f"SELECT * FROM `{table}`"
    return getprocess(sql)
    

def add_record(table:str,**kwargs)->bool:
    keys:list = list(kwargs.keys())
    values:list = list(kwargs.values())
    keys:str = "`,`".join(keys)
    vals:str = "','".join(values)
    sql:str = f"INSERT INTO `{table}`(`{keys}`) VALUES('{vals}')"
    return postprocess(sql)
    
def delete_record(table:str,**kwargs)->bool:
    keys:list = list(kwargs.keys())
    values:list = list(kwargs.values())
    sql:str = f"DELETE FROM `{table}` WHERE `{keys[0]}`='{values[0]}'"
    return postprocess(sql)
    
    
    
