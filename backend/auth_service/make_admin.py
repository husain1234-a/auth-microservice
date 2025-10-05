#!/usr/bin/env python3
"""
Script to make a user an admin in the database.
Run this script to grant admin privileges to a user.
"""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.user import User, UserRole
from config.settings import settings

async def make_user_admin(email_or_uid: str):
    """Make a user an admin by email or UID"""
    
    # Create database engine
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Try to find user by email first, then by UID
        result = await session.execute(
            select(User).where(
                (User.email == email_or_uid) | (User.uid == email_or_uid)
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User not found with email or UID: {email_or_uid}")
            return False
        
        # Update user role to admin
        await session.execute(
            update(User)
            .where(User.uid == user.uid)
            .values(role=UserRole.ADMIN)
        )
        await session.commit()
        
        print(f"✅ Successfully made user an admin:")
        print(f"   UID: {user.uid}")
        print(f"   Email: {user.email}")
        print(f"   Display Name: {user.display_name}")
        print(f"   Role: {UserRole.ADMIN.value}")
        
        return True

async def list_users():
    """List all users in the database"""
    
    # Create database engine
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("No users found in database")
            return
        
        print("📋 Users in database:")
        print("-" * 80)
        for user in users:
            print(f"UID: {user.uid}")
            print(f"Email: {user.email}")
            print(f"Display Name: {user.display_name}")
            print(f"Role: {user.role}")
            print(f"Active: {user.is_active}")
            print(f"Created: {user.created_at}")
            print("-" * 80)

async def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python make_admin.py list                    # List all users")
        print("  python make_admin.py <email_or_uid>          # Make user admin")
        print("")
        print("Examples:")
        print("  python make_admin.py list")
        print("  python make_admin.py user@example.com")
        print("  python make_admin.py abc123def456")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        await list_users()
    else:
        email_or_uid = command
        success = await make_user_admin(email_or_uid)
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())