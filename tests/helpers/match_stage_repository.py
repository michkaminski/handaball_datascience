class EtapMeczowInMemoryRepository:
    def pobierz_rundy(self) -> list[str]:
        return ["Runda zasadnicza", "Play-off"]

    def pobierz_kolejki(self) -> list[str]:
        return ["Kolejka 1", "Kolejka 2"]
