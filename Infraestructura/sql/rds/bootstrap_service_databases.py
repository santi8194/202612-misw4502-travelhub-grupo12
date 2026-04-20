from __future__ import annotations

import argparse
from dataclasses import dataclass

import psycopg
from psycopg import sql


@dataclass(frozen=True)
class ServiceDatabase:
    database: str
    role: str
    password: str
    search_path: tuple[str, ...]
    extra_schema: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap and reconcile service databases in PostgreSQL."
    )
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--admin-user", required=True)
    parser.add_argument("--admin-password", required=True)
    parser.add_argument("--authservice-password", required=True)
    parser.add_argument("--booking-password", required=True)
    parser.add_argument("--catalog-password", required=True)
    parser.add_argument("--search-password", required=True)
    return parser.parse_args()


def execute(cur: psycopg.Cursor, statement: sql.SQL) -> None:
    cur.execute(statement)


def ensure_role(cur: psycopg.Cursor, role_name: str, password: str) -> None:
    cur.execute("SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s", (role_name,))
    exists = cur.fetchone() is not None

    if not exists:
        execute(
            cur,
            sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                sql.Identifier(role_name),
                sql.Literal(password),
            ),
        )

    execute(
        cur,
        sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD {}").format(
            sql.Identifier(role_name),
            sql.Literal(password),
        ),
    )


def ensure_database(cur: psycopg.Cursor, database_name: str, owner_role: str) -> None:
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
    exists = cur.fetchone() is not None

    if not exists:
        execute(
            cur,
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)),
        )

    execute(
        cur,
        sql.SQL("ALTER DATABASE {} OWNER TO {}").format(
            sql.Identifier(database_name),
            sql.Identifier(owner_role),
        ),
    )
    execute(
        cur,
        sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(
            sql.Identifier(database_name)
        ),
    )
    execute(
        cur,
        sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
            sql.Identifier(database_name),
            sql.Identifier(owner_role),
        ),
    )


def configure_database(
    host: str,
    port: int,
    admin_user: str,
    admin_password: str,
    service: ServiceDatabase,
) -> None:
    with psycopg.connect(
        host=host,
        port=port,
        user=admin_user,
        password=admin_password,
        dbname=service.database,
        sslmode="require",
        autocommit=True,
    ) as conn:
        with conn.cursor() as cur:
            execute(cur, sql.SQL("REVOKE CREATE ON SCHEMA public FROM PUBLIC"))
            execute(
                cur,
                sql.SQL("GRANT USAGE, CREATE ON SCHEMA public TO {}").format(
                    sql.Identifier(service.role)
                ),
            )

            if service.extra_schema:
                execute(
                    cur,
                    sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                        sql.Identifier(service.extra_schema)
                    ),
                )
                execute(
                    cur,
                    sql.SQL("REVOKE ALL ON SCHEMA {} FROM PUBLIC").format(
                        sql.Identifier(service.extra_schema)
                    ),
                )
                execute(
                    cur,
                    sql.SQL("ALTER SCHEMA {} OWNER TO {}").format(
                        sql.Identifier(service.extra_schema),
                        sql.Identifier(service.role),
                    ),
                )
                execute(
                    cur,
                    sql.SQL("GRANT USAGE, CREATE ON SCHEMA {} TO {}").format(
                        sql.Identifier(service.extra_schema),
                        sql.Identifier(service.role),
                    ),
                )

            search_path = sql.SQL(", ").join(
                sql.Identifier(schema_name) for schema_name in service.search_path
            )
            execute(
                cur,
                sql.SQL("ALTER ROLE {} IN DATABASE {} SET search_path = {}").format(
                    sql.Identifier(service.role),
                    sql.Identifier(service.database),
                    search_path,
                ),
            )


def main() -> None:
    args = parse_args()
    services = (
        ServiceDatabase(
            database="authservice_db",
            role="authservice_app",
            password=args.authservice_password,
            search_path=("public",),
        ),
        ServiceDatabase(
            database="booking_db",
            role="booking_app",
            password=args.booking_password,
            search_path=("public",),
        ),
        ServiceDatabase(
            database="catalog_db",
            role="catalog_app",
            password=args.catalog_password,
            search_path=("public",),
        ),
        ServiceDatabase(
            database="search_db",
            role="search_app",
            password=args.search_password,
            search_path=("search", "public"),
            extra_schema="search",
        ),
    )

    with psycopg.connect(
        host=args.host,
        port=args.port,
        user=args.admin_user,
        password=args.admin_password,
        dbname="postgres",
        sslmode="require",
        autocommit=True,
    ) as conn:
        with conn.cursor() as cur:
            for service in services:
                ensure_role(cur, service.role, service.password)
                ensure_database(cur, service.database, service.role)

    for service in services:
        configure_database(
            host=args.host,
            port=args.port,
            admin_user=args.admin_user,
            admin_password=args.admin_password,
            service=service,
        )

    print("Bootstrap completed for authservice, booking, catalog, and search.")


if __name__ == "__main__":
    main()
