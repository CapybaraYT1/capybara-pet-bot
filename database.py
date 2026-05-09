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
            created_at TIMESTAMP DEFAULT NOW(),
            work_started_at TIMESTAMP DEFAULT NULL,
            last_collected_at TIMESTAMP DEFAULT NULL,
            is_working BOOLEAN DEFAULT FALSE
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
    # Add work columns if they don't exist (for existing tables)
    try:
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS work_started_at TIMESTAMP DEFAULT NULL")
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_collected_at TIMESTAMP DEFAULT NULL")
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_working BOOLEAN DEFAULT FALSE")
        conn.commit()
    except:
        conn.rollback()
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

def add_coins(user_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET coins = coins + %s WHERE user_id = %s", (amount, user_id))
    conn.commit()
    cur.close()
    conn.close()

# ─── РАБОТА ─────────────────────────────────────────────────
def start_work(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users SET is_working = TRUE, work_started_at = NOW(), last_collected_at = NOW()
        WHERE user_id = %s
    """, (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def collect_work(user_id):
    """Собирает заработанные монеты. Возвращает количество монет или 0."""
    import random
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()

    if not user or not user['is_working']:
        cur.close()
        conn.close()
        return 0, 0

    from datetime import datetime
    last = user['last_collected_at']
    if last is None:
        last = user['work_started_at']

    now = datetime.now()
    diff_minutes = (now - last).total_seconds() / 60

    periods = int(diff_minutes / 30)
    if periods <= 0:
        cur.close()
        conn.close()
        minutes_left = int(30 - diff_minutes)
        return 0, minutes_left

    earned = sum(random.randint(50, 150) for _ in range(periods))

    cur2 = conn.cursor()
    cur2.execute("""
        UPDATE users SET coins = coins + %s, last_collected_at = NOW()
        WHERE user_id = %s
    """, (earned, user_id))
    conn.commit()
    cur.close()
    cur2.close()
    conn.close()
    return earned, 0

def stop_work(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users SET is_working = FALSE, work_started_at = NULL, last_collected_at = NULL
        WHERE user_id = %s
    """, (user_id,))
    conn.commit()
    cur.close()
    conn.close()

# ─── ТОП ИГРОКОВ ────────────────────────────────────────────
def get_top_users(limit=15):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT username, capybara_name, coins FROM users
        ORDER BY coins DESC LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ─── КЛАНЫ ──────────────────────────────────────────────────
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
