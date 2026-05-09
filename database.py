import asyncpg
from config import DATABASE_URL

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    async with pool.acquire() as conn:
        await conn.execute("""
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

async def get_user(user_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)

async def create_user(user_id: int, username: str, capybara_name: str, referred_by: int = None):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, username, capybara_name, coins, referred_by)
            VALUES ($1, $2, $3, 150, $4)
            ON CONFLICT DO NOTHING
        """, user_id, username, capybara_name, referred_by)
        if referred_by:
            ref_user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", referred_by)
            if ref_user:
                await conn.execute("""
                    UPDATE users SET coins = coins + 70, referrals_count = referrals_count + 1
                    WHERE user_id = $1
                """, referred_by)
                await conn.execute("""
                    UPDATE users SET coins = coins + 50 WHERE user_id = $1
                """, user_id)

async def update_capybara_name(user_id: int, new_name: str):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET capybara_name = $1 WHERE user_id = $2", new_name, user_id)

async def get_clan(clan_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM clans WHERE id = $1", clan_id)

async def get_clan_by_name(name: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM clans WHERE name = $1", name)

async def create_clan(name: str, owner_id: int):
    async with pool.acquire() as conn:
        clan = await conn.fetchrow("""
            INSERT INTO clans (name, owner_id) VALUES ($1, $2) RETURNING *
        """, name, owner_id)
        await conn.execute("""
            UPDATE users SET clan_id = $1, clan_role = 'owner', coins = coins - 200
            WHERE user_id = $2
        """, clan['id'], owner_id)
        return clan

async def delete_clan(clan_id: int):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET clan_id = NULL, clan_role = NULL WHERE clan_id = $1", clan_id)
        await conn.execute("DELETE FROM clan_invites WHERE clan_id = $1", clan_id)
        await conn.execute("DELETE FROM clans WHERE id = $1", clan_id)

async def leave_clan(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET clan_id = NULL, clan_role = NULL WHERE user_id = $1", user_id)

async def donate_to_clan(user_id: int, clan_id: int, amount: int):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET coins = coins - $1 WHERE user_id = $2", amount, user_id)
        await conn.execute("UPDATE clans SET treasury = treasury + $1 WHERE id = $2", amount, clan_id)

async def get_clan_members(clan_id: int):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM users WHERE clan_id = $1", clan_id)

async def get_top_clans():
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT c.*, COUNT(u.user_id) as member_count
            FROM clans c
            LEFT JOIN users u ON u.clan_id = c.id
            GROUP BY c.id
            ORDER BY member_count DESC
            LIMIT 10
        """)

async def create_invite(clan_id: int, invited_user_id: int, invited_by: int):
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("""
            SELECT * FROM clan_invites WHERE clan_id = $1 AND invited_user_id = $2
        """, clan_id, invited_user_id)
        if not existing:
            await conn.execute("""
                INSERT INTO clan_invites (clan_id, invited_user_id, invited_by)
                VALUES ($1, $2, $3)
            """, clan_id, invited_user_id, invited_by)
            return True
        return False

async def get_invites(user_id: int):
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT ci.*, c.name as clan_name, u.username as inviter_name
            FROM clan_invites ci
            JOIN clans c ON c.id = ci.clan_id
            JOIN users u ON u.user_id = ci.invited_by
            WHERE ci.invited_user_id = $1
        """, user_id)

async def accept_invite(invite_id: int, user_id: int):
    async with pool.acquire() as conn:
        invite = await conn.fetchrow("SELECT * FROM clan_invites WHERE id = $1 AND invited_user_id = $2", invite_id, user_id)
        if invite:
            await conn.execute("""
                UPDATE users SET clan_id = $1, clan_role = 'member' WHERE user_id = $2
            """, invite['clan_id'], user_id)
            await conn.execute("DELETE FROM clan_invites WHERE invited_user_id = $1", user_id)
            return True
        return False

async def decline_invite(invite_id: int, user_id: int):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM clan_invites WHERE id = $1 AND invited_user_id = $2", invite_id, user_id)
