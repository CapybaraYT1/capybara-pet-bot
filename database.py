import psycopg2
import psycopg2.extras
from config import DATABASE_URL

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            capybara_name TEXT,
            coins INTEGER DEFAULT 150,
            referrals_count INTEGER DEFAULT 0,
            referred_by BIGINT DEFAULT NULL,
            clan_id INTEGER DEFAULT NULL,
            clan_role TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS clans (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            owner_id BIGINT NOT NULL,
            treasury INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS clan_invites (
            id SERIAL PRIMARY KEY,
            clan_id INTEGER NOT NULL,
            invited_user_id BIGINT NOT NULL,
            invited_by BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_user(user_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def create_user(user_id, username, capybara_name, referred_by=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (user_id, username, capybara_name, coins, referred_by)
        VALUES (%s, %s, %s, 150, %s)
        ON CONFLICT DO NOTHING
    """, (user_id, username, capybara_name, referred_by))
    if referred_by:
        cur.execute("SELECT user_id FROM users WHERE user_id = %s", (referred_by,))
        if cur.fetchone():
            cur.execute("UPDATE users SET coins = coins + 70, referrals_count = referrals_count + 1 WHERE user_id = %s", (referred_by,))
            cur.execute("UPDATE users SET coins = coins + 50 WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def update_capybara_name(user_id, new_name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET capybara_name = %s WHERE user_id = %s", (new_name, user_id))
    conn.commit()
    cur.close()
    conn.close()

def get_clan(clan_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM clans WHERE id = %s", (clan_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_clan_by_name(name):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM clans WHERE name = %s", (name,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def create_clan(name, owner_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("INSERT INTO clans (name, owner_id) VALUES (%s, %s) RETURNING *", (name, owner_id))
    clan = cur.fetchone()
    cur.execute("UPDATE users SET clan_id = %s, clan_role = 'owner', coins = coins - 200 WHERE user_id = %s", (clan['id'], owner_id))
    conn.commit()
    cur.close()
    conn.close()
    return clan

def delete_clan(clan_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET clan_id = NULL, clan_role = NULL WHERE clan_id = %s", (clan_id,))
    cur.execute("DELETE FROM clan_invites WHERE clan_id = %s", (clan_id,))
    cur.execute("DELETE FROM clans WHERE id = %s", (clan_id,))
    conn.commit()
    cur.close()
    conn.close()

def leave_clan(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET clan_id = NULL, clan_role = NULL WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def donate_to_clan(user_id, clan_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET coins = coins - %s WHERE user_id = %s", (amount, user_id))
    cur.execute("UPDATE clans SET treasury = treasury + %s WHERE id = %s", (amount, clan_id))
    conn.commit()
    cur.close()
    conn.close()

def get_clan_members(clan_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE clan_id = %s", (clan_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_top_clans():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT c.*, COUNT(u.user_id) as member_count
        FROM clans c
        LEFT JOIN users u ON u.clan_id = c.id
        GROUP BY c.id
        ORDER BY member_count DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def create_invite(clan_id, invited_user_id, invited_by):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clan_invites WHERE clan_id = %s AND invited_user_id = %s", (clan_id, invited_user_id))
    if cur.fetchone():
        cur.close()
        conn.close()
        return False
    cur.execute("INSERT INTO clan_invites (clan_id, invited_user_id, invited_by) VALUES (%s, %s, %s)", (clan_id, invited_user_id, invited_by))
    conn.commit()
    cur.close()
    conn.close()
    return True

def get_invites(user_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT ci.*, c.name as clan_name, u.username as inviter_name
        FROM clan_invites ci
        JOIN clans c ON c.id = ci.clan_id
        JOIN users u ON u.user_id = ci.invited_by
        WHERE ci.invited_user_id = %s
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def accept_invite(invite_id, user_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM clan_invites WHERE id = %s AND invited_user_id = %s", (invite_id, user_id))
    invite = cur.fetchone()
    if invite:
        cur.execute("UPDATE users SET clan_id = %s, clan_role = 'member' WHERE user_id = %s", (invite['clan_id'], user_id))
        cur.execute("DELETE FROM clan_invites WHERE invited_user_id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    cur.close()
    conn.close()
    return False

def decline_invite(invite_id, user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM clan_invites WHERE id = %s AND invited_user_id = %s", (invite_id, user_id))
    conn.commit()
    cur.close()
    conn.close()
