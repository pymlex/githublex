from githublex import gh_login, gh_setup


def main() -> None:
    gh_setup()
    gh_login()


if __name__ == "__main__":
    main()
