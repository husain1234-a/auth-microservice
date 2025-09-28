#!/usr/bin/env python3
"""
Data Synchronization Validation Script

This script validates data synchronization between new isolated databases
and the legacy shared database during the dual-write migration phase.
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSyncValidator:
    """Validates data synchronization between databases"""
    
    def __init__(self):
        self.validation_results: List[Dict[str, Any]] = []
        self.sync_issues = 0
        self.validated_entities = 0
    
    async def validate_user_sync(self, auth_db_url: str, legacy_db_url: str) -> Dict[str, Any]:
        """Validate user data synchronization between auth_db and legacy database"""
        logger.info("Validating user data synchronization...")
        
        auth_engine = create_async_engine(auth_db_url)
        legacy_engine = create_async_engine(legacy_db_url)
        
        auth_session_factory = async_sessionmaker(bind=auth_engine)
        legacy_session_factory = async_sessionmaker(bind=legacy_engine)
        
        validation_result = {
            'entity_type': 'users',
            'total_users': 0,
            'synchronized_users': 0,
            'sync_issues': [],
            'validation_timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Get all users from auth database
            async with auth_session_factory() as auth_session:
                auth_result = await auth_session.execute(
                    text("SELECT uid, email, display_name, role, is_active, created_at FROM users ORDER BY uid")
                )
                auth_users = auth_result.fetchall()
            
            validation_result['total_users'] = len(auth_users)
            
            # Check each user in legacy database
            async with legacy_session_factory() as legacy_session:
                for auth_user in auth_users:
                    legacy_result = await legacy_session.execute(
                        text("SELECT uid, email, display_name, role, is_active, created_at FROM users WHERE uid = :uid"),
                        {'uid': auth_user.uid}
                    )
                    legacy_user = legacy_result.fetchone()
                    
                    if not legacy_user:
                        validation_result['sync_issues'].append({
                            'uid': auth_user.uid,
                            'issue': 'User exists in auth_db but not in legacy database'
                        })
                        self.sync_issues += 1
                    else:
                        # Compare user data
                        differences = []
                        
                        if auth_user.email != legacy_user.email:
                            differences.append(f"email: auth='{auth_user.email}' vs legacy='{legacy_user.email}'")
                        
                        if auth_user.display_name != legacy_user.display_name:
                            differences.append(f"display_name: auth='{auth_user.display_name}' vs legacy='{legacy_user.display_name}'")
                        
                        if auth_user.role != legacy_user.role:
                            differences.append(f"role: auth='{auth_user.role}' vs legacy='{legacy_user.role}'")
                        
                        if auth_user.is_active != legacy_user.is_active:
                            differences.append(f"is_active: auth={auth_user.is_active} vs legacy={legacy_user.is_active}")
                        
                        if differences:
                            validation_result['sync_issues'].append({
                                'uid': auth_user.uid,
                                'issue': 'Data differences found',
                                'differences': differences
                            })
                            self.sync_issues += 1
                        else:
                            validation_result['synchronized_users'] += 1
                    
                    self.validated_entities += 1
        
        except Exception as e:
            logger.error(f"Error validating user sync: {e}")
            validation_result['error'] = str(e)
        
        finally:
            await auth_engine.dispose()
            await legacy_engine.dispose()
        
        self.validation_results.append(validation_result)
        return validation_result
    
    async def validate_product_sync(self, product_db_url: str, legacy_db_url: str) -> Dict[str, Any]:
        """Validate product data synchronization between product_db and legacy database"""
        logger.info("Validating product data synchronization...")
        
        product_engine = create_async_engine(product_db_url)
        legacy_engine = create_async_engine(legacy_db_url)
        
        product_session_factory = async_sessionmaker(bind=product_engine)
        legacy_session_factory = async_sessionmaker(bind=legacy_engine)
        
        validation_result = {
            'entity_type': 'products',
            'total_products': 0,
            'synchronized_products': 0,
            'sync_issues': [],
            'validation_timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Get all products from product database
            async with product_session_factory() as product_session:
                product_result = await product_session.execute(
                    text("SELECT id, name, price, stock_quantity, is_active FROM products ORDER BY id")
                )
                products = product_result.fetchall()
            
            validation_result['total_products'] = len(products)
            
            # Check each product in legacy database
            async with legacy_session_factory() as legacy_session:
                for product in products:
                    legacy_result = await legacy_session.execute(
                        text("SELECT id, name, price, stock_quantity, is_active FROM products WHERE id = :id"),
                        {'id': product.id}
                    )
                    legacy_product = legacy_result.fetchone()
                    
                    if not legacy_product:
                        validation_result['sync_issues'].append({
                            'product_id': product.id,
                            'issue': 'Product exists in product_db but not in legacy database'
                        })
                        self.sync_issues += 1
                    else:
                        # Compare product data
                        differences = []
                        
                        if product.name != legacy_product.name:
                            differences.append(f"name: product='{product.name}' vs legacy='{legacy_product.name}'")
                        
                        if abs(float(product.price) - float(legacy_product.price)) > 0.01:
                            differences.append(f"price: product={product.price} vs legacy={legacy_product.price}")
                        
                        if product.stock_quantity != legacy_product.stock_quantity:
                            differences.append(f"stock: product={product.stock_quantity} vs legacy={legacy_product.stock_quantity}")
                        
                        if product.is_active != legacy_product.is_active:
                            differences.append(f"is_active: product={product.is_active} vs legacy={legacy_product.is_active}")
                        
                        if differences:
                            validation_result['sync_issues'].append({
                                'product_id': product.id,
                                'issue': 'Data differences found',
                                'differences': differences
                            })
                            self.sync_issues += 1
                        else:
                            validation_result['synchronized_products'] += 1
                    
                    self.validated_entities += 1
        
        except Exception as e:
            logger.error(f"Error validating product sync: {e}")
            validation_result['error'] = str(e)
        
        finally:
            await product_engine.dispose()
            await legacy_engine.dispose()
        
        self.validation_results.append(validation_result)
        return validation_result
    
    async def validate_cart_sync(self, cart_db_url: str, legacy_db_url: str) -> Dict[str, Any]:
        """Validate cart data synchronization between cart_db and legacy database"""
        logger.info("Validating cart data synchronization...")
        
        cart_engine = create_async_engine(cart_db_url)
        legacy_engine = create_async_engine(legacy_db_url)
        
        cart_session_factory = async_sessionmaker(bind=cart_engine)
        legacy_session_factory = async_sessionmaker(bind=legacy_engine)
        
        validation_result = {
            'entity_type': 'carts',
            'total_carts': 0,
            'synchronized_carts': 0,
            'total_cart_items': 0,
            'synchronized_cart_items': 0,
            'sync_issues': [],
            'validation_timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Validate carts
            async with cart_session_factory() as cart_session:
                cart_result = await cart_session.execute(
                    text("SELECT id, user_id FROM carts ORDER BY id")
                )
                carts = cart_result.fetchall()
            
            validation_result['total_carts'] = len(carts)
            
            async with legacy_session_factory() as legacy_session:
                for cart in carts:
                    legacy_result = await legacy_session.execute(
                        text("SELECT id, user_id FROM carts WHERE id = :id"),
                        {'id': cart.id}
                    )
                    legacy_cart = legacy_result.fetchone()
                    
                    if not legacy_cart:
                        validation_result['sync_issues'].append({
                            'cart_id': cart.id,
                            'issue': 'Cart exists in cart_db but not in legacy database'
                        })
                        self.sync_issues += 1
                    elif cart.user_id != legacy_cart.user_id:
                        validation_result['sync_issues'].append({
                            'cart_id': cart.id,
                            'issue': f'User ID mismatch: cart_db={cart.user_id} vs legacy={legacy_cart.user_id}'
                        })
                        self.sync_issues += 1
                    else:
                        validation_result['synchronized_carts'] += 1
                    
                    self.validated_entities += 1
            
            # Validate cart items
            async with cart_session_factory() as cart_session:
                item_result = await cart_session.execute(
                    text("SELECT id, cart_id, product_id, quantity FROM cart_items ORDER BY id")
                )
                cart_items = item_result.fetchall()
            
            validation_result['total_cart_items'] = len(cart_items)
            
            async with legacy_session_factory() as legacy_session:
                for item in cart_items:
                    legacy_result = await legacy_session.execute(
                        text("SELECT id, cart_id, product_id, quantity FROM cart_items WHERE id = :id"),
                        {'id': item.id}
                    )
                    legacy_item = legacy_result.fetchone()
                    
                    if not legacy_item:
                        validation_result['sync_issues'].append({
                            'cart_item_id': item.id,
                            'issue': 'Cart item exists in cart_db but not in legacy database'
                        })
                        self.sync_issues += 1
                    else:
                        differences = []
                        
                        if item.cart_id != legacy_item.cart_id:
                            differences.append(f"cart_id: cart_db={item.cart_id} vs legacy={legacy_item.cart_id}")
                        
                        if item.product_id != legacy_item.product_id:
                            differences.append(f"product_id: cart_db={item.product_id} vs legacy={legacy_item.product_id}")
                        
                        if item.quantity != legacy_item.quantity:
                            differences.append(f"quantity: cart_db={item.quantity} vs legacy={legacy_item.quantity}")
                        
                        if differences:
                            validation_result['sync_issues'].append({
                                'cart_item_id': item.id,
                                'issue': 'Data differences found',
                                'differences': differences
                            })
                            self.sync_issues += 1
                        else:
                            validation_result['synchronized_cart_items'] += 1
                    
                    self.validated_entities += 1
        
        except Exception as e:
            logger.error(f"Error validating cart sync: {e}")
            validation_result['error'] = str(e)
        
        finally:
            await cart_engine.dispose()
            await legacy_engine.dispose()
        
        self.validation_results.append(validation_result)
        return validation_result
    
    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete data synchronization validation"""
        logger.info("Starting comprehensive data synchronization validation...")
        
        # Database URLs (these would typically come from configuration)
        auth_db_url = "postgresql+asyncpg://poc_user:admin123@localhost:5432/auth_db"
        product_db_url = "postgresql+asyncpg://poc_user:admin123@localhost:5432/product_db"
        cart_db_url = "postgresql+asyncpg://poc_user:admin123@localhost:5432/cart_db"
        legacy_db_url = "postgresql+asyncpg://poc_user:admin123@localhost:5432/poc"
        
        # Run validations
        user_validation = await self.validate_user_sync(auth_db_url, legacy_db_url)
        product_validation = await self.validate_product_sync(product_db_url, legacy_db_url)
        cart_validation = await self.validate_cart_sync(cart_db_url, legacy_db_url)
        
        # Generate summary report
        summary = {
            'validation_timestamp': datetime.utcnow().isoformat(),
            'total_entities_validated': self.validated_entities,
            'total_sync_issues': self.sync_issues,
            'sync_success_rate': ((self.validated_entities - self.sync_issues) / self.validated_entities * 100) if self.validated_entities > 0 else 0,
            'validations': {
                'users': user_validation,
                'products': product_validation,
                'carts': cart_validation
            }
        }
        
        return summary
    
    def generate_report(self, summary: Dict[str, Any]):
        """Generate and save validation report"""
        logger.info("\n" + "="*60)
        logger.info("DATA SYNCHRONIZATION VALIDATION REPORT")
        logger.info("="*60)
        logger.info(f"Total Entities Validated: {summary['total_entities_validated']}")
        logger.info(f"Synchronization Issues Found: {summary['total_sync_issues']}")
        logger.info(f"Sync Success Rate: {summary['sync_success_rate']:.1f}%")
        logger.info("="*60)
        
        # Print detailed results
        for validation_type, validation_data in summary['validations'].items():
            logger.info(f"\n{validation_type.upper()} VALIDATION:")
            
            if validation_type == 'users':
                logger.info(f"  Total Users: {validation_data['total_users']}")
                logger.info(f"  Synchronized: {validation_data['synchronized_users']}")
                logger.info(f"  Issues: {len(validation_data['sync_issues'])}")
            
            elif validation_type == 'products':
                logger.info(f"  Total Products: {validation_data['total_products']}")
                logger.info(f"  Synchronized: {validation_data['synchronized_products']}")
                logger.info(f"  Issues: {len(validation_data['sync_issues'])}")
            
            elif validation_type == 'carts':
                logger.info(f"  Total Carts: {validation_data['total_carts']}")
                logger.info(f"  Synchronized Carts: {validation_data['synchronized_carts']}")
                logger.info(f"  Total Cart Items: {validation_data['total_cart_items']}")
                logger.info(f"  Synchronized Items: {validation_data['synchronized_cart_items']}")
                logger.info(f"  Issues: {len(validation_data['sync_issues'])}")
            
            # Show first few issues if any
            if validation_data['sync_issues']:
                logger.info(f"  Sample Issues:")
                for issue in validation_data['sync_issues'][:3]:
                    logger.info(f"    - {issue}")
                if len(validation_data['sync_issues']) > 3:
                    logger.info(f"    ... and {len(validation_data['sync_issues']) - 3} more")
        
        # Save detailed report to file
        report_file = f"data_sync_validation_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\nDetailed report saved to: {report_file}")
        
        if summary['total_sync_issues'] > 0:
            logger.warning(f"⚠️  {summary['total_sync_issues']} synchronization issues found!")
        else:
            logger.info("✅ All data is properly synchronized!")


async def main():
    """Main validation execution function"""
    validator = DataSyncValidator()
    
    try:
        summary = await validator.run_full_validation()
        validator.generate_report(summary)
        
        # Exit with error code if sync issues found
        if summary['total_sync_issues'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Validation execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())