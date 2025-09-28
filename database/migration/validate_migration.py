#!/usr/bin/env python3
"""
Migration Validation Script

This script validates data consistency and integrity after migration
from monolithic database to separate service databases.
"""

import asyncio
import logging
import sys
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a validation check"""
    check_name: str
    passed: bool
    message: str
    details: Dict[str, Any] = None

class DatabaseConfig:
    """Database configuration for validation"""
    
    LEGACY_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'poc',
        'user': 'poc_user',
        'password': 'admin123'
    }
    
    AUTH_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'auth_db',
        'user': 'auth_user',
        'password': 'auth_pass123'
    }
    
    PRODUCT_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'product_db',
        'user': 'product_user',
        'password': 'product_pass123'
    }
    
    CART_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'cart_db',
        'user': 'cart_user',
        'password': 'cart_pass123'
    }
    
    PROMOTION_DB = {
        'host': 'localhost',
        'port': 5432,
        'database': 'promotion_db',
        'user': 'promotion_user',
        'password': 'promotion_pass123'
    }

class MigrationValidator:
    """Validates migration data consistency"""
    
    def __init__(self):
        self.validation_results: List[ValidationResult] = []
    
    async def run_all_validations(self) -> bool:
        """Run all validation checks"""
        logger.info("Starting migration validation...")
        
        validations = [
            self.validate_user_count,
            self.validate_product_count,
            self.validate_category_count,
            self.validate_cart_count,
            self.validate_cart_items_count,
            self.validate_wishlist_count,
            self.validate_promo_codes_count,
            self.validate_data_integrity,
            self.validate_reference_consistency,
            self.validate_denormalized_data
        ]
        
        for validation in validations:
            try:
                result = await validation()
                self.validation_results.append(result)
                
                if result.passed:
                    logger.info(f"[OK] {result.check_name}: {result.message}")
                else:
                    logger.error(f"[ERROR] {result.check_name}: {result.message}")
                    
            except Exception as e:
                error_result = ValidationResult(
                    check_name=validation.__name__,
                    passed=False,
                    message=f"Validation failed with error: {e}"
                )
                self.validation_results.append(error_result)
                logger.error(f"[ERROR] {validation.__name__}: {e}")
        
        # Summary
        passed_count = sum(1 for r in self.validation_results if r.passed)
        total_count = len(self.validation_results)
        
        logger.info(f"\nValidation Summary: {passed_count}/{total_count} checks passed")
        
        if passed_count == total_count:
            logger.info("[SUCCESS] All validations passed!")
            return True
        else:
            logger.error("[FAILED] Some validations failed!")
            return False
    
    async def validate_user_count(self) -> ValidationResult:
        """Validate user count matches between legacy and auth DB"""
        legacy_conn = await asyncpg.connect(**DatabaseConfig.LEGACY_DB)
        auth_conn = await asyncpg.connect(**DatabaseConfig.AUTH_DB)
        
        try:
            legacy_count = await legacy_conn.fetchval("SELECT COUNT(*) FROM users")
            auth_count = await auth_conn.fetchval("SELECT COUNT(*) FROM users")
            
            if legacy_count == auth_count:
                return ValidationResult(
                    check_name="User Count Validation",
                    passed=True,
                    message=f"User counts match: {legacy_count} users migrated"
                )
            else:
                return ValidationResult(
                    check_name="User Count Validation",
                    passed=False,
                    message=f"User count mismatch: Legacy={legacy_count}, Auth={auth_count}"
                )
        finally:
            await legacy_conn.close()
            await auth_conn.close()
    
    async def validate_product_count(self) -> ValidationResult:
        """Validate product count matches between legacy and product DB"""
        legacy_conn = await asyncpg.connect(**DatabaseConfig.LEGACY_DB)
        product_conn = await asyncpg.connect(**DatabaseConfig.PRODUCT_DB)
        
        try:
            legacy_count = await legacy_conn.fetchval("SELECT COUNT(*) FROM products")
            product_count = await product_conn.fetchval("SELECT COUNT(*) FROM products")
            
            if legacy_count == product_count:
                return ValidationResult(
                    check_name="Product Count Validation",
                    passed=True,
                    message=f"Product counts match: {legacy_count} products migrated"
                )
            else:
                return ValidationResult(
                    check_name="Product Count Validation",
                    passed=False,
                    message=f"Product count mismatch: Legacy={legacy_count}, Product={product_count}"
                )
        finally:
            await legacy_conn.close()
            await product_conn.close()
    
    async def validate_category_count(self) -> ValidationResult:
        """Validate category count matches between legacy and product DB"""
        legacy_conn = await asyncpg.connect(**DatabaseConfig.LEGACY_DB)
        product_conn = await asyncpg.connect(**DatabaseConfig.PRODUCT_DB)
        
        try:
            legacy_count = await legacy_conn.fetchval("SELECT COUNT(*) FROM categories")
            product_count = await product_conn.fetchval("SELECT COUNT(*) FROM categories")
            
            if legacy_count == product_count:
                return ValidationResult(
                    check_name="Category Count Validation",
                    passed=True,
                    message=f"Category counts match: {legacy_count} categories migrated"
                )
            else:
                return ValidationResult(
                    check_name="Category Count Validation",
                    passed=False,
                    message=f"Category count mismatch: Legacy={legacy_count}, Product={product_count}"
                )
        finally:
            await legacy_conn.close()
            await product_conn.close()
    
    async def validate_cart_count(self) -> ValidationResult:
        """Validate cart count matches between legacy and cart DB"""
        legacy_conn = await asyncpg.connect(**DatabaseConfig.LEGACY_DB)
        cart_conn = await asyncpg.connect(**DatabaseConfig.CART_DB)
        
        try:
            legacy_count = await legacy_conn.fetchval("SELECT COUNT(*) FROM carts")
            cart_count = await cart_conn.fetchval("SELECT COUNT(*) FROM carts")
            
            if legacy_count == cart_count:
                return ValidationResult(
                    check_name="Cart Count Validation",
                    passed=True,
                    message=f"Cart counts match: {legacy_count} carts migrated"
                )
            else:
                return ValidationResult(
                    check_name="Cart Count Validation",
                    passed=False,
                    message=f"Cart count mismatch: Legacy={legacy_count}, Cart={cart_count}"
                )
        finally:
            await legacy_conn.close()
            await cart_conn.close()
    
    async def validate_cart_items_count(self) -> ValidationResult:
        """Validate cart items count matches between legacy and cart DB"""
        legacy_conn = await asyncpg.connect(**DatabaseConfig.LEGACY_DB)
        cart_conn = await asyncpg.connect(**DatabaseConfig.CART_DB)
        
        try:
            legacy_count = await legacy_conn.fetchval("SELECT COUNT(*) FROM cart_items")
            cart_count = await cart_conn.fetchval("SELECT COUNT(*) FROM cart_items")
            
            if legacy_count == cart_count:
                return ValidationResult(
                    check_name="Cart Items Count Validation",
                    passed=True,
                    message=f"Cart item counts match: {legacy_count} items migrated"
                )
            else:
                return ValidationResult(
                    check_name="Cart Items Count Validation",
                    passed=False,
                    message=f"Cart item count mismatch: Legacy={legacy_count}, Cart={cart_count}"
                )
        finally:
            await legacy_conn.close()
            await cart_conn.close()
    
    async def validate_wishlist_count(self) -> ValidationResult:
        """Validate wishlist count matches between legacy and cart DB"""
        legacy_conn = await asyncpg.connect(**DatabaseConfig.LEGACY_DB)
        cart_conn = await asyncpg.connect(**DatabaseConfig.CART_DB)
        
        try:
            legacy_count = await legacy_conn.fetchval("SELECT COUNT(*) FROM wishlists")
            cart_count = await cart_conn.fetchval("SELECT COUNT(*) FROM wishlists")
            
            if legacy_count == cart_count:
                return ValidationResult(
                    check_name="Wishlist Count Validation",
                    passed=True,
                    message=f"Wishlist counts match: {legacy_count} wishlists migrated"
                )
            else:
                return ValidationResult(
                    check_name="Wishlist Count Validation",
                    passed=False,
                    message=f"Wishlist count mismatch: Legacy={legacy_count}, Cart={cart_count}"
                )
        finally:
            await legacy_conn.close()
            await cart_conn.close()
    
    async def validate_promo_codes_count(self) -> ValidationResult:
        """Validate promo codes count matches between legacy and promotion DB"""
        legacy_conn = await asyncpg.connect(**DatabaseConfig.LEGACY_DB)
        promo_conn = await asyncpg.connect(**DatabaseConfig.PROMOTION_DB)
        
        try:
            legacy_count = await legacy_conn.fetchval("SELECT COUNT(*) FROM promo_codes")
            promo_count = await promo_conn.fetchval("SELECT COUNT(*) FROM promo_codes")
            
            if legacy_count == promo_count:
                return ValidationResult(
                    check_name="Promo Codes Count Validation",
                    passed=True,
                    message=f"Promo code counts match: {legacy_count} codes migrated"
                )
            else:
                return ValidationResult(
                    check_name="Promo Codes Count Validation",
                    passed=False,
                    message=f"Promo code count mismatch: Legacy={legacy_count}, Promotion={promo_count}"
                )
        finally:
            await legacy_conn.close()
            await promo_conn.close()
    
    async def validate_data_integrity(self) -> ValidationResult:
        """Validate data integrity constraints"""
        cart_conn = await asyncpg.connect(**DatabaseConfig.CART_DB)
        
        try:
            # Check for negative quantities
            negative_qty = await cart_conn.fetchval(
                "SELECT COUNT(*) FROM cart_items WHERE quantity <= 0"
            )
            
            # Check for negative prices
            negative_price = await cart_conn.fetchval(
                "SELECT COUNT(*) FROM cart_items WHERE unit_price < 0"
            )
            
            # Check for missing snapshots
            missing_snapshots = await cart_conn.fetchval(
                "SELECT COUNT(*) FROM cart_items WHERE product_name_snapshot IS NULL"
            )
            
            issues = []
            if negative_qty > 0:
                issues.append(f"{negative_qty} items with invalid quantity")
            if negative_price > 0:
                issues.append(f"{negative_price} items with negative price")
            if missing_snapshots > 0:
                issues.append(f"{missing_snapshots} items missing product snapshots")
            
            if not issues:
                return ValidationResult(
                    check_name="Data Integrity Validation",
                    passed=True,
                    message="All data integrity constraints satisfied"
                )
            else:
                return ValidationResult(
                    check_name="Data Integrity Validation",
                    passed=False,
                    message=f"Data integrity issues found: {', '.join(issues)}"
                )
        finally:
            await cart_conn.close()
    
    async def validate_reference_consistency(self) -> ValidationResult:
        """Validate cross-service reference consistency"""
        auth_conn = await asyncpg.connect(**DatabaseConfig.AUTH_DB)
        product_conn = await asyncpg.connect(**DatabaseConfig.PRODUCT_DB)
        cart_conn = await asyncpg.connect(**DatabaseConfig.CART_DB)
        
        try:
            # Get all user IDs from auth service
            auth_users = await auth_conn.fetch("SELECT uid FROM users")
            auth_user_ids = {row['uid'] for row in auth_users}
            
            # Get all product IDs from product service
            products = await product_conn.fetch("SELECT id FROM products")
            product_ids = {row['id'] for row in products}
            
            # Check cart user references
            cart_users = await cart_conn.fetch("SELECT DISTINCT user_id_ref FROM carts")
            cart_user_refs = {row['user_id_ref'] for row in cart_users}
            
            # Check cart item product references
            cart_products = await cart_conn.fetch("SELECT DISTINCT product_id_ref FROM cart_items")
            cart_product_refs = {row['product_id_ref'] for row in cart_products}
            
            # Find orphaned references
            orphaned_users = cart_user_refs - auth_user_ids
            orphaned_products = cart_product_refs - product_ids
            
            issues = []
            if orphaned_users:
                issues.append(f"{len(orphaned_users)} orphaned user references")
            if orphaned_products:
                issues.append(f"{len(orphaned_products)} orphaned product references")
            
            if not issues:
                return ValidationResult(
                    check_name="Reference Consistency Validation",
                    passed=True,
                    message="All cross-service references are valid"
                )
            else:
                return ValidationResult(
                    check_name="Reference Consistency Validation",
                    passed=False,
                    message=f"Reference consistency issues: {', '.join(issues)}",
                    details={
                        'orphaned_users': list(orphaned_users),
                        'orphaned_products': list(orphaned_products)
                    }
                )
        finally:
            await auth_conn.close()
            await product_conn.close()
            await cart_conn.close()
    
    async def validate_denormalized_data(self) -> ValidationResult:
        """Validate denormalized data consistency"""
        product_conn = await asyncpg.connect(**DatabaseConfig.PRODUCT_DB)
        cart_conn = await asyncpg.connect(**DatabaseConfig.CART_DB)
        
        try:
            # Check if cart item snapshots match current product data
            mismatched_items = await cart_conn.fetch("""
                SELECT ci.id, ci.product_id_ref, ci.product_name_snapshot, ci.unit_price
                FROM cart_items ci
                WHERE ci.validation_status = 'valid'
                LIMIT 10
            """)
            
            mismatches = 0
            for item in mismatched_items:
                # Get current product data
                product = await product_conn.fetchrow(
                    "SELECT name, price FROM products WHERE id = $1",
                    item['product_id_ref']
                )
                
                if product:
                    if (product['name'] != item['product_name_snapshot'] or 
                        abs(float(product['price']) - float(item['unit_price'])) > 0.01):
                        mismatches += 1
            
            if mismatches == 0:
                return ValidationResult(
                    check_name="Denormalized Data Validation",
                    passed=True,
                    message="Denormalized data is consistent with source data"
                )
            else:
                return ValidationResult(
                    check_name="Denormalized Data Validation",
                    passed=False,
                    message=f"Found {mismatches} items with inconsistent denormalized data"
                )
        finally:
            await product_conn.close()
            await cart_conn.close()

async def main():
    """Main entry point"""
    try:
        validator = MigrationValidator()
        success = await validator.run_all_validations()
        
        if success:
            logger.info("Migration validation completed successfully!")
            sys.exit(0)
        else:
            logger.error("Migration validation failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())