#!/usr/bin/env python3
"""
Import oils from Shale's complete database into the soap calculator.

Handles:
- Adding new oils not in database
- Updating existing oils with new data
- Preserving database-specific fields (created_at, saponified_inci_name)
"""

import json
import sys

import psycopg2
from psycopg2.extras import Json


def load_oils_file(filepath):
    """Load and validate the oils JSON file"""
    with open(filepath) as f:
        data = json.load(f)

    if "oils" not in data:
        raise ValueError("JSON file must have 'oils' key")

    return data["oils"]


def connect_db(db_url):
    """Connect to PostgreSQL database"""
    # Convert asyncpg URL to psycopg2 format
    # postgresql+asyncpg://user:pass@host:port/db -> postgresql://user:pass@host:port/db
    sync_url = db_url.replace("+asyncpg", "")
    return psycopg2.connect(sync_url)


def get_existing_oil_ids(cursor):
    """Get set of existing oil IDs from database"""
    cursor.execute("SELECT id FROM oils")
    return {row[0] for row in cursor.fetchall()}


def insert_oil(cursor, oil):
    """Insert a new oil into the database"""
    sql = """
        INSERT INTO oils (
            id, common_name, inci_name, sap_value_naoh, sap_value_koh,
            iodine_value, ins_value, fatty_acids, quality_contributions
        ) VALUES (
            %(id)s, %(common_name)s, %(inci_name)s, %(sap_value_naoh)s, %(sap_value_koh)s,
            %(iodine_value)s, %(ins_value)s, %(fatty_acids)s, %(quality_contributions)s
        )
    """

    cursor.execute(
        sql,
        {
            "id": oil["id"],
            "common_name": oil["common_name"],
            "inci_name": oil.get("inci_name", ""),
            "sap_value_naoh": oil["sap_value_naoh"],
            "sap_value_koh": oil["sap_value_koh"],
            "iodine_value": oil["iodine_value"],
            "ins_value": oil["ins_value"],
            "fatty_acids": Json(oil["fatty_acids"]),
            "quality_contributions": Json(oil["quality_contributions"]),
        },
    )


def update_oil(cursor, oil):
    """Update an existing oil in the database"""
    sql = """
        UPDATE oils SET
            common_name = %(common_name)s,
            inci_name = %(inci_name)s,
            sap_value_naoh = %(sap_value_naoh)s,
            sap_value_koh = %(sap_value_koh)s,
            iodine_value = %(iodine_value)s,
            ins_value = %(ins_value)s,
            fatty_acids = %(fatty_acids)s,
            quality_contributions = %(quality_contributions)s,
            updated_at = NOW()
        WHERE id = %(id)s
    """

    cursor.execute(
        sql,
        {
            "id": oil["id"],
            "common_name": oil["common_name"],
            "inci_name": oil.get("inci_name", ""),
            "sap_value_naoh": oil["sap_value_naoh"],
            "sap_value_koh": oil["sap_value_koh"],
            "iodine_value": oil["iodine_value"],
            "ins_value": oil["ins_value"],
            "fatty_acids": Json(oil["fatty_acids"]),
            "quality_contributions": Json(oil["quality_contributions"]),
        },
    )


def main():
    if len(sys.argv) < 3:
        print("Usage: import_oils.py <oils-json-file> <database-url>")
        sys.exit(1)

    oils_file = sys.argv[1]
    db_url = sys.argv[2]

    print(f"Loading oils from {oils_file}...")
    oils = load_oils_file(oils_file)
    print(f"Loaded {len(oils)} oils from file")

    print("Connecting to database...")
    conn = connect_db(db_url)
    cursor = conn.cursor()

    print("Getting existing oils from database...")
    existing_ids = get_existing_oil_ids(cursor)
    print(f"Found {len(existing_ids)} existing oils in database")

    new_count = 0
    updated_count = 0
    error_count = 0

    for oil in oils:
        try:
            oil_id = oil["id"]

            if oil_id in existing_ids:
                # Update existing oil
                update_oil(cursor, oil)
                updated_count += 1
                print(f"Updated: {oil['common_name']} ({oil_id})")
            else:
                # Insert new oil
                insert_oil(cursor, oil)
                new_count += 1
                print(f"Added: {oil['common_name']} ({oil_id})")

        except Exception as e:
            error_count += 1
            print(f"ERROR processing {oil.get('common_name', 'unknown')}: {e}")

    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()

    print("\n" + "=" * 60)
    print("Import complete!")
    print(f"  New oils added: {new_count}")
    print(f"  Existing oils updated: {updated_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total processed: {len(oils)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
