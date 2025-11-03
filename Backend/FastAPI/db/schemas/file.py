def file_schema(file) -> dict:
    return {"id": str(file["_id"]),
            "file_number": file["file_number"],
            "creation_date": file["creation_date"],
            "observation_general": file["observation_general"]
            }


def files_schema(files) -> list:
    return [file_schema(file) for file in files]