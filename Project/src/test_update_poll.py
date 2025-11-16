from database import update_poll

def main():
    poll_id_str = input("Poll id to update: ")
    poll_id = int(poll_id_str)

    new_title = input("New title (leave blank to keep current): ")
    new_desc = input("New description (leave blank to keep current): ")
    new_ends = input("New ends_at (ISO timestamp, leave blank to keep current): ")

    kwargs = {}
    if new_title.strip():
        kwargs["title"] = new_title
    if new_desc.strip():
        kwargs["description"] = new_desc
    if new_ends.strip():
        kwargs["ends_at"] = new_ends

    updated = update_poll(poll_id, **kwargs)
    print("Updated poll:")
    print(updated)

if __name__ == "__main__":
    main()
