from .settings import settings


def main() -> None:
    print(settings.DISCORD_TOKEN)
    print(settings.LISTEN_CHANNEL_ID)


if __name__ == "__main__":
    main()
