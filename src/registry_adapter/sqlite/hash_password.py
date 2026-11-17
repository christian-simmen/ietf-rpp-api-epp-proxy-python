"""Prints the hash of a password for `rpp_sqlite_clients`: `python -m registry_adapter.sqlite.hash_password`. The
password is read from the standard input, so that it is not in the history of a shell."""
import sys

from registry_adapter.sqlite.password_hash import hash_password

if __name__ == "__main__":
    print(hash_password(sys.stdin.readline().rstrip("\n")))
