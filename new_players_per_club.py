#!/usr/bin/env python3
"""
Summarise which clubs (verein) registered additional players during the season.

Usage:
    python new_players_per_club.py start_of_season.csv end_of_season.csv

A player counts as "new" if their spielernr appears in the end-of-season file
but not in the start-of-season file. Players who were already in the first
file (even if they switched clubs) are ignored, since their fee was already
paid via their old club. Only spielernr is used for matching.
"""
import csv
import sys
from collections import defaultdict


def clean(value):
    """Strip the Excel-style ="..." wrapper and whitespace from a cell."""
    v = (value or "").strip()
    if v.startswith('="') and v.endswith('"'):
        v = v[2:-1]
    elif v.startswith("="):
        v = v[1:]
    return v.strip().strip('"').strip()


def read_players(path):
    """Return a dict spielernr -> row dict (cleaned)."""
    with open(path, encoding="cp1252", newline="") as f:
        lines = f.read().splitlines()

    # Drop the Excel "sep=" hint line if present
    if lines and lines[0].lower().startswith("sep="):
        lines = lines[1:]

    reader = csv.reader(lines, delimiter="\t")
    header = [clean(h).lower() for h in next(reader)]

    players = {}
    for raw in reader:
        if not any(c.strip() for c in raw):
            continue
        row = {h: clean(c) for h, c in zip(header, raw) if h}
        nr = row.get("spielernr", "")
        if nr:
            players[nr] = row
    return players


def main():
    if len(sys.argv) != 3:
        sys.exit(f"Usage: {sys.argv[0]} start_of_season.csv end_of_season.csv")

    start = read_players(sys.argv[1])
    end = read_players(sys.argv[2])
    
    print(f"Spieler am Anfang: {len(start)}")
    print(f"Spieler am Ende: {len(end)}")

    new_by_club = defaultdict(list)
    for nr, row in end.items():
        if nr not in start:
            new_by_club[row.get("verein", "(unbekannt)")].append(row)

    if not new_by_club:
        print("Keine neu registrierten Spieler in der Saison.")
        return

    total = 0
    print("Zusätzlich registrierte Spieler pro Verein")
    print("=" * 50)
    for club in sorted(new_by_club):
        players = sorted(new_by_club[club], key=lambda r: r["spielernr"])
        total += len(players)
        print(f"\n{club}: {len(players)} Spieler")
        for p in players:
            print(f"  - {p['spielernr']}  {p.get('nachname', '')}, {p.get('vorname', '')}")
    print("\n" + "=" * 50)
    print(f"Gesamt: {total} Spieler in {len(new_by_club)} Vereinen")


if __name__ == "__main__":
    main()
