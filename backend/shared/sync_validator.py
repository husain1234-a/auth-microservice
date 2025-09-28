"""
Data synchronization validation utilities for dual-write operations.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)


class SyncValidationResult:
    """Result of a synchronization validation"""
    
    def __init__(self, entity_id: Any, entity_type: str):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.is_synchronized = False
        self.differences: List[Dict[str, Any]] = []
        self.new_db_data: Optional[Dict[str, Any]] = None
        self.legacy_db_data: Optional[Dict[str, Any]] = None
        self.validation_timestamp = datetime.utcnow()
        self.error_message: Optional[str] = None
    
    def add_difference(self, field: str, new_value: Any, legacy_value: Any):
        """Add a field difference"""
        self.differences.append({
            'field': field,
            'new_db_value': new_value,
            'legacy_db_value': legacy_value
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'entity_id': str(self.entity_id),
            'entity_type': self.entity_type,
            'is_synchronized': self.is_synchronized,
            'differences': self.differences,
            'new_db_data': self.new_db_data,
            'legacy_db_data': self.legacy_db_data,
            'validation_timestamp': self.validation_timestamp.isoformat(),
            'error_message': self.error_message
        }


class DataSyncValidator:
    """Validates data synchronization between new and legacy databases"""
    
    def __init__(self, new_session_factory, legacy_session_factory):
        self.new_session_factory = new_session_factory
        self.legacy_session_factory = legacy_session_factory
    
    async def validate_entity_sync(
        self,
        entity_id: Any,
        entity_type: str,
        new_db_query: str,
        legacy_db_query: str,
        ignore_fields: Optional[List[str]] = None
    ) -> SyncValidationResult:
        """
        Validate synchronization of a specific entity between databases.
        
        Args:
            entity_id: ID of the entity to validate
            entity_type: Type of entity (for logging)
            new_db_query: SQL query to fetch entity from new database
            legacy_db_query: SQL query to fetch entity from legacy database
            ignore_fields: Fields to ignore during comparison
            
        Returns:
            SyncValidationResult with validation details
        """
        result = SyncValidationResult(entity_id, entity_type)
        ignore_fields = ignore_fields or []
        
        try:
            # Fetch data from both databases
            new_data = await self._fetch_entity_data(
                self.new_session_factory, new_db_query, entity_id
            )
            legacy_data = await self._fetch_entity_data(
                self.legacy_session_factory, legacy_db_query, entity_id
            )
            
            result.new_db_data = new_data
            result.legacy_db_data = legacy_data
            
            # Check if both records exist
            if new_data is None and legacy_data is None:
                result.is_synchronized = True  # Both don't exist
                return result
            
            if new_data is None or legacy_data is None:
                result.error_message = f"Entity exists in only one database: new_db={new_data is not None}, legacy_db={legacy_data is not None}"
                return result
            
            # Compare data
            result.is_synchronized = self._compare_entity_data(
                new_data, legacy_data, ignore_fields, result
            )
            
        except Exception as e:
            result.error_message = f"Validation error: {str(e)}"
            logger.error(f"Sync validation failed for {entity_type} {entity_id}: {e}")
        
        return result
    
    async def _fetch_entity_data(
        self,
        session_factory,
        query: str,
        entity_id: Any
    ) -> Optional[Dict[str, Any]]:
        """Fetch entity data from database"""
        try:
            async with session_factory() as session:
                result = await session.execute(text(query), {'entity_id': entity_id})
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return None
        except Exception as e:
            logger.error(f"Error fetching entity data: {e}")
            raise
    
    def _compare_entity_data(
        self,
        new_data: Dict[str, Any],
        legacy_data: Dict[str, Any],
        ignore_fields: List[str],
        result: SyncValidationResult
    ) -> bool:
        """Compare entity data between databases"""
        is_synchronized = True
        
        # Get all fields from both datasets
        all_fields = set(new_data.keys()) | set(legacy_data.keys())
        
        for field in all_fields:
            if field in ignore_fields:
                continue
            
            new_value = new_data.get(field)
            legacy_value = legacy_data.get(field)
            
            # Normalize values for comparison
            new_normalized = self._normalize_value(new_value)
            legacy_normalized = self._normalize_value(legacy_value)
            
            if new_normalized != legacy_normalized:
                result.add_difference(field, new_value, legacy_value)
                is_synchronized = False
        
        return is_synchronized
    
    def _normalize_value(self, value: Any) -> Any:
        """Normalize value for comparison"""
        if value is None:
            return None
        
        # Handle datetime objects
        if isinstance(value, datetime):
            # Truncate microseconds for comparison
            return value.replace(microsecond=0)
        
        # Handle decimal/float precision
        if isinstance(value, (float, int)):
            return round(float(value), 2)
        
        # Handle strings
        if isinstance(value, str):
            return value.strip()
        
        return value
    
    async def validate_batch_sync(
        self,
        entity_ids: List[Any],
        entity_type: str,
        new_db_query: str,
        legacy_db_query: str,
        ignore_fields: Optional[List[str]] = None
    ) -> List[SyncValidationResult]:
        """Validate synchronization for a batch of entities"""
        results = []
        
        for entity_id in entity_ids:
            result = await self.validate_entity_sync(
                entity_id, entity_type, new_db_query, legacy_db_query, ignore_fields
            )
            results.append(result)
        
        return results
    
    async def generate_sync_report(
        self,
        validation_results: List[SyncValidationResult]
    ) -> Dict[str, Any]:
        """Generate a comprehensive synchronization report"""
        total_entities = len(validation_results)
        synchronized_count = sum(1 for r in validation_results if r.is_synchronized)
        error_count = sum(1 for r in validation_results if r.error_message)
        
        # Group differences by field
        field_differences = {}
        for result in validation_results:
            for diff in result.differences:
                field = diff['field']
                if field not in field_differences:
                    field_differences[field] = 0
                field_differences[field] += 1
        
        # Find most common issues
        common_issues = sorted(
            field_differences.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        report = {
            'summary': {
                'total_entities': total_entities,
                'synchronized_count': synchronized_count,
                'unsynchronized_count': total_entities - synchronized_count,
                'error_count': error_count,
                'sync_percentage': (synchronized_count / total_entities * 100) if total_entities > 0 else 0
            },
            'field_differences': field_differences,
            'common_issues': common_issues,
            'unsynchronized_entities': [
                {
                    'entity_id': r.entity_id,
                    'entity_type': r.entity_type,
                    'difference_count': len(r.differences),
                    'error_message': r.error_message
                }
                for r in validation_results
                if not r.is_synchronized
            ],
            'report_timestamp': datetime.utcnow().isoformat()
        }
        
        return report


class SyncMetrics:
    """Tracks synchronization metrics"""
    
    def __init__(self):
        self.validation_count = 0
        self.sync_success_count = 0
        self.sync_failure_count = 0
        self.last_validation_time: Optional[datetime] = None
        self.validation_errors: List[str] = []
    
    def record_validation(self, success: bool, error_message: Optional[str] = None):
        """Record a validation attempt"""
        self.validation_count += 1
        self.last_validation_time = datetime.utcnow()
        
        if success:
            self.sync_success_count += 1
        else:
            self.sync_failure_count += 1
            if error_message:
                self.validation_errors.append(f"{datetime.utcnow().isoformat()}: {error_message}")
                # Keep only last 100 errors
                self.validation_errors = self.validation_errors[-100:]
    
    def get_success_rate(self) -> float:
        """Get validation success rate"""
        if self.validation_count == 0:
            return 0.0
        return (self.sync_success_count / self.validation_count) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'validation_count': self.validation_count,
            'sync_success_count': self.sync_success_count,
            'sync_failure_count': self.sync_failure_count,
            'success_rate': self.get_success_rate(),
            'last_validation_time': self.last_validation_time.isoformat() if self.last_validation_time else None,
            'recent_errors': self.validation_errors[-10:]  # Last 10 errors
        }