"""
Dual-Write Manager for Database Migration

This module provides a base class for implementing dual-write patterns during
the database migration from monolithic to microservices architecture.
"""

import logging
from typing import Any, Dict, Optional, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class DualWriteConfig:
    """Configuration for dual-write behavior"""
    
    def __init__(
        self,
        enabled: bool = True,
        write_to_legacy: bool = True,
        write_to_new: bool = True,
        validate_sync: bool = True,
        fail_on_legacy_error: bool = False,
        fail_on_new_error: bool = True,
        sync_validation_interval: int = 300  # 5 minutes
    ):
        self.enabled = enabled
        self.write_to_legacy = write_to_legacy
        self.write_to_new = write_to_new
        self.validate_sync = validate_sync
        self.fail_on_legacy_error = fail_on_legacy_error
        self.fail_on_new_error = fail_on_new_error
        self.sync_validation_interval = sync_validation_interval


class DualWriteResult:
    """Result of a dual-write operation"""
    
    def __init__(self):
        self.new_db_success: bool = False
        self.legacy_db_success: bool = False
        self.new_db_error: Optional[Exception] = None
        self.legacy_db_error: Optional[Exception] = None
        self.sync_validated: bool = False
        self.timestamp: datetime = datetime.utcnow()
    
    @property
    def success(self) -> bool:
        """Returns True if the operation was successful according to configuration"""
        return self.new_db_success and (self.legacy_db_success or not self.legacy_db_error)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'new_db_success': self.new_db_success,
            'legacy_db_success': self.legacy_db_success,
            'new_db_error': str(self.new_db_error) if self.new_db_error else None,
            'legacy_db_error': str(self.legacy_db_error) if self.legacy_db_error else None,
            'sync_validated': self.sync_validated,
            'timestamp': self.timestamp.isoformat()
        }


class BaseDualWriteManager(ABC):
    """
    Base class for implementing dual-write patterns during database migration.
    
    This class provides the infrastructure for writing to both legacy and new
    databases simultaneously, with configurable behavior and validation.
    """
    
    def __init__(
        self,
        new_db_url: str,
        legacy_db_url: str,
        config: Optional[DualWriteConfig] = None
    ):
        self.new_db_url = new_db_url
        self.legacy_db_url = legacy_db_url
        self.config = config or DualWriteConfig()
        
        # Create database engines
        self.new_engine = create_async_engine(
            new_db_url,
            pool_pre_ping=True,
            echo=False
        )
        
        self.legacy_engine = create_async_engine(
            legacy_db_url,
            pool_pre_ping=True,
            echo=False
        )
        
        # Create session factories
        self.new_session_factory = async_sessionmaker(
            bind=self.new_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self.legacy_session_factory = async_sessionmaker(
            bind=self.legacy_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info(f"DualWriteManager initialized with config: {vars(self.config)}")
    
    async def dual_write(
        self,
        operation_name: str,
        new_db_operation: Callable[[AsyncSession], Awaitable[Any]],
        legacy_db_operation: Callable[[AsyncSession], Awaitable[Any]],
        validation_operation: Optional[Callable[[], Awaitable[bool]]] = None
    ) -> DualWriteResult:
        """
        Execute a dual-write operation to both databases.
        
        Args:
            operation_name: Name of the operation for logging
            new_db_operation: Async function to execute on new database
            legacy_db_operation: Async function to execute on legacy database
            validation_operation: Optional validation function to check sync
            
        Returns:
            DualWriteResult with operation results
        """
        result = DualWriteResult()
        
        if not self.config.enabled:
            logger.info(f"Dual-write disabled, executing only new DB operation: {operation_name}")
            return await self._execute_new_db_only(new_db_operation, result)
        
        logger.info(f"Starting dual-write operation: {operation_name}")
        
        # Execute operations concurrently if both are enabled
        tasks = []
        
        if self.config.write_to_new:
            tasks.append(self._execute_new_db_operation(new_db_operation, result))
        
        if self.config.write_to_legacy:
            tasks.append(self._execute_legacy_db_operation(legacy_db_operation, result))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Validate synchronization if requested
        if self.config.validate_sync and validation_operation:
            try:
                result.sync_validated = await validation_operation()
                if not result.sync_validated:
                    logger.warning(f"Sync validation failed for operation: {operation_name}")
            except Exception as e:
                logger.error(f"Sync validation error for {operation_name}: {e}")
                result.sync_validated = False
        
        # Check if operation should be considered successful
        if self.config.fail_on_new_error and result.new_db_error:
            logger.error(f"Dual-write operation failed (new DB error): {operation_name}")
            raise result.new_db_error
        
        if self.config.fail_on_legacy_error and result.legacy_db_error:
            logger.error(f"Dual-write operation failed (legacy DB error): {operation_name}")
            raise result.legacy_db_error
        
        logger.info(f"Dual-write operation completed: {operation_name}, Result: {result.to_dict()}")
        return result
    
    async def _execute_new_db_only(
        self,
        operation: Callable[[AsyncSession], Awaitable[Any]],
        result: DualWriteResult
    ) -> DualWriteResult:
        """Execute operation only on new database"""
        try:
            async with self.new_session_factory() as session:
                await operation(session)
                await session.commit()
                result.new_db_success = True
        except Exception as e:
            result.new_db_error = e
            logger.error(f"New DB operation failed: {e}")
            raise
        
        return result
    
    async def _execute_new_db_operation(
        self,
        operation: Callable[[AsyncSession], Awaitable[Any]],
        result: DualWriteResult
    ) -> None:
        """Execute operation on new database"""
        try:
            async with self.new_session_factory() as session:
                await operation(session)
                await session.commit()
                result.new_db_success = True
                logger.debug("New DB operation successful")
        except Exception as e:
            result.new_db_error = e
            logger.error(f"New DB operation failed: {e}")
            if self.config.fail_on_new_error:
                raise
    
    async def _execute_legacy_db_operation(
        self,
        operation: Callable[[AsyncSession], Awaitable[Any]],
        result: DualWriteResult
    ) -> None:
        """Execute operation on legacy database"""
        try:
            async with self.legacy_session_factory() as session:
                await operation(session)
                await session.commit()
                result.legacy_db_success = True
                logger.debug("Legacy DB operation successful")
        except Exception as e:
            result.legacy_db_error = e
            logger.error(f"Legacy DB operation failed: {e}")
            if self.config.fail_on_legacy_error:
                raise
    
    async def validate_data_sync(self, entity_id: Any) -> bool:
        """
        Validate that data is synchronized between databases.
        
        This method should be implemented by subclasses to provide
        entity-specific validation logic.
        
        Args:
            entity_id: ID of the entity to validate
            
        Returns:
            True if data is synchronized, False otherwise
        """
        return True  # Default implementation
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of both database connections"""
        health_status = {
            'new_db': {'status': 'unknown', 'error': None},
            'legacy_db': {'status': 'unknown', 'error': None},
            'dual_write_config': vars(self.config)
        }
        
        # Check new database
        try:
            async with self.new_session_factory() as session:
                await session.execute(text("SELECT 1"))
                health_status['new_db']['status'] = 'healthy'
        except Exception as e:
            health_status['new_db']['status'] = 'unhealthy'
            health_status['new_db']['error'] = str(e)
        
        # Check legacy database
        try:
            async with self.legacy_session_factory() as session:
                await session.execute(text("SELECT 1"))
                health_status['legacy_db']['status'] = 'healthy'
        except Exception as e:
            health_status['legacy_db']['status'] = 'unhealthy'
            health_status['legacy_db']['error'] = str(e)
        
        return health_status
    
    async def close(self):
        """Close database connections"""
        try:
            await self.new_engine.dispose()
            await self.legacy_engine.dispose()
            logger.info("DualWriteManager connections closed")
        except Exception as e:
            logger.error(f"Error closing DualWriteManager connections: {e}")
    
    @abstractmethod
    async def sync_entity(self, entity_id: Any, direction: str = "new_to_legacy") -> bool:
        """
        Synchronize a specific entity between databases.
        
        Args:
            entity_id: ID of the entity to synchronize
            direction: Direction of sync ("new_to_legacy" or "legacy_to_new")
            
        Returns:
            True if synchronization was successful
        """
        pass
    
    @abstractmethod
    async def validate_entity_sync(self, entity_id: Any) -> Dict[str, Any]:
        """
        Validate synchronization of a specific entity.
        
        Args:
            entity_id: ID of the entity to validate
            
        Returns:
            Dictionary with validation results
        """
        pass