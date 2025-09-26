from db_players import add_player, get_codename

print("Insert first player:", add_player(500, "Frank")) # True
print("Insert second player:", add_player(501, "Jeremy")) # True

print("Inserting a duplicate id & name:", add_player(500, "Frank")) # False
print("Inserting a duplicate id:", add_player(500, "Jeff")) # False
print("Inserting a duplicate name:", add_player(502, "Frank")) # True

print("Lookup existing codename:", get_codename(500)) # Frank
print("Lookup non-existing codename:", get_codename(99999))  # None
