import sqlite3

# Conexión a la base de datos (se creará si no existe)
conn = sqlite3.connect('emaildb.sqlite')
cur = conn.cursor()

# Limpiar la tabla si ya existe
cur.execute('DROP TABLE IF EXISTS Counts')

# Crear la tabla
cur.execute('CREATE TABLE Counts (org TEXT, count INTEGER)')

# Leer archivo mbox.txt
fname = input('Enter file name: ')
if len(fname) < 1:
    fname = 'mbox.txt'

fh = open(fname)
for line in fh:
    if not line.startswith('From: '):
        continue
    pieces = line.split()
    email = pieces[1]
    org = email.split('@')[1]  # Obtener dominio
    
    # Insertar o actualizar el contador por organización
    cur.execute('SELECT count FROM Counts WHERE org = ? ', (org,))
    row = cur.fetchone()
    if row is None:
        cur.execute('INSERT INTO Counts (org, count) VALUES (?, 1)', (org,))
    else:
        cur.execute('UPDATE Counts SET count = count + 1 WHERE org = ?', (org,))

# Guardar cambios (mejor al final para eficiencia)
conn.commit()

# Mostrar los 10 resultados principales
sqlstr = 'SELECT org, count FROM Counts ORDER BY count DESC LIMIT 10'

print('\nTop organizations:')
for row in cur.execute(sqlstr):
    print(row[0], row[1])

cur.close()

