MIGRATIONS = []


def migration(fn):
    MIGRATIONS.append(fn)
    return fn
