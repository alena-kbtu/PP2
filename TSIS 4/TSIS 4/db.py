import psycopg2
from config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def get_or_create_player(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    player = cur.fetchone()

    if player:
        player_id = player[0]
    else:
        cur.execute(
            "INSERT INTO players (username) VALUES (%s) RETURNING id",
            (username,)
        )
        player_id = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return player_id


def save_game_result(username, score, level):
    player_id = get_or_create_player(username)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO game_sessions (player_id, score, level_reached)
        VALUES (%s, %s, %s)
        """,
        (player_id, score, level)
    )

    conn.commit()
    cur.close()
    conn.close()


def get_personal_best(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT MAX(gs.score)
        FROM game_sessions gs
        JOIN players p ON gs.player_id = p.id
        WHERE p.username = %s
        """,
        (username,)
    )

    result = cur.fetchone()[0]

    cur.close()
    conn.close()

    return result if result is not None else 0


def get_top_10():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT p.username, gs.score, gs.level_reached, gs.played_at
        FROM game_sessions gs
        JOIN players p ON gs.player_id = p.id
        ORDER BY gs.score DESC, gs.level_reached DESC
        LIMIT 10
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows