"""
Auth Service Dual-Write Manager

Implements dual-write pattern for Auth Service during database migration.
Handles writing to both new isolated auth_db and legacy shared database.
"""

import logging
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from datetime import datetime

# Import shared dual-write infrastructure
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from dual_write_manager import BaseDualWriteManager, DualWriteConfig, DualWriteResult
from sync_validator import DataSyncValidator
from dual_write_config import DualWriteSettings

logger = logging.getLogger(__name__)


class AuthDualWriteManager(BaseDualWriteManager):
    """
    Dual-write manager for Auth Service entities.
    
    Manages synchronization between new auth_db and legacy shared database
    for user-related entities.
    """
    
    def __init__(self, new_db_url: str, legacy_db_url: str, settings: DualWriteSettings):
        # Convert settings to DualWriteConfig
        config = DualWriteConfig(
            enabled=settings.enabled,
            write_to_legacy=settings.write_to_legacy,
            write_to_new=settings.write_to_new,
            validate_sync=settings.validate_sync,
            fail_on_legacy_error=settings.fail_on_legacy_error,
            fail_on_new_error=settings.fail_on_new_error,
            sync_validation_interval=settings.sync_validation_interval
        )
        
        super().__init__(new_db_url, legacy_db_url, config)
        self.settings = settings
        self.validator = DataSyncValidator(
            self.new_session_factory,
            self.legacy_session_factory
        )
    
    async def create_user(self, user_data: Dict[str, Any]) -> DualWriteResult:
        """Create a user in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            # Check if user already exists
            result = await session.execute(
                text("SELECT uid FROM users WHERE uid = :uid"),
                {'uid': user_data['uid']}
            )
            if result.fetchone():
                return  # User already exists
            
            # Insert user into new database
            await session.execute(
                text("""
                    INSERT INTO users (uid, email, phone_number, display_name, photo_url, role, is_active, created_at, updated_at)
                    VALUES (:uid, :email, :phone_number, :display_name, :photo_url, :role, :is_active, NOW(), NOW())
                """),
                {
                    'uid': user_data['uid'],
                    'email': user_data.get('email'),
                    'phone_number': user_data.get('phone_number'),
                    'display_name': user_data.get('display_name'),
                    'photo_url': user_data.get('photo_url'),
                    'role': user_data.get('role', 'customer'),
                    'is_active': user_data.get('is_active', True)
                }
            )
        
        async def legacy_db_operation(session: AsyncSession):
            # Check if user already exists in legacy DB
            result = await session.execute(
                text("SELECT uid FROM users WHERE uid = :uid"),
                {'uid': user_data['uid']}
            )
            if result.fetchone():
                return  # User already exists
            
            # Insert user into legacy database
            await session.execute(
                text("""
                    INSERT INTO users (uid, email, phone_number, display_name, photo_url, role, is_active, created_at, updated_at)
                    VALUES (:uid, :email, :phone_number, :display_name, :photo_url, :role, :is_active, NOW(), NOW())
                """),
                {
                    'uid': user_data['uid'],
                    'email': user_data.get('email'),
                    'phone_number': user_data.get('phone_number'),
                    'display_name': user_data.get('display_name'),
                    'photo_url': user_data.get('photo_url'),
                    'role': user_data.get('role', 'customer'),
                    'is_active': user_data.get('is_active', True)
                }
            )
        
        return await self.dual_write(
            "create_user",
            new_db_operation,
            legacy_db_operation,
            lambda: self.validate_user_sync(user_data['uid'])
        )
    
    async def update_user(self, uid: str, user_data: Dict[str, Any]) -> DualWriteResult:
        """Update a user in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            # Build dynamic update query
            set_clauses = []
            params = {'uid': uid}
            
            for key, value in user_data.items():
                if key != 'uid':  # Don't update the primary key
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value
            
            if set_clauses:
                set_clauses.append("updated_at = NOW()")
                query = f"UPDATE users SET {', '.join(set_clauses)} WHERE uid = :uid"
                await session.execute(text(query), params)
        
        async def legacy_db_operation(session: AsyncSession):
            # Build dynamic update query for legacy DB
            set_clauses = []
            params = {'uid': uid}
            
            for key, value in user_data.items():
                if key != 'uid':
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value
            
            if set_clauses:
                set_clauses.append("updated_at = NOW()")
                query = f"UPDATE users SET {', '.join(set_clauses)} WHERE uid = :uid"
                await session.execute(text(query), params)
        
        return await self.dual_write(
            "update_user",
            new_db_operation,
            legacy_db_operation,
            lambda: self.validate_user_sync(uid)
        )
    
    async def deactivate_user(self, uid: str) -> DualWriteResult:
        """Deactivate a user in both databases"""
        
        async def new_db_operation(session: AsyncSession):
            await session.execute(
                text("UPDATE users SET is_active = false, updated_at = NOW() WHERE uid = :uid"),
                {'uid': uid}
            )
        
        async def legacy_db_operation(session: AsyncSession):
            await session.execute(
                text("UPDATE users SET is_active = false, updated_at = NOW() WHERE uid = :uid"),
                {'uid': uid}
            )
        
        return await self.dual_write(
            "deactivate_user",
            new_db_operation,
            legacy_db_operation,
            lambda: self.validate_user_sync(uid)
        )
    
    async def validate_user_sync(self, uid: str) -> bool:
        """Validate user synchronization between databases"""
        try:
            new_db_query = "SELECT * FROM users WHERE uid = :entity_id"
            legacy_db_query = "SELECT * FROM users WHERE uid = :entity_id"
            
            result = await self.validator.validate_entity_sync(
                uid, "user", new_db_query, legacy_db_query,
                ignore_fields=['updated_at']  # Ignore timestamp differences
            )
            
            return result.is_synchronized
        except Exception as e:
            logger.error(f"User sync validation failed for uid {uid}: {e}")
            return False
    
    # Implementation of abstract methods
    async def sync_entity(self, entity_id: Any, direction: str = "new_to_legacy") -> bool:
        """Synchronize a specific user between databases"""
        try:
            if direction == "new_to_legacy":
                # Copy from new DB to legacy DB
                async with self.new_session_factory() as new_session:
                    result = await new_session.execute(
                        text("SELECT * FROM users WHERE uid = :uid"),
                        {'uid': entity_id}
                    )
                    user_data = result.fetchone()
                    
                    if user_data:
                        async with self.legacy_session_factory() as legacy_session:
                            # Upsert into legacy database
                            await legacy_session.execute(
                                text("""
                                    INSERT INTO users (uid, email, phone_number, display_name, photo_url, role, is_active, created_at, updated_at)
                                    VALUES (:uid, :email, :phone_number, :display_name, :photo_url, :role, :is_active, :created_at, :updated_at)
                                    ON CONFLICT (uid) DO UPDATE SET
                                        email = EXCLUDED.email,
                                        phone_number = EXCLUDED.phone_number,
                                        display_name = EXCLUDED.display_name,
                                        photo_url = EXCLUDED.photo_url,
                                        role = EXCLUDED.role,
                                        is_active = EXCLUDED.is_active,
                                        updated_at = NOW()
                                """),
                                dict(user_data._mapping)
                            )
                            await legacy_session.commit()
            
            elif direction == "legacy_to_new":
                # Copy from legacy DB to new DB
                async with self.legacy_session_factory() as legacy_session:
                    result = await legacy_session.execute(
                        text("SELECT * FROM users WHERE uid = :uid"),
                        {'uid': entity_id}
                    )
                    user_data = result.fetchone()
                    
                    if user_data:
                        async with self.new_session_factory() as new_session:
                            # Upsert into new database
                            await new_session.execute(
                                text("""
                                    INSERT INTO users (uid, email, phone_number, display_name, photo_url, role, is_active, created_at, updated_at)
                                    VALUES (:uid, :email, :phone_number, :display_name, :photo_url, :role, :is_active, :created_at, :updated_at)
                                    ON CONFLICT (uid) DO UPDATE SET
                                        email = EXCLUDED.email,
                                        phone_number = EXCLUDED.phone_number,
                                        display_name = EXCLUDED.display_name,
                                        photo_url = EXCLUDED.photo_url,
                                        role = EXCLUDED.role,
                                        is_active = EXCLUDED.is_active,
                                        updated_at = NOW()
                                """),
                                dict(user_data._mapping)
                            )
                            await new_session.commit()
            
            return True
        except Exception as e:
            logger.error(f"Entity sync failed for user {entity_id}: {e}")
            return False
    
    async def validate_entity_sync(self, entity_id: Any) -> Dict[str, Any]:
        """Validate synchronization of a specific user"""
        try:
            is_synchronized = await self.validate_user_sync(entity_id)
            
            return {
                'entity_id': entity_id,
                'entity_type': 'user',
                'is_synchronized': is_synchronized,
                'validation_timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'entity_id': entity_id,
                'entity_type': 'user',
                'is_synchronized': False,
                'error': str(e),
                'validation_timestamp': datetime.utcnow().isoformat()
            }