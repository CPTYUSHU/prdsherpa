#!/usr/bin/env python3
"""
添加 prd_draft 字段到 conversations 表
"""
import asyncio
import asyncpg
from backend.app.core.config import settings


async def main():
    print("=" * 60)
    print("添加 prd_draft 字段")
    print("=" * 60)
    print()

    # 解析数据库 URL
    db_url = settings.DATABASE_URL
    # 转换为 asyncpg 格式
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    conn = await asyncpg.connect(db_url)

    try:
        # 检查字段是否已存在
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='conversations'
                AND column_name='prd_draft'
            );
        """)

        if exists:
            print("✓ prd_draft 字段已存在，跳过")
        else:
            print("添加 prd_draft 字段...")
            await conn.execute("""
                ALTER TABLE conversations
                ADD COLUMN prd_draft JSONB NULL;
            """)
            print("✅ prd_draft 字段添加成功！")

    finally:
        await conn.close()

    print()
    print("迁移完成！")


if __name__ == "__main__":
    asyncio.run(main())
