import shelve

with shelve.open("frontier.shelve") as db:
    print("Total entries:", len(db))

    for key in db:
        print("Key:", key)
        print("Value:", db[key])
        print()
