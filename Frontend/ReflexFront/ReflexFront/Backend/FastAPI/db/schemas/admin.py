def admin_schema(admin) -> dict:
    return {"id": str(admin["_id"]),
            "name": admin["name"],
            "surname": admin["surname"],
            "email": admin["email"],
            "username": admin["username"]}

def admins_schema(admins) -> list:
    return [admin_schema(admin) for admin in admins]
