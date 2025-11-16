from database import get_unapproved_polls

def main():
    polls = get_unapproved_polls()
    print("Unapproved polls:")
    for p in polls:
        print(p)

if __name__ == "__main__":
    main()
