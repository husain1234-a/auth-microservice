#!/usr/bin/env python3
"""
Dual-Write Functionality Test Script

This script tests the dual-write functionality across all services
to ensure data is properly synchronized between new and legacy databases.
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, List
import json
from datetime import datetime

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from dual_write_config import DualWriteSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DualWriteTestSuite:
    """Test suite for dual-write functionality"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.failed_tests = 0
        self.passed_tests = 0
    
    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log a test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.test_results.append(result)
        
        if success:
            self.passed_tests += 1
            logger.info(f"✅ {test_name} - PASSED")
        else:
            self.failed_tests += 1
            logger.error(f"❌ {test_name} - FAILED: {details}")
    
    async def test_cart_service_dual_write(self):
        """Test Cart Service dual-write functionality"""
        logger.info("Testing Cart Service dual-write...")
        
        try:
            # Import cart service modules
            sys.path.append(os.path.join(os.path.dirname(__file__), 'cart_service'))
            from app.core.config import settings as cart_settings
            from app.core.dual_write_manager import CartDualWriteManager
            from app.core.dual_write_config import DualWriteSettings
            
            # Check configuration
            if not cart_settings.legacy_database_url:
                self.log_test_result(
                    "cart_service_config",
                    False,
                    {"error": "Legacy database URL not configured"}
                )
                return
            
            # Create dual-write manager
            dual_write_settings = DualWriteSettings(
                enabled=cart_settings.dual_write_enabled,
                write_to_legacy=cart_settings.dual_write_to_legacy,
                write_to_new=cart_settings.dual_write_to_new,
                fail_on_legacy_error=cart_settings.dual_write_fail_on_legacy_error,
                fail_on_new_error=cart_settings.dual_write_fail_on_new_error,
                validate_sync=cart_settings.dual_write_validate_sync
            )
            
            manager = CartDualWriteManager(
                new_db_url=cart_settings.database_url,
                legacy_db_url=cart_settings.legacy_database_url,
                settings=dual_write_settings
            )
            
            # Test health check
            health_status = await manager.health_check()
            
            self.log_test_result(
                "cart_service_health_check",
                health_status['new_db']['status'] == 'healthy' and 
                health_status['legacy_db']['status'] == 'healthy',
                health_status
            )
            
            # Test cart creation
            test_user_id = f"test_user_{datetime.utcnow().timestamp()}"
            result = await manager.create_cart(test_user_id)
            
            self.log_test_result(
                "cart_service_create_cart",
                result.success,
                result.to_dict()
            )
            
            # Test cart item addition
            if result.success:
                item_result = await manager.add_cart_item(1, 123, 2)
                self.log_test_result(
                    "cart_service_add_item",
                    item_result.success,
                    item_result.to_dict()
                )
            
            await manager.close()
            
        except Exception as e:
            self.log_test_result(
                "cart_service_dual_write",
                False,
                {"error": str(e), "type": type(e).__name__}
            )
    
    async def test_auth_service_dual_write(self):
        """Test Auth Service dual-write functionality"""
        logger.info("Testing Auth Service dual-write...")
        
        try:
            # Import auth service modules
            sys.path.append(os.path.join(os.path.dirname(__file__), 'auth_service'))
            from config.settings import settings as auth_settings
            from app.dual_write_manager import AuthDualWriteManager
            
            # Check configuration
            if not auth_settings.legacy_database_url:
                self.log_test_result(
                    "auth_service_config",
                    False,
                    {"error": "Legacy database URL not configured"}
                )
                return
            
            # Create dual-write manager
            dual_write_settings = DualWriteSettings(
                enabled=auth_settings.dual_write_enabled,
                write_to_legacy=auth_settings.dual_write_to_legacy,
                write_to_new=auth_settings.dual_write_to_new,
                fail_on_legacy_error=auth_settings.dual_write_fail_on_legacy_error,
                fail_on_new_error=auth_settings.dual_write_fail_on_new_error,
                validate_sync=auth_settings.dual_write_validate_sync
            )
            
            manager = AuthDualWriteManager(
                new_db_url=auth_settings.database_url,
                legacy_db_url=auth_settings.legacy_database_url,
                settings=dual_write_settings
            )
            
            # Test health check
            health_status = await manager.health_check()
            
            self.log_test_result(
                "auth_service_health_check",
                health_status['new_db']['status'] == 'healthy' and 
                health_status['legacy_db']['status'] == 'healthy',
                health_status
            )
            
            # Test user creation
            test_user_data = {
                'uid': f"test_user_{datetime.utcnow().timestamp()}",
                'email': 'test@example.com',
                'display_name': 'Test User',
                'role': 'customer',
                'is_active': True
            }
            
            result = await manager.create_user(test_user_data)
            
            self.log_test_result(
                "auth_service_create_user",
                result.success,
                result.to_dict()
            )
            
            await manager.close()
            
        except Exception as e:
            self.log_test_result(
                "auth_service_dual_write",
                False,
                {"error": str(e), "type": type(e).__name__}
            )
    
    async def test_product_service_dual_write(self):
        """Test Product Service dual-write functionality"""
        logger.info("Testing Product Service dual-write...")
        
        try:
            # Import product service modules
            sys.path.append(os.path.join(os.path.dirname(__file__), 'product_service'))
            from app.core.config import settings as product_settings
            from app.dual_write_manager import ProductDualWriteManager
            
            # Check configuration
            if not product_settings.legacy_database_url:
                self.log_test_result(
                    "product_service_config",
                    False,
                    {"error": "Legacy database URL not configured"}
                )
                return
            
            # Create dual-write manager
            dual_write_settings = DualWriteSettings(
                enabled=product_settings.dual_write_enabled,
                write_to_legacy=product_settings.dual_write_to_legacy,
                write_to_new=product_settings.dual_write_to_new,
                fail_on_legacy_error=product_settings.dual_write_fail_on_legacy_error,
                fail_on_new_error=product_settings.dual_write_fail_on_new_error,
                validate_sync=product_settings.dual_write_validate_sync
            )
            
            manager = ProductDualWriteManager(
                new_db_url=product_settings.database_url,
                legacy_db_url=product_settings.legacy_database_url,
                settings=dual_write_settings
            )
            
            # Test health check
            health_status = await manager.health_check()
            
            self.log_test_result(
                "product_service_health_check",
                health_status['new_db']['status'] == 'healthy' and 
                health_status['legacy_db']['status'] == 'healthy',
                health_status
            )
            
            # Test category creation
            test_category_data = {
                'name': f'Test Category {datetime.utcnow().timestamp()}',
                'image_url': 'https://example.com/test.jpg',
                'is_active': True
            }
            
            result = await manager.create_category(test_category_data)
            
            self.log_test_result(
                "product_service_create_category",
                result.success,
                result.to_dict()
            )
            
            await manager.close()
            
        except Exception as e:
            self.log_test_result(
                "product_service_dual_write",
                False,
                {"error": str(e), "type": type(e).__name__}
            )
    
    async def test_configuration_validation(self):
        """Test dual-write configuration validation"""
        logger.info("Testing configuration validation...")
        
        try:
            # Test DualWriteSettings creation from environment
            settings = DualWriteSettings.from_env("CART")
            
            self.log_test_result(
                "config_validation",
                isinstance(settings, DualWriteSettings),
                {"settings": settings.to_dict()}
            )
            
        except Exception as e:
            self.log_test_result(
                "config_validation",
                False,
                {"error": str(e), "type": type(e).__name__}
            )
    
    async def run_all_tests(self):
        """Run all dual-write tests"""
        logger.info("Starting dual-write test suite...")
        
        # Run configuration tests first
        await self.test_configuration_validation()
        
        # Run service-specific tests
        await self.test_cart_service_dual_write()
        await self.test_auth_service_dual_write()
        await self.test_product_service_dual_write()
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate and display test summary report"""
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("\n" + "="*60)
        logger.info("DUAL-WRITE TEST SUMMARY REPORT")
        logger.info("="*60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {self.passed_tests}")
        logger.info(f"Failed: {self.failed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("="*60)
        
        if self.failed_tests > 0:
            logger.info("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    logger.info(f"- {result['test_name']}: {result['details']}")
        
        # Save detailed report to file
        report_file = f"dual_write_test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': self.passed_tests,
                    'failed_tests': self.failed_tests,
                    'success_rate': success_rate
                },
                'test_results': self.test_results
            }, f, indent=2)
        
        logger.info(f"\nDetailed report saved to: {report_file}")


async def main():
    """Main test execution function"""
    test_suite = DualWriteTestSuite()
    
    try:
        await test_suite.run_all_tests()
        
        # Exit with error code if tests failed
        if test_suite.failed_tests > 0:
            sys.exit(1)
        else:
            logger.info("All tests passed! ✅")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Test suite execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())